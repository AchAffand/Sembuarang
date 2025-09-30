from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class ReportCreate(BaseModel):
	category: str = Field(..., pattern=r"^(spam|fraud|scam|harassment|other)$")
	confidence: int = Field(ge=0, le=100, default=50)
	note: Optional[str] = Field(default=None, max_length=1000)


class ReportOut(BaseModel):
	id: int
	category: str
	confidence: int
	note: Optional[str]
	is_approved: bool
	is_hidden: bool
	created_at: datetime

	class Config:
		from_attributes = True


class PhoneOut(BaseModel):
	e164: str
	region: str
	carrier: Optional[str]
	line_type: Optional[str]
	reports: List[ReportOut] = []

	class Config:
		from_attributes = True


class SearchResponse(BaseModel):
	e164: str
	region: str
	report_count: int
	carrier: Optional[str] = None
	line_type: Optional[str] = None
	description: Optional[str] = None


class Formats(BaseModel):
	e164: str
	international: str
	national: str


class ReportStats(BaseModel):
	by_category: Dict[str, int]
	total_approved: int


class PhoneDetailOut(BaseModel):
	e164: str
	region: str
	carrier: Optional[str]
	line_type: Optional[str]
	valid: bool
	formats: Formats
	number_type: Optional[str] = None
	timezones: List[str] = []
	description: Optional[str] = None
	report_stats: ReportStats
	risk_score: int
	reports: List[ReportOut] = []