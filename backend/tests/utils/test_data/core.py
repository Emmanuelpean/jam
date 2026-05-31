"""Centralised test data for both conftest.py and seed_database.py"""

# -------------------------------------------------------- USER --------------------------------------------------------


USER_DATA = [
    # Regular user
    {
        "email": "regular@example.com",
        "password": "password1",
        "premium": {"is_active": True},
        "is_verified": True,
        "first_name": "Regular",
        "last_name": "User",
        "app_version": "10.0.0",
        "preferences": {"dark_mode": "dark"},
    },
    # Admin user
    {
        "email": "admin@example.com",
        "password": "password2",
        "is_admin": True,
        "is_verified": True,
        "first_name": "Admin",
        "last_name": "User",
        "app_version": "10.0.0",
    },
    # Inactive user
    {
        "email": "inactive@example.com",
        "password": "password3",
        "is_active": False,
        "is_verified": True,
        "app_version": "10.0.0",
    },
    # Unverified user
    {
        "email": "user5@example.com",
        "password": "password5",
        "is_verified": False,
        "app_version": "10.0.0",
    },
    # Demo user
    {
        "email": "demo@example.com",
        "password": "demo_password",
        "is_verified": True,
        "is_demo": True,
    },
    # Named users for specific tests
    {
        "email": "emmanuelpean@gmail.com",
        "password": "test_password",
        "is_verified": True,
        "premium": {"is_active": True},
        "app_version": "10.0.0",
    },
    # Named users for specific tests
    {
        "email": "jessicaaggood@live.co.uk",
        "password": "test_password",
        "is_verified": True,
        "premium": {"is_active": True},
        "app_version": "10.0.0",
    },
    # User with stripe details
    {
        "email": "strip_customer@example.com",
        "password": "password6",
        "is_verified": True,
        "stripe_details": {"customer_id": "cus_test_123", "subscription_id": "sub_id"},
        "app_version": "10.0.0",
    },
    # Non-premium user
    {
        "email": "non-premium_user@example.com",
        "password": "password7",
        "is_verified": True,
        "app_version": "10.0.0",
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
assert USER_DATA[DEMO_USER_INDEX]["is_demo"], "DEMO_USER_INDEX does not point to a demo user"

# TOAST user 1
TOAST_USER_1_INDEX = 5
assert USER_DATA[TOAST_USER_1_INDEX]["premium"]

# TOAST user 2
TOAST_USER_INDEX_2 = 6
assert USER_DATA[TOAST_USER_INDEX_2]["premium"]

# Stripe user
STRIPE_USER_INDEX = 7
assert USER_DATA[STRIPE_USER_INDEX]["stripe_details"], "STRIPE_USER_INDEX does not point to a stripe_details user"

# Non premium used
NON_PREMIUM_USER_INDEX = 8
assert not USER_DATA[NON_PREMIUM_USER_INDEX].get(
    "premium"
), "NON_PREMIUM_USER_INDEX does not point to a non premium user"

# ------------------------------------------------------ SETTINGS ------------------------------------------------------


SETTINGS_DATA = [
    {
        "name": "allowlist",
        "value": ", ".join([data["email"] for data in USER_DATA] + ["newuser@user.com"]),
        "description": "Emails allowed to sign up",
    },
    {
        "name": "default_person_role",
        "value": "Recruiter",
        "description": "Default role for new persons",
    },
]


# ------------------------------------------------- USER QUALIFICATIONS ------------------------------------------------


USER_QUALIFICATION_DATA = [
    {"owner_id": 1, "education": "BSc Computer Science"},
    {"owner_id": 1, "education": "BSc Computer Science + PhD Artificial Intelligence"},
    {"owner_id": 2, "education": "BSc Computer Science"},
    {"owner_id": 2, "education": "MSc Computer Science"},
    {
        "owner_id": 6,
        "education": "BSc in physics; MSc in Nanosciences; PhD in photochemistry of perovksite solar cells",
        "experience": "12 years Python",
        "skills": "3D printing",
        "interests": "software engineering",
    },
    {
        "owner_id": 7,
        "education": "Nutritionist",
        "interests": "Animal rights",
    },
]
