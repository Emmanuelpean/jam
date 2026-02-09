"""Tests for Gmail forwarding confirmation email utility functions."""

import pytest

from app.job_email_scraping.gmail import extract_forwarding_confirmation_link, extract_gmail_originator


FORWARDING_EMAIL_BODY = (
    "user@gmail.com a demandé à transférer automatiquement ses messages vers votre adresse e-mail "
    "(jam.scraper@example.com). Pour autoriser user@gmail.com à transférer ses messages vers votre "
    "adresse e-mail, veuillez cliquer sur le lien ci-dessous pour approuver la demande : "
    "https://mail-settings.google.com/mail/vf-%5BANGjdJ8nH5EPXs18VsktRI5FvcVbPItTXTNFFl5sjz1XUIGVieZte"
    "SQoV6ykFZv0o2Ou3CTdGM3dgs6slAWi6RL-tOquSVglge4DwfIeLw%5D-YPBzzHEVNTIn_UsssjTeatvjBPg "
    "Si le lien ne fonctionne pas, veuillez le copier et le coller dans une nouvelle fenêtre de "
    "navigateur. Merci d'avoir choisi Gmail. Cordialement, L'équipe Gmail Si vous n'approuvez pas "
    "cette demande, aucune action de votre part n'est requise. user@gmail.com ne peut pas transférer "
    "automatiquement ses messages vers votre adresse e-mail, sauf si vous approuvez la demande en "
    "cliquant sur le lien ci-dessus. Si vous avez accidentellement cliqué sur le lien, mais que vous "
    "ne souhaitez pas autoriser user@gmail.com à transférer automatiquement ses messages vers votre "
    "adresse, cliquez sur le lien suivant pour annuler la validation : "
    "https://mail-settings.google.com/mail/uf-%5BANGjdJ8crp9rBh5i9I-r3iERmjhlyamWW6AjJnoz2nzjEAYpevJY"
    "VJBCnSl8-peOQHxG99zkoz27zS8fQrYlciEmDRqWoHgWTIQEfMmjBg%5D-YPBzzHEVNTIn_UsssjTeatvjBPg "
    "Pour savoir pourquoi vous avez reçu ce message, veuillez consulter la page "
    "http://support.google.com/mail/bin/answer.py?answer=184973. "
    "Veuillez ne pas répondre à ce message."
)

CONFIRMATION_URL = (
    "https://mail-settings.google.com/mail/vf-%5BANGjdJ8nH5EPXs18VsktRI5FvcVbPItTXTNFFl5sjz1XUIGVieZte"
    "SQoV6ykFZv0o2Ou3CTdGM3dgs6slAWi6RL-tOquSVglge4DwfIeLw%5D-YPBzzHEVNTIn_UsssjTeatvjBPg"
)


class TestExtractForwardingConfirmationLink:
    """Test suite for extract_forwarding_confirmation_link function."""

    def test_extracts_confirmation_link(self) -> None:
        result = extract_forwarding_confirmation_link(FORWARDING_EMAIL_BODY)
        assert result == CONFIRMATION_URL

    def test_ignores_cancellation_link(self) -> None:
        result = extract_forwarding_confirmation_link(FORWARDING_EMAIL_BODY)
        assert result is not None
        assert "vf-" in result
        assert "uf-" not in result

    def test_returns_none_for_empty_body(self) -> None:
        assert extract_forwarding_confirmation_link("") is None

    def test_returns_none_for_no_urls(self) -> None:
        assert extract_forwarding_confirmation_link("This is a plain text email with no links.") is None

    def test_returns_none_for_unrelated_urls(self) -> None:
        body = "Visit https://www.google.com and https://support.google.com/mail for help."
        assert extract_forwarding_confirmation_link(body) is None

    def test_returns_none_when_only_cancellation_link(self) -> None:
        body = "Cancel here: https://mail-settings.google.com/mail/uf-sometoken123"
        assert extract_forwarding_confirmation_link(body) is None

    def test_extracts_from_english_email(self) -> None:
        body = (
            "user@gmail.com has requested to automatically forward mail to your email address. "
            "Please click the link below to confirm: "
            "https://mail-settings.google.com/mail/vf-token123abc "
            "If you did not expect this, ignore it."
        )
        result = extract_forwarding_confirmation_link(body)
        assert result == "https://mail-settings.google.com/mail/vf-token123abc"

    def test_extracts_first_confirmation_link_when_multiple(self) -> None:
        body = (
            "Link 1: https://mail-settings.google.com/mail/vf-firsttoken "
            "Link 2: https://mail-settings.google.com/mail/vf-secondtoken"
        )
        result = extract_forwarding_confirmation_link(body)
        assert result == "https://mail-settings.google.com/mail/vf-firsttoken"


class TestExtractGmailOriginator:
    """Test suite for extract_gmail_originator function."""

    def test_extracts_gmail_address(self) -> None:
        result = extract_gmail_originator(FORWARDING_EMAIL_BODY)
        assert result == "user@gmail.com"

    def test_returns_none_for_empty_body(self) -> None:
        assert extract_gmail_originator("") is None

    def test_returns_none_for_no_email(self) -> None:
        assert extract_gmail_originator("This is a plain text email with no addresses.") is None

    def test_returns_none_for_non_gmail_address(self) -> None:
        assert extract_gmail_originator("Contact us at user@outlook.com for help.") is None

    def test_extracts_first_gmail_when_multiple(self) -> None:
        body = "From first@gmail.com to second@gmail.com"
        result = extract_gmail_originator(body)
        assert result == "first@gmail.com"

    @pytest.mark.parametrize(
        "email_address",
        [
            "simple@gmail.com",
            "user.name@gmail.com",
            "user+tag@gmail.com",
            "user123@gmail.com",
            "UPPER@gmail.com",
        ],
    )
    def test_extracts_various_gmail_formats(self, email_address: str) -> None:
        body = f"Forwarding request from {email_address} received."
        result = extract_gmail_originator(body)
        assert result == email_address

    def test_does_not_match_non_gmail_domain(self) -> None:
        body = "Contact user@notgmail.com for info."
        result = extract_gmail_originator(body)
        assert result is None
