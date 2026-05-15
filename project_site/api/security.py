from fastapi import APIRouter
from pydantic import BaseModel
from core.security_proxy import SecurityProxy, VanguardSystem

router = APIRouter(prefix="/api/security", tags=["security"])
_proxy = SecurityProxy(VanguardSystem())


class ScanRequest(BaseModel):
    token: str


@router.post("/scan")
async def run_scan(payload: ScanRequest):
    result = await _proxy.scan(payload.token)
    return result
