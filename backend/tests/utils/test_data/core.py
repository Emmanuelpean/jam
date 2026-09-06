"""Centralised test data for both conftest.py and seed_database.py"""

# -------------------------------------------------------- USER --------------------------------------------------------

REGULAR_USER = {
    "email": "regular@example.com",
    "password": "password1",
    "premium": {"is_active": True},
    "is_verified": True,
    "first_name": "Regular",
    "last_name": "User",
    "app_version": "10.0.0",
    "preferences": {"dark_mode": "dark"},
}


ADMIN_USER = {
    "email": "admin@example.com",
    "password": "password2",
    "is_admin": True,
    "is_verified": True,
    "first_name": "Admin",
    "last_name": "User",
    "app_version": "10.0.0",
}

INACTIVE_USER = {
    "email": "inactive@example.com",
    "password": "password3",
    "is_active": False,
    "is_verified": True,
    "app_version": "10.0.0",
}


UNVERIFIED_USER = {
    "email": "user5@example.com",
    "password": "password5",
    "is_verified": False,
    "app_version": "10.0.0",
}


PREMIUM_USER_1 = {
    "email": "emmanuelpean@gmail.com",
    "password": "test_password",
    "is_verified": True,
    "premium": {"is_active": True},
    "app_version": "10.0.0",
}

PREMIUM_USER_2 = {
    "email": "jessicaaggood@live.co.uk",
    "password": "test_password",
    "is_verified": True,
    "premium": {"is_active": True},
    "app_version": "10.0.0",
}

STRIPE_USER = {
    "email": "strip_customer@example.com",
    "password": "password6",
    "is_verified": True,
    "stripe_details": {"customer_id": "cus_test_123", "subscription_id": "sub_id"},
    "app_version": "10.0.0",
}

NON_PREMIUM_USER = {
    "email": "non-premium_user@example.com",
    "password": "password7",
    "is_verified": True,
    "app_version": "10.0.0",
}

USER_DATA = [
    REGULAR_USER,
    ADMIN_USER,
    INACTIVE_USER,
    UNVERIFIED_USER,
    PREMIUM_USER_1,
    PREMIUM_USER_2,
    STRIPE_USER,
    NON_PREMIUM_USER,
]


# ------------------------------------------------------ SETTINGS ------------------------------------------------------


SETTINGS_DATA = [
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
        "owner_id": 5,
        "education": "BSc in physics; MSc in Nanosciences; PhD in photochemistry of perovksite solar cells",
        "experience": "12 years Python",
        "skills": "3D printing",
        "interests": "software engineering",
    },
    {
        "owner_id": 6,
        "education": "Nutritionist",
        "interests": "Animal rights",
    },
]
