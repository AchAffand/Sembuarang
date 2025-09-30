from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from .. import models
from ..services_lookup import enrich_with_twilio

router = APIRouter()


def require_admin(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
	if not x_api_key or x_api_key != settings.api_admin_key:
		raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/numbers/{e164}/enrich")
async def enrich_number(e164: str, _: None = Depends(require_admin), db: Session = Depends(get_db)):
	num = db.query(models.PhoneNumber).filter(models.PhoneNumber.e164 == e164).first()
	if not num:
		raise HTTPException(status_code=404, detail="Not found")
	carrier, line_type = await enrich_with_twilio(e164)
	if not carrier and not line_type:
		return {"ok": False, "updated": False}
	num.carrier = carrier or num.carrier
	num.line_type = line_type or num.line_type
	db.commit()
	return {"ok": True, "updated": True, "carrier": num.carrier, "line_type": num.line_type}