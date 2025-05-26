from app.utils import hash_password, verify_password


class TestPasswordUtils:

    def test_hash_is_not_plaintext(self) -> None:
        """Check that hashed password is not plaintext."""

        password = "securepassword"
        hashed = hash_password(password)
        assert hashed != password
        assert isinstance(hashed, str)

    def test_correct_password_verifies(self) -> None:
        """Check that correct password verifies."""

        password = "anothersecurepassword"
        hashed = hash_password(password)
        assert verify_password(password, hashed)

    def test_incorrect_password_fails(self) -> None:
        """Check that incorrect password fails."""

        password = "correcthorsebatterystaple"
        wrong_password = "correcthorsecarrotstaple"
        hashed = hash_password(password)
        assert not verify_password(wrong_password, hashed)

    def test_hash_is_unique_due_to_salt(self) -> None:
        """Check that hash is unique due to salt."""

        password = "saltypassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2  # because bcrypt adds salt
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
