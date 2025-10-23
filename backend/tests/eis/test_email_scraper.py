"""Test module for email_scaper.py functions and JobScraper class"""

import datetime
from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session

from app.eis import schemas
from app.eis.email_scraper import JobScraper
from app.eis.job_scraper import extract_indeed_jobs_from_email
from app.eis.models import JobAlertEmail, ScrapedJob, EisServiceLog
from app.models import Setting
from tests.conftest import open_file
from tests.eis import resources
from tests.eis.test_job_scraper import MockLinkedinJobScraper, MockIndeedJobScraper


# ------------------------------------------------------ FIXTURES ------------------------------------------------------


@pytest.fixture
def test_service_log(session) -> EisServiceLog:
    """Create a test EisServiceLog record"""

    # noinspection PyArgumentList
    service_log = EisServiceLog(run_datetime=datetime.datetime.now())
    session.add(service_log)
    session.commit()
    return service_log


@pytest.fixture(autouse=True)
def patch_get_indeed_redirected_url(monkeypatch) -> None:
    """Automatically patch get_indeed_redirected_url in all tests to avoid real HTTP requests"""

    def mock_get_indeed_redirected_url(url: str) -> str:
        """Mock function to replace get_indeed_redirected_url"""

        conversion = {
            "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0CaUNNDciQjB8b911OChydWlMiE438Jot_lydiWr9Z7lbj9cwyJAEEXhSuW8SoD7Wz1bcqpb5rq8IzPxIcuirUCwOlLSL9SL1F572G6Ye9pXIlV00tsAM20VfzF1b86kTFEpwUl5cqoBjsMlRudbS30FMebfIGC01chUG_dRw15uQJAniZZ9m2OwXKNijACF8VWjBKulQ_zZI6qbz8kD41WGqtaC6lMPRCw5kXUrJbTDCaqSpugfThHENgjlu3j5DBWMjvzWpApXtcxY1NTDKT2jg6q-Z5ZkxpZFWJpPicGjeEfETjD8De3kM__AclzfTjESmozVOJMXW85h3mgPZ94GIuFEx8ppqwDwLENrDoalprKNGMFQOeZ9u9dMbxUX_RJCqW9z1vgoP6UivsqTanzYlukGXOhEQ6IFVnNvDODivSUcZCpO_yBMmxlJxaYuRjPQmnuvS8CFyF8B-M_msQscB4GMRxaiGJuzie7_iJr6nKUP2O7lo1n69wInEp_MnehsLtxzcDysc6eBzfF4v2KkuXm1RRPbFqeIA7TK2sPoy2Z8b3VGKVcWv8k90XwuftkqxlnbbXeP3t1ygWiIMHdoJNVKkxUu46MZXtM498k9txG9p9ByQhDcOI8_BRoVsP3DM1wQl1ang-WkAVoo2PTwmdtETp3VlZZuUfSGtYYEdj-E9JmOVulmnyjbLfssmM%3D&xkcb=SoB56_M3u5Oxdj0MCJ0ObzkdCdPP&camk=UoKtGZLa3XLCRNJifgWECQ%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true": "06498cad9de95b12",
            "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0D_vIW1HWJamhhVblwSY9vEnB3YehQDBaLQWgEpQbAFvEB66TXnGDud1dy-8adNNEA8NkJwfd77g5zBB1ZOXhf8PEjWP1V1-Zs6swoSDNPKB4lvVzHxu1T3qM7FYs12eUEkiIA-iiINRZ_P2VMyvYooQezlTWytMkd2UWxnVCG9a3_m1cyaMA7DTm_syy5wCWCpCUUvgVdIOEOARvgAhUnIIz9x2Chk3LMqtby4HJFP4Jl7C-Vi5YB8H0bSA1FeugROif2FHIwU9gEobz-VsFvEz_Z4cCH3oft61BFqWCWU_wWimKzWAcDGINsjLw9tAunN_xjEdupF33Iwcd77c1urVC1OLKbL3-o2oJRyEPfNL1YN7H5cP_VieI3Fir6psGrVHQv_bNy0yYleEmT0E_DofaYunYAnzMqD_SUhvCDHia8MqrGJkTcgJp16KsMZPr5_mVLck5-3PYB-3khV71Oqfoa7q1yRWl-SN-Qfwc2OdZ8zl9PsK42-6iQ34faa2uibd37I4QFVw_Rwx7r8W-xyXpiwfe4xmkhhRGK1DeiQibftk7Dyp41hCpPZbTW_bL5F98fT1mfh1u1enhw3sXxk_BjcAXS_HZpuWi5zMuwbIztF4a8ZtEo_fNdlevRIwrN-0-0qjuEDoJYSxnY3mvd2WkDit7XyYAQWaCBCtSOLVSvgSDi4pd033dZ1KPZD7a0uFkrEyWaWSQ%3D%3D&xkcb=SoBQ6_M3u5Oxdj0MCJ0MbzkdCdPP&camk=ethIe0s0hedS-FZyNnahJA%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true": "42b107e214095d56",
            "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0Cf-siO93BSuJ_a-mQFMzVvPBmFGGJg8IeoYoU7n3Hr-wyttwxtthbeGbpHFYWwmmWPWQtznc_slvzvpsaBmSWUWC64QSSNhEuwuNUWHSLtah1bwBpWniJ8vAR5oqbmqlY296quUSNSViPhje6fSFgDWLhGJWLOZaQ6OJRAp-V8a91no5GJKrUzj_KWnmJKR4rz_W6vZS8NYU5v9qDqx0uOlGmg1BnkC5lIZzyqlYwwOiZdPPVaEKKEr_G0GeQvlH67sGm1xTNyJw8sK6-4jN_ENAf2kd7JTexBVkGw5Mo02tAYXFvdA29R0CGRR0lyQRZtFJjgkhZvLHHLYO8JNjy_mia4G2BQ7Sx4ktyjaStia3kR4-BQNNWnr3k3ocyacfQEMHQlqE-Boaf4mwI0-BtJXesJsw9bvP207NBnfZFLJs1hUmSgvHhdYukY2qIsWXJLUVJgOyjwxdLhap0eFBEyti7g0G0mb3e1eO9ATdBP_e0h_p932Dm6wVyAZEXOddagVLoHFiJWPYnq8BUyKvm_S3vp9I57lYRrxWVTKZve2VIP18Uex6Bz0SozYOEEdgfyqQMBRAcp935Hg8aUW8GrXb3Q-js8GxuFke_S_tiEhCyNOEMjhQ-VRl5QOPdFttLD6e9-WR_H8IFLZUu3KwcfMBy1qEq1Tio%3D&xkcb=SoAk6_M3u5Oxdj0MCJ0AbzkdCdPP&camk=ethIe0s0hedep5fbP4CFtg%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true": "14a9001ba6ebb965",
            "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0COSBp8KgMXxewvi58QAG0wwdlVlJfveGrD5vFIguWoXakoblclqS-4T_znVTPKawHOSHZOxsl_jK0JZuGPspNA9roT-uonvDv2P6RZVLNvLfm0KdPGmVMWwoNgo5H64KiIVwOuf_UrhuMQzHBJIgwJkroSRqxeEQ_3FKwvys8bTaQ85PMumf55yR90-LeyTGL3GXnHmXVXSfC1MDn6qf5BpprmfFM-RGc2WNblsNn6hNEtF-n7NfrAi-f-PzOE_Fjwhx-Y50MEMdlex_3U6MgwFpw7CADiD1Fch2HOI_bhNgCdt6qoLUO2qEA1AX1Ax0_pwn33z2XS_4FOGRcb4ZGqTii1rx-Elj6c6n-95wiR2sks-xrI0uMrPaE2w8P5k5v6tx1ixIQT9liqyzcXoSS6vzmARulIHV4NUWn0e_K4EvX-A-zYBjcEGSGUrLelauCc21fXrDww_gNV_ZSmedh1M06WDaPc3K_6WYtv6-_kkYQhQJyLlyW0Ws23VNL5nfJygGuW8pXeZhbniMlcDaavPtyGoDp4EWGOAI45uMzcbnJ0UyZcRPmuQxfCD8cFz-lmNle1TxlSWFB7j5QOAIn1UbXcKS7gdbhBijiUJWdSdzfbaPNHZdIPMBs6CDUZT5dPrhj_mtNopw4DVvv-OUOAzOpx9mlyJpr5aE7ivabt7_V3CMtJpw7ieYZ4UBA5ZQQ%3D&xkcb=SoCq6_M3u5Oxdj0MCJ0HbzkdCdPP&camk=UoKtGZLa3XL6dp7SxnkD1A%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true": "eafb032fabcd77bc",
            "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0DUGxYnv6px9uI6dWZhSaSeqMgHWZda7534TRDDAqMKu87sK88i_2Gbq8z1VBS-lbE9HOACaDVAT4jwhaVY_xabO_rq24Y_veJqW-7_usP-_0tRugSmofb5DuxCq5IvmHBw1rNykLW3A5edDY3v_jFGsNtRR7fiXWfgXBO9BJc6FCnwMo2I8cy9hPyydcFqH8iy9UHGKCJzlwGZAiKzNQyLn0rE_XB9MXJX9itgkAFNjlDq17qpEbAnLeIOJCcDXQ03H-DIxBN3ycBF9r29kZ45spvjQItrgoMklzXH3jPwU2j7qTpqQxKVcw5xKYuIWDhM5YqzbSTzr7Z97yKVWDKaB7gM87UyTYdJ32cflCxws1brYrULvaC8SfbTlTbsHvAdrl7BHnq6r6j_pBdFDKWUW-HcBCMgYk3ikg7sr5qwJAmQMqMjyLYUfWLVQ2ouX79v1awn5CT_sz7DqSikuv7MUgfzGrvbjHnov-zAxQfFPwdSmWZkgIz7UdZVOXCV0M6bw-XkaWtkDrGyiJRLOmEPNiiNwLnsKek3SWBSR8qHNbsrDWHz391rS2onjNWfo5gnmims0O-R-8jgV2J2NQyYP0ZNTYquIehRay6WTLbEZRsxgCy4Pgz42H-Z71EnOTwqnZ-8qLPoJRHV0K9oMQL6&xkcb=SoC36_M3u5Oxdj0MCJ0ebzkdCdPP&camk=ethIe0s0hefv8CfXU2K9Rw%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true": "5aa22054e7a8b76e",
            "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0BqgWWSVbq3rqstnfUzC8xqhdOuKqZ9Avj77mYlc-g-lgy-1FSdO6PyFnAuQRYfp-JTSxMGeZR4wFhLR1UE4XYsePMvv1exKBMkCeCy9Dh-JYDgYqQLDREEwr5Bfy7uoO_og4WXgkp9rnXdiC6ej8lfOCDGtLs0xpRssH8ApFDX2WPI2WZLU3Dr_bYyzL-F51cHyx5ndFwTEKvG8FqgvbkNe1y7DDUUNUQ1EIdLP4bXw1hDuYRjJm9fbGQDc8LmmrzvdE37KxUZqeU3mzGz2moMrdAZPMufhp93UnQ8QmfOD8uq1LGUenfAtLXc7JvOdVmgZkFtGBtdlJ2Dce9Ty8I9XNaZR1vVTXVwfiM9K6yVwKEH5xhUCsr8a3DFXmcVOrivfiMWlzjRM8Bhtnwff6uJ8CLpNr-VdvfAHJTrsflPiwb6FZFX9sKw1kbd-zDyBDq_vEXiJor5MJKcuzQZ2DH62Tgv_dZllHjmGCWfk5775BFywNThFfEpBqM_-8GhAUHBfb6TSXITGIOiwWH6s7fbs7Fhz8wv20YInHAp2vJ--cjK9uVra5jKMPXk8XB1cUTG-ZWtKfzOtVi4TkT5lfFWC12tyMHgv72MFU3YxnXQZrswfP6D5JhZUJM5toctt1AkDeniJsTqR1-JtOeuQaLjQe7KvUV9qJ_ZUXba6qtMvOfz-BCYBDjc&xkcb=SoAq6_M3u5Oxdj0MCJ0dbzkdCdPP&camk=UoKtGZLa3XJTEZOPwEn50w%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true": "ae47862d410bbd39",
        }
        jk = conversion.get(url)
        if jk:
            return f"https://uk.indeed.com/rc/clk/dl?jk={jk}"
        return url

    import app.eis.email_parser as email_parser

    monkeypatch.setattr(email_parser, "get_indeed_redirected_url", mock_get_indeed_redirected_url, raising=False)


@pytest.fixture
def test_job_scraper(session) -> JobScraper:
    """Create a JobScraper instance for testing with mocked file dependencies."""

    # noinspection PyArgumentList
    entry = Setting(name="indeed_scraper", value="brightapi")
    session.add(entry)
    session.commit()
    return JobScraper(session)


@pytest.fixture
def job_scraper_with_brightapi_skip(session) -> JobScraper:
    """Create a JobScraper instance with BrightAPI skip enabled for indeed jobs."""

    # noinspection PyArgumentList
    entry = Setting(name="indeed_scraper", value="email")
    session.add(entry)
    session.commit()
    return JobScraper(session)


def create_email_data(
    test_users,
    filename: str,
    platform: str,
    user_index: int,
) -> schemas.JobAlertEmailCreate:
    """Create a JobAlertEmailCreate data for testing
    :param test_users: test users
    :param filename: file name
    :param platform: platform name
    :param user_index: user index"""

    ofile = open_file(f"{filename}.txt")
    return schemas.JobAlertEmailCreate(
        external_email_id=f"{filename}_{platform}_{user_index}",
        subject="Subject",
        sender=test_users[user_index].email,
        date_received=datetime.datetime.now(),
        platform=platform,
        body=ofile,
    )


# Job ids extracted from the veganjobs email body
VEGANJOBS_JOB_IDS = [
    "physicians-committee-for-responsible-medicine-remote-from-anywhere-in-the-united-states-building-healthy-communities-internship",
    "chill-gelato-canada-water-london-gelato-scooper",
]


@pytest.fixture
def linkedin_email_data(test_users) -> tuple[schemas.JobAlertEmailCreate, list[str]]:
    """Create a LinkedIn job alert email record for testing."""

    return create_email_data(test_users, "linkedin_email", "linkedin", 0), resources.LINKEDIN_JOB_IDS_1


@pytest.fixture
def linkedin_email_data_user2(test_users) -> tuple[schemas.JobAlertEmailCreate, list[str]]:
    """Create a LinkedIn job alert email record for testing."""

    return create_email_data(test_users, "linkedin_email", "linkedin", 1), resources.LINKEDIN_JOB_IDS_1


@pytest.fixture
def indeed_email_data(test_users) -> tuple[schemas.JobAlertEmailCreate, list[str]]:
    """Create an Indeed job alert email record for testing."""

    return create_email_data(test_users, "indeed_email", "indeed", 0), resources.INDEED_JOB_IDS_1


@pytest.fixture
def indeed_email_data_user2(session, test_users) -> tuple[schemas.JobAlertEmailCreate, list[str]]:
    """Create an Indeed job alert email record for testing."""

    return create_email_data(test_users, "indeed_email", "indeed", 1), resources.INDEED_JOB_IDS_1


@pytest.fixture
def veganjobs_email_data(test_users) -> tuple[schemas.JobAlertEmailCreate, list[str]]:
    """Create a VeganJobs job alert email record for testing."""

    return create_email_data(test_users, "veganjobs_email_1", "veganjobs", 0), VEGANJOBS_JOB_IDS


def create_email_record(session, test_users, filename: str, platform: str, user_index: int) -> JobAlertEmail:
    """Create a ScrapedJob record for testing.
    :param session: database session
    :param test_users: test users
    :param filename: file name
    :param platform: platform name
    :param user_index: user index"""

    email_data = create_email_data(test_users, filename, platform, user_index)
    # noinspection PyArgumentList
    email_record = JobAlertEmail(**email_data.model_dump(), owner_id=test_users[user_index].id)
    session.add(email_record)
    session.commit()
    return email_record


@pytest.fixture
def linkedin_email_record(session, test_users) -> tuple[JobAlertEmail, list[str]]:
    """Create a LinkedIn job alert email record for testing."""

    return create_email_record(session, test_users, "linkedin_email", "linkedin", 0), resources.LINKEDIN_JOB_IDS_1


@pytest.fixture
def linkedin_email_record_user2(session, test_users) -> tuple[JobAlertEmail, list[str]]:
    """Create a LinkedIn job alert email record for testing."""

    return create_email_record(session, test_users, "linkedin_email", "linkedin", 1), resources.LINKEDIN_JOB_IDS_1


@pytest.fixture
def indeed_email_record(session, test_users) -> tuple[JobAlertEmail, list[str]]:
    """Create an Indeed job alert email record for testing."""

    return create_email_record(session, test_users, "indeed_email", "indeed", 0), resources.INDEED_JOB_IDS_1


@pytest.fixture
def indeed_email_record_user2(session, test_users) -> tuple[JobAlertEmail, list[str]]:
    """Create an Indeed job alert email record for testing."""

    return create_email_record(session, test_users, "indeed_email", "indeed", 1), resources.INDEED_JOB_IDS_1


@pytest.fixture
def veganjobs_email_record(session, test_users) -> tuple[JobAlertEmail, list[str]]:
    """Create a VeganJobs job alert email record for testing."""

    return create_email_record(session, test_users, "veganjobs_email_1", "veganjobs", 0), VEGANJOBS_JOB_IDS


# ---------------------------------------------------- EMAIL METHODS ---------------------------------------------------


class TestSaveEmailToDb:
    """Test class for JobScraper.save_email_to_db method"""

    TEST_EMAILS = [
        resources.INDEED_EMAIL_1,
        resources.INDEED_EMAIL_2,
        resources.LINKEDIN_EMAIL_1,
        resources.LINKEDIN_EMAIL_2,
        resources.VEGANJOBS_EMAIL_1,
    ]
    PLATFORMS = [
        "indeed",
        "indeed",
        "linkedin",
        "linkedin",
        "veganjobs",
    ]

    def test_save_new_email_success(self, test_job_scraper, test_users, test_service_log, session) -> None:
        """Test saving a new email successfully"""

        with (patch.object(test_job_scraper, "get_email_data") as mock_get_email_data,):

            mock_get_email_data.side_effect = lambda email_id: [e for e in self.TEST_EMAILS if e["id"] == email_id][0]

            for i, message in enumerate(self.TEST_EMAILS):
                result_email, is_created = test_job_scraper.get_and_save_email_to_db(
                    message["id"], test_users[0], test_service_log.id
                )

                assert is_created
                assert result_email.external_email_id == message["id"]
                assert result_email.subject
                assert result_email.sender == message["to"]
                assert result_email.platform == self.PLATFORMS[i]
                assert result_email.body == message["body"]
                assert result_email.owner_id
                assert result_email.service_log_id == test_service_log.id

    def test_save_existing_email_returns_existing(
        self, test_job_scraper, test_service_log, session, test_users
    ) -> None:
        """Test that existing email is returned without creating a new record"""

        with (patch.object(test_job_scraper, "get_email_data") as mock_get_email_data,):

            mock_get_email_data.side_effect = lambda email_id: [e for e in self.TEST_EMAILS if e["id"] == email_id][0]

            message_id = self.TEST_EMAILS[0]["id"]

            # noinspection PyArgumentList
            existing_email = JobAlertEmail(
                external_email_id=message_id,
                subject="Different Subject",
                sender="different@example.com",
                owner_id=test_users[0].id,
                service_log_id=test_service_log.id,
                platform="indeed",
                date_received=datetime.datetime.now(),
                body="Different body content",
            )
            session.add(existing_email)
            session.commit()

            # Try to save it with a different user
            result_email, is_created = test_job_scraper.get_and_save_email_to_db(
                message_id, test_users[1], test_service_log.id
            )

            assert is_created is False
            assert result_email.id == existing_email.id
            assert result_email.subject == "Different Subject"

            # Verify only one record exists
            email_count = session.query(JobAlertEmail).count()
            assert email_count == 1


# ----------------------------------------------------- JOB METHODS ----------------------------------------------------


class TestSaveJobBaseInfoToDb:
    """Test class for JobScraper.save_job_base_info_to_db method"""

    def test_save_new_jobs_success(self, test_job_scraper, test_job_alert_emails, session, test_users) -> None:
        """Test saving new job IDs successfully"""

        job_ids = ["job_123", "job_456", "job_789"]

        result = test_job_scraper.save_job_base_info_to_db(email_record=test_job_alert_emails[0], job_ids=job_ids)

        # Verify returned list has correct length
        assert len(result) == 3

        # Verify all jobs are ScrapedJob instances
        for job_record in result:
            assert job_record.owner_id == test_users[0].id
            assert job_record.external_job_id in job_ids
            assert test_job_alert_emails[0] in job_record.emails

    def test_save_existing_jobs_returns_existing(
        self, test_job_scraper, test_job_alert_emails, session, test_users
    ) -> None:
        """Test that existing jobs are returned without creating duplicates"""

        # Create existing jobs
        existing_job_id = "existing_job_123"
        # noinspection PyArgumentList
        existing_job = ScrapedJob(external_job_id=existing_job_id, owner_id=test_users[0].id)
        session.add(existing_job)
        session.commit()
        session.refresh(existing_job)

        job_ids = [existing_job_id, "new_job_456"]

        result = test_job_scraper.save_job_base_info_to_db(email_record=test_job_alert_emails[0], job_ids=job_ids)

        # Verify returned list has correct length
        assert len(result) == 2

    def test_save_jobs_different_owners(self, test_job_scraper, test_job_alert_emails, session, test_users) -> None:
        """Test that jobs with same external_job_id but different owners are created separately"""

        assert test_job_alert_emails[0].owner_id != test_job_alert_emails[-1].owner_id

        # Save same job ID for both users
        job_ids = ["same_job_123"]

        result_1 = test_job_scraper.save_job_base_info_to_db(email_record=test_job_alert_emails[0], job_ids=job_ids)

        result_2 = test_job_scraper.save_job_base_info_to_db(email_record=test_job_alert_emails[-1], job_ids=job_ids)

        # Verify separate job records were created for each owner
        assert len(result_1) == 1
        assert len(result_2) == 1
        assert result_1[0].id != result_2[0].id
        assert result_1[0].owner_id == test_users[0].id
        assert result_2[0].owner_id == test_users[1].id

        # Verify both have the same external job ID
        assert result_1[0].external_job_id == "same_job_123"
        assert result_2[0].external_job_id == "same_job_123"

        # Verify total count in the database
        total_jobs = session.query(ScrapedJob).count()
        assert total_jobs == 2


class TestUpdateScrapedJobData:
    """Test class for JobScraper.update_scraped_job_data method"""

    def test_save_job_data_single_job_and_data(self, test_job_scraper, session, test_users) -> None:
        """Test saving job data to a single job record"""

        # noinspection PyArgumentList
        sample_scraped_job = ScrapedJob(
            external_job_id="test_job_123",
            owner_id=test_users[0].id,
        )
        session.add(sample_scraped_job)
        session.commit()
        session.refresh(sample_scraped_job)

        # Verify initial state
        assert sample_scraped_job.is_scraped is False
        assert sample_scraped_job.title is None
        assert sample_scraped_job.company is None

        sample_job_data = {
            "company": "Test Company Ltd",
            "location": "London, UK",
            "job": {
                "title": "Senior Software Engineer",
                "description": "We are looking for a senior software engineer to join our team...",
                "url": "https://example.com/job/123",
                "salary": {"min_amount": 50000.0, "max_amount": 70000.0},
            },
        }

        # Save job data
        test_job_scraper.update_scraped_job_data(job_record=sample_scraped_job, job_data=sample_job_data)

        # Refresh the record from database
        session.refresh(sample_scraped_job)

        # Verify the data was saved correctly
        assert sample_scraped_job.is_scraped is True
        assert sample_scraped_job.company == sample_job_data["company"]
        assert sample_scraped_job.location_city == "London"
        assert sample_scraped_job.location_country == "United Kingdom"
        assert sample_scraped_job.title == sample_job_data["job"]["title"]
        assert sample_scraped_job.description == sample_job_data["job"]["description"]
        assert sample_scraped_job.url == sample_job_data["job"]["url"]
        assert sample_scraped_job.salary_min == sample_job_data["job"]["salary"]["min_amount"]
        assert sample_scraped_job.salary_max == sample_job_data["job"]["salary"]["max_amount"]


# ----------------------------------------------------- RUN METHODS ----------------------------------------------------


def create_email_record1(
    session: Session, data: dict, platform: str, service_log: EisServiceLog, user
) -> JobAlertEmail:
    """Create a ScrapedJob record for testing.
    :param session: database session
    :param data: email data
    :param service_log: service log entry
    :param user: email owner
    :param platform: platform name"""

    # noinspection PyArgumentList
    email_record = JobAlertEmail(
        external_email_id=data["id"],
        subject=data["subject"],
        sender=data["to"],
        body=data["body"],
        date_received=datetime.datetime.now(),
        platform=platform,
        service_log_id=service_log.id,
        owner_id=user.id,
    )
    session.add(email_record)
    session.commit()
    return email_record


class TestProcessEmails:
    """Test suite for the _process_email_jobs method."""

    def test_process_linkedin_email_jobs_success(self, test_job_scraper, session, test_service_log, test_users) -> None:
        """Test successful processing of LinkedIn email job ids"""

        email_entry = create_email_record1(
            session,
            resources.LINKEDIN_EMAIL_1,
            "linkedin",
            test_service_log,
            test_users[0],
        )
        test_job_scraper.extract_email_data(email_record=email_entry, service_log_entry=test_service_log)

        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry.owner_id).all()
        assert len(scraped_jobs) == len(resources.LINKEDIN_JOB_IDS_1)

    def test_process_indeed_email_jobs_success(self, test_job_scraper, session, test_service_log, test_users) -> None:
        """Test successful processing of Indeed email jobs."""

        with patch("app.eis.email_scraper.extract_indeed_jobs_from_email") as mock_extract:
            email_entry = create_email_record1(
                session,
                resources.INDEED_EMAIL_1,
                "indeed",
                test_service_log,
                test_users[0],
            )
            test_job_scraper.extract_email_data(email_record=email_entry, service_log_entry=test_service_log)

            # assert it was called exactly once
            mock_extract.assert_not_called()

            scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry.owner_id).all()
            assert len(scraped_jobs) == len(resources.INDEED_JOB_IDS_1)

    def test_process_veganjobs_email_jobs_success(
        self, test_job_scraper, session, test_service_log, test_users
    ) -> None:
        """Test successful processing of VeganJobs email jobs."""

        email_entry = create_email_record1(
            session,
            resources.VEGANJOBS_EMAIL_1,
            "veganjobs",
            test_service_log,
            test_users[0],
        )
        test_job_scraper.extract_email_data(email_record=email_entry, service_log_entry=test_service_log)

        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry.owner_id).all()
        assert len(scraped_jobs) == len(resources.VEGANJOBS_JOB_IDS_1)

    def test_process_indeed_email_jobs_success_no_brightapi(
        self, job_scraper_with_brightapi_skip, session, test_service_log, test_users
    ) -> None:
        """Test successful processing of Indeed email jobs."""

        with patch("app.eis.email_scraper.extract_indeed_jobs_from_email") as mock_extract:
            email_entry = create_email_record1(
                session,
                resources.INDEED_EMAIL_1,
                "indeed",
                test_service_log,
                test_users[0],
            )
            result = job_scraper_with_brightapi_skip.extract_email_data(
                email_record=email_entry, service_log_entry=test_service_log
            )

            # assert it was called exactly once
            mock_extract.assert_called_once()

            scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == email_entry.owner_id).all()
            # assert len(scraped_jobs) == len(resources.INDEED_JOB_IDS_1)
            assert len(result) == len(resources.INDEED_EMAIL_1)

    def test_process_linkedin_email_jobs_success_duplicates_different_owners(
        self, test_job_scraper, session, linkedin_email_record, linkedin_email_record_user2, test_service_log
    ) -> None:
        """Test processing of LinkedIn email job ids for different owners but same data"""

        test_job_scraper.extract_email_data(email_record=linkedin_email_record[0], service_log_entry=test_service_log)
        test_job_scraper.extract_email_data(
            email_record=linkedin_email_record_user2[0], service_log_entry=test_service_log
        )

        # Check that each use has a copy of the jobs
        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == linkedin_email_record[0].owner_id).all()
        assert len(scraped_jobs) == len(linkedin_email_record[1])
        scraped_jobs = (
            session.query(ScrapedJob).filter(ScrapedJob.owner_id == linkedin_email_record_user2[0].owner_id).all()
        )
        assert len(scraped_jobs) == len(linkedin_email_record_user2[1])

        # Check that the jobs unique record
        assert session.query(ScrapedJob).distinct(ScrapedJob.external_job_id).count() == len(linkedin_email_record[1])

    def test_process_linkedin_email_jobs_success_duplicates_same_owner(
        self, test_job_scraper, session, linkedin_email_record, test_service_log
    ) -> None:
        """Test successful processing of LinkedIn email for the same user with duplicate job ids"""

        test_job_scraper.extract_email_data(email_record=linkedin_email_record[0], service_log_entry=test_service_log)
        test_job_scraper.extract_email_data(email_record=linkedin_email_record[0], service_log_entry=test_service_log)

        scraped_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == linkedin_email_record[0].owner_id).all()
        assert len(scraped_jobs) == len(linkedin_email_record[1])


class TestProcessAllEmails:
    """Test class for JobScraper._process_user_emails method"""

    def test_single_user(
        self,
        test_job_scraper,
        session,
        test_users,
        test_service_log,
        linkedin_email_data,
    ) -> None:
        """Test successful processing of emails for a single user with LinkedIn email"""

        # Mock get_email_ids to return emails only for first user
        with (
            patch.object(test_job_scraper, "get_email_ids") as mock_get_email_ids,
            patch.object(test_job_scraper, "get_email_data") as mock_get_email_data,
        ):

            # Setup mocks to be user-dependent
            def mock_get_email_ids_side_effect(user_email, _inbox_only, _timedelta_days) -> list[str]:
                """Mock get_email_ids to return emails only for first user"""
                if user_email == test_users[0].email:
                    return [linkedin_email_data[0].external_email_id]
                else:
                    return []

            def mock_get_email_data_side_effect(_email_id) -> schemas.JobAlertEmailCreate:
                """Mock get_email_data to return emails only for first user"""
                return linkedin_email_data[0]

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect
            mock_get_email_data.side_effect = mock_get_email_data_side_effect

            # Call the method
            result = test_job_scraper.process_emails(timedelta_days=1, service_log_entry=test_service_log)

            # Verify service log updates
            assert test_service_log.users_processed_n == 2
            assert test_service_log.emails_found_n == 1
            assert test_service_log.emails_saved_n == 1

            # Verify email was saved to database
            saved_emails = (
                session.query(JobAlertEmail)
                .filter(JobAlertEmail.external_email_id == linkedin_email_data[0].external_email_id)
                .all()
            )
            assert len(saved_emails) == 1
            assert saved_emails[0].platform == linkedin_email_data[0].platform

            # Verify jobs were created only for the first user
            user1_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[0].id).all()
            assert len(user1_jobs) == len(linkedin_email_data[1])

            # Verify no jobs for other users
            for i in range(1, len(test_users)):
                user_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[i].id).all()
                assert len(user_jobs) == 0

            # Verify empty result (no job data for LinkedIn without scraping)
            assert result == {}

    def test_multiple_users_same_jobs(
        self,
        test_job_scraper,
        session,
        test_users,
        test_service_logs,
        linkedin_email_data,
        linkedin_email_data_user2,
    ) -> None:
        """Test successful processing of emails for multiple users with different email types"""

        with (
            patch.object(test_job_scraper, "get_email_ids") as mock_get_email_ids,
            patch.object(test_job_scraper, "get_email_data") as mock_get_email_data,
        ):

            # Setup mocks to return different emails for different users
            def mock_get_email_ids_side_effect(user_email, _inbox_only, _timedelta_days) -> list[str]:
                """Mock function to return different emails for different users"""
                if user_email == test_users[0].email:
                    return [linkedin_email_data[0].external_email_id]
                elif user_email == test_users[1].email:
                    return [linkedin_email_data_user2[0].external_email_id]
                return []

            def mock_get_email_data_side_effect(email_id, user_email) -> schemas.JobAlertEmailCreate:
                """Mock method to return job data for a given email ID and user email"""
                if user_email == test_users[0].email:
                    return linkedin_email_data[0]
                elif user_email == test_users[1].email:
                    return linkedin_email_data_user2[0]
                raise ValueError(f"Unexpected call for user {user_email} and email {email_id}")

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect
            mock_get_email_data.side_effect = mock_get_email_data_side_effect

            # Call the method
            test_job_scraper.process_emails(timedelta_days=2, service_log_entry=test_service_logs[0])

            # Verify service log updates
            assert test_service_logs[0].users_processed_n == len(test_users)
            assert test_service_logs[0].emails_found_n == 2
            assert test_service_logs[0].emails_saved_n == 2
            assert test_service_logs[0].linkedin_job_n == len(linkedin_email_data[1]) + len(
                linkedin_email_data_user2[1]
            )
            assert test_service_logs[0].indeed_job_n == 0
            assert test_service_logs[0].jobs_extracted_n == len(linkedin_email_data[1]) + len(
                linkedin_email_data_user2[1]
            )

            # Verify jobs were created for appropriate users
            user1_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[0].id).all()
            user2_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[1].id).all()
            assert len(user1_jobs) == len(linkedin_email_data[1])
            assert len(user2_jobs) == len(linkedin_email_data_user2[1])

            # Verify no jobs for remaining users (if any)
            for i in range(2, len(test_users)):
                user_jobs = session.query(ScrapedJob).filter(ScrapedJob.owner_id == test_users[i].id).all()
                assert len(user_jobs) == 0

    def test_skip_brightdata(
        self,
        job_scraper_with_brightapi_skip,
        session,
        test_users,
        test_service_logs,
        indeed_email_data,
    ) -> None:
        """Test successful processing of emails for multiple users with different email types"""

        with (
            patch.object(job_scraper_with_brightapi_skip, "get_email_ids") as mock_get_email_ids,
            patch.object(job_scraper_with_brightapi_skip, "get_email_data") as mock_get_email_data,
        ):

            # Setup mocks to return different emails for different users
            def mock_get_email_ids_side_effect(user_email, _inbox_only, _timedelta_days) -> list[str]:
                """Mock get_email_ids method to return emails only for first user"""
                if user_email == test_users[0].email:
                    return [indeed_email_data[0].external_email_id]
                return []

            def mock_get_email_data_side_effect(email_id, user_email) -> schemas.JobAlertEmailCreate:
                """Mock get_email_data method to return email data only for first user"""
                if user_email == test_users[0].email:
                    return indeed_email_data[0]
                raise ValueError(f"Unexpected call for user {user_email} and email {email_id}")

            mock_get_email_ids.side_effect = mock_get_email_ids_side_effect
            mock_get_email_data.side_effect = mock_get_email_data_side_effect

            # Call the method
            result = job_scraper_with_brightapi_skip.process_emails(2, test_service_logs[0])

            assert len(result) == 23


class TestScrapeRemainingJobs:
    """Test cases for the _scrape_remaining_jobs method"""

    @staticmethod
    def _scraped_jobs(session, email_record) -> list[ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        scraped_jobs = []
        owner_id = email_record[0].owner_id
        for job_id in email_record[1]:
            # noinspection PyArgumentList
            scraped_job = ScrapedJob(external_job_id=job_id, owner_id=owner_id)
            scraped_job.emails.append(email_record[0])
            session.add(scraped_job)
            scraped_jobs.append(scraped_job)
        session.commit()
        return scraped_jobs

    @pytest.fixture
    def indeed_scraped_jobs(self, test_users, session, indeed_email_record) -> list[ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        return self._scraped_jobs(session, indeed_email_record)

    @pytest.fixture
    def indeed_scraped_jobs_user2(self, test_users, session, indeed_email_record_user2) -> list[ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        return self._scraped_jobs(session, indeed_email_record_user2)

    @pytest.fixture
    def linkedin_scraped_jobs(self, test_users, session, linkedin_email_record) -> list[ScrapedJob]:
        """Fixture to create Indeed scraped jobs for multiple users"""

        return self._scraped_jobs(session, linkedin_email_record)

    def test_indeed_success(
        self,
        indeed_scraped_jobs,
        test_service_logs,
        test_job_scraper,
        session,
    ) -> None:
        """Test successful processing of Indeed email jobs"""

        with patch("app.eis.email_scraper.IndeedJobScraper") as mock_scraper_class:
            # Create mock instance
            mock_scraper_instance = MockIndeedJobScraper(resources.INDEED_JOB_IDS_1)
            mock_scraper_class.return_value = mock_scraper_instance

            # Call the method we're testing
            test_job_scraper.scrape_save_jobs(session, test_service_logs[0], {})

            # Verify all jobs are now scraped
            unscraped_jobs_after = session.query(ScrapedJob).filter().all()
            for job in unscraped_jobs_after:
                assert job.is_scraped
                assert job.scrape_error is None

    def test_indeed_nobrightapi_success(
        self,
        indeed_scraped_jobs,
        test_service_logs,
        job_scraper_with_brightapi_skip,
        session,
    ) -> None:
        """Test successful processing of Indeed email jobs"""

        with patch("app.eis.email_scraper.IndeedJobScraper") as mock_scraper_class:
            # Create mock instance
            mock_scraper_instance = MockIndeedJobScraper(resources.INDEED_JOB_IDS_1)
            mock_scraper_class.return_value = mock_scraper_instance

            # Call the method we're testing
            jobs = extract_indeed_jobs_from_email(indeed_scraped_jobs[0].emails[0].body)
            job_data = {}
            for job in jobs:
                job_ids = job_scraper_with_brightapi_skip.extract_indeed_job_ids(job["job"]["url"])
                if job_ids:  # Make sure we have at least one job ID
                    job_data[job_ids[0]] = job
            job_scraper_with_brightapi_skip.scrape_save_jobs(session, test_service_logs[0], job_data)

            # Verify all jobs are now scraped
            jobs_after = session.query(ScrapedJob).filter().all()
            for job in jobs_after:
                assert job.is_scraped
                assert not job.is_failed

    def test_indeed_nobrightapi_fail(
        self,
        indeed_scraped_jobs,
        test_service_logs,
        job_scraper_with_brightapi_skip,
        session,
    ) -> None:
        """Test successful processing of Indeed email jobs"""

        with patch("app.eis.email_scraper.IndeedJobScraper") as mock_scraper_class:
            # Create mock instance
            mock_scraper_instance = MockIndeedJobScraper(resources.INDEED_JOB_IDS_1)
            mock_scraper_class.return_value = mock_scraper_instance

            # Call the method we're testing
            job_scraper_with_brightapi_skip.scrape_save_jobs(session, test_service_logs[0], {})

            # Verify all jobs are now scraped
            jobs_after = session.query(ScrapedJob).filter().all()
            for job in jobs_after:
                assert job.is_scraped
                assert job.is_failed

    def test_linkedin_success(
        self,
        linkedin_scraped_jobs,
        test_service_logs,
        test_job_scraper,
        session,
    ) -> None:
        """Test successful processing of Indeed email jobs"""

        with patch("app.eis.email_scraper.LinkedinJobScraper") as mock_scraper_class:
            # Create mock instance
            mock_scraper_instance = MockLinkedinJobScraper(resources.INDEED_JOB_IDS_1)
            mock_scraper_class.return_value = mock_scraper_instance

            # Call the method we're testing
            test_job_scraper.scrape_save_jobs(session, test_service_logs[0], {})

            # Verify all jobs are now scraped
            jobs_after = session.query(ScrapedJob).filter().all()
            for job in jobs_after:
                assert job.is_scraped
                assert not job.is_failed

    def test_indeed_multiple_users_shared_jobs_success(
        self,
        indeed_scraped_jobs,
        indeed_scraped_jobs_user2,
        test_service_logs,
        test_job_scraper,
        session,
    ) -> None:
        """Test successful processing of Indeed email jobs"""
        from unittest.mock import patch, MagicMock

        with patch("app.eis.email_scraper.IndeedJobScraper") as mock_scraper_class:
            # Create mock instance
            mock_scraper_instance = MockIndeedJobScraper(resources.INDEED_JOB_IDS_1)

            # Wrap the scrape_job method with a MagicMock to track calls
            original_scrape_job = mock_scraper_instance.scrape_job
            mock_scraper_instance.scrape_job = MagicMock(side_effect=original_scrape_job)

            mock_scraper_class.return_value = mock_scraper_instance

            # Call the method we're testing
            test_job_scraper.scrape_save_jobs(session, test_service_logs[0], {})

            # Verify all jobs are now scraped
            jobs_after = session.query(ScrapedJob).filter().all()
            assert len(jobs_after) == len(indeed_scraped_jobs) + len(indeed_scraped_jobs_user2)
            for job in jobs_after:
                assert job.is_scraped
                assert not job.is_failed

            # Count how many times scrape_job() was called
            scrape_job_call_count = mock_scraper_instance.scrape_job.call_count
            assert scrape_job_call_count == len(indeed_scraped_jobs)
