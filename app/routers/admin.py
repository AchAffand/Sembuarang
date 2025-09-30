from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from .. import models

router = APIRouter()


def require_admin(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
	if not x_api_key or x_api_key != settings.api_admin_key:
		raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/reports/{report_id}/approve")
def approve_report(report_id: int, _: None = Depends(require_admin), db: Session = Depends(get_db)):
	report = db.query(models.Report).filter(models.Report.id == report_id).first()
	if not report:
		raise HTTPException(status_code=404, detail="Not found")
	report.is_approved = True
	db.commit()
	return {"ok": True}


@router.post("/reports/{report_id}/hide")
def hide_report(report_id: int, _: None = Depends(require_admin), db: Session = Depends(get_db)):
	report = db.query(models.Report).filter(models.Report.id == report_id).first()
	if not report:
		raise HTTPException(status_code=404, detail="Not found")
	report.is_hidden = True
	db.commit()
	return {"ok": True}


@router.delete("/reports/{report_id}")
def delete_report(report_id: int, _: None = Depends(require_admin), db: Session = Depends(get_db)):
	report = db.query(models.Report).filter(models.Report.id == report_id).first()
	if not report:
		raise HTTPException(status_code=404, detail="Not found")
	db.delete(report)
	db.commit()
	return {"ok": True}