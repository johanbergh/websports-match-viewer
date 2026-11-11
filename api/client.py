import requests

# base url's
WEBSITE_URL = "https://www.websports.co.za"
API_BASE = f"{WEBSITE_URL}/api/live"
LOGO_BASE = f"{WEBSITE_URL}/images/logo"
REQUEST_TIMEOUT = 6

session = requests.Session()

def get_json(endpoint):
    """Requests an endpoint and returns the JSON, or None if something went wrong."""
    try:
        response = session.get(f"{API_BASE}/{endpoint}", timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json() # returns json

    except Exception:
        return None