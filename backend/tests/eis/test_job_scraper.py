"""Test module for job_scraper.py
Integration tests that use real job IDs and make actual API calls to test the scraping functionality.
These tests require valid BrightData credentials in the eis_secrets.json file."""

import pytest

from app.eis.job_scraper import extract_indeed_jobs_from_email, parse_indeed_job_section

body_content = """Indeed Job Alert
23 new R&D Development Engineer jobs

Jobs 1-17 of 23 new jobs
See matching results on Indeed: https://uk.indeed.com/jobs?q=R%26D+Development+Engineer&hl=en&from=ja&radius=25&alid=672a6c661e474561bc946956&tmtk=1j3p3fhn5gc8r800&utm_campaign=job_alerts&utm_medium=email&utm_source=jobseeker_emails&of=1&fr=t


Laboratory Chemist
Thermulon - London
£30,000 - £37,000 a year
Easily apply to this job
Experience of analytical method development - required. Prepare reagents and stock solutions. Manage inventory, stock control, and ordering of lab supplies.
1 day ago
https://uk.indeed.com/rc/clk/dl?jk=8799a57d87058103&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=AbLHrm6GRQMtYBMzyEs2L1_MKnaSAFGAsD6kfERFt3g&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=axeEQ2YdV_i8d7kFQd70_zHA0XH-pdPZY5Ms1fdcAsN_P_g9MTatEg1qmJBNpzHpPU_7e6P3_Orkz_B4Mb3w5WTaQdaLwQUUZTsCY9FwBSJoahPDEuktV4nbr7dvvdgXLBSAoc2_lzfHm_EO6AxBMA%3D%3D&g1tAS=true

Graduate Photonic Scientist
Seagate Technology - Derry
Career – Degree / non degree assistance Externally accredited training and development opportunities, Service awards, LinkedIn learning, Learning & development…
1 day ago
https://uk.indeed.com/rc/clk/dl?jk=d489097ca0fb185f&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=4ZrZ-vtiYwdobVTLuwlSBM_GpDQUpdPT4XwZZ0YIiXc&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=QT9UYEItMIkcEPJesR9x4aMx4b77hZfy_kgKdEgV1wbjnhQCLQuYXwqa8THOU2OKMTg8SkNIMAA0cof6yAA6OrOM1nS5X_-w3oZDMcn2LmT0c9vbjqqH_O5sz_qRzWcH2ICqn97quxX8mS3Wgbv1Gg%3D%3D&g1tAS=true

R&D Senior Engineer (Process Development Function)
PepsiCo - Leicester
Easily apply to this job
Passion for innovation, sustainability, and talent development aligned with PEP+ goals. Support economic modeling and business case development for new process…
Just posted
https://uk.indeed.com/rc/clk/dl?jk=7f9c701ebf265b69&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=jsmukDLNB-vgMHfRjq5BnHEwqdD0vnOb9P51Phyha6c&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=QT9UYEItMIkcEPJesR9x4aMx4b77hZfyuFDZk7fGPsH4DIJZGtOYGtN298G7dmHtaHKw3KKKx_TL0onAS3QdYb4EB_vEGqDLbrAaJ9ovIiCbI8CM7CljeUohD6eos4s23zIaXgK5E78qW82keX1qoA%3D%3D&g1tAS=true

Senior Process Development Engineer, Process Chemistry
Pharmaron - Hoddesdon
Easily apply to this job
Strong understanding of standard unit operations in pharmaceutical process development. Familiarity with drug product development/formulation is a plus.
1 day ago
https://uk.indeed.com/rc/clk/dl?jk=0537336f99ba1650&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=Xsq4GqYm6lhmnLqcCCZBx3pHiNhXzRhj_cnpiDh5URU&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=QT9UYEItMIkcEPJesR9x4aMx4b77hZfyiA1X9CD0NDPO7dVqdWLkTHpbZMLVD6rDvIYTsSE9yYwqu0RtOKmMLDuDpgE95Omax8cYaREJnoUlMgRBy_X98AYier0Otf1H-Cmwz8d5rPP8VXdj-48ovw%3D%3D&g1tAS=true

Market Applications Engineer
G&H - Ilminster
£40,000 a year
Easily apply to this job
Assist with development of formal sales plans and proposals for assigned opportunities. Provide technical and pre-sales support for accounts; to work alongside…
1 day ago
https://uk.indeed.com/rc/clk/dl?jk=312725e138947a4b&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=S-68c07Poy-gqQdxtJ8OnF_MKnaSAFGAsD6kfERFt3g&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=QT9UYEItMIkcEPJesR9x4aMx4b77hZfyCQkX6AxDJVSjygIR8cSuF94MPaHZ3coc3IDOBXiEVfJt5wv_Rrh98y1AggnvVYS-Qr9GmRjwEpnn7EbFbQwk8LelqheGIFo2RZLOeRWoEMH_ICrjX2FdyQ%3D%3D&g1tAS=true

Regulatory Compliance Engineer
Raytec Ltd - Ashington
Responsive employer
Easily apply to this job
Cross functional collaboration with R&D, Purchasing and Commercial teams to integrate environmental compliance into product design, development and procurement.
1 day ago
https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0CaUNNDciQjB8b911OChydWlMiE438Jot_lydiWr9Z7lbj9cwyJAEEXhSuW8SoD7Wz1bcqpb5rq8IzPxIcuirUCwOlLSL9SL1F572G6Ye9pXIlV00tsAM20VfzF1b86kTFEpwUl5cqoBjsMlRudbS30FMebfIGC01chUG_dRw15uQJAniZZ9m2OwXKNijACF8VWjBKulQ_zZI6qbz8kD41WGqtaC6lMPRCw5kXUrJbTDCaqSpugfThHENgjlu3j5DBWMjvzWpApXtcxY1NTDKT2jg6q-Z5ZkxpZFWJpPicGjeEfETjD8De3kM__AclzfTjESmozVOJMXW85h3mgPZ94GIuFEx8ppqwDwLENrDoalprKNGMFQOeZ9u9dMbxUX_RJCqW9z1vgoP6UivsqTanzYlukGXOhEQ6IFVnNvDODivSUcZCpO_yBMmxlJxaYuRjPQmnuvS8CFyF8B-M_msQscB4GMRxaiGJuzie7_iJr6nKUP2O7lo1n69wInEp_MnehsLtxzcDysc6eBzfF4v2KkuXm1RRPbFqeIA7TK2sPoy2Z8b3VGKVcWv8k90XwuftkqxlnbbXeP3t1ygWiIMHdoJNVKkxUu46MZXtM498k9txG9p9ByQhDcOI8_BRoVsP3DM1wQl1ang-WkAVoo2PTwmdtETp3VlZZuUfSGtYYEdj-E9JmOVulmnyjbLfssmM%3D&xkcb=SoB56_M3u5Oxdj0MCJ0ObzkdCdPP&camk=UoKtGZLa3XLCRNJifgWECQ%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true

Biologist
Bindbridge - Remote
Easily apply to this job
Collaborate with AI engineers and chemists to integrate biological insights into degrader design and discovery pipelines. Strong publication or patent record.
Just posted
https://uk.indeed.com/rc/clk/dl?jk=bd60005166216639&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=x5SUCvphgkEZUN6bPKxzIl_MKnaSAFGAsD6kfERFt3g&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=QT9UYEItMIkcEPJesR9x4aMx4b77hZfy7BnQzzT8inJtK5rBzj2YjJXol-TexT4ONnLUQTDh-OxxuK7ZoZwoAW3A4J6IJH1OvjwiHV6NUX-6ML6cQy6T10v46qqGGtIWDjyDvyYqWaMxn2blF5IjKQ%3D%3D&g1tAS=true

Technical Support Engineer
Fortress Technology (Europe) Ltd - Banbury
£30,000 - £40,000 a year
Responsive employer
Easily apply to this job
The post holder will be required to support product development, testing, and production by providing technical expertise across R&D, Electrical Design, and…
7 days ago
https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0D_vIW1HWJamhhVblwSY9vEnB3YehQDBaLQWgEpQbAFvEB66TXnGDud1dy-8adNNEA8NkJwfd77g5zBB1ZOXhf8PEjWP1V1-Zs6swoSDNPKB4lvVzHxu1T3qM7FYs12eUEkiIA-iiINRZ_P2VMyvYooQezlTWytMkd2UWxnVCG9a3_m1cyaMA7DTm_syy5wCWCpCUUvgVdIOEOARvgAhUnIIz9x2Chk3LMqtby4HJFP4Jl7C-Vi5YB8H0bSA1FeugROif2FHIwU9gEobz-VsFvEz_Z4cCH3oft61BFqWCWU_wWimKzWAcDGINsjLw9tAunN_xjEdupF33Iwcd77c1urVC1OLKbL3-o2oJRyEPfNL1YN7H5cP_VieI3Fir6psGrVHQv_bNy0yYleEmT0E_DofaYunYAnzMqD_SUhvCDHia8MqrGJkTcgJp16KsMZPr5_mVLck5-3PYB-3khV71Oqfoa7q1yRWl-SN-Qfwc2OdZ8zl9PsK42-6iQ34faa2uibd37I4QFVw_Rwx7r8W-xyXpiwfe4xmkhhRGK1DeiQibftk7Dyp41hCpPZbTW_bL5F98fT1mfh1u1enhw3sXxk_BjcAXS_HZpuWi5zMuwbIztF4a8ZtEo_fNdlevRIwrN-0-0qjuEDoJYSxnY3mvd2WkDit7XyYAQWaCBCtSOLVSvgSDi4pd033dZ1KPZD7a0uFkrEyWaWSQ%3D%3D&xkcb=SoBQ6_M3u5Oxdj0MCJ0MbzkdCdPP&camk=ethIe0s0hedS-FZyNnahJA%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true

Technical Senior Scientist
Bactobio - London
Easily apply to this job
Experience conducting bioassay development/optimisation. Access to 1000s of training courses through Udemy, with an allowance for both personal development and…
Just posted
https://uk.indeed.com/rc/clk/dl?jk=d30493c008b601e3&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=gy7MCxDMWln4LWQRywCz51_MKnaSAFGAsD6kfERFt3g&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=QT9UYEItMIkcEPJesR9x4aMx4b77hZfyifFxFNk543UcaCLncBW7q0DkkYtIhYcw8jVEthvI3PJMdVqoIwYbkGSe463wCrTYcAWzX6zOnQstZ4WOTVPsYiJIe8L2RtgQhVDflg5gZt-pGVupX6-cMQ%3D%3D&g1tAS=true

Verification Engineer
Riverlane - Cambridge
£55,000 - £68,000 a year
Hybrid remote
Easily apply to this job
Cambridge, UK | Full-time or Part-time | Permanent | Hybrid. We will also consider part-time applications for this role.
Just posted
https://uk.indeed.com/rc/clk/dl?jk=da413431a0c55ec7&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=atk-kgV92m6TJ3g-AHTrAV_MKnaSAFGAsD6kfERFt3g&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00LqW_VlwJmL4GmSpaxcAdLqxsrWhmbiiln7hacwiRs5n-ruyq8STr4kLl8xuOFzz0PNbTkWeKl9oWB8Sps-8NhkCPNJ6ELTFDXT3m-NXmm1171x_bZXOtHdA%3D%3D&g1tAS=true

Graduate Mechanical Design Engineer
Panasonic Manufacturing - Cardiff
Consider new technology to improve and implement new R&D systems and processes, ensuring efficient product development and future improvement to product…
Just posted
https://uk.indeed.com/rc/clk/dl?jk=2ed37852402643ab&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=BJMmApqLf7EDBTY5CIqAvM_GpDQUpdPT4XwZZ0YIiXc&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00LiJ4Qcfb4Qd2d3_aNnXJiIGjs95hGD_VtUSs5AFKLsr0SzVFfMyR5NHTymcHIgivpASGeCxMHauvpeeT5j7MPoqX3n7LhDSDtvrHzXgOrQPGI8iBLM0f4MQ%3D%3D&g1tAS=true

DataOps Engineer
Allegis Global Solutions RPO UK for GSK - London
Easily apply to this job
They are standard-bearers for software engineering and quality coding practices within the team and are expected to mentor more junior engineers; they may even…
Just posted
https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0Cf-siO93BSuJ_a-mQFMzVvPBmFGGJg8IeoYoU7n3Hr-wyttwxtthbeGbpHFYWwmmWPWQtznc_slvzvpsaBmSWUWC64QSSNhEuwuNUWHSLtah1bwBpWniJ8vAR5oqbmqlY296quUSNSViPhje6fSFgDWLhGJWLOZaQ6OJRAp-V8a91no5GJKrUzj_KWnmJKR4rz_W6vZS8NYU5v9qDqx0uOlGmg1BnkC5lIZzyqlYwwOiZdPPVaEKKEr_G0GeQvlH67sGm1xTNyJw8sK6-4jN_ENAf2kd7JTexBVkGw5Mo02tAYXFvdA29R0CGRR0lyQRZtFJjgkhZvLHHLYO8JNjy_mia4G2BQ7Sx4ktyjaStia3kR4-BQNNWnr3k3ocyacfQEMHQlqE-Boaf4mwI0-BtJXesJsw9bvP207NBnfZFLJs1hUmSgvHhdYukY2qIsWXJLUVJgOyjwxdLhap0eFBEyti7g0G0mb3e1eO9ATdBP_e0h_p932Dm6wVyAZEXOddagVLoHFiJWPYnq8BUyKvm_S3vp9I57lYRrxWVTKZve2VIP18Uex6Bz0SozYOEEdgfyqQMBRAcp935Hg8aUW8GrXb3Q-js8GxuFke_S_tiEhCyNOEMjhQ-VRl5QOPdFttLD6e9-WR_H8IFLZUu3KwcfMBy1qEq1Tio%3D&xkcb=SoAk6_M3u5Oxdj0MCJ0AbzkdCdPP&camk=ethIe0s0hedep5fbP4CFtg%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true

Industrial Product Designer
NUMATIC INTERNATIONAL LIMITED - Chard
£34,000 - £42,000 a year
Hybrid remote
Easily apply to this job
Demonstrable experience of design work in product development from concept to production. Take full part in the development and improvement of the R&D…
6 days ago
https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0COSBp8KgMXxewvi58QAG0wwdlVlJfveGrD5vFIguWoXakoblclqS-4T_znVTPKawHOSHZOxsl_jK0JZuGPspNA9roT-uonvDv2P6RZVLNvLfm0KdPGmVMWwoNgo5H64KiIVwOuf_UrhuMQzHBJIgwJkroSRqxeEQ_3FKwvys8bTaQ85PMumf55yR90-LeyTGL3GXnHmXVXSfC1MDn6qf5BpprmfFM-RGc2WNblsNn6hNEtF-n7NfrAi-f-PzOE_Fjwhx-Y50MEMdlex_3U6MgwFpw7CADiD1Fch2HOI_bhNgCdt6qoLUO2qEA1AX1Ax0_pwn33z2XS_4FOGRcb4ZGqTii1rx-Elj6c6n-95wiR2sks-xrI0uMrPaE2w8P5k5v6tx1ixIQT9liqyzcXoSS6vzmARulIHV4NUWn0e_K4EvX-A-zYBjcEGSGUrLelauCc21fXrDww_gNV_ZSmedh1M06WDaPc3K_6WYtv6-_kkYQhQJyLlyW0Ws23VNL5nfJygGuW8pXeZhbniMlcDaavPtyGoDp4EWGOAI45uMzcbnJ0UyZcRPmuQxfCD8cFz-lmNle1TxlSWFB7j5QOAIn1UbXcKS7gdbhBijiUJWdSdzfbaPNHZdIPMBs6CDUZT5dPrhj_mtNopw4DVvv-OUOAzOpx9mlyJpr5aE7ivabt7_V3CMtJpw7ieYZ4UBA5ZQQ%3D&xkcb=SoCq6_M3u5Oxdj0MCJ0HbzkdCdPP&camk=UoKtGZLa3XL6dp7SxnkD1A%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true

Staff AI Engineer
bp - Sunbury
Hybrid remote
Mentor junior engineers and data scientists, and contribute to technical design reviews. You will work closely with data scientists, software engineers, and…
1 day ago
https://uk.indeed.com/rc/clk/dl?jk=6838e604ddffd5ac&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=hW5WLDedIUk_fnMJS2cPms_GpDQUpdPT4XwZZ0YIiXc&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00LarkEDH7QWQhKkwJayEEi3Szwm7bx6bODq8DVDiFzI2t1SYFnyUTbn1-3AHu3Bwm320W_ELzBv1EZtjY8I5QWZJc0PBFtNYngYq9YsSytSTfHoBtnu7J0yg%3D%3D&g1tAS=true

Laboratory Technician
Element Materials Technology - Deeside
The laboratory has an international reputation for service excellence and supports clients that require a higher level of technical expertise, reliability in…
Just posted
https://uk.indeed.com/rc/clk/dl?jk=227d4ccd0823fc96&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=yON7vZ4td41GGpAPelGL6XktNMQXNJMt63n0dyPvluI&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00LQ4kcQmQ6-NsudtY9hO9tcsDZC2tsMdHw9R49AzUwjxB8uTaFmgD-jTbP3tDjs_65Jjn8bI5-N2k7HnaSVqw-fPaFNDBFYIXOcMzo7qcnLDWEGSOMpOtcpA%3D%3D&g1tAS=true

Production Engineer
Kirsty's - Harrogate
£40,000 - £50,000 a year
Responsive employer
Easily apply to this job
The successful applicant will be responsible for maintaining and optimising equipment to ensure efficient, cost-effective, and high-quality food production.
1 day ago
https://uk.indeed.com/rc/clk/dl?jk=804b940d2d96b30b&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=1TOXcrFOmkfoxG9vW65Ktx1nad7mHeJIvvNS1DT4gjQ&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00Lp1lisol8TG0o7-b0Wbdw241WCmFs7NSmgzzrhGQjcYOIiMXVWysybzRtJzKkYNXLoA_pwWZaFpFvSCmS-TDNnA8OIMK2OZEh5Ou8jxvsQCuQbwbPHt0Oiw%3D%3D&g1tAS=true

Acoustics & Product Development Intern (Paid Internship)
Cambridge Audio - London
£25,000 a year
Hybrid remote
Easily apply to this job
Working alongside experienced engineers and designers, contributing your own ideas. Real-world product development experience in a high-performance audio…
1 day ago
https://uk.indeed.com/rc/clk/dl?jk=f9aafc9ba4c31c6d&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=UXIDHwmzP4uiAG0GShYBjQbXCHXgJEVMrHKBS2mW9rM&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00LMRV0pfrycSM3EoupSxnaiiLkbZYDNu33H0NANwOM8SJzsWxp50cBY1S9ZskwpnXf0uYPlsKJDw_CvVcwgkYmhdSgWSXOx4deq1zDRf4S2o6D4z3PqECSMA%3D%3D&g1tAS=true

Manufacturing Senior Engineer
Aston Martin Lagonda Ltd - Gaydon
Work type: Full Time - Permanent. You’ll play a central role in driving process and quality improvements across our Assembly facility.
Just posted
https://uk.indeed.com/rc/clk/dl?jk=e034f0b761e410ea&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=7cirY-xwcXV7HnfrzfUNqgsnOLhQXJeGPvQQwS5osgc&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00La0CIZQlvlElmFjBh_dYh-ysP-p1p7nSeyeGdu-nKylpqghhUQxbh6ajp4FR-7yaPu00SHxY4jkP_apxytRlZcy_umBiXXhVzqoa8kuquYdoAoX3BKByaWg%3D%3D&g1tAS=true

DECT Tier 2 Technical Support Engineer
Spectralink - Bracknell
Hybrid remote
Role Overview: The Tier 2 Technical Support Engineer is responsible for helping the technical support team in providing exceptional service and support to…
Just posted
https://uk.indeed.com/rc/clk/dl?jk=37cdb0ba59e12295&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=smUUrqiVqNsNGZeiwPcpWAbXCHXgJEVMrHKBS2mW9rM&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00LM7IJ0bf3Jgql1er9MYS_SijyKyV4awlliNTfcePVxtDM2pwpCWwMvQKy5Q00ZuOpcq6YfgcRxyAnFAQFs9Jp_k0bnnCEeaOpnd8emq0Dxgp-_xTHwAZDLQ%3D%3D&g1tAS=true

Applications Engineer
Wabtec - Lincoln
Provide input into NAPIER’s forward product development strategy. Work closely supporting NAPIER’s aerodynamic design and R&D departments in the testing and…
Just posted
https://uk.indeed.com/rc/clk/dl?jk=7b272f46e4e46a14&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=oxzfBJg7v5bH-lEX1a3a73ktNMQXNJMt63n0dyPvluI&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=Lhy-df8irCMFtzMYBpSKkuGuY8A7aKcAgqG_DKQsSwVocpc9HGGRG-qHhO6pGD5qJlW3RY_g1gef45K-PusFOob4mjB2lMEvn0paGQDfEvk9M25-w9Hyx9GSiN_uA1q0OQxxqTS5Ke65KMUdeT47Kw%3D%3D&g1tAS=true

PMO Lead
NP Aerospace Limited - Coventry
Vacancy Type: Full-time, Permanent and On-site 5 days per week. Salary: £Competitive per annum+ discretionary bonus.
Just posted
https://uk.indeed.com/rc/clk/dl?jk=d6110bfb54bdeddb&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=PB7Cktu4U76b9CbUjRuPvh0LXlTnqJu9xBoiZnP_1pQ&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=Lhy-df8irCMFtzMYBpSKkuGuY8A7aKcAw4imB_JUeq7-VIbIWHeVCZgTrQcrvtvP9x3l8oAdy2mpoCKKcl-P_A5Knkx5S-Va_xi9WKSMjEB2Xjir3T31FOLyFTP9MhdXmDQ_oq-KiZyvyIkTNtZqSA%3D%3D&g1tAS=true

Tech Support Engineer
SER (Staffing) Limited - Banbury
£30,000 - £40,000 a year
Easily apply to this job
Collaborate with engineers to support new and existing machine development. This is an exciting opportunity for an engineer who enjoys problem-solving,…
6 days ago
https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0DUGxYnv6px9uI6dWZhSaSeqMgHWZda7534TRDDAqMKu87sK88i_2Gbq8z1VBS-lbE9HOACaDVAT4jwhaVY_xabO_rq24Y_veJqW-7_usP-_0tRugSmofb5DuxCq5IvmHBw1rNykLW3A5edDY3v_jFGsNtRR7fiXWfgXBO9BJc6FCnwMo2I8cy9hPyydcFqH8iy9UHGKCJzlwGZAiKzNQyLn0rE_XB9MXJX9itgkAFNjlDq17qpEbAnLeIOJCcDXQ03H-DIxBN3ycBF9r29kZ45spvjQItrgoMklzXH3jPwU2j7qTpqQxKVcw5xKYuIWDhM5YqzbSTzr7Z97yKVWDKaB7gM87UyTYdJ32cflCxws1brYrULvaC8SfbTlTbsHvAdrl7BHnq6r6j_pBdFDKWUW-HcBCMgYk3ikg7sr5qwJAmQMqMjyLYUfWLVQ2ouX79v1awn5CT_sz7DqSikuv7MUgfzGrvbjHnov-zAxQfFPwdSmWZkgIz7UdZVOXCV0M6bw-XkaWtkDrGyiJRLOmEPNiiNwLnsKek3SWBSR8qHNbsrDWHz391rS2onjNWfo5gnmims0O-R-8jgV2J2NQyYP0ZNTYquIehRay6WTLbEZRsxgCy4Pgz42H-Z71EnOTwqnZ-8qLPoJRHV0K9oMQL6&xkcb=SoC36_M3u5Oxdj0MCJ0ebzkdCdPP&camk=ethIe0s0hefv8CfXU2K9Rw%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true

Multi Skilled Engineer
Orchard Professional Solutions Ltd - Harrogate
£45,000 - £55,000 a year
Easily apply to this job
In joining you will be responsible for maintaining and optimizing equipment to ensure efficient, cost-effective, and high-quality food production.
Just posted
https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0BqgWWSVbq3rqstnfUzC8xqhdOuKqZ9Avj77mYlc-g-lgy-1FSdO6PyFnAuQRYfp-JTSxMGeZR4wFhLR1UE4XYsePMvv1exKBMkCeCy9Dh-JYDgYqQLDREEwr5Bfy7uoO_og4WXgkp9rnXdiC6ej8lfOCDGtLs0xpRssH8ApFDX2WPI2WZLU3Dr_bYyzL-F51cHyx5ndFwTEKvG8FqgvbkNe1y7DDUUNUQ1EIdLP4bXw1hDuYRjJm9fbGQDc8LmmrzvdE37KxUZqeU3mzGz2moMrdAZPMufhp93UnQ8QmfOD8uq1LGUenfAtLXc7JvOdVmgZkFtGBtdlJ2Dce9Ty8I9XNaZR1vVTXVwfiM9K6yVwKEH5xhUCsr8a3DFXmcVOrivfiMWlzjRM8Bhtnwff6uJ8CLpNr-VdvfAHJTrsflPiwb6FZFX9sKw1kbd-zDyBDq_vEXiJor5MJKcuzQZ2DH62Tgv_dZllHjmGCWfk5775BFywNThFfEpBqM_-8GhAUHBfb6TSXITGIOiwWH6s7fbs7Fhz8wv20YInHAp2vJ--cjK9uVra5jKMPXk8XB1cUTG-ZWtKfzOtVi4TkT5lfFWC12tyMHgv72MFU3YxnXQZrswfP6D5JhZUJM5toctt1AkDeniJsTqR1-JtOeuQaLjQe7KvUV9qJ_ZUXba6qtMvOfz-BCYBDjc&xkcb=SoAq6_M3u5Oxdj0MCJ0dbzkdCdPP&camk=UoKtGZLa3XJTEZOPwEn50w%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true



Do not share this email
This email contains secure links that are personalised to you. Please do not share this email or links with others.

Salaries estimated if unavailable. When a job posting doesn't include a salary, we estimate it by looking at similar jobs. Estimated salaries are not endorsed by the companies offering those positions and may vary from actual salaries.

© 2025 Indeed Ireland Operations, Ltd. 
Indeed Ireland Operations Limited, Block B, Capital Dock, 80 Sir John Rogerson's Quay, Grand Canal Dock, Dublin, 2, D02 HE36 
Privacy Policy: https://uk.indeed.com/legal?hl=en#privacy 
Terms: https://uk.indeed.com/legal?hl=en 
Help Centre: https://support.indeed.com/hc/en-gb 
Manage email settings: https://subscriptions.indeed.com?token=CkCJBYNPg6n7apazzd2fL8-6iK3wXjjpWcKE_KMfyyPIEVGFzTDV2g_bTIXugSH8Hs22kbQ_ptUWtPUacAnXbXcbEiCNjKJM7oiHzkQqzKNKCOjqszazbom2xRBvMYDmwhR74hoQJUdodqD6OMAdxZAQdmdKGg%3D%3D&co=GB&hl=en&tmtk=1j3p3fhn5gc8r800&from=ja 
Unsubscribe from this email: https://subscriptions.indeed.com/alerts/cancel?token=CkCJBYNPg6n7apazzd2fL8-6iK3wXjjpWcKE_KMfyyPIEVGFzTDV2g_bTIXugSH8Hs22kbQ_ptUWtPUacAnXbXcbEiCNjKJM7oiHzkQqzKNKCOjqszazbom2xRBvMYDmwhR74hoQJUdodqD6OMAdxZAQdmdKGg%3D%3D&co=GB&hl=en&tmtk=1j3p3fhn5gc8r800&subId=672a6c661e474561bc946956&rgtk=1j3p3fl5qjnu8801&from=ja
"""


def test_extract_indeed_jobs_from_email() -> None:
    result = extract_indeed_jobs_from_email(body_content)
    assert len(result) == 23


job_expected = [
    {
        "company": "Thermulon",
        "location": "London",
        "job": {
            "title": "Laboratory Chemist",
            "description": "Experience of analytical method development - required. Prepare reagents and stock solutions. Manage inventory, stock control, and ordering of lab supplies.",
            "url": "https://uk.indeed.com/rc/clk/dl?jk=8799a57d87058103&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=AbLHrm6GRQMtYBMzyEs2L1_MKnaSAFGAsD6kfERFt3g&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=axeEQ2YdV_i8d7kFQd70_zHA0XH-pdPZY5Ms1fdcAsN_P_g9MTatEg1qmJBNpzHpPU_7e6P3_Orkz_B4Mb3w5WTaQdaLwQUUZTsCY9FwBSJoahPDEuktV4nbr7dvvdgXLBSAoc2_lzfHm_EO6AxBMA%3D%3D&g1tAS=true",
            "salary": {"min_amount": 30000.0, "max_amount": 37000.0},
        },
        "raw": "\nLaboratory Chemist\nThermulon - London\n£30,000 - £37,000 a year\nEasily apply to this job\nExperience of analytical method development - required. Prepare reagents and stock solutions. Manage inventory, stock control, and ordering of lab supplies.\n1 day ago\nhttps://uk.indeed.com/rc/clk/dl?jk=8799a57d87058103&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=AbLHrm6GRQMtYBMzyEs2L1_MKnaSAFGAsD6kfERFt3g&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=axeEQ2YdV_i8d7kFQd70_zHA0XH-pdPZY5Ms1fdcAsN_P_g9MTatEg1qmJBNpzHpPU_7e6P3_Orkz_B4Mb3w5WTaQdaLwQUUZTsCY9FwBSJoahPDEuktV4nbr7dvvdgXLBSAoc2_lzfHm_EO6AxBMA%3D%3D&g1tAS=true",
    },
    {
        "company": "Seagate Technology",
        "location": "Derry",
        "job": {
            "title": "Graduate Photonic Scientist",
            "description": "Career – Degree / non degree assistance Externally accredited training and development opportunities, Service awards, LinkedIn learning, Learning & development…",
            "url": "https://uk.indeed.com/rc/clk/dl?jk=d489097ca0fb185f&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=4ZrZ-vtiYwdobVTLuwlSBM_GpDQUpdPT4XwZZ0YIiXc&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=QT9UYEItMIkcEPJesR9x4aMx4b77hZfy_kgKdEgV1wbjnhQCLQuYXwqa8THOU2OKMTg8SkNIMAA0cof6yAA6OrOM1nS5X_-w3oZDMcn2LmT0c9vbjqqH_O5sz_qRzWcH2ICqn97quxX8mS3Wgbv1Gg%3D%3D&g1tAS=true",
            "salary": {"min_amount": None, "max_amount": None},
        },
        "raw": "Graduate Photonic Scientist\nSeagate Technology - Derry\nCareer – Degree / non degree assistance Externally accredited training and development opportunities, Service awards, LinkedIn learning, Learning & development…\n1 day ago\nhttps://uk.indeed.com/rc/clk/dl?jk=d489097ca0fb185f&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=4ZrZ-vtiYwdobVTLuwlSBM_GpDQUpdPT4XwZZ0YIiXc&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=QT9UYEItMIkcEPJesR9x4aMx4b77hZfy_kgKdEgV1wbjnhQCLQuYXwqa8THOU2OKMTg8SkNIMAA0cof6yAA6OrOM1nS5X_-w3oZDMcn2LmT0c9vbjqqH_O5sz_qRzWcH2ICqn97quxX8mS3Wgbv1Gg%3D%3D&g1tAS=true",
    },
    {
        "company": "PepsiCo",
        "location": "Leicester",
        "job": {
            "title": "R&D Senior Engineer (Process Development Function)",
            "description": "Passion for innovation, sustainability, and talent development aligned with PEP+ goals. Support economic modeling and business case development for new process…",
            "url": "https://uk.indeed.com/rc/clk/dl?jk=7f9c701ebf265b69&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=jsmukDLNB-vgMHfRjq5BnHEwqdD0vnOb9P51Phyha6c&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=QT9UYEItMIkcEPJesR9x4aMx4b77hZfyuFDZk7fGPsH4DIJZGtOYGtN298G7dmHtaHKw3KKKx_TL0onAS3QdYb4EB_vEGqDLbrAaJ9ovIiCbI8CM7CljeUohD6eos4s23zIaXgK5E78qW82keX1qoA%3D%3D&g1tAS=true",
            "salary": {"min_amount": None, "max_amount": None},
        },
        "raw": "R&D Senior Engineer (Process Development Function)\nPepsiCo - Leicester\nEasily apply to this job\nPassion for innovation, sustainability, and talent development aligned with PEP+ goals. Support economic modeling and business case development for new process…\nJust posted\nhttps://uk.indeed.com/rc/clk/dl?jk=7f9c701ebf265b69&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=jsmukDLNB-vgMHfRjq5BnHEwqdD0vnOb9P51Phyha6c&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=QT9UYEItMIkcEPJesR9x4aMx4b77hZfyuFDZk7fGPsH4DIJZGtOYGtN298G7dmHtaHKw3KKKx_TL0onAS3QdYb4EB_vEGqDLbrAaJ9ovIiCbI8CM7CljeUohD6eos4s23zIaXgK5E78qW82keX1qoA%3D%3D&g1tAS=true",
    },
    {
        "company": "Pharmaron",
        "location": "Hoddesdon",
        "job": {
            "title": "Senior Process Development Engineer, Process Chemistry",
            "description": "Strong understanding of standard unit operations in pharmaceutical process development. Familiarity with drug product development/formulation is a plus.",
            "url": "https://uk.indeed.com/rc/clk/dl?jk=0537336f99ba1650&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=Xsq4GqYm6lhmnLqcCCZBx3pHiNhXzRhj_cnpiDh5URU&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=QT9UYEItMIkcEPJesR9x4aMx4b77hZfyiA1X9CD0NDPO7dVqdWLkTHpbZMLVD6rDvIYTsSE9yYwqu0RtOKmMLDuDpgE95Omax8cYaREJnoUlMgRBy_X98AYier0Otf1H-Cmwz8d5rPP8VXdj-48ovw%3D%3D&g1tAS=true",
            "salary": {"min_amount": None, "max_amount": None},
        },
        "raw": "Senior Process Development Engineer, Process Chemistry\nPharmaron - Hoddesdon\nEasily apply to this job\nStrong understanding of standard unit operations in pharmaceutical process development. Familiarity with drug product development/formulation is a plus.\n1 day ago\nhttps://uk.indeed.com/rc/clk/dl?jk=0537336f99ba1650&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=Xsq4GqYm6lhmnLqcCCZBx3pHiNhXzRhj_cnpiDh5URU&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=QT9UYEItMIkcEPJesR9x4aMx4b77hZfyiA1X9CD0NDPO7dVqdWLkTHpbZMLVD6rDvIYTsSE9yYwqu0RtOKmMLDuDpgE95Omax8cYaREJnoUlMgRBy_X98AYier0Otf1H-Cmwz8d5rPP8VXdj-48ovw%3D%3D&g1tAS=true",
    },
    {
        "company": "G&H",
        "location": "Ilminster",
        "job": {
            "title": "Market Applications Engineer",
            "description": "£40,000 a year Assist with development of formal sales plans and proposals for assigned opportunities. Provide technical and pre-sales support for accounts; to work alongside…",
            "url": "https://uk.indeed.com/rc/clk/dl?jk=312725e138947a4b&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=S-68c07Poy-gqQdxtJ8OnF_MKnaSAFGAsD6kfERFt3g&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=QT9UYEItMIkcEPJesR9x4aMx4b77hZfyCQkX6AxDJVSjygIR8cSuF94MPaHZ3coc3IDOBXiEVfJt5wv_Rrh98y1AggnvVYS-Qr9GmRjwEpnn7EbFbQwk8LelqheGIFo2RZLOeRWoEMH_ICrjX2FdyQ%3D%3D&g1tAS=true",
            "salary": {"min_amount": None, "max_amount": None},
        },
        "raw": "Market Applications Engineer\nG&H - Ilminster\n£40,000 a year\nEasily apply to this job\nAssist with development of formal sales plans and proposals for assigned opportunities. Provide technical and pre-sales support for accounts; to work alongside…\n1 day ago\nhttps://uk.indeed.com/rc/clk/dl?jk=312725e138947a4b&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=S-68c07Poy-gqQdxtJ8OnF_MKnaSAFGAsD6kfERFt3g&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=QT9UYEItMIkcEPJesR9x4aMx4b77hZfyCQkX6AxDJVSjygIR8cSuF94MPaHZ3coc3IDOBXiEVfJt5wv_Rrh98y1AggnvVYS-Qr9GmRjwEpnn7EbFbQwk8LelqheGIFo2RZLOeRWoEMH_ICrjX2FdyQ%3D%3D&g1tAS=true",
    },
    {
        "company": "Raytec Ltd",
        "location": "Ashington",
        "job": {
            "title": "Regulatory Compliance Engineer",
            "description": "Responsive employer Cross functional collaboration with R&D, Purchasing and Commercial teams to integrate environmental compliance into product design, development and procurement.",
            "url": "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0CaUNNDciQjB8b911OChydWlMiE438Jot_lydiWr9Z7lbj9cwyJAEEXhSuW8SoD7Wz1bcqpb5rq8IzPxIcuirUCwOlLSL9SL1F572G6Ye9pXIlV00tsAM20VfzF1b86kTFEpwUl5cqoBjsMlRudbS30FMebfIGC01chUG_dRw15uQJAniZZ9m2OwXKNijACF8VWjBKulQ_zZI6qbz8kD41WGqtaC6lMPRCw5kXUrJbTDCaqSpugfThHENgjlu3j5DBWMjvzWpApXtcxY1NTDKT2jg6q-Z5ZkxpZFWJpPicGjeEfETjD8De3kM__AclzfTjESmozVOJMXW85h3mgPZ94GIuFEx8ppqwDwLENrDoalprKNGMFQOeZ9u9dMbxUX_RJCqW9z1vgoP6UivsqTanzYlukGXOhEQ6IFVnNvDODivSUcZCpO_yBMmxlJxaYuRjPQmnuvS8CFyF8B-M_msQscB4GMRxaiGJuzie7_iJr6nKUP2O7lo1n69wInEp_MnehsLtxzcDysc6eBzfF4v2KkuXm1RRPbFqeIA7TK2sPoy2Z8b3VGKVcWv8k90XwuftkqxlnbbXeP3t1ygWiIMHdoJNVKkxUu46MZXtM498k9txG9p9ByQhDcOI8_BRoVsP3DM1wQl1ang-WkAVoo2PTwmdtETp3VlZZuUfSGtYYEdj-E9JmOVulmnyjbLfssmM%3D&xkcb=SoB56_M3u5Oxdj0MCJ0ObzkdCdPP&camk=UoKtGZLa3XLCRNJifgWECQ%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true",
            "salary": {"min_amount": None, "max_amount": None},
        },
        "raw": "Regulatory Compliance Engineer\nRaytec Ltd - Ashington\nResponsive employer\nEasily apply to this job\nCross functional collaboration with R&D, Purchasing and Commercial teams to integrate environmental compliance into product design, development and procurement.\n1 day ago\nhttps://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0CaUNNDciQjB8b911OChydWlMiE438Jot_lydiWr9Z7lbj9cwyJAEEXhSuW8SoD7Wz1bcqpb5rq8IzPxIcuirUCwOlLSL9SL1F572G6Ye9pXIlV00tsAM20VfzF1b86kTFEpwUl5cqoBjsMlRudbS30FMebfIGC01chUG_dRw15uQJAniZZ9m2OwXKNijACF8VWjBKulQ_zZI6qbz8kD41WGqtaC6lMPRCw5kXUrJbTDCaqSpugfThHENgjlu3j5DBWMjvzWpApXtcxY1NTDKT2jg6q-Z5ZkxpZFWJpPicGjeEfETjD8De3kM__AclzfTjESmozVOJMXW85h3mgPZ94GIuFEx8ppqwDwLENrDoalprKNGMFQOeZ9u9dMbxUX_RJCqW9z1vgoP6UivsqTanzYlukGXOhEQ6IFVnNvDODivSUcZCpO_yBMmxlJxaYuRjPQmnuvS8CFyF8B-M_msQscB4GMRxaiGJuzie7_iJr6nKUP2O7lo1n69wInEp_MnehsLtxzcDysc6eBzfF4v2KkuXm1RRPbFqeIA7TK2sPoy2Z8b3VGKVcWv8k90XwuftkqxlnbbXeP3t1ygWiIMHdoJNVKkxUu46MZXtM498k9txG9p9ByQhDcOI8_BRoVsP3DM1wQl1ang-WkAVoo2PTwmdtETp3VlZZuUfSGtYYEdj-E9JmOVulmnyjbLfssmM%3D&xkcb=SoB56_M3u5Oxdj0MCJ0ObzkdCdPP&camk=UoKtGZLa3XLCRNJifgWECQ%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true",
    },
    {
        "company": "Bindbridge",
        "location": "Remote",
        "job": {
            "title": "Biologist",
            "description": "Collaborate with AI engineers and chemists to integrate biological insights into degrader design and discovery pipelines. Strong publication or patent record.",
            "url": "https://uk.indeed.com/rc/clk/dl?jk=bd60005166216639&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=x5SUCvphgkEZUN6bPKxzIl_MKnaSAFGAsD6kfERFt3g&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=QT9UYEItMIkcEPJesR9x4aMx4b77hZfy7BnQzzT8inJtK5rBzj2YjJXol-TexT4ONnLUQTDh-OxxuK7ZoZwoAW3A4J6IJH1OvjwiHV6NUX-6ML6cQy6T10v46qqGGtIWDjyDvyYqWaMxn2blF5IjKQ%3D%3D&g1tAS=true",
            "salary": {"min_amount": None, "max_amount": None},
        },
        "raw": "Biologist\nBindbridge - Remote\nEasily apply to this job\nCollaborate with AI engineers and chemists to integrate biological insights into degrader design and discovery pipelines. Strong publication or patent record.\nJust posted\nhttps://uk.indeed.com/rc/clk/dl?jk=bd60005166216639&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=x5SUCvphgkEZUN6bPKxzIl_MKnaSAFGAsD6kfERFt3g&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=QT9UYEItMIkcEPJesR9x4aMx4b77hZfy7BnQzzT8inJtK5rBzj2YjJXol-TexT4ONnLUQTDh-OxxuK7ZoZwoAW3A4J6IJH1OvjwiHV6NUX-6ML6cQy6T10v46qqGGtIWDjyDvyYqWaMxn2blF5IjKQ%3D%3D&g1tAS=true",
    },
    {
        "company": "Fortress Technology (Europe) Ltd",
        "location": "Banbury",
        "job": {
            "title": "Technical Support Engineer",
            "description": "Responsive employer The post holder will be required to support product development, testing, and production by providing technical expertise across R&D, Electrical Design, and…",
            "url": "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0D_vIW1HWJamhhVblwSY9vEnB3YehQDBaLQWgEpQbAFvEB66TXnGDud1dy-8adNNEA8NkJwfd77g5zBB1ZOXhf8PEjWP1V1-Zs6swoSDNPKB4lvVzHxu1T3qM7FYs12eUEkiIA-iiINRZ_P2VMyvYooQezlTWytMkd2UWxnVCG9a3_m1cyaMA7DTm_syy5wCWCpCUUvgVdIOEOARvgAhUnIIz9x2Chk3LMqtby4HJFP4Jl7C-Vi5YB8H0bSA1FeugROif2FHIwU9gEobz-VsFvEz_Z4cCH3oft61BFqWCWU_wWimKzWAcDGINsjLw9tAunN_xjEdupF33Iwcd77c1urVC1OLKbL3-o2oJRyEPfNL1YN7H5cP_VieI3Fir6psGrVHQv_bNy0yYleEmT0E_DofaYunYAnzMqD_SUhvCDHia8MqrGJkTcgJp16KsMZPr5_mVLck5-3PYB-3khV71Oqfoa7q1yRWl-SN-Qfwc2OdZ8zl9PsK42-6iQ34faa2uibd37I4QFVw_Rwx7r8W-xyXpiwfe4xmkhhRGK1DeiQibftk7Dyp41hCpPZbTW_bL5F98fT1mfh1u1enhw3sXxk_BjcAXS_HZpuWi5zMuwbIztF4a8ZtEo_fNdlevRIwrN-0-0qjuEDoJYSxnY3mvd2WkDit7XyYAQWaCBCtSOLVSvgSDi4pd033dZ1KPZD7a0uFkrEyWaWSQ%3D%3D&xkcb=SoBQ6_M3u5Oxdj0MCJ0MbzkdCdPP&camk=ethIe0s0hedS-FZyNnahJA%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true",
            "salary": {"min_amount": 30000.0, "max_amount": 40000.0},
        },
        "raw": "Technical Support Engineer\nFortress Technology (Europe) Ltd - Banbury\n£30,000 - £40,000 a year\nResponsive employer\nEasily apply to this job\nThe post holder will be required to support product development, testing, and production by providing technical expertise across R&D, Electrical Design, and…\n7 days ago\nhttps://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0D_vIW1HWJamhhVblwSY9vEnB3YehQDBaLQWgEpQbAFvEB66TXnGDud1dy-8adNNEA8NkJwfd77g5zBB1ZOXhf8PEjWP1V1-Zs6swoSDNPKB4lvVzHxu1T3qM7FYs12eUEkiIA-iiINRZ_P2VMyvYooQezlTWytMkd2UWxnVCG9a3_m1cyaMA7DTm_syy5wCWCpCUUvgVdIOEOARvgAhUnIIz9x2Chk3LMqtby4HJFP4Jl7C-Vi5YB8H0bSA1FeugROif2FHIwU9gEobz-VsFvEz_Z4cCH3oft61BFqWCWU_wWimKzWAcDGINsjLw9tAunN_xjEdupF33Iwcd77c1urVC1OLKbL3-o2oJRyEPfNL1YN7H5cP_VieI3Fir6psGrVHQv_bNy0yYleEmT0E_DofaYunYAnzMqD_SUhvCDHia8MqrGJkTcgJp16KsMZPr5_mVLck5-3PYB-3khV71Oqfoa7q1yRWl-SN-Qfwc2OdZ8zl9PsK42-6iQ34faa2uibd37I4QFVw_Rwx7r8W-xyXpiwfe4xmkhhRGK1DeiQibftk7Dyp41hCpPZbTW_bL5F98fT1mfh1u1enhw3sXxk_BjcAXS_HZpuWi5zMuwbIztF4a8ZtEo_fNdlevRIwrN-0-0qjuEDoJYSxnY3mvd2WkDit7XyYAQWaCBCtSOLVSvgSDi4pd033dZ1KPZD7a0uFkrEyWaWSQ%3D%3D&xkcb=SoBQ6_M3u5Oxdj0MCJ0MbzkdCdPP&camk=ethIe0s0hedS-FZyNnahJA%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true",
    },
    {
        "company": "Bactobio",
        "location": "London",
        "job": {
            "title": "Technical Senior Scientist",
            "description": "Experience conducting bioassay development/optimisation. Access to 1000s of training courses through Udemy, with an allowance for both personal development and…",
            "url": "https://uk.indeed.com/rc/clk/dl?jk=d30493c008b601e3&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=gy7MCxDMWln4LWQRywCz51_MKnaSAFGAsD6kfERFt3g&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=QT9UYEItMIkcEPJesR9x4aMx4b77hZfyifFxFNk543UcaCLncBW7q0DkkYtIhYcw8jVEthvI3PJMdVqoIwYbkGSe463wCrTYcAWzX6zOnQstZ4WOTVPsYiJIe8L2RtgQhVDflg5gZt-pGVupX6-cMQ%3D%3D&g1tAS=true",
            "salary": {"min_amount": None, "max_amount": None},
        },
        "raw": "Technical Senior Scientist\nBactobio - London\nEasily apply to this job\nExperience conducting bioassay development/optimisation. Access to 1000s of training courses through Udemy, with an allowance for both personal development and…\nJust posted\nhttps://uk.indeed.com/rc/clk/dl?jk=d30493c008b601e3&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=gy7MCxDMWln4LWQRywCz51_MKnaSAFGAsD6kfERFt3g&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=QT9UYEItMIkcEPJesR9x4aMx4b77hZfyifFxFNk543UcaCLncBW7q0DkkYtIhYcw8jVEthvI3PJMdVqoIwYbkGSe463wCrTYcAWzX6zOnQstZ4WOTVPsYiJIe8L2RtgQhVDflg5gZt-pGVupX6-cMQ%3D%3D&g1tAS=true",
    },
    {
        "company": "Riverlane",
        "location": "Cambridge",
        "job": {
            "title": "Verification Engineer",
            "description": "Hybrid remote Cambridge, UK | Full-time or Part-time | Permanent | Hybrid. We will also consider part-time applications for this role.",
            "url": "https://uk.indeed.com/rc/clk/dl?jk=da413431a0c55ec7&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=atk-kgV92m6TJ3g-AHTrAV_MKnaSAFGAsD6kfERFt3g&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00LqW_VlwJmL4GmSpaxcAdLqxsrWhmbiiln7hacwiRs5n-ruyq8STr4kLl8xuOFzz0PNbTkWeKl9oWB8Sps-8NhkCPNJ6ELTFDXT3m-NXmm1171x_bZXOtHdA%3D%3D&g1tAS=true",
            "salary": {"min_amount": 55000.0, "max_amount": 68000.0},
        },
        "raw": "Verification Engineer\nRiverlane - Cambridge\n£55,000 - £68,000 a year\nHybrid remote\nEasily apply to this job\nCambridge, UK | Full-time or Part-time | Permanent | Hybrid. We will also consider part-time applications for this role.\nJust posted\nhttps://uk.indeed.com/rc/clk/dl?jk=da413431a0c55ec7&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=atk-kgV92m6TJ3g-AHTrAV_MKnaSAFGAsD6kfERFt3g&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00LqW_VlwJmL4GmSpaxcAdLqxsrWhmbiiln7hacwiRs5n-ruyq8STr4kLl8xuOFzz0PNbTkWeKl9oWB8Sps-8NhkCPNJ6ELTFDXT3m-NXmm1171x_bZXOtHdA%3D%3D&g1tAS=true",
    },
    {
        "company": "Panasonic Manufacturing",
        "location": "Cardiff",
        "job": {
            "title": "Graduate Mechanical Design Engineer",
            "description": "Consider new technology to improve and implement new R&D systems and processes, ensuring efficient product development and future improvement to product…",
            "url": "https://uk.indeed.com/rc/clk/dl?jk=2ed37852402643ab&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=BJMmApqLf7EDBTY5CIqAvM_GpDQUpdPT4XwZZ0YIiXc&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00LiJ4Qcfb4Qd2d3_aNnXJiIGjs95hGD_VtUSs5AFKLsr0SzVFfMyR5NHTymcHIgivpASGeCxMHauvpeeT5j7MPoqX3n7LhDSDtvrHzXgOrQPGI8iBLM0f4MQ%3D%3D&g1tAS=true",
            "salary": {"min_amount": None, "max_amount": None},
        },
        "raw": "Graduate Mechanical Design Engineer\nPanasonic Manufacturing - Cardiff\nConsider new technology to improve and implement new R&D systems and processes, ensuring efficient product development and future improvement to product…\nJust posted\nhttps://uk.indeed.com/rc/clk/dl?jk=2ed37852402643ab&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=BJMmApqLf7EDBTY5CIqAvM_GpDQUpdPT4XwZZ0YIiXc&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00LiJ4Qcfb4Qd2d3_aNnXJiIGjs95hGD_VtUSs5AFKLsr0SzVFfMyR5NHTymcHIgivpASGeCxMHauvpeeT5j7MPoqX3n7LhDSDtvrHzXgOrQPGI8iBLM0f4MQ%3D%3D&g1tAS=true",
    },
    {
        "company": "Allegis Global Solutions RPO UK for GSK",
        "location": "London",
        "job": {
            "title": "DataOps Engineer",
            "description": "They are standard-bearers for software engineering and quality coding practices within the team and are expected to mentor more junior engineers; they may even…",
            "url": "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0Cf-siO93BSuJ_a-mQFMzVvPBmFGGJg8IeoYoU7n3Hr-wyttwxtthbeGbpHFYWwmmWPWQtznc_slvzvpsaBmSWUWC64QSSNhEuwuNUWHSLtah1bwBpWniJ8vAR5oqbmqlY296quUSNSViPhje6fSFgDWLhGJWLOZaQ6OJRAp-V8a91no5GJKrUzj_KWnmJKR4rz_W6vZS8NYU5v9qDqx0uOlGmg1BnkC5lIZzyqlYwwOiZdPPVaEKKEr_G0GeQvlH67sGm1xTNyJw8sK6-4jN_ENAf2kd7JTexBVkGw5Mo02tAYXFvdA29R0CGRR0lyQRZtFJjgkhZvLHHLYO8JNjy_mia4G2BQ7Sx4ktyjaStia3kR4-BQNNWnr3k3ocyacfQEMHQlqE-Boaf4mwI0-BtJXesJsw9bvP207NBnfZFLJs1hUmSgvHhdYukY2qIsWXJLUVJgOyjwxdLhap0eFBEyti7g0G0mb3e1eO9ATdBP_e0h_p932Dm6wVyAZEXOddagVLoHFiJWPYnq8BUyKvm_S3vp9I57lYRrxWVTKZve2VIP18Uex6Bz0SozYOEEdgfyqQMBRAcp935Hg8aUW8GrXb3Q-js8GxuFke_S_tiEhCyNOEMjhQ-VRl5QOPdFttLD6e9-WR_H8IFLZUu3KwcfMBy1qEq1Tio%3D&xkcb=SoAk6_M3u5Oxdj0MCJ0AbzkdCdPP&camk=ethIe0s0hedep5fbP4CFtg%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true",
            "salary": {"min_amount": None, "max_amount": None},
        },
        "raw": "DataOps Engineer\nAllegis Global Solutions RPO UK for GSK - London\nEasily apply to this job\nThey are standard-bearers for software engineering and quality coding practices within the team and are expected to mentor more junior engineers; they may even…\nJust posted\nhttps://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0Cf-siO93BSuJ_a-mQFMzVvPBmFGGJg8IeoYoU7n3Hr-wyttwxtthbeGbpHFYWwmmWPWQtznc_slvzvpsaBmSWUWC64QSSNhEuwuNUWHSLtah1bwBpWniJ8vAR5oqbmqlY296quUSNSViPhje6fSFgDWLhGJWLOZaQ6OJRAp-V8a91no5GJKrUzj_KWnmJKR4rz_W6vZS8NYU5v9qDqx0uOlGmg1BnkC5lIZzyqlYwwOiZdPPVaEKKEr_G0GeQvlH67sGm1xTNyJw8sK6-4jN_ENAf2kd7JTexBVkGw5Mo02tAYXFvdA29R0CGRR0lyQRZtFJjgkhZvLHHLYO8JNjy_mia4G2BQ7Sx4ktyjaStia3kR4-BQNNWnr3k3ocyacfQEMHQlqE-Boaf4mwI0-BtJXesJsw9bvP207NBnfZFLJs1hUmSgvHhdYukY2qIsWXJLUVJgOyjwxdLhap0eFBEyti7g0G0mb3e1eO9ATdBP_e0h_p932Dm6wVyAZEXOddagVLoHFiJWPYnq8BUyKvm_S3vp9I57lYRrxWVTKZve2VIP18Uex6Bz0SozYOEEdgfyqQMBRAcp935Hg8aUW8GrXb3Q-js8GxuFke_S_tiEhCyNOEMjhQ-VRl5QOPdFttLD6e9-WR_H8IFLZUu3KwcfMBy1qEq1Tio%3D&xkcb=SoAk6_M3u5Oxdj0MCJ0AbzkdCdPP&camk=ethIe0s0hedep5fbP4CFtg%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true",
    },
    {
        "company": "NUMATIC INTERNATIONAL LIMITED",
        "location": "Chard",
        "job": {
            "title": "Industrial Product Designer",
            "description": "Hybrid remote Demonstrable experience of design work in product development from concept to production. Take full part in the development and improvement of the R&D…",
            "url": "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0COSBp8KgMXxewvi58QAG0wwdlVlJfveGrD5vFIguWoXakoblclqS-4T_znVTPKawHOSHZOxsl_jK0JZuGPspNA9roT-uonvDv2P6RZVLNvLfm0KdPGmVMWwoNgo5H64KiIVwOuf_UrhuMQzHBJIgwJkroSRqxeEQ_3FKwvys8bTaQ85PMumf55yR90-LeyTGL3GXnHmXVXSfC1MDn6qf5BpprmfFM-RGc2WNblsNn6hNEtF-n7NfrAi-f-PzOE_Fjwhx-Y50MEMdlex_3U6MgwFpw7CADiD1Fch2HOI_bhNgCdt6qoLUO2qEA1AX1Ax0_pwn33z2XS_4FOGRcb4ZGqTii1rx-Elj6c6n-95wiR2sks-xrI0uMrPaE2w8P5k5v6tx1ixIQT9liqyzcXoSS6vzmARulIHV4NUWn0e_K4EvX-A-zYBjcEGSGUrLelauCc21fXrDww_gNV_ZSmedh1M06WDaPc3K_6WYtv6-_kkYQhQJyLlyW0Ws23VNL5nfJygGuW8pXeZhbniMlcDaavPtyGoDp4EWGOAI45uMzcbnJ0UyZcRPmuQxfCD8cFz-lmNle1TxlSWFB7j5QOAIn1UbXcKS7gdbhBijiUJWdSdzfbaPNHZdIPMBs6CDUZT5dPrhj_mtNopw4DVvv-OUOAzOpx9mlyJpr5aE7ivabt7_V3CMtJpw7ieYZ4UBA5ZQQ%3D&xkcb=SoCq6_M3u5Oxdj0MCJ0HbzkdCdPP&camk=UoKtGZLa3XL6dp7SxnkD1A%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true",
            "salary": {"min_amount": 34000.0, "max_amount": 42000.0},
        },
        "raw": "Industrial Product Designer\nNUMATIC INTERNATIONAL LIMITED - Chard\n£34,000 - £42,000 a year\nHybrid remote\nEasily apply to this job\nDemonstrable experience of design work in product development from concept to production. Take full part in the development and improvement of the R&D…\n6 days ago\nhttps://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0COSBp8KgMXxewvi58QAG0wwdlVlJfveGrD5vFIguWoXakoblclqS-4T_znVTPKawHOSHZOxsl_jK0JZuGPspNA9roT-uonvDv2P6RZVLNvLfm0KdPGmVMWwoNgo5H64KiIVwOuf_UrhuMQzHBJIgwJkroSRqxeEQ_3FKwvys8bTaQ85PMumf55yR90-LeyTGL3GXnHmXVXSfC1MDn6qf5BpprmfFM-RGc2WNblsNn6hNEtF-n7NfrAi-f-PzOE_Fjwhx-Y50MEMdlex_3U6MgwFpw7CADiD1Fch2HOI_bhNgCdt6qoLUO2qEA1AX1Ax0_pwn33z2XS_4FOGRcb4ZGqTii1rx-Elj6c6n-95wiR2sks-xrI0uMrPaE2w8P5k5v6tx1ixIQT9liqyzcXoSS6vzmARulIHV4NUWn0e_K4EvX-A-zYBjcEGSGUrLelauCc21fXrDww_gNV_ZSmedh1M06WDaPc3K_6WYtv6-_kkYQhQJyLlyW0Ws23VNL5nfJygGuW8pXeZhbniMlcDaavPtyGoDp4EWGOAI45uMzcbnJ0UyZcRPmuQxfCD8cFz-lmNle1TxlSWFB7j5QOAIn1UbXcKS7gdbhBijiUJWdSdzfbaPNHZdIPMBs6CDUZT5dPrhj_mtNopw4DVvv-OUOAzOpx9mlyJpr5aE7ivabt7_V3CMtJpw7ieYZ4UBA5ZQQ%3D&xkcb=SoCq6_M3u5Oxdj0MCJ0HbzkdCdPP&camk=UoKtGZLa3XL6dp7SxnkD1A%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true",
    },
    {
        "company": "bp",
        "location": "Sunbury",
        "job": {
            "title": "Staff AI Engineer",
            "description": "Hybrid remote Mentor junior engineers and data scientists, and contribute to technical design reviews. You will work closely with data scientists, software engineers, and…",
            "url": "https://uk.indeed.com/rc/clk/dl?jk=6838e604ddffd5ac&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=hW5WLDedIUk_fnMJS2cPms_GpDQUpdPT4XwZZ0YIiXc&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00LarkEDH7QWQhKkwJayEEi3Szwm7bx6bODq8DVDiFzI2t1SYFnyUTbn1-3AHu3Bwm320W_ELzBv1EZtjY8I5QWZJc0PBFtNYngYq9YsSytSTfHoBtnu7J0yg%3D%3D&g1tAS=true",
            "salary": {"min_amount": None, "max_amount": None},
        },
        "raw": "Staff AI Engineer\nbp - Sunbury\nHybrid remote\nMentor junior engineers and data scientists, and contribute to technical design reviews. You will work closely with data scientists, software engineers, and…\n1 day ago\nhttps://uk.indeed.com/rc/clk/dl?jk=6838e604ddffd5ac&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=hW5WLDedIUk_fnMJS2cPms_GpDQUpdPT4XwZZ0YIiXc&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00LarkEDH7QWQhKkwJayEEi3Szwm7bx6bODq8DVDiFzI2t1SYFnyUTbn1-3AHu3Bwm320W_ELzBv1EZtjY8I5QWZJc0PBFtNYngYq9YsSytSTfHoBtnu7J0yg%3D%3D&g1tAS=true",
    },
    {
        "company": "Element Materials Technology",
        "location": "Deeside",
        "job": {
            "title": "Laboratory Technician",
            "description": "The laboratory has an international reputation for service excellence and supports clients that require a higher level of technical expertise, reliability in…",
            "url": "https://uk.indeed.com/rc/clk/dl?jk=227d4ccd0823fc96&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=yON7vZ4td41GGpAPelGL6XktNMQXNJMt63n0dyPvluI&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00LQ4kcQmQ6-NsudtY9hO9tcsDZC2tsMdHw9R49AzUwjxB8uTaFmgD-jTbP3tDjs_65Jjn8bI5-N2k7HnaSVqw-fPaFNDBFYIXOcMzo7qcnLDWEGSOMpOtcpA%3D%3D&g1tAS=true",
            "salary": {"min_amount": None, "max_amount": None},
        },
        "raw": "Laboratory Technician\nElement Materials Technology - Deeside\nThe laboratory has an international reputation for service excellence and supports clients that require a higher level of technical expertise, reliability in…\nJust posted\nhttps://uk.indeed.com/rc/clk/dl?jk=227d4ccd0823fc96&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=yON7vZ4td41GGpAPelGL6XktNMQXNJMt63n0dyPvluI&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00LQ4kcQmQ6-NsudtY9hO9tcsDZC2tsMdHw9R49AzUwjxB8uTaFmgD-jTbP3tDjs_65Jjn8bI5-N2k7HnaSVqw-fPaFNDBFYIXOcMzo7qcnLDWEGSOMpOtcpA%3D%3D&g1tAS=true",
    },
    {
        "company": "Kirsty's",
        "location": "Harrogate",
        "job": {
            "title": "Production Engineer",
            "description": "Responsive employer The successful applicant will be responsible for maintaining and optimising equipment to ensure efficient, cost-effective, and high-quality food production.",
            "url": "https://uk.indeed.com/rc/clk/dl?jk=804b940d2d96b30b&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=1TOXcrFOmkfoxG9vW65Ktx1nad7mHeJIvvNS1DT4gjQ&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00Lp1lisol8TG0o7-b0Wbdw241WCmFs7NSmgzzrhGQjcYOIiMXVWysybzRtJzKkYNXLoA_pwWZaFpFvSCmS-TDNnA8OIMK2OZEh5Ou8jxvsQCuQbwbPHt0Oiw%3D%3D&g1tAS=true",
            "salary": {"min_amount": 40000.0, "max_amount": 50000.0},
        },
        "raw": "Production Engineer\nKirsty's - Harrogate\n£40,000 - £50,000 a year\nResponsive employer\nEasily apply to this job\nThe successful applicant will be responsible for maintaining and optimising equipment to ensure efficient, cost-effective, and high-quality food production.\n1 day ago\nhttps://uk.indeed.com/rc/clk/dl?jk=804b940d2d96b30b&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=1TOXcrFOmkfoxG9vW65Ktx1nad7mHeJIvvNS1DT4gjQ&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00Lp1lisol8TG0o7-b0Wbdw241WCmFs7NSmgzzrhGQjcYOIiMXVWysybzRtJzKkYNXLoA_pwWZaFpFvSCmS-TDNnA8OIMK2OZEh5Ou8jxvsQCuQbwbPHt0Oiw%3D%3D&g1tAS=true",
    },
    {
        "company": "Cambridge Audio",
        "location": "London",
        "job": {
            "title": "Acoustics & Product Development Intern (Paid Internship)",
            "description": "£25,000 a year Hybrid remote Working alongside experienced engineers and designers, contributing your own ideas. Real-world product development experience in a high-performance audio…",
            "url": "https://uk.indeed.com/rc/clk/dl?jk=f9aafc9ba4c31c6d&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=UXIDHwmzP4uiAG0GShYBjQbXCHXgJEVMrHKBS2mW9rM&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00LMRV0pfrycSM3EoupSxnaiiLkbZYDNu33H0NANwOM8SJzsWxp50cBY1S9ZskwpnXf0uYPlsKJDw_CvVcwgkYmhdSgWSXOx4deq1zDRf4S2o6D4z3PqECSMA%3D%3D&g1tAS=true",
            "salary": {"min_amount": None, "max_amount": None},
        },
        "raw": "Acoustics & Product Development Intern (Paid Internship)\nCambridge Audio - London\n£25,000 a year\nHybrid remote\nEasily apply to this job\nWorking alongside experienced engineers and designers, contributing your own ideas. Real-world product development experience in a high-performance audio…\n1 day ago\nhttps://uk.indeed.com/rc/clk/dl?jk=f9aafc9ba4c31c6d&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=UXIDHwmzP4uiAG0GShYBjQbXCHXgJEVMrHKBS2mW9rM&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00LMRV0pfrycSM3EoupSxnaiiLkbZYDNu33H0NANwOM8SJzsWxp50cBY1S9ZskwpnXf0uYPlsKJDw_CvVcwgkYmhdSgWSXOx4deq1zDRf4S2o6D4z3PqECSMA%3D%3D&g1tAS=true",
    },
    {
        "company": "Aston Martin Lagonda Ltd",
        "location": "Gaydon",
        "job": {
            "title": "Manufacturing Senior Engineer",
            "description": "Work type: Full Time - Permanent. You’ll play a central role in driving process and quality improvements across our Assembly facility.",
            "url": "https://uk.indeed.com/rc/clk/dl?jk=e034f0b761e410ea&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=7cirY-xwcXV7HnfrzfUNqgsnOLhQXJeGPvQQwS5osgc&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00La0CIZQlvlElmFjBh_dYh-ysP-p1p7nSeyeGdu-nKylpqghhUQxbh6ajp4FR-7yaPu00SHxY4jkP_apxytRlZcy_umBiXXhVzqoa8kuquYdoAoX3BKByaWg%3D%3D&g1tAS=true",
            "salary": {"min_amount": None, "max_amount": None},
        },
        "raw": "Manufacturing Senior Engineer\nAston Martin Lagonda Ltd - Gaydon\nWork type: Full Time - Permanent. You’ll play a central role in driving process and quality improvements across our Assembly facility.\nJust posted\nhttps://uk.indeed.com/rc/clk/dl?jk=e034f0b761e410ea&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=7cirY-xwcXV7HnfrzfUNqgsnOLhQXJeGPvQQwS5osgc&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00La0CIZQlvlElmFjBh_dYh-ysP-p1p7nSeyeGdu-nKylpqghhUQxbh6ajp4FR-7yaPu00SHxY4jkP_apxytRlZcy_umBiXXhVzqoa8kuquYdoAoX3BKByaWg%3D%3D&g1tAS=true",
    },
    {
        "company": "Spectralink",
        "location": "Bracknell",
        "job": {
            "title": "DECT Tier 2 Technical Support Engineer",
            "description": "Hybrid remote Role Overview: The Tier 2 Technical Support Engineer is responsible for helping the technical support team in providing exceptional service and support to…",
            "url": "https://uk.indeed.com/rc/clk/dl?jk=37cdb0ba59e12295&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=smUUrqiVqNsNGZeiwPcpWAbXCHXgJEVMrHKBS2mW9rM&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00LM7IJ0bf3Jgql1er9MYS_SijyKyV4awlliNTfcePVxtDM2pwpCWwMvQKy5Q00ZuOpcq6YfgcRxyAnFAQFs9Jp_k0bnnCEeaOpnd8emq0Dxgp-_xTHwAZDLQ%3D%3D&g1tAS=true",
            "salary": {"min_amount": None, "max_amount": None},
        },
        "raw": "DECT Tier 2 Technical Support Engineer\nSpectralink - Bracknell\nHybrid remote\nRole Overview: The Tier 2 Technical Support Engineer is responsible for helping the technical support team in providing exceptional service and support to…\nJust posted\nhttps://uk.indeed.com/rc/clk/dl?jk=37cdb0ba59e12295&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=smUUrqiVqNsNGZeiwPcpWAbXCHXgJEVMrHKBS2mW9rM&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=2L9TpTwJFG2qCB48rN3UyB2DGZP7Q00LM7IJ0bf3Jgql1er9MYS_SijyKyV4awlliNTfcePVxtDM2pwpCWwMvQKy5Q00ZuOpcq6YfgcRxyAnFAQFs9Jp_k0bnnCEeaOpnd8emq0Dxgp-_xTHwAZDLQ%3D%3D&g1tAS=true",
    },
    {
        "company": "Wabtec",
        "location": "Lincoln",
        "job": {
            "title": "Applications Engineer",
            "description": "Provide input into NAPIER’s forward product development strategy. Work closely supporting NAPIER’s aerodynamic design and R&D departments in the testing and…",
            "url": "https://uk.indeed.com/rc/clk/dl?jk=7b272f46e4e46a14&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=oxzfBJg7v5bH-lEX1a3a73ktNMQXNJMt63n0dyPvluI&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=Lhy-df8irCMFtzMYBpSKkuGuY8A7aKcAgqG_DKQsSwVocpc9HGGRG-qHhO6pGD5qJlW3RY_g1gef45K-PusFOob4mjB2lMEvn0paGQDfEvk9M25-w9Hyx9GSiN_uA1q0OQxxqTS5Ke65KMUdeT47Kw%3D%3D&g1tAS=true",
            "salary": {"min_amount": None, "max_amount": None},
        },
        "raw": "Applications Engineer\nWabtec - Lincoln\nProvide input into NAPIER’s forward product development strategy. Work closely supporting NAPIER’s aerodynamic design and R&D departments in the testing and…\nJust posted\nhttps://uk.indeed.com/rc/clk/dl?jk=7b272f46e4e46a14&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=oxzfBJg7v5bH-lEX1a3a73ktNMQXNJMt63n0dyPvluI&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=Lhy-df8irCMFtzMYBpSKkuGuY8A7aKcAgqG_DKQsSwVocpc9HGGRG-qHhO6pGD5qJlW3RY_g1gef45K-PusFOob4mjB2lMEvn0paGQDfEvk9M25-w9Hyx9GSiN_uA1q0OQxxqTS5Ke65KMUdeT47Kw%3D%3D&g1tAS=true",
    },
    {
        "company": "NP Aerospace Limited",
        "location": "Coventry",
        "job": {
            "title": "PMO Lead",
            "description": "Vacancy Type: Full-time, Permanent and On-site 5 days per week. Salary: £Competitive per annum+ discretionary bonus.",
            "url": "https://uk.indeed.com/rc/clk/dl?jk=d6110bfb54bdeddb&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=PB7Cktu4U76b9CbUjRuPvh0LXlTnqJu9xBoiZnP_1pQ&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=Lhy-df8irCMFtzMYBpSKkuGuY8A7aKcAw4imB_JUeq7-VIbIWHeVCZgTrQcrvtvP9x3l8oAdy2mpoCKKcl-P_A5Knkx5S-Va_xi9WKSMjEB2Xjir3T31FOLyFTP9MhdXmDQ_oq-KiZyvyIkTNtZqSA%3D%3D&g1tAS=true",
            "salary": {"min_amount": None, "max_amount": None},
        },
        "raw": "PMO Lead\nNP Aerospace Limited - Coventry\nVacancy Type: Full-time, Permanent and On-site 5 days per week. Salary: £Competitive per annum+ discretionary bonus.\nJust posted\nhttps://uk.indeed.com/rc/clk/dl?jk=d6110bfb54bdeddb&from=ja&qd=RnZhMybXSk4M3QtTVGXWocdt9s72ZYhyE4pohXkvAgkyOwEulsvE1QlvSsvHz9UXDjEyTGH30B-w8qHbTVlkk4hi3cflWi9lK3bqLLVopI0&rd=PB7Cktu4U76b9CbUjRuPvh0LXlTnqJu9xBoiZnP_1pQ&tk=1j3p3fhn5gc8r800&alid=672a6c661e474561bc946956&bb=Lhy-df8irCMFtzMYBpSKkuGuY8A7aKcAw4imB_JUeq7-VIbIWHeVCZgTrQcrvtvP9x3l8oAdy2mpoCKKcl-P_A5Knkx5S-Va_xi9WKSMjEB2Xjir3T31FOLyFTP9MhdXmDQ_oq-KiZyvyIkTNtZqSA%3D%3D&g1tAS=true",
    },
    {
        "company": "SER (Staffing) Limited",
        "location": "Banbury",
        "job": {
            "title": "Tech Support Engineer",
            "description": "Collaborate with engineers to support new and existing machine development. This is an exciting opportunity for an engineer who enjoys problem-solving,…",
            "url": "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0DUGxYnv6px9uI6dWZhSaSeqMgHWZda7534TRDDAqMKu87sK88i_2Gbq8z1VBS-lbE9HOACaDVAT4jwhaVY_xabO_rq24Y_veJqW-7_usP-_0tRugSmofb5DuxCq5IvmHBw1rNykLW3A5edDY3v_jFGsNtRR7fiXWfgXBO9BJc6FCnwMo2I8cy9hPyydcFqH8iy9UHGKCJzlwGZAiKzNQyLn0rE_XB9MXJX9itgkAFNjlDq17qpEbAnLeIOJCcDXQ03H-DIxBN3ycBF9r29kZ45spvjQItrgoMklzXH3jPwU2j7qTpqQxKVcw5xKYuIWDhM5YqzbSTzr7Z97yKVWDKaB7gM87UyTYdJ32cflCxws1brYrULvaC8SfbTlTbsHvAdrl7BHnq6r6j_pBdFDKWUW-HcBCMgYk3ikg7sr5qwJAmQMqMjyLYUfWLVQ2ouX79v1awn5CT_sz7DqSikuv7MUgfzGrvbjHnov-zAxQfFPwdSmWZkgIz7UdZVOXCV0M6bw-XkaWtkDrGyiJRLOmEPNiiNwLnsKek3SWBSR8qHNbsrDWHz391rS2onjNWfo5gnmims0O-R-8jgV2J2NQyYP0ZNTYquIehRay6WTLbEZRsxgCy4Pgz42H-Z71EnOTwqnZ-8qLPoJRHV0K9oMQL6&xkcb=SoC36_M3u5Oxdj0MCJ0ebzkdCdPP&camk=ethIe0s0hefv8CfXU2K9Rw%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true",
            "salary": {"min_amount": 30000.0, "max_amount": 40000.0},
        },
        "raw": "Tech Support Engineer\nSER (Staffing) Limited - Banbury\n£30,000 - £40,000 a year\nEasily apply to this job\nCollaborate with engineers to support new and existing machine development. This is an exciting opportunity for an engineer who enjoys problem-solving,…\n6 days ago\nhttps://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0DUGxYnv6px9uI6dWZhSaSeqMgHWZda7534TRDDAqMKu87sK88i_2Gbq8z1VBS-lbE9HOACaDVAT4jwhaVY_xabO_rq24Y_veJqW-7_usP-_0tRugSmofb5DuxCq5IvmHBw1rNykLW3A5edDY3v_jFGsNtRR7fiXWfgXBO9BJc6FCnwMo2I8cy9hPyydcFqH8iy9UHGKCJzlwGZAiKzNQyLn0rE_XB9MXJX9itgkAFNjlDq17qpEbAnLeIOJCcDXQ03H-DIxBN3ycBF9r29kZ45spvjQItrgoMklzXH3jPwU2j7qTpqQxKVcw5xKYuIWDhM5YqzbSTzr7Z97yKVWDKaB7gM87UyTYdJ32cflCxws1brYrULvaC8SfbTlTbsHvAdrl7BHnq6r6j_pBdFDKWUW-HcBCMgYk3ikg7sr5qwJAmQMqMjyLYUfWLVQ2ouX79v1awn5CT_sz7DqSikuv7MUgfzGrvbjHnov-zAxQfFPwdSmWZkgIz7UdZVOXCV0M6bw-XkaWtkDrGyiJRLOmEPNiiNwLnsKek3SWBSR8qHNbsrDWHz391rS2onjNWfo5gnmims0O-R-8jgV2J2NQyYP0ZNTYquIehRay6WTLbEZRsxgCy4Pgz42H-Z71EnOTwqnZ-8qLPoJRHV0K9oMQL6&xkcb=SoC36_M3u5Oxdj0MCJ0ebzkdCdPP&camk=ethIe0s0hefv8CfXU2K9Rw%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true",
    },
    {
        "company": "Orchard Professional Solutions Ltd",
        "location": "Harrogate",
        "job": {
            "title": "Multi Skilled Engineer",
            "description": "In joining you will be responsible for maintaining and optimizing equipment to ensure efficient, cost-effective, and high-quality food production.",
            "url": "https://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0BqgWWSVbq3rqstnfUzC8xqhdOuKqZ9Avj77mYlc-g-lgy-1FSdO6PyFnAuQRYfp-JTSxMGeZR4wFhLR1UE4XYsePMvv1exKBMkCeCy9Dh-JYDgYqQLDREEwr5Bfy7uoO_og4WXgkp9rnXdiC6ej8lfOCDGtLs0xpRssH8ApFDX2WPI2WZLU3Dr_bYyzL-F51cHyx5ndFwTEKvG8FqgvbkNe1y7DDUUNUQ1EIdLP4bXw1hDuYRjJm9fbGQDc8LmmrzvdE37KxUZqeU3mzGz2moMrdAZPMufhp93UnQ8QmfOD8uq1LGUenfAtLXc7JvOdVmgZkFtGBtdlJ2Dce9Ty8I9XNaZR1vVTXVwfiM9K6yVwKEH5xhUCsr8a3DFXmcVOrivfiMWlzjRM8Bhtnwff6uJ8CLpNr-VdvfAHJTrsflPiwb6FZFX9sKw1kbd-zDyBDq_vEXiJor5MJKcuzQZ2DH62Tgv_dZllHjmGCWfk5775BFywNThFfEpBqM_-8GhAUHBfb6TSXITGIOiwWH6s7fbs7Fhz8wv20YInHAp2vJ--cjK9uVra5jKMPXk8XB1cUTG-ZWtKfzOtVi4TkT5lfFWC12tyMHgv72MFU3YxnXQZrswfP6D5JhZUJM5toctt1AkDeniJsTqR1-JtOeuQaLjQe7KvUV9qJ_ZUXba6qtMvOfz-BCYBDjc&xkcb=SoAq6_M3u5Oxdj0MCJ0dbzkdCdPP&camk=UoKtGZLa3XJTEZOPwEn50w%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true",
            "salary": {"min_amount": 45000.0, "max_amount": 55000.0},
        },
        "raw": "Multi Skilled Engineer\nOrchard Professional Solutions Ltd - Harrogate\n£45,000 - £55,000 a year\nEasily apply to this job\nIn joining you will be responsible for maintaining and optimizing equipment to ensure efficient, cost-effective, and high-quality food production.\nJust posted\nhttps://uk.indeed.com/pagead/clk/dl?mo=r&ad=-6NYlbfkN0BqgWWSVbq3rqstnfUzC8xqhdOuKqZ9Avj77mYlc-g-lgy-1FSdO6PyFnAuQRYfp-JTSxMGeZR4wFhLR1UE4XYsePMvv1exKBMkCeCy9Dh-JYDgYqQLDREEwr5Bfy7uoO_og4WXgkp9rnXdiC6ej8lfOCDGtLs0xpRssH8ApFDX2WPI2WZLU3Dr_bYyzL-F51cHyx5ndFwTEKvG8FqgvbkNe1y7DDUUNUQ1EIdLP4bXw1hDuYRjJm9fbGQDc8LmmrzvdE37KxUZqeU3mzGz2moMrdAZPMufhp93UnQ8QmfOD8uq1LGUenfAtLXc7JvOdVmgZkFtGBtdlJ2Dce9Ty8I9XNaZR1vVTXVwfiM9K6yVwKEH5xhUCsr8a3DFXmcVOrivfiMWlzjRM8Bhtnwff6uJ8CLpNr-VdvfAHJTrsflPiwb6FZFX9sKw1kbd-zDyBDq_vEXiJor5MJKcuzQZ2DH62Tgv_dZllHjmGCWfk5775BFywNThFfEpBqM_-8GhAUHBfb6TSXITGIOiwWH6s7fbs7Fhz8wv20YInHAp2vJ--cjK9uVra5jKMPXk8XB1cUTG-ZWtKfzOtVi4TkT5lfFWC12tyMHgv72MFU3YxnXQZrswfP6D5JhZUJM5toctt1AkDeniJsTqR1-JtOeuQaLjQe7KvUV9qJ_ZUXba6qtMvOfz-BCYBDjc&xkcb=SoAq6_M3u5Oxdj0MCJ0dbzkdCdPP&camk=UoKtGZLa3XJTEZOPwEn50w%3D%3D&p=0&jsa=1997&rjs=1&tmtk=1j3p3fhn5gc8r800&gdfvj=1&alid=672a6c661e474561bc946956&fvj=1&g1tAS=true",
    },
]

job_sections = body_content.split("\n\n")[2:-4]


@pytest.mark.parametrize("job_section, expected", zip(job_sections, job_expected))
def test_parse_indeed_job_section(job_section, expected) -> None:
    result = parse_indeed_job_section(job_section)
    assert result == expected
