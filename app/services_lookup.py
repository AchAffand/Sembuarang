from typing import Optional
import httpx

from .config import settings


async def enrich_with_twilio(e164: str) -> tuple[Optional[str], Optional[str]]:
	if not settings.twilio_lookup_sid or not settings.twilio_lookup_token:
		return None, None
	url = f"https://lookups.twilio.com/v2/PhoneNumbers/{e164}?type=carrier"
	auth = (settings.twilio_lookup_sid, settings.twilio_lookup_token)
	async with httpx.AsyncClient(timeout=8.0) as client:
		resp = await client.get(url, auth=auth)
		if resp.status_code != 200:
			return None, None
		data = resp.json()
		carrier_name = data.get("carrier", {}).get("name")
		line_type = data.get("carrier", {}).get("type")
		return carrier_name, line_type