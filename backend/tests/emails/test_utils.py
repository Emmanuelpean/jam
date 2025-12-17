"""Tests for email utility functions"""

import pytest

from app.emails.utils import clean_email_address, get_user_id_from_email, build_multi_from_query


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
            ("emmanuel péan, phd <emmanuelpean@gmail.com>", "emmanuelpean@gmail.com"),
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


class TestBuildMultiFromQuery:
    """Test suite for build_multi_from_query function"""

    @pytest.mark.parametrize(
        "input_emails, expected_output",
        [
            # Single email as string
            ("alert@indeed.com", 'FROM "alert@indeed.com"'),
            # Single email as list
            (["alert@indeed.com"], 'FROM "alert@indeed.com"'),
            # Two emails
            (["alert@indeed.com", "noreply@indeed.com"], 'OR FROM "alert@indeed.com" FROM "noreply@indeed.com"'),
            # Three emails - nested OR
            (
                ["email1@domain.com", "email2@domain.com", "email3@domain.com"],
                'OR OR FROM "email1@domain.com" FROM "email2@domain.com" FROM "email3@domain.com"',
            ),
            # Four emails - double nested OR
            (
                ["a@test.com", "b@test.com", "c@test.com", "d@test.com"],
                'OR OR OR FROM "a@test.com" FROM "b@test.com" FROM "c@test.com" FROM "d@test.com"',
            ),
        ],
        ids=[
            "single_email_string",
            "single_email_list",
            "two_emails",
            "three_emails",
            "four_emails",
        ],
    )
    def test_valid_email_queries(self, input_emails, expected_output) -> None:
        """Test that valid email inputs produce correct IMAP query strings"""
        result = build_multi_from_query(input_emails)
        assert result == expected_output

    def test_empty_list_raises_index_error(self) -> None:
        """Test that empty list raises IndexError"""
        with pytest.raises(IndexError):
            build_multi_from_query([])

    def test_string_with_special_characters(self) -> None:
        """Test email addresses with special characters"""
        result = build_multi_from_query("user+tag@example.com")
        assert result == 'FROM "user+tag@example.com"'

    def test_preserves_email_case(self) -> None:
        """Test that email address case is preserved"""
        result = build_multi_from_query("Alert@Indeed.COM")
        assert result == 'FROM "Alert@Indeed.COM"'

    @pytest.mark.parametrize(
        "input_emails",
        [
            ["email@domain.com", "another@domain.com", "third@domain.com", "fourth@domain.com", "fifth@domain.com"],
        ],
        ids=["five_emails"],
    )
    def test_large_email_list(self, input_emails) -> None:
        """Test that larger lists produce correct nested OR structure"""
        result = build_multi_from_query(input_emails)

        # Verify structure
        assert result.startswith("OR " * (len(input_emails) - 1))
        for email in input_emails:
            assert f'FROM "{email}"' in result

    def test_whitespace_in_emails(self) -> None:
        """Test emails with leading/trailing whitespace are handled"""
        result = build_multi_from_query([" email@domain.com ", "test@domain.com"])
        # Note: Function doesn't strip whitespace - test actual behavior
        assert 'FROM " email@domain.com "' in result
