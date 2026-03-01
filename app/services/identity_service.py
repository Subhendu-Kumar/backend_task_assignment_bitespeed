from __future__ import annotations

from app.database import db
from app.schemas import IdentifyRequest, IdentifyResponse, ConsolidatedContact


async def _find_matching_contacts(email: str | None, phone: str | None):
    filters: list[dict] = []
    if email:
        filters.append({"email": email})
    if phone:
        filters.append({"phoneNumber": phone})

    if not filters:
        return []

    return await db.contact.find_many(
        where={"deletedAt": None, "OR": filters},
        order={"createdAt": "asc"},
    )


async def _get_primary(contact) -> object:
    if contact.linkPrecedence == "primary":
        return contact
    parent = await db.contact.find_unique(where={"id": contact.linkedId})
    if parent is None:
        return contact
    return await _get_primary(parent)


async def _collect_cluster(primary_id: int) -> list:
    primary = await db.contact.find_unique(where={"id": primary_id})
    if primary is None:
        return []
    secondaries = await db.contact.find_many(
        where={"linkedId": primary_id, "deletedAt": None},
        order={"createdAt": "asc"},
    )
    return [primary, *secondaries]


def _build_response(primary, cluster: list) -> IdentifyResponse:
    """Build the consolidated response payload."""
    emails: list[str] = []
    phones: list[str] = []
    secondary_ids: list[int] = []

    if primary.email and primary.email not in emails:
        emails.append(primary.email)
    if primary.phoneNumber and primary.phoneNumber not in phones:
        phones.append(primary.phoneNumber)

    for c in cluster:
        if c.id == primary.id:
            continue
        secondary_ids.append(c.id)
        if c.email and c.email not in emails:
            emails.append(c.email)
        if c.phoneNumber and c.phoneNumber not in phones:
            phones.append(c.phoneNumber)

    return IdentifyResponse(
        contact=ConsolidatedContact(
            primaryContatctId=primary.id,
            emails=emails,
            phoneNumbers=phones,
            secondaryContactIds=secondary_ids,
        )
    )


async def identify(req: IdentifyRequest) -> IdentifyResponse:
    """Core identity reconciliation entry-point."""
    email = req.email
    phone = req.phoneNumber

    if not email and not phone:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="email or phoneNumber is required")

    matches = await _find_matching_contacts(email, phone)

    if not matches:
        new_contact = await db.contact.create(
            data={
                "email": email,
                "phoneNumber": phone,
                "linkPrecedence": "primary",
            }
        )
        return _build_response(new_contact, [new_contact])

    primary_map: dict[int, object] = {}
    for m in matches:
        p = await _get_primary(m)
        primary_map[p.id] = p

    primaries = sorted(primary_map.values(), key=lambda c: c.createdAt)

    if len(primaries) > 1:
        keeper = primaries[0]
        for loser in primaries[1:]:
            await db.contact.update(
                where={"id": loser.id},
                data={
                    "linkPrecedence": "secondary",
                    "linkedId": keeper.id,
                },
            )
            await db.contact.update_many(
                where={"linkedId": loser.id},
                data={"linkedId": keeper.id},
            )
        primary = keeper
    else:
        primary = primaries[0]

    cluster = await _collect_cluster(primary.id)

    existing_emails = {c.email for c in cluster if c.email}
    existing_phones = {c.phoneNumber for c in cluster if c.phoneNumber}

    has_new_email = bool(email) and email not in existing_emails
    has_new_phone = bool(phone) and phone not in existing_phones

    if has_new_email or has_new_phone:
        exact_match = any(c.email == email and c.phoneNumber == phone for c in cluster)
        if not exact_match:
            await db.contact.create(
                data={
                    "email": email,
                    "phoneNumber": phone,
                    "linkPrecedence": "secondary",
                    "linkedId": primary.id,
                }
            )
            cluster = await _collect_cluster(primary.id)

    return _build_response(primary, cluster)
