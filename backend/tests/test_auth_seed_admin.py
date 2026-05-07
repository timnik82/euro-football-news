import os
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from auth_service import hash_password, seed_admin, verify_password
from database import db


# Auth playbook regression: seed_admin should update existing admin password hash when env password changes/mismatches
@pytest.mark.anyio
async def test_seed_admin_updates_existing_admin_hash_when_mismatch():
    admin_email = os.environ["ADMIN_EMAIL"]
    admin_password = os.environ["ADMIN_PASSWORD"]

    await db.users.update_one(
        {"email": admin_email},
        {"$set": {"password_hash": hash_password("TEST_wrong_password_123")}},
        upsert=True,
    )

    await seed_admin()

    admin_doc = await db.users.find_one({"email": admin_email}, {"_id": 0, "password_hash": 1})
    assert isinstance(admin_doc, dict)
    assert isinstance(admin_doc.get("password_hash"), str)
    assert verify_password(admin_password, admin_doc["password_hash"])
