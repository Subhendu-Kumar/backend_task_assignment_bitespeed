from fastapi import APIRouter

from app.schemas import IdentifyRequest, IdentifyResponse
from app.services.identity_service import identify

router = APIRouter(tags=["Identity"])


@router.post("/identify", response_model=IdentifyResponse)
async def identify_contact(body: IdentifyRequest):
    return await identify(body)
