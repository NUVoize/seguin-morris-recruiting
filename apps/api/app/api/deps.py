"""Auth dependencies — current user resolution and permission gates.

Usage:
    user: User = Depends(get_current_user)                      # any signed-in user
    user: User = Depends(require_permission("can_manage_sources"))  # permission gate

Spec hard rule: never skip role-based access. Routers are protected at
include time (routes/__init__.py); write endpoints add permission gates.
"""

from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import Role, User

_bearer = HTTPBearer(auto_error=False)

_CREDENTIALS_401 = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)


def _dev_bypass_user(db: Session) -> User:
    """When AUTH_ENABLED is false, resolve a stable 'dev' user so protected
    routes work and audit logs still attribute actions. Picks the first admin
    if one is seeded, otherwise any user; never creates rows."""
    admin_role = db.query(Role).filter(Role.name == "admin").one_or_none()
    if admin_role is not None:
        user = (
            db.query(User)
            .filter(User.role_id == admin_role.id, User.status == "active")
            .first()
        )
        if user is not None:
            return user
    user = db.query(User).options(joinedload(User.role)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth disabled but no users seeded — run scripts.seed_admin.",
        )
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if not settings.auth_enabled:
        return _dev_bypass_user(db)

    if credentials is None:
        raise _CREDENTIALS_401
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = uuid.UUID(str(payload.get("sub")))
    except (JWTError, ValueError, TypeError):
        raise _CREDENTIALS_401 from None

    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.id == user_id)
        .one_or_none()
    )
    if user is None or user.status != "active":
        raise _CREDENTIALS_401
    return user


def require_permission(permission: str):
    """Dependency factory: 403 unless the user's role grants `permission`."""

    def _check(user: User = Depends(get_current_user)) -> User:
        # Auth disabled in dev: get_current_user already returned the dev user;
        # don't gate on permissions.
        if not settings.auth_enabled:
            return user
        perms = (user.role.permissions if user.role else {}) or {}
        if not perms.get(permission, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission}",
            )
        return user

    return _check
