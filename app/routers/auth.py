from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.database import db
from app.schemas import (
    TokenResponse,
    UserLoginRequest,
    UserOut,
    UserRegisterRequest,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegisterRequest):
    existing = await db.user.find_first(
        where={"OR": [{"username": body.username}, {"email": body.email}]}
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already taken",
        )

    user = await db.user.create(
        data={
            "username": body.username,
            "email": body.email,
            "password": hash_password(body.password),
        }
    )
    return user


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLoginRequest):
    user = await db.user.find_first(where={"username": body.username})
    if not user or not verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token(data={"sub": user.username, "user_id": user.id})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
async def me(current_user: dict = Depends(get_current_user)):
    user = await db.user.find_first(where={"username": current_user["sub"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
