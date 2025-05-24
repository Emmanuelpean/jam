from app.utils import hash_password, verify_password


class TestPasswordUtils:

    def test_hash_is_not_plaintext(self) -> None:
        password = "securepassword"
        hashed = hash_password(password)
        assert hashed != password
        assert isinstance(hashed, str)

    def test_correct_password_verifies(self) -> None:
        password = "anothersecurepassword"
        hashed = hash_password(password)
        assert verify_password(password, hashed)

    def test_incorrect_password_fails(self) -> None:
        password = "correcthorsebatterystaple"
        wrong_password = "correcthorsecarrotstaple"
        hashed = hash_password(password)
        assert not verify_password(wrong_password, hashed)

    def test_hash_is_unique_due_to_salt(self) -> None:
        password = "saltypassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2  # because bcrypt adds salt
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
