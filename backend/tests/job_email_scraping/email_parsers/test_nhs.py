"""Tests for NHS email parser."""

import pytest

from app.job_email_scraping.email_parsers.nhs import parse_nhs_job_email, extract_alert_name
from utils.job_email_resources import NHS_EMAIL_3, NHS_EMAIL_4


class TestParseIndeedJobEmail:

    def test_email_1(self) -> None:

        output = parse_nhs_job_email(NHS_EMAIL_3["body"])
        assert len(output) == len(NHS_EMAIL_3["parsed_output"])
        for out, exp in zip(output, NHS_EMAIL_3["parsed_output"]):
            assert out.model_dump() == exp.model_dump()

    def test_email_2(self) -> None:

        output = parse_nhs_job_email(NHS_EMAIL_4["body"])
        assert len(output) == len(NHS_EMAIL_4["parsed_output"])
        for out, exp in zip(output, NHS_EMAIL_4["parsed_output"]):
            assert out.model_dump() == exp.model_dump()


class TestExtractJobAlertTitle:
    """Test suite for extract_job_alert_title function."""

    @pytest.mark.parametrize(
        "html_body,expected_result",
        [
            # Full HTML with both keywords and location
            (
                """<html><body>
                    <td>
                        <h3>Your job alert settings</h3>
                        <ul>
                            <li>Your keywords: public health</li>
                            <li>Your location: Cardiff (Caerdydd)</li>
                            <li>Frequency: Daily</li>
                        </ul>
                    </td>
                    </body></html>""",
                "public health Cardiff (Caerdydd)",
            ),
            # Simplified HTML
            (
                """<td>
                        <h3>Your job alert settings</h3>
                        <li>Your keywords: software engineer</li>
                        <li>Your location: London</li>
                    </td>""",
                "software engineer London",
            ),
            # With inline styles
            (
                """<td style="font-family:Arial; max-width:560px; color:#000">
                        <h3>Your job alert settings</h3>
                        <li>Your keywords: data science</li>
                        <li>Your location: Manchester</li>
                    </td>""",
                "data science Manchester",
            ),
            # Different keyword types
            (
                """<td>
                        <h3>Your job alert settings</h3>
                        <li>Your keywords: python developer</li>
                        <li>Your location: Bristol</li>
                    </td>""",
                "python developer Bristol",
            ),
            (
                """<td>
                        <h3>Your job alert settings</h3>
                        <li>Your keywords: R&D engineer</li>
                        <li>Your location: Oxford</li>
                    </td>""",
                "R&D engineer Oxford",
            ),
            # Location with special characters
            (
                """<td>
                        <h3>Your job alert settings</h3>
                        <li>Your keywords: analyst</li>
                        <li>Your location: Edinburgh (Dùn Èideann)</li>
                    </td>""",
                "analyst Edinburgh (Dùn Èideann)",
            ),
            # Heading in different tag
            (
                """<td>
                        <div>Your job alert settings</div>
                        <li>Your keywords: engineer</li>
                        <li>Your location: Leeds</li>
                    </td>""",
                "engineer Leeds",
            ),
        ],
    )
    def test_extract_both_keywords_and_location(self, html_body: str, expected_result: str) -> None:
        """Test extraction and concatenation of both keywords and location."""
        result = extract_alert_name(html_body)
        assert result == expected_result

    @pytest.mark.parametrize(
        "html_body,expected_result",
        [
            # Only keywords
            (
                "<td><h3>Your job alert settings</h3><li>Your keywords: engineer</li></td>",
                "engineer",
            ),
            (
                "<td><h3>Your job alert settings</h3><li>Your keywords: data analyst</li></td>",
                "data analyst",
            ),
            # Only location
            (
                "<td><h3>Your job alert settings</h3><li>Your location: London</li></td>",
                "London",
            ),
            (
                "<td><h3>Your job alert settings</h3><li>Your location: Manchester</li></td>",
                "Manchester",
            ),
        ],
    )
    def test_extract_single_field(self, html_body: str, expected_result: str) -> None:
        """Test extraction when only keywords or location are present."""
        result = extract_alert_name(html_body)
        assert result == expected_result

    @pytest.mark.parametrize(
        "html_body",
        [
            # No "Your job alert settings" heading
            "<td><li>Your keywords: test</li></td>",
            # Empty HTML
            "",
            # Heading exists but no keywords/location
            "<td><h3>Your job alert settings</h3><li>Frequency: Daily</li></td>",
            # Heading not inside td
            "<div>Your job alert settings</div><span>Your keywords: test</span>",
        ],
    )
    def test_extract_returns_none(self, html_body: str) -> None:
        """Test that None is returned when heading not found or no keywords/location found."""
        result = extract_alert_name(html_body)
        assert result is None

    def test_case_insensitivity(self) -> None:
        """Test that function works with different cases."""
        html_variations = [
            "<td><h3>Your job alert settings</h3><li>YOUR KEYWORDS: test</li><li>YOUR LOCATION: city</li></td>",
            "<td><h3>Your job alert settings</h3><li>your keywords: test</li><li>your location: city</li></td>",
            "<td><h3>Your job alert settings</h3><li>Your Keywords: test</li><li>Your Location: city</li></td>",
        ]

        for html in html_variations:
            result = extract_alert_name(html)
            assert result == "test city"

    def test_whitespace_handling(self) -> None:
        """Test that extra whitespace is properly handled."""
        html = """<td>
            <h3>Your job alert settings</h3>
            <li>Your keywords:   data scientist   </li>
            <li>Your location:   London   </li>
        </td>"""
        result = extract_alert_name(html)

        assert result == "data scientist London"
        assert "  " not in result  # No double spaces

    def test_multiline_html(self) -> None:
        """Test extraction from multiline HTML with various formatting."""
        html = """
        <table>
            <tr>
                <td style="padding:20px">
                    <h3>Your job alert settings</h3>
                    <ul>
                        <li style="font-size:19px">
                            Your keywords: machine learning
                        </li>
                        <li style="font-size:19px">
                            Your location: Cambridge
                        </li>
                    </ul>
                </td>
            </tr>
        </table>
        """
        result = extract_alert_name(html)
        assert result == "machine learning Cambridge"

    def test_order_is_keywords_then_location(self) -> None:
        """Test that keywords always come before location in result."""
        html = """<td>
            <h3>Your job alert settings</h3>
            <li>Your location: London</li>
            <li>Your keywords: engineer</li>
        </td>"""
        result = extract_alert_name(html)
        # Should be "engineer London" regardless of order in HTML
        assert result == "engineer London"

    def test_single_space_separator(self) -> None:
        """Test that parts are separated by single space."""
        html = "<td><h3>Your job alert settings</h3><li>Your keywords: test</li><li>Your location: city</li></td>"
        result = extract_alert_name(html)
        assert result.count(" ") == 1  # Only one space between parts

    def test_multiple_td_elements_finds_correct_one(self) -> None:
        """Test that function finds the correct td when multiple td elements exist."""
        html = """
        <table>
            <td>Wrong td with keywords</td>
            <td>
                <h3>Your job alert settings</h3>
                <li>Your keywords: correct</li>
                <li>Your location: here</li>
            </td>
            <td>Another wrong td</td>
        </table>
        """
        result = extract_alert_name(html)
        assert result == "correct here"

    def test_heading_case_variations(self) -> None:
        """Test that function handles different cases of the heading text."""
        html_variations = [
            "<td><h3>YOUR JOB ALERT SETTINGS</h3><li>Your keywords: test</li></td>",
            "<td><h3>your job alert settings</h3><li>Your keywords: test</li></td>",
            "<td><h3>Your Job Alert Settings</h3><li>Your keywords: test</li></td>",
        ]

        for html in html_variations:
            result = extract_alert_name(html)
            assert result == "test"

    def test_emails(self) -> None:

        output = extract_alert_name(NHS_EMAIL_3["body"])
        assert output == NHS_EMAIL_3["alert_name"]
        output = extract_alert_name(NHS_EMAIL_4["body"])
        assert output == NHS_EMAIL_4["alert_name"]
