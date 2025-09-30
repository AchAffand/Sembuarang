from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict

from ..database import get_db
from .. import models, schemas
from ..utils_phone import normalize_indonesian_number, infer_carrier_local_prefix, enrich_number_details, compute_risk_score

router = APIRouter()


@router.get("/search", response_model=schemas.SearchResponse)
def search_number(q: str = Query(..., description="Phone number to search"), db: Session = Depends(get_db)):
	e164 = normalize_indonesian_number(q)
	if not e164:
		raise HTTPException(status_code=400, detail="Invalid or non-Indonesian number")
	num = db.query(models.PhoneNumber).filter(models.PhoneNumber.e164 == e164).first()
	enriched = enrich_number_details(e164)
	desc = enriched.get("description") if enriched else None
	if not num:
		carrier_local = infer_carrier_local_prefix(e164)
		carrier_name = enriched.get("carrier_name") if enriched and enriched.get("carrier_name") else carrier_local
		return schemas.SearchResponse(e164=e164, region="ID", report_count=0, carrier=carrier_name, description=desc)
	approved = [r for r in num.reports if r.is_approved and not r.is_hidden]
	return schemas.SearchResponse(
		e164=num.e164,
		region=num.region,
		report_count=len(approved),
		carrier=num.carrier or (enriched.get("carrier_name") if enriched else None) or infer_carrier_local_prefix(e164),
		line_type=num.line_type,
		description=desc,
	)


@router.get("/numbers/{e164}", response_model=schemas.PhoneDetailOut)
def get_number(e164: str, db: Session = Depends(get_db)):
	num = db.query(models.PhoneNumber).filter(models.PhoneNumber.e164 == e164).first()
	if not num:
		raise HTTPException(status_code=404, detail="Not found")
	enriched = enrich_number_details(e164) or {}
	approved_reports = [r for r in num.reports if r.is_approved and not r.is_hidden]
	report_dicts: List[Dict] = [
		{"category": r.category, "confidence": r.confidence, "note": r.note, "id": r.id, "is_approved": r.is_approved, "is_hidden": r.is_hidden, "created_at": r.created_at}
		for r in approved_reports
	]
	by_cat: Dict[str, int] = {}
	for r in approved_reports:
		by_cat[r.category] = by_cat.get(r.category, 0) + 1
	risk = compute_risk_score(report_dicts)
	formats = enriched.get("formats") or {"e164": num.e164, "international": num.e164, "national": num.e164}
	return schemas.PhoneDetailOut(
		e164=num.e164,
		region=num.region,
		carrier=num.carrier or enriched.get("carrier_name") or infer_carrier_local_prefix(e164),
		line_type=num.line_type,
		valid=bool(enriched.get("valid", True)),
		formats=schemas.Formats(**formats),
		number_type=enriched.get("number_type"),
		timezones=enriched.get("timezones", []),
		description=enriched.get("description"),
		report_stats=schemas.ReportStats(by_category=by_cat, total_approved=len(approved_reports)),
		risk_score=risk,
		reports=approved_reports,
	)


@router.post("/numbers/{e164}/reports", response_model=schemas.ReportOut, status_code=201)
def submit_report(e164: str, payload: schemas.ReportCreate, db: Session = Depends(get_db)):
	num = db.query(models.PhoneNumber).filter(models.PhoneNumber.e164 == e164).first()
	if not num:
		# basic creation if missing, ensure e164 formats
		norm = normalize_indonesian_number(e164)
		if not norm or norm != e164:
			raise HTTPException(status_code=400, detail="Invalid e164 for Indonesia")
		num = models.PhoneNumber(e164=e164, region="ID")
		enriched = enrich_number_details(e164) or {}
		num.carrier = enriched.get("carrier_name") or infer_carrier_local_prefix(e164)
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