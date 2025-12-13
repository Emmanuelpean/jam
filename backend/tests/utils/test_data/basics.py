"""Centralised test data for both conftest.py and seed_database.py"""

USER_DATA = [
    # Regular user
    {
        "email": "regular@example.com",
        "password": "password1",
        "toast_active": True,
        "is_verified": True,
    },
    # Admin user
    {
        "email": "admin@example.com",
        "password": "password2",
        "is_admin": True,
        "is_verified": True,
    },
    # Inactive user
    {
        "email": "inactive@example.com",
        "password": "password3",
        "is_active": False,
        "is_verified": True,
    },
    # Unverified user
    {
        "email": "user5@example.com",
        "password": "password5",
        "is_verified": False,
    },
    # Demo user
    {
        "email": "test@example.com",
        "password": "password4",
        "is_verified": True,
        "is_demo": True,
    },
    # Named users for specific tests
    {
        "email": "emmanuelpean@gmail.com",
        "password": "test_password",
        "is_verified": True,
        "toast_active": True,
    },
    # Named users for specific tests
    {
        "email": "jessicaaggood@live.co.uk",
        "password": "test_password",
        "is_verified": True,
        "toast_active": True,
    },
]

# Regular user
REGULAR_USER_INDEX = 0
assert (
    USER_DATA[REGULAR_USER_INDEX]["is_verified"]
    and not USER_DATA[REGULAR_USER_INDEX].get("is_demo")
    and not USER_DATA[REGULAR_USER_INDEX].get("is_admin")
)

# Admin user
ADMIN_USER_INDEX = 1
assert USER_DATA[ADMIN_USER_INDEX]["is_admin"], "ADMIN_USER_INDEX does not point to an admin user"

# Inactive user (e.g. deactivated by admin)
INACTIVE_USER_INDEX = 2
assert not USER_DATA[INACTIVE_USER_INDEX]["is_active"], "INACTIVE_USER_INDEX does not point to an inactive user"

# Unverified user (i.e. email address not verified)
UNVERIFIED_USER_INDEX = 3
assert not USER_DATA[UNVERIFIED_USER_INDEX]["is_verified"], "UNVERIFIED_USER_INDEX does not point to an unverified user"

# Test user (for demo)
DEMO_USER_INDEX = 4
assert USER_DATA[DEMO_USER_INDEX]["is_demo"], "TEST_USER_INDEX does not point to a test user"


# TOAST user 1
TOAST_USER_1_INDEX = 5
assert USER_DATA[TOAST_USER_1_INDEX]["toast_active"]

# TOAST user 1
TOAST_USER_INDEX_2 = 6
assert USER_DATA[TOAST_USER_INDEX_2]["toast_active"]


SETTINGS_DATA = [
    {
        "name": "allowlist",
        "value": ",".join([data["email"] for data in USER_DATA] + ["newuser@user.com"]),
        "description": "Emails allowed to sign up",
    },
    {
        "name": "default_person_role",
        "value": "Recruiter",
        "description": "Default role for new persons",
    },
]

USER_QUALIFICATION_DATA = [
    {"owner_id": 1, "education": "BSc Computer Science"},
    {"owner_id": 1, "education": "BSc Computer Science + PhD Artificial Intelligence"},
    {"owner_id": 2, "education": "BSc Computer Science"},
    {"owner_id": 2, "education": "MSc Computer Science"},
    {"owner_id": 4, "education": "BSc Computer Science"},
    {"owner_id": 5, "education": "BSc Computer Science"},
    {
        "owner_id": 6,
        "education": "BSc in physics; MSc in Nanosciences; PhD in photochemistry of perovksite solar cells",
        "experience": "12 years Python",
        "skills": "3D printing",
        "interests": "software engineering",
    },
]
