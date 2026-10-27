from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, List, Callable
import uuid

from app.db.session import get_db
from app.models.auth import User, Role, RolePermission
from app.security.tokens import decode_token
from app.security.passwords import hash_password
from app.core.config import settings
from app.core.logging import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

# Default Role Permissions Matrix
ROLE_PERMISSIONS = {
    "Admin": [
        "endpoints:read", "endpoints:manage", "endpoints:delete",
        "policies:read", "policies:manage",
        "events:read", "events:export",
        "alerts:read", "alerts:manage",
        "reports:read", "reports:export",
        "audit:read",
        "users:read", "users:manage",
        "settings:manage",
    ],
    "Analyst": [
        "endpoints:read",
        "policies:read",
        "events:read", "events:export",
        "alerts:read", "alerts:manage",
        "reports:read", "reports:export",
    ],
    "Auditor": [
        "endpoints:read",
        "policies:read",
        "events:read", "events:export",
        "alerts:read",
        "reports:read", "reports:export",
        "audit:read",
    ]
}


async def seed_initial_security(db: AsyncSession):
    """
    Seeds initial RBAC roles, permissions, and the default administrator account
    if no users exist in the database.
    """
    stmt = select(Role)
    result = await db.execute(stmt)
    existing_roles = {r.name: r for r in result.scalars().all()}

    # Create default roles & permissions
    for role_name, perms in ROLE_PERMISSIONS.items():
        if role_name not in existing_roles:
            role = Role(
                id=str(uuid.uuid4()),
                name=role_name,
                description=f"Standard {role_name} security role",
            )
            db.add(role)
            await db.flush()
            existing_roles[role_name] = role

            for perm in perms:
                rp = RolePermission(
                    id=str(uuid.uuid4()),
                    role_id=role.id,
                    permission=perm,
                )
                db.add(rp)

    # Check if admin user exists
    user_stmt = select(User).where(User.email == settings.INITIAL_ADMIN_EMAIL)
    u_res = await db.execute(user_stmt)
    admin_user = u_res.scalar_one_or_none()

    if not admin_user:
        admin_role = existing_roles.get("Admin")
        admin_user = User(
            id=str(uuid.uuid4()),
            email=settings.INITIAL_ADMIN_EMAIL,
            hashed_password=hash_password(settings.INITIAL_ADMIN_PASSWORD),
            full_name=settings.INITIAL_ADMIN_NAME,
            is_active=True,
            is_superuser=True,
            role_id=admin_role.id if admin_role else None,
        )
        db.add(admin_user)
        logger.info(f"Initialized default administrator account: {settings.INITIAL_ADMIN_EMAIL}")

    await db.commit()


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload["sub"]
    stmt = (
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .where(User.id == user_id)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with this token no longer exists",
        )

    return user


async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account")
    return user


def require_permission(required_perm: str) -> Callable:
    """
    Dependency checking whether the active user has the specified RBAC permission.
    Superusers automatically pass all checks.
    """
    async def permission_checker(user: User = Depends(get_current_active_user)) -> User:
        if user.is_superuser:
            return user

        if not user.role or not user.role.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: Missing permission '{required_perm}'"
            )

        user_perms = {p.permission for p in user.role.permissions}
        if required_perm not in user_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: Missing permission '{required_perm}'"
            )

        return user

    return permission_checker
