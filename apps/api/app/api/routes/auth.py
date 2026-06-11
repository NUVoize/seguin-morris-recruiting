"""Auth routes — login, logout, current user.

Stateless JWT sessions (12h, HS256, secret from Railway env). Login and
logout are audit-logged per spec hard rule #6. Failed logins are audited
without revealing whether the email exists.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.models import AuditLog, User
from app.schemas.auth import AuthUser, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _to_auth_user(user: User) -> AuthUser:
    return AuthUser(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        preferred_language=getattr(user.preferred_language, "value", str(user.preferred_language)),
        role_name=user.role.name if user.role else None,
        permissions=(user.role.permissions if user.role else {}) or {},
    )


@router.post("/login", response_model=TokenResponse, summary="Authenticate and receive a JWT")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.execute(
        select(User).options(joinedload(User.role)).where(User.email == payload.email.lower())
    ).scalar_one_or_none()

    valid = (
        user is not None
        and user.status == "active"
        and user.password_hash is not None
        and verify_password(payload.password, user.password_hash)
    )

    if not valid:
        db.add(
            AuditLog(
                user_id=user.id if user else None,
                action="auth.login_failed",
                entity_type="user",
                entity_id=user.id if user else None,
                audit_metadata={"email": payload.email.lower()},
            )
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    assert user is not None  # narrowed by `valid`
    token = create_access_token(
        subject=str(user.id),
        extra_claims={"role": user.role.name if user.role else None},
    )
    db.add(
        AuditLog(
            user_id=user.id,
            action="auth.login",
            entity_type="user",
            entity_id=user.id,
            audit_metadata={"email": user.email},
        )
    )
    db.commit()

    return TokenResponse(
        access_token=token,
        expires_in_minutes=settings.jwt_expire_minutes,
        user=_to_auth_user(user),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="End the session")
def logout(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """JWTs are stateless — the client discards the token; we log the event."""
    db.add(
        AuditLog(
            user_id=user.id,
            action="auth.logout",
            entity_type="user",
            entity_id=user.id,
        )
    )
    db.commit()


@router.get("/me", response_model=AuthUser, summary="Current authenticated user")
def me(user: User = Depends(get_current_user)) -> AuthUser:
    return _to_auth_user(user)
