"""Pytest fixtures for EIS tests"""

import datetime as dt
from typing import Any, Generator
from unittest import mock

import pytest

from app.eis.email_parsers import indeed
from app.eis import models
from app.eis.email_scraper import JobEmailScraper
from app.models import Setting
from tests.eis import resources
from tests.eis.test_job_scrapers import (
    MockVeganJobsBrightdataJobScraper,
    MockIndeedBrightdataJobScraper,
    MockLinkedinBrightdataJobScraper,
    MockNhsBrightdataJobScraper,
)
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
            "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0BqHw2Kdabow-zaZerv7IYvcs9NXwgGXCQ4Yq9ZuNDUZupX_PjHHQtlBSgsuvZxmuMvOmrGU-_LFM84aMj8DWumNAKURYRrRrrmecvJeZ0Q0_2SytDuZDaOgG1PREvGWfL9yQKky5AIoUi5FKM3kEd1e3SHIPJZy3krBF8wS5EsnipP3maoH4hONlbhhNXpXHq3Btzs3Ro1hQLlXSnhfqBSh6Kt26MDCw06ur6mnq1d1wr1taSjAYznYN9bJuwetdYvZLVX9IY8i7m7v5HGTQ0tqQtcyZAIwHbYZuRdZ5XuuRfxIA92LCLPgAi8xya8JrmOYHxjegboMJqmKBEzk3hmhyWPlc7FnMw4KoIVGu_IrLpmI6zk5GfXH7K8kWfs0XuVcnumnQk_iC2Z42jN_ZP2LcZVHGbKepkK_RoPtbbz1WqjZ3p-gJpFLurNnR8r79PafoAW02WtBPRW3FfTDXosdUdc0BwP1T9a3LvWAX3mZd1HdfpphyvfC717SR3Ugi2HcwIGG0GahBezatLZIpoaBOAq3J9Ss-lJNaiShJowpBIa8K7sATH-OMbM6XurFuXOamoPaOdPeYwmk1-pEIJKfr-R5js3i0gLyt0jhmbf_S6_rR7NkhxRplH1zyiUTlNMWCRIb3t9GIVx5ZnYwrc8D5ofb94ipolHl0pPjwPlrr_oO49xs-Szxs-WD4AelPRZhr_kDszXFJhTPdIzF709zPMf0aNOVy8%3D&xkcb=SoBc6_M3qqbMHd70qJ0UbzkdCdPP&camk=UoKtGZLa3XLcsBzeqbBEJw%3D%3D&p=0&jsa=3136&rjs=1&tmtk=1jba9gso3jat7800&gdfvj=1&plid=indeed-jobalert&alid=673f848ab1dadb7545004995&fvj=1&g1tAS=true": "69dc0e80e86c41fd",
            "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0CL1bq_XcmbMJxyFrECa_KvguSmCDjHlqIXbxc4E8cdcCc-X5a-3G8Dvc8o_tbC5rkvfHkxvK9FxryQx_wDKnayxKZY1xbx4Z2VdsoELeiU_Sa8uqE3WnMv28uW8wRfxnXcenjh-BNC6Sz9MCajAmNbs0h5HqkUpcmhpM4ykZDkMOToHATd6oydyjUM_JdjqWzDID7FvN6TkdqHbximVwFnqVDgHDb7voKPM7aw6531m-oLZTYk9U6fTK_QK0JgnYzu8k0F4oHhQFGkX7cVUpmhw2GIBMnhI39xKPPEyBILvG2s9ddcJh90PmK_zuwma0tktHJGD0JKKm90Gk60yNas6U4VAb6gAVNpEAKl-erTBYsJ4lySlBVQ4TkcIC4KK0tuYlvYR3UlWTCoCH02pcmk7EGv8-iJpLNrJYSFA5mKoInJaKeiqTSamwFT9AKwoHb9MGKoCfWq8gh8-5Ek4xFNsO3ipAnthHe9iUcb0NQbt2UJMsVoSgW6VBiNkixwLjoj_j169xT3N0DIUCBI7NWHZu-qmt4-VC3BruR1U5-ouTr6juWc479wGUfcQPfNq0YXjoW50T1sycvl_3rKDdDfXjKXuIguf9Rw-jA67nhRjunQ_rnhdjb0QRPB4hJsqyTRXF3F6AhDAVCOM_XFuHiUQE1uKw1RJXcGewSZ296TKzdudj9vpjjSle-DcC2exUF-BeXFRPzpKZh5BhlR7vwScnhXjA4WGd_E0rD5pfcjiox3-LspDjb3Vj5QT2Ywq8WSrr1IaM1yFce0XUVIBHeRtWPK5l50zvs%3D&xkcb=SoAd6_M3qqbMHd70qJ0gbzkdCdPP&camk=UoKtGZLa3XJXNLYW0dNy-Q%3D%3D&p=0&jsa=3136&rjs=1&tmtk=1jba9gso3jat7800&gdfvj=1&plid=indeed-jobalert&alid=673f848ab1dadb7545004995&fvj=1&g1tAS=true": "c60a03a7c36863e0",
            "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0BmPNLmPDCqdSYNUCTKgszmmOXenJJM-5zhk3Y4TZkJd6YIeUOCKkFXLkW5oKxIjfe60bhsRacnvgafjcBI7Rx6xZztqOXWG9-m70aoRvT9wn4Fu-gAymWWo88BF2ts_mtciL7Uwxvh5xqhUUElc8atMx-Pn3fEzmT3WQJv3uf9HhCYxkwcIAnllbsgIdfcp1Er7fqrGqZgS06qXteUfUZBXe8zF7rVchypdR8RfeFfj3YPsZIy3AyDUfu5MGSc5UfYi6783RLxBKu8AjOAGsbS3i1VoE9pCidgdUpE_An_hOdIqJAI7iXsQYIKQRR-M5W221Q6Bt7cUVJ51uI522_slUezhsM4heR3DeAr71iLLvKIts6-z9ClHQAVZPiFCLRj1yRZXI9w3Os-l5276PAcDrpgJJeykaI14LG9x83d28-fqKpMXJnL5xz7zrfaa0S7-t1EDYtKZk9Z2XfIbtskmcJdhFafKSC2bI-EJ5XBYMjTie7oLOUecDL2nBkbnHB22nQBPjEiXZ0tVJT4WXI1AWDfvoybyNbmE55jiqGPCvwRaRjuFfR3LmKujUMCa9rlF-PB0MxvJlTno2UCKRPStqMS_C8PpaP6-1xo-jznwar9TfMOSAhhKQ771V-sDM9Ln3xJcyNO16Y1s3UbR9O3eq1h4GEbFJ1IDDqwKHwUDTR2zPbyvSmtfpPlU7MTHQNk1nlqaCxpsRyyvaf4kcFb&xkcb=SoDm6_M3qqbMHcb0qJ0PbzkdCdPP&camk=UoKtGZLa3XKY29MlAqlVBQ%3D%3D&p=0&jsa=3136&rjs=1&tmtk=1jba9gso3jat7800&gdfvj=1&plid=indeed-jobalert&alid=673f848ab1dadb7545004995&fvj=1&g1tAS=true": "5905c38dc605509f",
            "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0AC1TTQBgD1ihv5Ah-0XElhog-c4C718UNMoShFurW3J70yntcGk-hqygBCs_b93-UhJDyMteycp9xg1SL1VAhSIovk9h8o2Mwu5UGDHgF7-GwnTh5266v09jNIdrAvWug_LaONoQpPj41sraKXxMAzxvhGDROWDfJMw7s-Lyi3qJMQlZ4m-vPtDlDKhFsRcMfjJYcZ69UlLmob1j2Fdyn9wL71qo9dhB5W3L_hisSoony42TNMpTxjrPO6JyWtg8hExLSiArlTX5a-8QIaA_scMH75Mr9hP4zEl6UvqX6_xzbe6HmVrtD-h2IXsZaKcPxC8VFVEoLi4EZM0dmdVIEiov0bRDcxuESapomH4ViLs_Ksyd19atVh46wNyYjhtG60D9KO_AzOvvKKYz03vv8V07mZJeY75S9331UCqII4-gmkno_qfEW8uXdN8g-eHXDdPvMNOKc2cCCrQLBo1_SfRXaCh3VZiXvyrr-97j9j7AF5-15NRlda4FnZjC_ahNwCIpJfFbDQvlNQaOTa30FK5-RAw7lbLtKmVx82P9qMBizIizfC2bQfNqJEXH_v00q8evfZybnfggr0IYzLRhrQiAvBQZ1ZuubT-G4cL6qcnUk0jc9dEHqqBo3JeNu1foM6XmGRtJSdGMSCaQL1RhLHUtxQN1EGQuUthE7Bg2MlfeEToarS8Z5S1DQPrd1gKoHcWcvoxPIpeA%3D%3D&xkcb=SoCB6_M3qqbMHcb0qJ0HbzkdCdPP&camk=UoKtGZLa3XK9vA_O1mPLrA%3D%3D&p=0&jsa=3136&rjs=1&tmtk=1jba9gso3jat7800&gdfvj=1&plid=indeed-jobalert&alid=673f848ab1dadb7545004995&fvj=1&g1tAS=true": "995e08bb529563bf",
            "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0AyB6-03b0maBjwOYRHed0zGdKYeeDUcmdmD572RvVaIz0Bz4szoCM7RDvw8GIkuB21ZuZBRuTw3LQVDOTf5j_XJ05E2yUuzJt8RFi9CZ4gMvKeqTzphLlNNXHzolszGy80mwULwL2dQXQFbd7V2Y8mH9MbrP-M3JIyH-pyMU08QymJQOn7sO1si_ufoL1R7ZVgD7llO2T-RSxuuKmiIYJpmr4lRLuazzU2AByagsNaY4SSJMkd64xcbx4Qq7ARLtzL-Hx2KlmP1GrQkP2S-F_vTbVZm8iIEJVS1faWvloGXvpFsEtTQ2RE4od4ygT0eY8ML0hmaPKqv6wYLm71nf8juBa6IjoOAvF59gQKz0IEMB3GFfRqRGTJ2nU9nbJj7pRBvTFKS75ib6wsAS7plm0wpYJd16NxzZGHOxy-jLmyxdpaWuAOs_PR8xOImaFNkWThnXnoCZPqe9EnLQq5MhCh62r5_7Vo6r5LI7D7vbRnjJrDOKyIlKiqoYy4gP32eZE-G1KTmkPiALEUbHxqTVQv5Q0yFa0J6My5PvJaZRHfETODvvK8EormSzNM84HtrzVpV2cVb7UA4H7TBfdq_8DVgAQ2ClhxcsTinPo6BXmIH1q_36ZuA4tq5a-9dFozz1TFo3HMlOETSAc-UxLlzne-T47dTQ_APtA8UVPUEZTQk_R9HPHOkipOYvW7HsfRhRI%3D&xkcb=SoCP6_M3qqbMHcb0qJ0abzkdCdPP&camk=UoKtGZLa3XJRCZiT9osVjw%3D%3D&p=0&jsa=3136&rjs=1&tmtk=1jba9gso3jat7800&gdfvj=1&plid=indeed-jobalert&alid=673f848ab1dadb7545004995&fvj=1&g1tAS=true": "01d9b888da4655ae",
            "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0AC1TTQBgD1ihv5Ah-0XElhog-c4C718UNMoShFurW3J70yntcGk-hq3y7qr9o2vrEUoV4EluMkPUhets4tuVS7pPkkvdIeUIZxrivHwmP0AV7ioNGxEdGnUebRi7n6iu486R8fO-zAJ-9j4Px7nL1C2HQPOn8l57JOt3tYqh1k-ea9AQw40JxoEskE8s2bul-fnhpX_d-dCuWF9ivd8X8M5oG3W2oRF2yrkkY84fyaWV7Hfs6ti1NYIjb4sC2d7gz3baIZcZyVEBy6prb7MuHfKF3HnzhRSCB03WryWDOD-hrf3v33O-nHoIQilkatAxB2wmSBpyOjVQCQT5XLLbcZKST-4tOUWD4NRkZnHCVah2dFSqtSJ12_TgPGVYgbBXxhzmKLuXttJhXO7SDNYceEhQvXrbGhqyztK4IRpJa84PpB519UKMqleJG-B90Ql5Ei0dU7Z_AioGsqIZdCiwgy1-yWhntmeZXw6BK_Ujuo5u65wUzd6EXg8a1YCXXEmlz5J_BbWuR17cA7y28R_1x_cKCA3392Boft0TARIv3cylmv-iS2aTjh9iNjIAY6GtYVC29vRI7ka30gwX1C1E_t197AvC1TBSnCxyFWxkfcYMT9QHuQckvQVMqWt03jxdaNWJxo30lF5XEVRWbNcBOsFcLGYvgdg-D-v-NuGMp5pnylxCs25coxChHhI7Ml3kgAc3Qxz_Xz3g%3D%3D&xkcb=SoCc6_M3qqbMHcb0qJ0ebzkdCdPP&camk=UoKtGZLa3XIBTnXoXRt3Ew%3D%3D&p=0&jsa=3136&rjs=1&tmtk=1jba9gso3jat7800&gdfvj=1&plid=indeed-jobalert&alid=673f848ab1dadb7545004995&fvj=1&g1tAS=true": "f956884733eeef61",
            "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0AyB6-03b0maBjwOYRHed0zGdKYeeDUcmdmD572RvVaIz0Bz4szoCM7LTAxS4WBsK0POCGtq0FH2CDSCJ8P0kkcc3y-JDs9IjzPl9Tgk0555ZxZy5vBm9TbiuIiVAY6t4v_6h0n6Y0D3K3zTeRre8wQDTAe6Cw2_TnyzjzcN2JcV6WDdRluKOoyMXrYTLkmqmgjFbWVzyR0DJxr_yQJw27BE1mnJYqu6bib8kTOsDKn8m-Y2FGJtj3MIj6tDKmjCdrJlwRRcmNZE7SOpruFqs7QtFGry6XL4JD6WGpitcIxjxVSnOkeOSyhnmJlfpsPlY_qpiII8qD5YeisTi87ayNWraenY2YhDNTqUDKSwXhy4vTY4vduZuCFO8KtmLiZ-xQza_7n3nHuuTgeFP8528e6lvmqMMDhJsQhkabbfLiPJwm6iq5KUl2-5udOQh6F0tuYFUWKR2p85rsW1ymrJ8OOxYScKHQVUSfTgIwYLOXAqRDOgQXqmQgRxe2-O9BCWYKxLuXy-P37M6ov6pWra0BmOhHH33_dyyXtP0pJ_x_rgjonDoaDrLp3Lokyp2YZROVVEJnj02agt_kfTEV-oePJ_8oP81s0bPBR6mopfrx9wAIUqSFLFguOlAaBe9FsVQGaNXyqVfCGuIr4qBH_RQYFzVrbmELCj0q4OymNlTSJGpyCy9vwfR0LoT4mbYSAs6Fbak3hZP2dqkuPhmRdG5SC&xkcb=SoDo6_M3qqbMHcb0qJ0SbzkdCdPP&camk=UoKtGZLa3XLF8DIo2Ny9ew%3D%3D&p=0&jsa=3136&rjs=1&tmtk=1jba9gso3jat7800&gdfvj=1&plid=indeed-jobalert&alid=673f848ab1dadb7545004995&fvj=1&g1tAS=true": "2763488177ff4bbc",
            "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0D7aWMMTiD0MLUf8BGBBaTXYC_8rjZJSU5Qoa0D94Bkf5Zt2NKKkklcd83_UZUJoz_-oQCk4kQXB1mNnlYWcS-BJjShtIpjmDU7UR71Nz8zgqqVCDwjzmY0F9a-w5mI5sDobfFGUaflaoS48TYZ2Z5kSrQU_A80quVGPA_Ki4WGP02kud1AQ0Kuqv2xsnxF2QMy8opd5X6oCy5yiUCpvWB2NcqMYvo-2JvWiyUf_dc29o484SIiRBMptobBI8YIOr8QaPbNwQ0Ya2QBitT5YqC50r1DnSh_4ntdweQdiDr3vVgZvCeuRK16pkkAJfT2_vqZNFfocr3Y6EyWtIAd9Vho7p-7HC_IlwRbVncGj5VwrFVwBvAal2M4qzJaqsBgJy3FlUOupgrfU1zEPTOjy2lhN_HuNRDzf3UOyOWOW5LZf4dmXrg_h7bsdnsbe2ga8SARADJqazk3rrtg7NHycEfrVtCUt4oZFuJldvWUACDRYWjDZcltQur4v-OxtNk2nHZh2gg5gQneS49ug-fVwwuII3dFtlabVb8VKIr5wpGITaXaUFT7mQyZZfLN_3fvxbktzsDEU9gEX6SYuscWpWtL0eMOHp-x5yggWbG2wy86w4jHrNc2Y7uhHpREWALYvKclubZ6Sy-0EWLVCTSHo2B_zm03DR7WE_0bk94fN96tGg%3D%3D&xkcb=SoBJ6_M3qSSPJHXcXR0CbzkdCdPP&camk=4HOcmqOLYrBpUxr5z1JeNg%3D%3D&p=0&jsa=3695&rjs=1&tmtk=1jaid05i1hghb800&gdfvj=1&plid=indeed-jobalert&alid=68c494f3aacfa1792822774c&fvj=1&g1tAS=true": "18fcef299b7a0072",
            "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0Bi6A_Oun8FvQAAhpPq3O2DMYREfOL2TH_q05cd5kTje9bY_9-jo-D2lZBLx7t6YgDMkbz4UY3UzZ8oVvPVxSnR1U60rOkTrBM-ACR4qHhPjGZ2pUAPGLMDsIn9S9c725fIaqJuRFxLjlVqy0nnH3Zup8h37OYcbiFxh84F2d-nE2c2xrwxV-NPVtEddSf2WBczlH0-6sL1rqo6XJtocw9fQWN8pRCQopHmHvEqQRdMmxlKYIViyPQTqRQcOWPnVGrjE2KUS_HX5jWxQPZZFJ5MXJEkucGunPHUVqlZ6009rqaZcdIZu84hMbBr6vsC_W4-kJjhMR1uXwzk9wVf0sY4CNIbKzQ0zXBJCl4JU4hMP04rnr54c4goN7glFoCPH4cgzDcIRQOhIMBEG4fnIIcolhRx9zC1Cd86YTAsezYVviejlEG5p5MAROqIOJGH--kNyzw3S26dYwZu_12_n7PvkiKGoGycm6ssNp8GYLCJcHAPdXAYSxBfwKSROzuAdMkTbgcJWsXqMSKq8Z0Bupr5IWATKO593RDY8ES1Vokk2tFSNlFZ1VUq2-yuV0qU_OfY1rc7gbQ5lkYuEi7c0YK4BFi5cc4VLmtTiLcBBZbLyV-yn-S1krNtjNaJNQeWRjPvy3zH-4mS0sbbMiRBPavBLyMWO0ZBy2_XM8ieRpff3InQJRgW2e5m1hxPDpffJfkA_lIbdXBwgHJNVo_snFgE5gmJ5fQP9Fw%3D&xkcb=SoCk6_M3qSSPJE3cXR0DbzkdCdPP&camk=UoKtGZLa3XIp0HpG1Wa7rA%3D%3D&p=0&jsa=3695&rjs=1&tmtk=1jaid05i1hghb800&gdfvj=1&plid=indeed-jobalert&alid=68c494f3aacfa1792822774c&fvj=1&g1tAS=true": "4a05c3ef450f6704",
        }

        jk = conversion.get(url)
        if jk:
            return f"https://uk.indeed.com/rc/clk/dl?jk={jk}"
        return url

    monkeypatch.setattr(indeed, "get_indeed_redirected_url", mock_get_indeed_redirected_url, raising=False)


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
def mock_linkedin_job_scrapers() -> Generator[type[MockLinkedinBrightdataJobScraper], Any, None]:
    """Mock LinkedinJobScraper for all tests"""

    with mock.patch("app.eis.email_scraper.LinkedinBrightdataJobScraper", MockLinkedinBrightdataJobScraper) as mocked:
        yield mocked


@pytest.fixture(scope="session", autouse=True)
def mock_indeed_job_scrapers() -> Generator[type[MockIndeedBrightdataJobScraper], Any, None]:
    """Mock IndeedJobScraper for all tests"""

    with mock.patch("app.eis.email_scraper.IndeedBrightdataJobScraper", MockIndeedBrightdataJobScraper) as mocked:
        yield mocked


@pytest.fixture(scope="session", autouse=True)
def mock_veganjobs_job_scrapers() -> Generator[type[MockVeganJobsBrightdataJobScraper], Any, None]:
    """Mock VeganJobsJobScraper for all tests"""

    with mock.patch("app.eis.email_scraper.VeganJobsJobScraper", MockVeganJobsBrightdataJobScraper) as mocked:
        yield mocked


@pytest.fixture(scope="session", autouse=True)
def mock_nhs_job_scrapers() -> Generator[type[MockNhsBrightdataJobScraper], Any, None]:
    """Mock NhsJobScraper for all tests"""

    with mock.patch("app.eis.email_scraper.NhsJobScraper", MockNhsBrightdataJobScraper) as mocked:
        yield mocked


@pytest.fixture
def test_service_log(session) -> models.EisServiceLog:
    """Create a test EisServiceLog record"""

    # noinspection PyArgumentList
    service_log = models.EisServiceLog(run_datetime=dt.datetime.now())
    session.add(service_log)
    session.commit()
    return service_log


@pytest.fixture
def test_job_scraper(session) -> JobEmailScraper:
    """Create a JobScraper instance for testing with mocked file dependencies."""

    # noinspection PyArgumentList
    entry = Setting(name="indeed_scraper", value="brightapi")
    session.add(entry)
    session.commit()
    return JobEmailScraper(session)


@pytest.fixture
def job_scraper_with_brightapi_skip(session) -> JobEmailScraper:
    """Create a JobScraper instance with BrightAPI skip enabled for indeed jobs."""

    # noinspection PyArgumentList
    entry = Setting(name="indeed_scraper", value="email")
    session.add(entry)
    session.commit()
    return JobEmailScraper(session)


@pytest.fixture
def email_record_factory(session, test_users, test_service_log) -> Any:
    """Factory fixture for creating email records in the database."""

    def _create(email_id: str, user_index: int = 0) -> tuple[models.JobAlertEmail, list[str]]:
        email_resource = resources.TEST_EMAILS.get(email_id + "_" + test_users[user_index].email)

        email_data = dict(
            external_email_id=str(email_resource["id"]),
            subject=email_resource["subject"],
            sender=email_resource["from"],
            date_received=email_resource["date"],
            platform=email_resource["platform"],
            body=email_resource["body"],
            service_log_id=test_service_log.id,
        )

        # noinspection PyArgumentList
        email_record = models.JobAlertEmail(**email_data, owner_id=test_users[user_index].id)
        session.add(email_record)
        session.commit()

        return email_record, email_resource["parsed_output"]

    return _create


@pytest.fixture(autouse=True)
def mock_get_email_data() -> Generator[mock.MagicMock, Any, None]:
    """Auto-applied mock for get_email_data across all tests in module"""
    with mock.patch(
        "app.emails.email_service.EmailService.get_email_data", side_effect=lambda eid: resources.TEST_EMAILS[eid]
    ) as email_mock:
        yield email_mock
