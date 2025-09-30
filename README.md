## Indonesian Phone Number Reputation Tracker

A professional, legal phone number reputation tracker for Indonesia (+62). Users can search numbers, view reports, and submit fraud/spam reports. Admins can moderate via API key.

### Features
- Indonesia-only numbers, normalized to E.164 (+62...)
- Offline carrier/prefix mapping and optional Twilio Lookup enrichment
- Reports with category, confidence, and free-text notes
- Public search and detail pages (Jinja2 templates)
- Admin moderation endpoints (API key)
- SQLite storage, FastAPI backend

### Quickstart

1. Create a `.env` (see `.env.example`).
2. Install dependencies:
```bash
python -m pip install -r requirements.txt
```
3. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
4. Open `http://localhost:8000`.

### Environment
- `API_ADMIN_KEY`: required for admin endpoints
- `TWILIO_LOOKUP_SID` and `TWILIO_LOOKUP_TOKEN`: optional for carrier/line_type enrichment
- `DATABASE_URL`: optional; default `sqlite:///./data.db`

### Legal
This app does not perform real-time device geolocation or unlawful tracking. It provides a community-driven reputation database and optional carrier lookup. Ensure your use complies with Indonesian law and platform policies.