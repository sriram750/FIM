from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.auth import User, Role
from app.security.passwords import verify_password
from app.security.tokens import create_access_token
from app.security.rbac import get_current_active_user, seed_initial_security
from app.schemas.auth import LoginRequest, TokenResponse, UserSummary
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user credentials (email & password) and issue a JWT access token.
    """
    # Ensure default admin is seeded
    await seed_initial_security(db)

    stmt = (
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .where(User.email == req.email)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact an administrator.",
        )

    role_name = user.role.name if user.role else "Analyst"
    permissions = [p.permission for p in user.role.permissions] if user.role and user.role.permissions else []
    if user.is_superuser:
        permissions.append("*:*")

    token = create_access_token(subject=user.id, role=role_name)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user=UserSummary(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=role_name,
            is_superuser=user.is_superuser,
            permissions=permissions,
        )
    )


@router.get("/me", response_model=UserSummary)
async def get_me(user: User = Depends(get_current_active_user)):
    """
    Returns current authenticated user details and active RBAC permissions.
    """
    role_name = user.role.name if user.role else "Analyst"
    permissions = [p.permission for p in user.role.permissions] if user.role and user.role.permissions else []
    if user.is_superuser:
        permissions.append("*:*")

    return UserSummary(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=role_name,
        is_superuser=user.is_superuser,
        permissions=permissions,
    )


@router.post("/logout")
async def logout(user: User = Depends(get_current_active_user)):
    """
    Logout current session.
    """
    return {"message": "Successfully logged out"}
