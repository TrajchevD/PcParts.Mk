from fastapi import APIRouter, Response
import requests

router = APIRouter()

@router.get("/image-proxy")
def image_proxy(url: str):
    r = requests.get(url, timeout=5)
    return Response(
        content=r.content,
        media_type=r.headers.get("Content-Type", "image/jpeg")
    )
