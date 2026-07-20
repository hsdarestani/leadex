import logging
from typing import Optional
import requests

logger = logging.getLogger(__name__)

def is_whatsapp_registered(api_key: str, phone_number: str, timeout_sec: float = 4.0) -> Optional[bool]:
    if not api_key or not phone_number:
        return None

    # WhatsiPlus expects digits (no '+')
    normalized_phone = "".join(ch for ch in phone_number if ch.isdigit())
    if not normalized_phone:
        return None

    url = f"https://api.whatsiplus.com/isRegistered/{api_key}"
    try:
        r = requests.get(url, params={"phonenumber": normalized_phone}, timeout=timeout_sec)
        r.raise_for_status()
        data = r.json()

        # docs: {"success": true, "result": true/false}
        if isinstance(data, dict) and data.get("success") is True and isinstance(data.get("result"), bool):
            return data["result"]

        logger.warning("Unexpected isRegistered response: %s", data)
        return None
    except Exception as e:
        logger.warning("isRegistered check failed: %s", e)
        return None
