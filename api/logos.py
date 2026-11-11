import io
import time
from PIL import Image

from api.client import *

_logo_cache = {}
_logo_failures = {} # logo name , when download failed

def get_logo(logo_name):
    """Downloads a team logo as a PIL image (cached)"""
    if not logo_name:
        return None

    # checks if image is already cached, returns cached image
    if logo_name in _logo_cache:
        return _logo_cache[logo_name]

    # don't hammer the server if this logo failed less than a minute ago
    last_failure = _logo_failures.get(logo_name, 0)
    if time.time() - last_failure < 60:
        return None

    try:
        response = session.get(LOGO_BASE + logo_name, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        # load the raw downloaded bytes into a Pillow image with transparency support (RGBA)
        logo_image = Image.open(io.BytesIO(response.content)).convert("RGBA")
        logo_image.thumbnail((200, 200), Image.LANCZOS)

        # save the processed image in the cache for future calls and return it
        _logo_cache[logo_name] = logo_image
        return logo_image
    except Exception:
        # record the current timestamp of the failure so we wait 60 seconds before retrying
        _logo_failures[logo_name] = time.time()
        return None