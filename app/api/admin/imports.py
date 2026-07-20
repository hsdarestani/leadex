"""
Admin Imports API
Endpoints for lead import and bulk operations
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models import AdminUser, ImportHistory, ImportStatus, Asset
from app.api.dependencies import get_current_admin
from app.services.import_service import ImportService
import uuid

router = APIRouter()


class ImportHistoryResponse(BaseModel):
    """Import history response"""
    id: str
    filename: str
    file_size: Optional[int]
    file_type: Optional[str]
    status: str
    total_rows: int
    processed_rows: int
    successful_imports: int
    failed_imports: int
    duplicate_skipped: int
    success_rate: float
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    processing_time_seconds: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ImportStatsResponse(BaseModel):
    """Import statistics"""
    total_imports: int
    completed_imports: int
    failed_imports: int
    partial_imports: int
    total_leads_imported: int
    total_duplicates_skipped: int
    average_success_rate: float


class BulkUpdateRequest(BaseModel):
    """Bulk update request"""
    lead_ids: List[str]
    status: Optional[str] = None
    campaign_id: Optional[str] = None
    landing_page_id: Optional[str] = None


class BulkUpdateResponse(BaseModel):
    """Bulk update response"""
    updated_count: int
    failed_count: int
    errors: List[str]


@router.post("/upload", response_model=ImportHistoryResponse)
async def upload_leads(
    file: UploadFile = File(...),
    campaign_id: Optional[str] = Form(None),
    landing_page_id: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
    skip_duplicates: bool = Form(True),
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Upload and import leads from CSV or Excel file
    
    Supports CSV and Excel (.xlsx, .xls) files
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    file_ext = file.filename.lower().split('.')[-1]
    if file_ext not in ['csv', 'xlsx', 'xls']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV and Excel files are supported"
        )
    
    # Validate file size (max 10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 10MB limit"
        )
    
    # Parse UUIDs
    campaign_uuid = None
    if campaign_id:
        try:
            campaign_uuid = uuid.UUID(campaign_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid campaign_id format"
            )
    
    landing_page_uuid = None
    if landing_page_id:
        try:
            landing_page_uuid = uuid.UUID(landing_page_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid landing_page_id format"
            )
    
    # Import leads
    try:
        import_record = ImportService.import_leads(
            db=db,
            file_content=content,
            filename=file.filename,
            admin_user_id=admin.id,
            campaign_id=campaign_uuid,
            landing_page_id=landing_page_uuid,
            source=source,
            skip_duplicates=skip_duplicates
        )
        
        return ImportHistoryResponse(
            id=str(import_record.id),
            filename=import_record.filename,
            file_size=import_record.file_size,
            file_type=import_record.file_type,
            status=import_record.status.value,
            total_rows=import_record.total_rows,
            processed_rows=import_record.processed_rows,
            successful_imports=import_record.successful_imports,
            failed_imports=import_record.failed_imports,
            duplicate_skipped=import_record.duplicate_skipped,
            success_rate=import_record.success_rate,
            error_message=import_record.error_message,
            started_at=import_record.started_at,
            completed_at=import_record.completed_at,
            processing_time_seconds=import_record.processing_time_seconds,
            created_at=import_record.created_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )


@router.get("/history", response_model=List[ImportHistoryResponse])
def get_import_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get import history
    
    Returns a list of import records with optional filtering
    """
    query = db.query(ImportHistory)
    
    if status_filter:
        try:
            status_enum = ImportStatus(status_filter)
            query = query.filter(ImportHistory.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    query = query.order_by(ImportHistory.created_at.desc())
    query = query.offset(offset).limit(limit)
    
    imports = query.all()
    
    return [
        ImportHistoryResponse(
            id=str(imp.id),
            filename=imp.filename,
            file_size=imp.file_size,
            file_type=imp.file_type,
            status=imp.status.value,
            total_rows=imp.total_rows,
            processed_rows=imp.processed_rows,
            successful_imports=imp.successful_imports,
            failed_imports=imp.failed_imports,
            duplicate_skipped=imp.duplicate_skipped,
            success_rate=imp.success_rate,
            error_message=imp.error_message,
            started_at=imp.started_at,
            completed_at=imp.completed_at,
            processing_time_seconds=imp.processing_time_seconds,
            created_at=imp.created_at
        )
        for imp in imports
    ]


@router.get("/history/{import_id}", response_model=ImportHistoryResponse)
def get_import_details(
    import_id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific import
    """
    try:
        import_uuid = uuid.UUID(import_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid import_id format"
        )

    import_record = db.query(ImportHistory).filter(ImportHistory.id == import_uuid).first()

    if not import_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import not found"
        )

    return ImportHistoryResponse(
        id=str(import_record.id),
        filename=import_record.filename,
        file_size=import_record.file_size,
        file_type=import_record.file_type,
        status=import_record.status.value,
        total_rows=import_record.total_rows,
        processed_rows=import_record.processed_rows,
        successful_imports=import_record.successful_imports,
        failed_imports=import_record.failed_imports,
        duplicate_skipped=import_record.duplicate_skipped,
        success_rate=import_record.success_rate,
        error_message=import_record.error_message,
        started_at=import_record.started_at,
        completed_at=import_record.completed_at,
        processing_time_seconds=import_record.processing_time_seconds,
        created_at=import_record.created_at
    )


@router.get("/stats", response_model=ImportStatsResponse)
def get_import_stats(
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get import statistics
    """
    from sqlalchemy import func

    total_imports = db.query(ImportHistory).count()
    completed_imports = db.query(ImportHistory).filter(
        ImportHistory.status == ImportStatus.COMPLETED
    ).count()
    failed_imports = db.query(ImportHistory).filter(
        ImportHistory.status == ImportStatus.FAILED
    ).count()
    partial_imports = db.query(ImportHistory).filter(
        ImportHistory.status == ImportStatus.PARTIAL
    ).count()

    total_leads_imported = db.query(func.sum(ImportHistory.successful_imports)).scalar() or 0
    total_duplicates_skipped = db.query(func.sum(ImportHistory.duplicate_skipped)).scalar() or 0

    # Calculate average success rate
    avg_success_rate = db.query(func.avg(
        (ImportHistory.successful_imports * 100.0) / ImportHistory.total_rows
    )).filter(
        ImportHistory.total_rows > 0
    ).scalar() or 0.0

    return ImportStatsResponse(
        total_imports=total_imports,
        completed_imports=completed_imports,
        failed_imports=failed_imports,
        partial_imports=partial_imports,
        total_leads_imported=int(total_leads_imported),
        total_duplicates_skipped=int(total_duplicates_skipped),
        average_success_rate=round(avg_success_rate, 2)
    )


@router.post("/bulk-update", response_model=BulkUpdateResponse)
def bulk_update_leads(
    request: BulkUpdateRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Bulk update leads

    Update status, campaign, or landing page for multiple leads
    """
    errors = []
    updated_count = 0
    failed_count = 0

    # Parse UUIDs
    lead_uuids = []
    for lead_id in request.lead_ids:
        try:
            lead_uuids.append(uuid.UUID(lead_id))
        except ValueError:
            errors.append(f"Invalid lead_id: {lead_id}")
            failed_count += 1

    # Get leads
    leads = db.query(Asset).filter(Asset.id.in_(lead_uuids)).all()

    if len(leads) != len(lead_uuids):
        failed_count += len(lead_uuids) - len(leads)
        errors.append(f"{len(lead_uuids) - len(leads)} leads not found")

    # Update leads
    for lead in leads:
        try:
            if request.status:
                lead.status = request.status

            if request.campaign_id:
                try:
                    lead.campaign_id = uuid.UUID(request.campaign_id)
                except ValueError:
                    errors.append(f"Invalid campaign_id for lead {lead.id}")
                    failed_count += 1
                    continue

            if request.landing_page_id:
                try:
                    lead.landing_page_id = uuid.UUID(request.landing_page_id)
                except ValueError:
                    errors.append(f"Invalid landing_page_id for lead {lead.id}")
                    failed_count += 1
                    continue

            updated_count += 1

        except Exception as e:
            errors.append(f"Error updating lead {lead.id}: {str(e)}")
            failed_count += 1

    db.commit()

    return BulkUpdateResponse(
        updated_count=updated_count,
        failed_count=failed_count,
        errors=errors
    )

