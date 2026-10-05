"""Cloudflare Stream.

The panel does not upload the video: it asks Cloudflare for a one-time upload
URL and the browser sends the file straight there. A 2 GB video never passes
through Django --no ten-minute requests, no nginx body limit-- and the upload
is resumable because that URL speaks the tus protocol."""

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

API = "https://api.cloudflare.com/client/v4"
TIMEOUT = 15

# The Cloudflare account is shared with other products. Everything this panel
# uploads is tagged with this creator, and every read filters by it, so Neural
# never sees --or imports-- another platform's library.
CREATOR = "neural-manager"


def is_configured():
    """No token, no Stream: the panel falls back to its own upload."""
    return bool(settings.CLOUDFLARE_STREAM_TOKEN and settings.CLOUDFLARE_ACCOUNT_ID)


def _headers(extra=None):
    headers = {"Authorization": f"Bearer {settings.CLOUDFLARE_STREAM_TOKEN}"}
    headers.update(extra or {})
    return headers


def playback_url(uid):
    return f"https://{settings.CLOUDFLARE_STREAM_SUBDOMAIN}/{uid}/manifest/video.m3u8"


def thumbnail_url(uid, second=1):
    return (
        f"https://{settings.CLOUDFLARE_STREAM_SUBDOMAIN}/{uid}/thumbnails/"
        f"thumbnail.jpg?time={second}s"
    )


def iframe_url(uid):
    return f"https://{settings.CLOUDFLARE_STREAM_SUBDOMAIN}/{uid}/iframe"


def create_direct_upload(filename, size, minutes=120):
    """Ask for a one-time, resumable (tus) upload URL.

    Returns (upload_url, uid). The uid is stored on the Video right away: if the
    upload breaks, the record still points at the right video in Cloudflare and can
    be resumed against the same URL."""
    import base64

    metadata = ",".join(
        f"{key} {base64.b64encode(str(value).encode()).decode()}"
        for key, value in [("name", filename), ("requiresignedurls", "")]
        if value != ""
    )

    response = requests.post(
        f"{API}/accounts/{settings.CLOUDFLARE_ACCOUNT_ID}/stream?direct_user=true",
        headers=_headers(
            {
                "Tus-Resumable": "1.0.0",
                "Upload-Length": str(size),
                "Upload-Metadata": metadata,
                "Upload-Creator": CREATOR,
            }
        ),
        timeout=TIMEOUT,
    )
    if response.status_code not in (200, 201):
        logger.error("Stream direct upload failed: %s %s", response.status_code, response.text[:400])
        raise RuntimeError(
            f"Cloudflare respondió {response.status_code} al pedir la URL de subida."
        )

    return response.headers.get("Location"), response.headers.get("stream-media-id")


def get_video(uid):
    """An uploaded video's data: duration, state, thumbnail."""
    response = requests.get(
        f"{API}/accounts/{settings.CLOUDFLARE_ACCOUNT_ID}/stream/{uid}",
        headers=_headers(),
        timeout=TIMEOUT,
    )
    if response.status_code != 200:
        return None
    return response.json().get("result")


def list_videos(limit=1000, creator=CREATOR):
    """The panel's own videos on Stream.

    Filtered by creator on purpose: the account hosts other products, and an
    unfiltered list would pull their content into the gym's library.
    Pass creator=None only when you really want everything.
    """
    params = {"limit": limit}
    if creator:
        params["creator"] = creator

    response = requests.get(
        f"{API}/accounts/{settings.CLOUDFLARE_ACCOUNT_ID}/stream",
        headers=_headers(),
        params=params,
        timeout=TIMEOUT,
    )
    if response.status_code != 200:
        logger.error("Stream list failed: %s %s", response.status_code, response.text[:400])
        return []
    return response.json().get("result", [])
