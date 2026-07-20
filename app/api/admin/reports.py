"""
Reports and export API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import Integer
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.models.report import Report, ReportSchedule, ReportExport
from app.services.report_service import ReportService, REPORT_TEMPLATES
from app.api.dependencies import get_current_admin

router = APIRouter(tags=["Reports"])


# Request/Response models
class ReportCreate(BaseModel):
    name: str
    description: Optional[str] = None
    report_type: str
    fields: List[str]
    filters: Optional[dict] = None
    grouping: Optional[dict] = None
    aggregations: Optional[dict] = None
    sorting: Optional[dict] = None


class ReportUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[List[str]] = None
    filters: Optional[dict] = None
    grouping: Optional[dict] = None
    aggregations: Optional[dict] = None
    sorting: Optional[dict] = None
    is_active: Optional[bool] = None


class ReportScheduleCreate(BaseModel):
    report_id: str
    frequency: str  # daily, weekly, monthly, custom
    cron_expression: Optional[str] = None
    day_of_week: Optional[int] = None
    day_of_month: Optional[int] = None
    time_of_day: str = "09:00"
    delivery_method: str = "email"
    recipients: List[str]
    export_format: str = "pdf"


class ExportRequest(BaseModel):
    report_id: str
    export_format: str  # pdf, excel, csv


# Endpoints
@router.post("/create")
async def create_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Create a new custom report"""
    try:
        service = ReportService(db)
        report = service.create_report(
            name=report_data.name,
            description=report_data.description,
            report_type=report_data.report_type,
            fields=report_data.fields,
            filters=report_data.filters,
            grouping=report_data.grouping,
            aggregations=report_data.aggregations,
            sorting=report_data.sorting,
            created_by_admin_id=str(current_admin.id)
        )

        return {
            'success': True,
            'message': 'Report created successfully',
            'report_id': str(report.id),
            'report': {
                'id': str(report.id),
                'name': report.name,
                'description': report.description,
                'report_type': report.report_type,
                'fields': report.fields,
                'created_at': report.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating report: {str(e)}"
        )


@router.get("/list")
async def list_reports(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """List all saved reports"""
    try:
        reports = db.query(Report).filter(
            Report.is_template == False,
            Report.is_active == True
        ).all()

        return {
            'success': True,
            'reports': [
                {
                    'id': str(r.id),
                    'name': r.name,
                    'description': r.description,
                    'report_type': r.report_type,
                    'fields': r.fields,
                    'created_at': r.created_at.isoformat(),
                    'is_template': r.is_template
                }
                for r in reports
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching reports: {str(e)}"
        )


@router.get("/{report_id}")
async def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Get a specific report"""
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        return {
            'success': True,
            'report': {
                'id': str(report.id),
                'name': report.name,
                'description': report.description,
                'report_type': report.report_type,
                'fields': report.fields,
                'filters': report.filters,
                'grouping': report.grouping,
                'aggregations': report.aggregations,
                'sorting': report.sorting,
                'created_at': report.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching report: {str(e)}"
        )


@router.put("/{report_id}")
async def update_report(
    report_id: str,
    report_data: ReportUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Update a report"""
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        # Update fields
        if report_data.name is not None:
            report.name = report_data.name
        if report_data.description is not None:
            report.description = report_data.description
        if report_data.fields is not None:
            report.fields = report_data.fields
        if report_data.filters is not None:
            report.filters = report_data.filters
        if report_data.grouping is not None:
            report.grouping = report_data.grouping
        if report_data.aggregations is not None:
            report.aggregations = report_data.aggregations
        if report_data.sorting is not None:
            report.sorting = report_data.sorting
        if report_data.is_active is not None:
            report.is_active = report_data.is_active

        report.updated_at = datetime.utcnow()

        db.commit()

        return {
            'success': True,
            'message': 'Report updated successfully'
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating report: {str(e)}"
        )


@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Delete a report"""
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        db.delete(report)
        db.commit()

        return {
            'success': True,
            'message': 'Report deleted successfully'
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting report: {str(e)}"
        )


@router.post("/export")
async def export_report(
    export_data: ExportRequest,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Export a report to file"""
    try:
        service = ReportService(db)
        export = service.create_export(
            report_id=export_data.report_id,
            export_format=export_data.export_format,
            generated_by_admin_id=str(current_admin.id)
        )

        if export.status == 'completed':
            return {
                'success': True,
                'message': 'Report exported successfully',
                'export_id': str(export.id),
                'file_path': export.file_path,
                'file_size': export.file_size,
                'record_count': export.record_count
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Export failed: {export.error_message}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting report: {str(e)}"
        )


@router.get("/download/{export_id}")
async def download_export(
    export_id: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Download an exported report file"""
    try:
        export = db.query(ReportExport).filter(ReportExport.id == export_id).first()
        if not export:
            raise HTTPException(status_code=404, detail="Export not found")

        if export.status != 'completed':
            raise HTTPException(status_code=400, detail="Export not completed")

        import os
        if not os.path.exists(export.file_path):
            raise HTTPException(status_code=404, detail="Export file not found")

        # Determine media type
        media_types = {
            'pdf': 'application/pdf',
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'csv': 'text/csv'
        }
        media_type = media_types.get(export.export_format, 'application/octet-stream')

        return FileResponse(
            export.file_path,
            media_type=media_type,
            filename=os.path.basename(export.file_path)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading export: {str(e)}"
        )


@router.get("/templates/list")
async def list_templates(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """List available report templates"""
    return {
        'success': True,
        'templates': [
            {
                'id': key,
                'name': template['name'],
                'description': template['description'],
                'report_type': template['report_type'],
                'fields': template['fields']
            }
            for key, template in REPORT_TEMPLATES.items()
        ]
    }


@router.post("/templates/{template_id}/create")
async def create_from_template(
    template_id: str,
    name: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Create a report from a template"""
    try:
        if template_id not in REPORT_TEMPLATES:
            raise HTTPException(status_code=404, detail="Template not found")

        template = REPORT_TEMPLATES[template_id]
        service = ReportService(db)

        report = service.create_report(
            name=name,
            description=template['description'],
            report_type=template['report_type'],
            fields=template['fields'],
            created_by_admin_id=str(current_admin.id)
        )

        return {
            'success': True,
            'message': 'Report created from template',
            'report_id': str(report.id)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating report from template: {str(e)}"
        )


@router.post("/schedule/create")
async def create_schedule(
    schedule_data: ReportScheduleCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Schedule automated report generation and delivery"""
    try:
        # Validate report exists
        report = db.query(Report).filter(Report.id == schedule_data.report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        # Create schedule
        schedule = ReportSchedule(
            report_id=schedule_data.report_id,
            frequency=schedule_data.frequency,
            cron_expression=schedule_data.cron_expression,
            day_of_week=schedule_data.day_of_week,
            day_of_month=schedule_data.day_of_month,
            time_of_day=schedule_data.time_of_day,
            delivery_method=schedule_data.delivery_method,
            recipients=schedule_data.recipients,
            export_format=schedule_data.export_format
        )

        db.add(schedule)
        db.commit()
        db.refresh(schedule)

        return {
            'success': True,
            'message': 'Report schedule created successfully',
            'schedule_id': str(schedule.id)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating schedule: {str(e)}"
        )


@router.get("/schedule/list")
async def list_schedules(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """List all scheduled reports"""
    try:
        schedules = db.query(ReportSchedule).filter(ReportSchedule.is_active == True).all()

        return {
            'success': True,
            'schedules': [
                {
                    'id': str(s.id),
                    'report_id': str(s.report_id),
                    'report_name': s.report.name,
                    'frequency': s.frequency,
                    'time_of_day': s.time_of_day,
                    'recipients': s.recipients,
                    'export_format': s.export_format,
                    'is_active': s.is_active,
                    'last_run': s.last_run.isoformat() if s.last_run else None,
                    'next_run': s.next_run.isoformat() if s.next_run else None
                }
                for s in schedules
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching schedules: {str(e)}"
        )


@router.delete("/schedule/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Delete a scheduled report"""
    try:
        schedule = db.query(ReportSchedule).filter(ReportSchedule.id == schedule_id).first()
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        db.delete(schedule)
        db.commit()

        return {
            'success': True,
            'message': 'Schedule deleted successfully'
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting schedule: {str(e)}"
        )


@router.get("/exports/history")
async def export_history(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Get export history"""
    try:
        exports = db.query(ReportExport).order_by(ReportExport.generated_at.desc()).limit(50).all()

        return {
            'success': True,
            'exports': [
                {
                    'id': str(e.id),
                    'report_id': str(e.report_id),
                    'report_name': e.report.name,
                    'export_format': e.export_format,
                    'file_size': e.file_size,
                    'record_count': e.record_count,
                    'status': e.status,
                    'generated_at': e.generated_at.isoformat() if e.generated_at else None
                }
                for e in exports
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching export history: {str(e)}"
        )


# Quick Report Generation Endpoints (No Database Storage)
@router.get("/quick/lead-summary")
async def quick_lead_summary(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Generate quick lead summary report"""
    from app.models.asset import Asset
    from app.models.client import Client
    from sqlalchemy import func
    
    total_leads = db.query(Asset).count()
    status_breakdown = db.query(Asset.status, func.count(Asset.id)).group_by(Asset.status).all()
    
    # Leads by client (through deliveries)
    from app.models.delivery import Delivery
    leads_by_client = db.query(
        Client.name,
        func.count(func.distinct(Delivery.asset_id)).label('count')
    ).outerjoin(
        Delivery, Delivery.client_id == Client.id
    ).group_by(Client.name).all()
    
    # Leads by date (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_leads = db.query(
        func.date(Asset.created_at).label('date'),
        func.count(Asset.id).label('count')
    ).filter(Asset.created_at >= thirty_days_ago).group_by(func.date(Asset.created_at)).all()
    
    return {
        "report_type": "lead_summary",
        "generated_at": datetime.utcnow().isoformat(),
        "data": {
            "total_leads": total_leads,
            "status_breakdown": {status: count for status, count in status_breakdown},
            "leads_by_client": [{"client": name, "count": count} for name, count in leads_by_client],
            "recent_leads": [{"date": str(date), "count": count} for date, count in recent_leads]
        }
    }


@router.get("/quick/performance")
async def quick_performance_report(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Generate quick performance report"""
    from app.models.delivery import Delivery
    from app.models.client import Client
    from sqlalchemy import func
    
    # Delivery success rate by client
    delivery_stats = db.query(
        Client.name,
        func.count(Delivery.id).label('total'),
        func.sum(func.cast(Delivery.success, Integer)).label('successful')
    ).join(Delivery).group_by(Client.name).all()
    
    # Delivery method breakdown
    method_stats = db.query(
        Delivery.delivery_method,
        func.count(Delivery.id).label('count'),
        func.sum(func.cast(Delivery.success, Integer)).label('successful')
    ).group_by(Delivery.delivery_method).all()
    
    return {
        "report_type": "performance",
        "generated_at": datetime.utcnow().isoformat(),
        "data": {
            "client_performance": [
                {
                    "client": name,
                    "total_deliveries": total,
                    "successful": successful or 0,
                    "success_rate": round((successful or 0) / total * 100, 2) if total > 0 else 0
                }
                for name, total, successful in delivery_stats
            ],
            "delivery_methods": [
                {
                    "method": method,
                    "total": count,
                    "successful": successful or 0,
                    "success_rate": round((successful or 0) / count * 100, 2) if count > 0 else 0
                }
                for method, count, successful in method_stats
            ]
        }
    }


@router.get("/quick/revenue")
async def quick_revenue_report(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Generate quick revenue report"""
    from app.models.client import Client
    from app.models.delivery import Delivery
    from sqlalchemy import func
    
    clients = db.query(Client).all()
    
    revenue_data = []
    for client in clients:
        deliveries = db.query(Delivery).filter(Delivery.client_id == client.id).count()
        total_cost = deliveries * client.credit_cost_per_lead
        
        revenue_data.append({
            "client": client.name,
            "credits_balance": client.credits_balance,
            "cost_per_lead": client.credit_cost_per_lead,
            "total_deliveries": deliveries,
            "total_spent": total_cost,
            "status": client.status
        })
    
    total_revenue = sum(item["total_spent"] for item in revenue_data)
    total_balance = sum(item["credits_balance"] for item in revenue_data)
    
    return {
        "report_type": "revenue",
        "generated_at": datetime.utcnow().isoformat(),
        "data": {
            "total_revenue": total_revenue,
            "total_credits_balance": total_balance,
            "clients": revenue_data
        }
    }


@router.get("/quick/clients")
async def quick_clients_report(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Generate quick clients report"""
    from app.models.client import Client
    from app.models.delivery import Delivery
    from sqlalchemy import func
    
    clients = db.query(Client).all()
    
    clients_data = []
    for client in clients:
        deliveries = db.query(Delivery).filter(Delivery.client_id == client.id)
        total_deliveries = deliveries.count()
        successful = deliveries.filter(Delivery.success == True).count()
        
        clients_data.append({
            "id": str(client.id),
            "name": client.name,
            "email": client.email,
            "phone": client.phone_number,
            "status": client.status,
            "credits_balance": client.credits_balance,
            "cost_per_lead": client.credit_cost_per_lead,
            "delivery_methods": {
                "webhook": client.accept_webhook,
                "sheets": client.accept_sheets,
                "email": client.accept_email,
                "sms": client.accept_sms
            },
            "total_deliveries": total_deliveries,
            "successful_deliveries": successful,
            "success_rate": round(successful / total_deliveries * 100, 2) if total_deliveries > 0 else 0,
            "created_at": client.created_at.isoformat() if client.created_at else None
        })
    
    return {
        "report_type": "clients",
        "generated_at": datetime.utcnow().isoformat(),
        "data": {
            "total_clients": len(clients_data),
            "active_clients": len([c for c in clients_data if c["status"] == "active"]),
            "clients": clients_data
        }
    }


@router.get("/quick/webhooks")
async def quick_webhooks_report(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Generate quick webhooks activity report"""
    from app.models.delivery import Delivery
    from app.models.client import Client
    from sqlalchemy import func, desc
    from datetime import datetime, timedelta
    
    # Recent webhook deliveries (last 100)
    webhook_deliveries = db.query(Delivery).filter(
        Delivery.delivery_method == "webhook"
    ).order_by(desc(Delivery.timestamp)).limit(100).all()
    
    # Webhook stats by client
    webhook_stats = db.query(
        Client.name,
        func.count(Delivery.id).label('total'),
        func.sum(func.cast(Delivery.success, Integer)).label('successful')
    ).join(Delivery).filter(
        Delivery.delivery_method == "webhook"
    ).group_by(Client.name).all()
    
    # Last 7 days activity
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_activity = db.query(
        func.date(Delivery.timestamp).label('date'),
        func.count(Delivery.id).label('total'),
        func.sum(func.cast(Delivery.success, Integer)).label('successful')
    ).filter(
        Delivery.delivery_method == "webhook",
        Delivery.timestamp >= seven_days_ago
    ).group_by(func.date(Delivery.timestamp)).all()
    
    return {
        "report_type": "webhooks",
        "generated_at": datetime.utcnow().isoformat(),
        "data": {
            "recent_deliveries": [
                {
                    "id": str(d.id),
                    "success": d.success,
                    "response_status": d.response_status,
                    "attempt_number": d.attempt_number,
                    "created_at": d.created_at.isoformat() if d.created_at else None
                }
                for d in webhook_deliveries
            ],
            "client_stats": [
                {
                    "client": name,
                    "total": total,
                    "successful": successful or 0,
                    "failed": total - (successful or 0),
                    "success_rate": round((successful or 0) / total * 100, 2) if total > 0 else 0
                }
                for name, total, successful in webhook_stats
            ],
            "daily_activity": [
                {
                    "date": str(date),
                    "total": total,
                    "successful": successful or 0,
                    "failed": total - (successful or 0)
                }
                for date, total, successful in daily_activity
            ]
        }
    }
