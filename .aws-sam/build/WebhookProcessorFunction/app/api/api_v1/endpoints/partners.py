"""
Partner Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.partner import DeliveryPartner
from app.schemas.partner import PartnerOut, DeliverySummary

router = APIRouter()


@router.post("/")
async def create_partner():
    """Create new delivery partner."""
    return {"message": "Create partner endpoint - implementation pending"}


@router.get("/{partner_id}", response_model=PartnerOut)
async def get_partner(partner_id: str, db: Session = Depends(get_db)):
    partner = db.query(DeliveryPartner).filter(DeliveryPartner.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    return PartnerOut(
        id=partner.id,
        name=partner.name,
        description=partner.description,
        partner_type=partner.partner_type,
        active=partner.active,
        deliveries=[
            DeliverySummary(id=d.id, status=d.status) for d in getattr(partner, "deliveries", [])
        ]
    )


@router.put("/{partner_id}")
async def update_partner(partner_id: str):
    """Update existing partner."""
    return {"message": f"Update partner {partner_id} - implementation pending"}


@router.delete("/{partner_id}")
async def delete_partner(partner_id: str):
    """Delete partner by ID."""
    return {"message": f"Delete partner {partner_id} - implementation pending"}
