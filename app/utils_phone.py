import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from typing import Optional

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