"""
Advanced Features API
Endpoints for lead notes, custom fields, tags, and scoring
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime
import uuid

from app.core.database import get_db
from app.api.dependencies import get_current_admin
from app.models.admin_user import AdminUser
from app.models.lead_note import LeadNote, LeadTag, AssetTag
from app.models.custom_field import CustomField, CustomFieldValue, LeadScore, FieldType
from app.models.asset import Asset
from pydantic import BaseModel, field_serializer


router = APIRouter()


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class LeadNoteCreate(BaseModel):
    asset_id: str
    note: str
    is_internal: bool = False
    is_pinned: bool = False


class LeadNoteResponse(BaseModel):
    id: str
    asset_id: str
    note: str
    is_internal: bool
    is_pinned: bool
    created_by_admin_id: Optional[str]
    created_by_client_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    @field_serializer('id', 'asset_id', 'created_by_admin_id', 'created_by_client_id')
    def serialize_uuid(self, value):
        return str(value) if value else None

    class Config:
        from_attributes = True


class LeadTagCreate(BaseModel):
    name: str
    color: Optional[str] = None
    description: Optional[str] = None


class LeadTagResponse(BaseModel):
    id: str
    name: str
    color: Optional[str]
    description: Optional[str]
    created_at: datetime

    @field_serializer('id')
    def serialize_uuid(self, value):
        return str(value) if value else None

    class Config:
        from_attributes = True


class AssetTagCreate(BaseModel):
    asset_id: str
    tag_id: str


class CustomFieldCreate(BaseModel):
    name: str
    label: str
    field_type: str
    description: Optional[str] = None
    is_required: bool = False
    is_active: bool = True
    default_value: Optional[str] = None
    options: Optional[List[str]] = None
    display_order: int = 0
    show_in_list: bool = False


class CustomFieldResponse(BaseModel):
    id: str
    name: str
    label: str
    field_type: str
    description: Optional[str]
    is_required: bool
    is_active: bool
    default_value: Optional[str]
    options: Optional[List[str]]
    display_order: int
    show_in_list: bool
    created_at: datetime

    @field_serializer('id')
    def serialize_uuid(self, value):
        return str(value) if value else None

    class Config:
        from_attributes = True


class CustomFieldValueCreate(BaseModel):
    asset_id: str
    custom_field_id: str
    value: Optional[str] = None


class CustomFieldValueResponse(BaseModel):
    id: str
    asset_id: str
    custom_field_id: str
    value: Optional[str]
    created_at: datetime

    @field_serializer('id', 'asset_id', 'custom_field_id')
    def serialize_uuid(self, value):
        return str(value) if value else None

    class Config:
        from_attributes = True


class LeadScoreResponse(BaseModel):
    id: str
    asset_id: str
    score: int
    grade: Optional[str]
    score_breakdown: Optional[dict]
    last_calculated_at: datetime

    @field_serializer('id', 'asset_id')
    def serialize_uuid(self, value):
        return str(value) if value else None

    class Config:
        from_attributes = True


# ============================================================================
# LEAD NOTES ENDPOINTS
# ============================================================================

@router.post("/notes")
def create_lead_note(
    request: LeadNoteCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new lead note"""
    # Verify asset exists
    asset = db.query(Asset).filter(Asset.id == uuid.UUID(request.asset_id)).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Create note
    note = LeadNote(
        asset_id=uuid.UUID(request.asset_id),
        note=request.note,
        is_internal=request.is_internal,
        is_pinned=request.is_pinned,
        created_by_admin_id=admin.id
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    return {
        "id": str(note.id),
        "asset_id": str(note.asset_id),
        "note": note.note,
        "is_internal": note.is_internal,
        "is_pinned": note.is_pinned,
        "created_by_admin_id": str(note.created_by_admin_id) if note.created_by_admin_id else None,
        "created_by_client_id": str(note.created_by_client_id) if note.created_by_client_id else None,
        "created_at": note.created_at,
        "updated_at": note.updated_at
    }


@router.get("/notes/{asset_id}")
def get_lead_notes(
    asset_id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all notes for a lead"""
    notes = db.query(LeadNote).filter(
        LeadNote.asset_id == uuid.UUID(asset_id)
    ).order_by(desc(LeadNote.is_pinned), desc(LeadNote.created_at)).all()

    return [
        {
            "id": str(note.id),
            "asset_id": str(note.asset_id),
            "note": note.note,
            "is_internal": note.is_internal,
            "is_pinned": note.is_pinned,
            "created_by_admin_id": str(note.created_by_admin_id) if note.created_by_admin_id else None,
            "created_by_client_id": str(note.created_by_client_id) if note.created_by_client_id else None,
            "created_at": note.created_at,
            "updated_at": note.updated_at
        }
        for note in notes
    ]


@router.delete("/notes/{note_id}")
def delete_lead_note(
    note_id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a lead note"""
    note = db.query(LeadNote).filter(LeadNote.id == uuid.UUID(note_id)).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(note)
    db.commit()

    return {"message": "Note deleted successfully"}


# ============================================================================
# LEAD TAGS ENDPOINTS
# ============================================================================

@router.post("/tags")
def create_tag(
    request: LeadTagCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new tag"""
    # Check if tag already exists
    existing = db.query(LeadTag).filter(LeadTag.name == request.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already exists")

    tag = LeadTag(
        name=request.name,
        color=request.color,
        description=request.description
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)

    return {
        "id": str(tag.id),
        "name": tag.name,
        "color": tag.color,
        "description": tag.description,
        "created_at": tag.created_at
    }


@router.get("/tags")
def get_all_tags(
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all tags"""
    tags = db.query(LeadTag).order_by(LeadTag.name).all()
    return [
        {
            "id": str(tag.id),
            "name": tag.name,
            "color": tag.color,
            "description": tag.description,
            "created_at": tag.created_at
        }
        for tag in tags
    ]


@router.post("/tags/assign")
def assign_tag_to_lead(
    request: AssetTagCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Assign a tag to a lead"""
    # Check if already assigned
    existing = db.query(AssetTag).filter(
        AssetTag.asset_id == uuid.UUID(request.asset_id),
        AssetTag.tag_id == uuid.UUID(request.tag_id)
    ).first()

    if existing:
        return {"message": "Tag already assigned"}

    asset_tag = AssetTag(
        asset_id=uuid.UUID(request.asset_id),
        tag_id=uuid.UUID(request.tag_id),
        created_by_admin_id=admin.id
    )
    db.add(asset_tag)
    db.commit()

    return {"message": "Tag assigned successfully"}


@router.delete("/tags/assign/{asset_id}/{tag_id}")
def remove_tag_from_lead(
    asset_id: str,
    tag_id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Remove a tag from a lead"""
    asset_tag = db.query(AssetTag).filter(
        AssetTag.asset_id == uuid.UUID(asset_id),
        AssetTag.tag_id == uuid.UUID(tag_id)
    ).first()

    if not asset_tag:
        raise HTTPException(status_code=404, detail="Tag assignment not found")

    db.delete(asset_tag)
    db.commit()

    return {"message": "Tag removed successfully"}


@router.get("/tags/lead/{asset_id}")
def get_lead_tags(
    asset_id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all tags for a specific lead"""
    tags = db.query(LeadTag).join(AssetTag).filter(
        AssetTag.asset_id == uuid.UUID(asset_id)
    ).all()

    return [
        {
            "id": str(tag.id),
            "name": tag.name,
            "color": tag.color,
            "description": tag.description,
            "created_at": tag.created_at
        }
        for tag in tags
    ]


# ============================================================================
# CUSTOM FIELDS ENDPOINTS
# ============================================================================

@router.post("/custom-fields")
def create_custom_field(
    request: CustomFieldCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new custom field"""
    # Check if field already exists
    existing = db.query(CustomField).filter(CustomField.name == request.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Custom field already exists")

    field = CustomField(
        name=request.name,
        label=request.label,
        field_type=FieldType(request.field_type),
        description=request.description,
        is_required=request.is_required,
        is_active=request.is_active,
        default_value=request.default_value,
        options=request.options,
        display_order=request.display_order,
        show_in_list=request.show_in_list
    )
    db.add(field)
    db.commit()
    db.refresh(field)

    return {
        "id": str(field.id),
        "name": field.name,
        "label": field.label,
        "field_type": field.field_type.value,
        "description": field.description,
        "is_required": field.is_required,
        "is_active": field.is_active,
        "default_value": field.default_value,
        "options": field.options,
        "display_order": field.display_order,
        "show_in_list": field.show_in_list,
        "created_at": field.created_at
    }


@router.get("/custom-fields")
def get_custom_fields(
    active_only: bool = Query(True),
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all custom fields"""
    query = db.query(CustomField)
    if active_only:
        query = query.filter(CustomField.is_active == True)

    fields = query.order_by(CustomField.display_order, CustomField.name).all()
    return [
        {
            "id": str(field.id),
            "name": field.name,
            "label": field.label,
            "field_type": field.field_type.value,
            "description": field.description,
            "is_required": field.is_required,
            "is_active": field.is_active,
            "default_value": field.default_value,
            "options": field.options,
            "display_order": field.display_order,
            "show_in_list": field.show_in_list,
            "created_at": field.created_at
        }
        for field in fields
    ]


@router.put("/custom-fields/{field_id}")
def update_custom_field(
    field_id: str,
    request: CustomFieldCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update a custom field"""
    field = db.query(CustomField).filter(CustomField.id == uuid.UUID(field_id)).first()
    if not field:
        raise HTTPException(status_code=404, detail="Custom field not found")

    field.label = request.label
    field.description = request.description
    field.is_required = request.is_required
    field.is_active = request.is_active
    field.default_value = request.default_value
    field.options = request.options
    field.display_order = request.display_order
    field.show_in_list = request.show_in_list

    db.commit()
    db.refresh(field)

    return {
        "id": str(field.id),
        "name": field.name,
        "label": field.label,
        "field_type": field.field_type.value,
        "description": field.description,
        "is_required": field.is_required,
        "is_active": field.is_active,
        "default_value": field.default_value,
        "options": field.options,
        "display_order": field.display_order,
        "show_in_list": field.show_in_list,
        "created_at": field.created_at
    }


@router.post("/custom-field-values")
def set_custom_field_value(
    request: CustomFieldValueCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Set a custom field value for a lead"""
    # Check if value already exists
    existing = db.query(CustomFieldValue).filter(
        CustomFieldValue.asset_id == uuid.UUID(request.asset_id),
        CustomFieldValue.custom_field_id == uuid.UUID(request.custom_field_id)
    ).first()

    if existing:
        # Update existing value
        existing.value = request.value
        db.commit()
        db.refresh(existing)
        return {
            "id": str(existing.id),
            "asset_id": str(existing.asset_id),
            "custom_field_id": str(existing.custom_field_id),
            "value": existing.value,
            "created_at": existing.created_at
        }

    # Create new value
    value = CustomFieldValue(
        asset_id=uuid.UUID(request.asset_id),
        custom_field_id=uuid.UUID(request.custom_field_id),
        value=request.value
    )
    db.add(value)
    db.commit()
    db.refresh(value)

    return {
        "id": str(value.id),
        "asset_id": str(value.asset_id),
        "custom_field_id": str(value.custom_field_id),
        "value": value.value,
        "created_at": value.created_at
    }


@router.get("/custom-field-values/{asset_id}")
def get_custom_field_values(
    asset_id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all custom field values for a lead"""
    values = db.query(CustomFieldValue).filter(
        CustomFieldValue.asset_id == uuid.UUID(asset_id)
    ).all()

    return [
        {
            "id": str(value.id),
            "asset_id": str(value.asset_id),
            "custom_field_id": str(value.custom_field_id),
            "value": value.value,
            "created_at": value.created_at
        }
        for value in values
    ]


# ============================================================================
# LEAD SCORING ENDPOINTS
# ============================================================================

@router.post("/scoring/calculate/{asset_id}")
def calculate_lead_score(
    asset_id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Calculate lead score based on various factors"""
    # Verify asset exists
    asset = db.query(Asset).filter(Asset.id == uuid.UUID(asset_id)).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Calculate score based on various factors
    score = 0
    breakdown = {}

    # Factor 1: Has email (+20 points)
    if asset.email:
        score += 20
        breakdown["has_email"] = 20

    # Factor 2: Has name (+15 points)
    if asset.name:
        score += 15
        breakdown["has_name"] = 15

    # Factor 3: Source quality (+10-30 points)
    if asset.utm and asset.utm.get("utm_source"):
        source = asset.utm.get("utm_source").lower()
        if source in ["google", "facebook", "linkedin"]:
            score += 30
            breakdown["premium_source"] = 30
        else:
            score += 10
            breakdown["standard_source"] = 10

    # Factor 4: Has custom fields (+5 per field, max 25)
    custom_values = db.query(CustomFieldValue).filter(
        CustomFieldValue.asset_id == uuid.UUID(asset_id)
    ).count()
    custom_score = min(custom_values * 5, 25)
    score += custom_score
    breakdown["custom_fields"] = custom_score

    # Factor 5: Has notes (+10 points)
    notes_count = db.query(LeadNote).filter(LeadNote.asset_id == uuid.UUID(asset_id)).count()
    if notes_count > 0:
        score += 10
        breakdown["has_notes"] = 10

    # Determine grade
    if score >= 80:
        grade = "A"
    elif score >= 60:
        grade = "B"
    elif score >= 40:
        grade = "C"
    elif score >= 20:
        grade = "D"
    else:
        grade = "F"

    # Check if score already exists
    existing_score = db.query(LeadScore).filter(LeadScore.asset_id == uuid.UUID(asset_id)).first()

    if existing_score:
        # Update existing score
        existing_score.score = score
        existing_score.grade = grade
        existing_score.score_breakdown = breakdown
        existing_score.last_calculated_at = datetime.utcnow()
        existing_score.calculation_version = "1.0"
        db.commit()
        db.refresh(existing_score)
        return {
            "id": str(existing_score.id),
            "asset_id": str(existing_score.asset_id),
            "score": existing_score.score,
            "grade": existing_score.grade,
            "score_breakdown": existing_score.score_breakdown,
            "last_calculated_at": existing_score.last_calculated_at
        }

    # Create new score
    lead_score = LeadScore(
        asset_id=uuid.UUID(asset_id),
        score=score,
        grade=grade,
        score_breakdown=breakdown,
        calculation_version="1.0"
    )
    db.add(lead_score)
    db.commit()
    db.refresh(lead_score)

    return {
        "id": str(lead_score.id),
        "asset_id": str(lead_score.asset_id),
        "score": lead_score.score,
        "grade": lead_score.grade,
        "score_breakdown": lead_score.score_breakdown,
        "last_calculated_at": lead_score.last_calculated_at
    }


@router.get("/scoring/{asset_id}")
def get_lead_score(
    asset_id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get lead score"""
    score = db.query(LeadScore).filter(LeadScore.asset_id == uuid.UUID(asset_id)).first()
    if not score:
        raise HTTPException(status_code=404, detail="Lead score not found. Calculate it first.")

    return {
        "id": str(score.id),
        "asset_id": str(score.asset_id),
        "score": score.score,
        "grade": score.grade,
        "score_breakdown": score.score_breakdown,
        "last_calculated_at": score.last_calculated_at
    }


@router.get("/scoring/stats/overview")
def get_scoring_stats(
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get scoring statistics"""
    total_scored = db.query(LeadScore).count()
    avg_score = db.query(func.avg(LeadScore.score)).scalar() or 0

    # Grade distribution
    grade_dist = {}
    for grade in ["A", "B", "C", "D", "F"]:
        count = db.query(LeadScore).filter(LeadScore.grade == grade).count()
        grade_dist[grade] = count

    return {
        "total_scored_leads": total_scored,
        "average_score": round(float(avg_score), 2),
        "grade_distribution": grade_dist
    }

