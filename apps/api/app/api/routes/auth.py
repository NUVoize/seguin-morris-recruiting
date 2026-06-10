"""Auth route placeholders. Real login / logout / me arrive in Phase 2 once users are seeded."""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", summary="Authenticate a user (Phase 2)")
def login() -> dict[str, str]:
    """Placeholder. Phase 2 will accept credentials, return a JWT, and write an audit log."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Auth is scaffolded in Phase 1; full login lands in Phase 2.",
    )


@router.post("/logout", summary="Invalidate the current session (Phase 2)")
def logout() -> dict[str, str]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Logout lands in Phase 2.",
    )


@router.get("/me", summary="Current authenticated user (Phase 2)")
def me() -> dict[str, str]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="/me lands in Phase 2.",
    )
