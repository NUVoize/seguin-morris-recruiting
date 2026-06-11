"""Create (or reset) an admin user. Idempotent on email.

Usage from apps/api/:
    python -m scripts.seed_admin "frederic@example.com" "Frederic Dawson"

Optional: set ADMIN_PASSWORD env var to choose the password; otherwise a
strong random one is generated and printed ONCE. Change it after first login
(password management UI arrives with the admin module).
"""

from __future__ import annotations

import os
import secrets
import sys

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import Role, User


def main() -> None:
    if len(sys.argv) < 3:
        print('Usage: python -m scripts.seed_admin "email" "Full Name"')
        sys.exit(1)

    email = sys.argv[1].strip().lower()
    full_name = sys.argv[2].strip()
    password = os.environ.get("ADMIN_PASSWORD") or secrets.token_urlsafe(14)

    with SessionLocal() as db:
        admin_role = db.execute(select(Role).where(Role.name == "admin")).scalar_one_or_none()
        if admin_role is None:
            print("ERROR: 'admin' role missing — run python -m scripts.seed first.")
            sys.exit(1)

        user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if user is None:
            user = User(
                full_name=full_name,
                email=email,
                password_hash=hash_password(password),
                role_id=admin_role.id,
                status="active",
            )
            db.add(user)
            action = "created"
        else:
            user.full_name = full_name
            user.password_hash = hash_password(password)
            user.role_id = admin_role.id
            user.status = "active"
            action = "updated (password reset)"
        db.commit()

    print(f"Admin user {action}: {email}")
    print(f"Password: {password}")
    print("Store it now — it is not shown again.")


if __name__ == "__main__":
    main()
