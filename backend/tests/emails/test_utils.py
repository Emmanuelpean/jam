import pytest

from app.emails.utils import clean_email_address, get_user_id_from_email


class TestCleanEmailAddress:
    """Test class for clean_email_address function"""

    @pytest.mark.parametrize(
        "sender_field,expected",
        [
            ("John Doe <john.doe@gmail.com>", "john.doe@gmail.com"),
            ("john.doe@gmail.com", "john.doe@gmail.com"),
            ('"John Doe" <john.doe@gmail.com>', "john.doe@gmail.com"),
            ("Test User <TEST.USER@EXAMPLE.COM>", "test.user@example.com"),
            ("  test@example.com  ", "test@example.com"),
            ("Invalid Format", "invalid"),
            ("Jane Smith <jane.smith+tag@company.co.uk>", "jane.smith+tag@company.co.uk"),
            ("Multiple Words Name <multi.word@domain.org>", "multi.word@domain.org"),
        ],
    )
    def test_clean_email_address(self, sender_field, expected) -> None:
        """Test email address cleaning with various formats"""

        result = clean_email_address(sender_field)
        assert result == expected


class TestGetUserIdFromEmail:
    """Test class for get_user_id_from_email function"""

    def test_get_user_id_existing_user(self, session, test_users) -> None:
        """Test getting user ID for existing user"""

        test_user = test_users[0]
        result = get_user_id_from_email(test_user.email, session)
        assert result == test_user.id

    def test_get_user_id_non_existing_user(self, session) -> None:
        """Test getting user ID for non-existing user returns default ID 1"""

        with pytest.raises(AssertionError):
            get_user_id_from_email("nonexistent@example.com", session)

    def test_get_user_id_empty_email(self, session) -> None:
        """Test getting user ID with empty email"""

        with pytest.raises(AssertionError):
            get_user_id_from_email("", session)

    def test_get_user_id_case_sensitivity(self, session, test_users) -> None:
        """Test that email lookup is case-sensitive (as per database collation)"""

        test_user = test_users[0]
        upper_email = test_user.email.upper()
        with pytest.raises(AssertionError):
            get_user_id_from_email(upper_email, session)
