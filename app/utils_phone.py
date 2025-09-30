import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from phonenumbers import geocoder, carrier, number_type, PhoneNumberType
from phonenumbers import timezone as phtimezone
from typing import Optional, Dict, Any, List

ID_REGION = "ID"

# Common Indonesian mobile prefixes mapping (approximate)
PREFIX_TO_CARRIER = {
	"0811": "Telkomsel",
	"0812": "Telkomsel",
	"0813": "Telkomsel",
	"0821": "Telkomsel",
	"0822": "Telkomsel",
	"0823": "Telkomsel",
	"0851": "Telkomsel",
	"0852": "Telkomsel",
	"0853": "Telkomsel",
	"0814": "Indosat",
	"0815": "Indosat",
	"0816": "Indosat",
	"0855": "Indosat",
	"0856": "Indosat",
	"0857": "Indosat",
	"0858": "Indosat",
	"0817": "XL",
	"0818": "XL",
	"0819": "XL",
	"0859": "XL",
	"0877": "XL",
	"0878": "XL",
	"0838": "AXIS",
	"0831": "AXIS",
	"0832": "AXIS",
	"0833": "AXIS",
	"0881": "Smartfren",
	"0882": "Smartfren",
	"0883": "Smartfren",
	"0884": "Smartfren",
	"0885": "Smartfren",
	"0886": "Smartfren",
	"0887": "Smartfren",
	"0888": "Smartfren",
	"0895": "3",
	"0896": "3",
	"0897": "3",
	"0898": "3",
	"0899": "3",
}


def normalize_indonesian_number(raw: str) -> Optional[str]:
	try:
		num = phonenumbers.parse(raw, ID_REGION)
	except NumberParseException:
		return None
	if not phonenumbers.is_valid_number(num):
		return None
	if phonenumbers.region_code_for_number(num) != ID_REGION:
		return None
	return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)


def infer_carrier_local_prefix(e164: str) -> Optional[str]:
	# e164 like +62812...
	if not e164.startswith("+62"):
		return None
	local = "0" + e164[3:]  # convert +62xxx to 0xxx to match local prefixes
	for length in (4, 3):
		prefix = local[:length]
		if prefix in PREFIX_TO_CARRIER:
			return PREFIX_TO_CARRIER[prefix]
	return None


def enrich_number_details(raw: str, locale: str = "en") -> Optional[Dict[str, Any]]:
	try:
		num = phonenumbers.parse(raw, ID_REGION)
	except NumberParseException:
		return None
	valid = phonenumbers.is_valid_number(num)
	if not valid or phonenumbers.region_code_for_number(num) != ID_REGION:
		return None
	formats = {
		"e164": phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164),
		"international": phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
		"national": phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.NATIONAL),
	}
	num_type = number_type(num)
	if num_type == PhoneNumberType.MOBILE:
		type_label = "mobile"
	elif num_type == PhoneNumberType.FIXED_LINE:
		type_label = "fixed_line"
	elif num_type == PhoneNumberType.FIXED_LINE_OR_MOBILE:
		type_label = "fixed_or_mobile"
	elif num_type == PhoneNumberType.TOLL_FREE:
		type_label = "toll_free"
	elif num_type == PhoneNumberType.PREMIUM_RATE:
		type_label = "premium_rate"
	else:
		type_label = "unknown"
	tzs: List[str] = list(phtimezone.time_zones_for_number(num))
	desc = geocoder.description_for_number(num, locale) or geocoder.description_for_number(num, "en")
	car = carrier.name_for_number(num, locale) or carrier.name_for_number(num, "en")
	return {
		"valid": valid,
		"formats": formats,
		"number_type": type_label,
		"timezones": tzs,
		"description": desc or None,
		"carrier_name": car or None,
	}


def compute_risk_score(approved_reports: List[Dict[str, Any]]) -> int:
	if not approved_reports:
		return 0
	weights = {"fraud": 3, "scam": 3, "harassment": 2, "spam": 1, "other": 1}
	total_weight = 0
	score_accum = 0
	for r in approved_reports:
		w = weights.get(r.get("category"), 1)
		conf = int(r.get("confidence", 50))
		score_accum += w * conf
		total_weight += w * 100
	raw = int(round((score_accum / total_weight) * 100))
	return max(0, min(100, raw))