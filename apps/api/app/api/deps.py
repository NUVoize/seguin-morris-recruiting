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

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import User

_bearer = HTTPBearer(auto_error=False)

_CREDENTIALS_401 = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
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
        perms = (user.role.permissions if user.role else {}) or {}
        if not perms.get(permission, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission}",
            )
        return user

    return _check
