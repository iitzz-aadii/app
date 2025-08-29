from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional


class DummyUser:
    def __init__(
        self, user_id: int = 1, email: str = "admin@example.com", role: str = "admin"
    ):
        self.id = user_id
        self.email = email
        self.role = role


security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> DummyUser:
    # Minimal permissive auth: accept any bearer token or none, return admin user
    # Replace with real JWT/session validation later
    if credentials is None or not credentials.credentials:
        # Still allow access in development; return admin
        return DummyUser()
    # If provided, pretend it's valid and return a mentor for variety
    return DummyUser(user_id=2, email="mentor@example.com", role="mentor")
