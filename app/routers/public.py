from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from .. import models, schemas
from ..utils_phone import normalize_indonesian_number, infer_carrier_local_prefix

router = APIRouter()


@router.get("/search", response_model=schemas.SearchResponse)
def search_number(q: str = Query(..., description="Phone number to search"), db: Session = Depends(get_db)):
	e164 = normalize_indonesian_number(q)
	if not e164:
		raise HTTPException(status_code=400, detail="Invalid or non-Indonesian number")
	num = db.query(models.PhoneNumber).filter(models.PhoneNumber.e164 == e164).first()
	if not num:
		carrier = infer_carrier_local_prefix(e164)
		return schemas.SearchResponse(e164=e164, region="ID", report_count=0, carrier=carrier)
	approved_reports = [r for r in num.reports if r.is_approved and not r.is_hidden]
	return schemas.SearchResponse(
		e164=num.e164,
		region=num.region,
		report_count=len(approved_reports),
		carrier=num.carrier,
		line_type=num.line_type,
	)


@router.get("/numbers/{e164}", response_model=schemas.PhoneOut)
def get_number(e164: str, db: Session = Depends(get_db)):
	num = db.query(models.PhoneNumber).filter(models.PhoneNumber.e164 == e164).first()
	if not num:
		raise HTTPException(status_code=404, detail="Not found")
	return num


@router.post("/numbers/{e164}/reports", response_model=schemas.ReportOut, status_code=201)
def submit_report(e164: str, payload: schemas.ReportCreate, db: Session = Depends(get_db)):
	num = db.query(models.PhoneNumber).filter(models.PhoneNumber.e164 == e164).first()
	if not num:
		# basic creation if missing, ensure e164 formats
		norm = normalize_indonesian_number(e164)
		if not norm or norm != e164:
			raise HTTPException(status_code=400, detail="Invalid e164 for Indonesia")
		num = models.PhoneNumber(e164=e164, region="ID")
		num.carrier = infer_carrier_local_prefix(e164)
		db.add(num)
		db.flush()
	report = models.Report(
		number_id=num.id,
		category=payload.category,
		confidence=payload.confidence,
		note=payload.note,
		is_approved=False,
		is_hidden=False,
	)
	db.add(report)
	db.commit()
	db.refresh(report)
	return report