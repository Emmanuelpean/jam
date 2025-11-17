"""Pytest fixtures for EIS tests"""

import datetime as dt
from typing import Any, Generator
from unittest import mock

import pytest

from app.eis import email_parser
from app.eis import schemas, models
from app.eis.email_scraper import JobEmailScraper
from app.models import Setting
from tests.eis import resources
from tests.eis.test_job_scraper import MockVeganJobsJobScraper, MockIndeedJobScraper, MockLinkedinJobScraper
from tests.utils.create_data import create_service_logs, create_job_alert_emails, create_scraped_jobs


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

    monkeypatch.setattr(email_parser, "get_indeed_redirected_url", mock_get_indeed_redirected_url, raising=False)


@pytest.fixture
def test_service_logs(session) -> list[models.EisServiceLog]:
    """Create test service logs"""

    return create_service_logs(session)


@pytest.fixture
def test_job_alert_emails(session, test_users, test_service_logs) -> list[models.JobAlertEmail]:
    """Create test job alert emails"""

    return create_job_alert_emails(session, test_users, test_service_logs)


@pytest.fixture
def test_scraped_jobs(session, test_users, test_job_alert_emails) -> list[models.ScrapedJob]:
    """Create test job alert email jobs"""

    return create_scraped_jobs(session, test_job_alert_emails, test_users)


@pytest.fixture(scope="session", autouse=True)
def mock_linkedin_job_scrapers() -> Generator[type[MockLinkedinJobScraper], Any, None]:
    """Mock LinkedinJobScraper for all tests"""

    with mock.patch("app.eis.email_scraper.LinkedinJobScraper", MockLinkedinJobScraper) as mocked:
        yield mocked


@pytest.fixture(scope="session", autouse=True)
def mock_indeed_job_scrapers() -> Generator[type[MockIndeedJobScraper], Any, None]:
    """Mock IndeedJobScraper for all tests"""

    with mock.patch("app.eis.email_scraper.IndeedJobScraper", MockIndeedJobScraper) as mocked:
        yield mocked


@pytest.fixture(scope="session", autouse=True)
def mock_veganjobs_job_scrapers() -> Generator[type[MockVeganJobsJobScraper], Any, None]:
    """Mock VeganJobsJobScraper for all tests"""

    with mock.patch("app.eis.email_scraper.VeganJobsJobScraper", MockVeganJobsJobScraper) as mocked:
        yield mocked


@pytest.fixture
def test_service_log(session) -> models.EisServiceLog:
    """Create a test EisServiceLog record"""

    service_log = models.EisServiceLog(run_datetime=dt.datetime.now())
    session.add(service_log)
    session.commit()
    return service_log


@pytest.fixture
def test_job_scraper(session) -> JobEmailScraper:
    """Create a JobScraper instance for testing with mocked file dependencies."""

    entry = Setting(name="indeed_scraper", value="brightapi")
    session.add(entry)
    session.commit()
    return JobEmailScraper(session)


@pytest.fixture
def job_scraper_with_brightapi_skip(session) -> JobEmailScraper:
    """Create a JobScraper instance with BrightAPI skip enabled for indeed jobs."""

    entry = Setting(name="indeed_scraper", value="email")
    session.add(entry)
    session.commit()
    return JobEmailScraper(session)


@pytest.fixture
def email_data_factory(test_users, test_service_log):
    """Factory fixture for creating email data from resources"""

    def _create(email_id: str, user_index: int = 0) -> tuple[schemas.JobAlertEmailCreate, list[str]]:
        email_resource = resources.TEST_EMAILS.get(email_id + "_" + test_users[user_index].email)

        email_data = schemas.JobAlertEmailCreate(
            external_email_id=str(email_resource["id"]),
            subject=email_resource["subject"],
            sender=email_resource["from"],
            date_received=email_resource["date"],
            platform=email_resource["platform"],
            body=email_resource["body"],
            service_log_id=test_service_log.id,
        )

        return email_data, email_resource["job_ids"]

    return _create


@pytest.fixture
def email_record_factory(session, test_users, email_data_factory):
    """Factory fixture for creating email records in the database."""

    def _create(email_id: str, user_index: int = 0) -> tuple[models.JobAlertEmail, list[str]]:
        email_data, job_ids = email_data_factory(email_id, user_index)
        email_record = models.JobAlertEmail(**email_data.model_dump(), owner_id=test_users[user_index].id)
        session.add(email_record)
        session.commit()

        return email_record, job_ids

    return _create


@pytest.fixture(autouse=True)
def mock_get_email_data():
    """Auto-applied mock for get_email_data across all tests in module"""
    with mock.patch(
        "app.emails.email_service.EmailService.get_email_data", side_effect=lambda eid: resources.NEW_TEST_EMAILS[eid]
    ) as email_mock:
        yield email_mock
