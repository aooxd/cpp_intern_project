from typing import Any
from core.event_bus import EventBus

SECRET_TOKEN = "VANGUARD-7749-NEXVALO"


class SecurityProxy:
    def __init__(self, real_subject: Any) -> None:
        self._subject = real_subject
        self._bus = EventBus()

    async def scan(self, token: str) -> dict:
        if token != SECRET_TOKEN:
            await self._bus.emit(
                event="security.denied",
                tag="SECURITY",
                message=f"Unauthorized scan attempt. Invalid token provided.",
                status="denied",
            )
            return {"authorized": False, "message": "Access denied. Invalid token."}

        await self._bus.emit(
            event="security.authorized",
            tag="SECURITY",
            message="Token validated. Initiating Vanguard integrity scan...",
            status="authorized",
        )
        result = await self._subject.run_scan()
        await self._bus.emit(
            event="security.scan_complete",
            tag="SUCCESS",
            message=f"Vanguard scan complete. Integrity: {result['integrity']}%",
            status="clean",
        )
        return result


class VanguardSystem:
    async def run_scan(self) -> dict:
        import asyncio, random
        await asyncio.sleep(0.4)
        integrity = random.randint(94, 100)
        threats = random.randint(0, 1)
        return {
            "authorized": True,
            "integrity": integrity,
            "threats_detected": threats,
            "status": "CLEAN" if threats == 0 else "WARNING",
            "message": f"System scan complete. Integrity at {integrity}%.",
        }
