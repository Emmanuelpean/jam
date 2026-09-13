"""Tests for string helper utilities."""

import pytest

from app.utilities.strings import clean_email, sanitize_rich_text


class TestCleanEmail:

    @pytest.mark.parametrize(
        "value,expected",
        [
            ("  Test@Example.com  ", "test@example.com"),
            ("ALREADY@LOWER.COM", "already@lower.com"),
            ("no_change@example.com", "no_change@example.com"),
        ],
    )
    def test_strips_and_lowercases(self, value: str, expected: str) -> None:
        assert clean_email(value) == expected


class TestSanitizeRichText:

    @pytest.mark.parametrize(
        "value,expected",
        [
            (None, None),
            ("", ""),
            ("Plain text, no html", "Plain text, no html"),
            ("<p>Paragraph</p>", "<p>Paragraph</p>"),
            (
                "<p>Bold <strong>word</strong> and <em>italic</em></p>",
                "<p>Bold <strong>word</strong> and <em>italic</em></p>",
            ),
            ("<ul><li>one</li><li>two</li></ul>", "<ul><li>one</li><li>two</li></ul>"),
            ("<h2>Heading</h2><p>Body</p>", "<h2>Heading</h2><p>Body</p>"),
        ],
    )
    def test_allowed_formatting_passes_through_unchanged(self, value: str | None, expected: str | None) -> None:
        assert sanitize_rich_text(value) == expected

    def test_strips_script_tag_and_content(self) -> None:
        result = sanitize_rich_text("<p>Hello</p><script>alert(document.cookie)</script>")
        assert "<script" not in result
        assert "alert" not in result
        assert result == "<p>Hello</p>"

    def test_strips_event_handler_attributes(self) -> None:
        result = sanitize_rich_text('<p onclick="alert(1)">Click me</p>')
        assert "onclick" not in result
        assert "alert" not in result
        assert result == "<p>Click me</p>"

    def test_strips_onerror_from_disallowed_img_tag(self) -> None:
        result = sanitize_rich_text('<img src=x onerror="alert(document.cookie)">Text')
        assert "onerror" not in result
        assert "<img" not in result
        assert "Text" in result

    def test_strips_javascript_href_scheme(self) -> None:
        result = sanitize_rich_text('<a href="javascript:alert(1)">click</a>')
        assert "javascript:" not in result
        assert "click" in result

    def test_keeps_safe_href_scheme(self) -> None:
        result = sanitize_rich_text('<a href="https://example.com">link</a>')
        assert 'href="https://example.com"' in result

    def test_strips_style_attribute_and_tag(self) -> None:
        result = sanitize_rich_text('<p style="background:url(javascript:alert(1))">Text</p><style>body{}</style>')
        assert "style" not in result
        assert result == "<p>Text</p>"

    def test_strips_disallowed_tag_but_keeps_its_text(self) -> None:
        # iframe/object/etc. aren't in the allow-list: nh3 drops the tag but keeps inner text (it isn't executable).
        assert sanitize_rich_text("<iframe>not executed</iframe>") == "not executed"

    def test_idempotent(self) -> None:
        once = sanitize_rich_text("<p>Bold <strong>word</strong></p><script>alert(1)</script>")
        twice = sanitize_rich_text(once)
        assert once == twice
