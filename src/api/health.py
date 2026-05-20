"""健康检查 API"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def CheckHealth():
    return {"status": "OK"}