import pytest


class TestPage(object):

    title = None
    company = None
    platform = None
    location = None
    attendance_type = None
    salary_min = None
    salary_max = None
    salary_currency = None
    description = None
    file = None

    def get_scraper(self):
        if self.platform == "linkedin":
            return "scrapeLinkedInJob"
        else:
            return "scrapeIndeedJob"

    @pytest.fixture(scope="class")
    def data(self, scrape) -> dict:
        driver = scrape(self.file)
        return driver.execute_script(f"return {self.get_scraper()}();")

    def test_title(self, data) -> None:
        assert data["title"] == self.title

    def test_company(self, data) -> None:
        assert data["company"] == self.company

    def test_location(self, data) -> None:
        assert data["location"] == self.location

    def test_attendance_type(self, data) -> None:
        assert data["attendance_type"] == self.attendance_type

    def test_salary(self, data) -> None:
        assert data["salary_min"] == self.salary_min
        assert data["salary_max"] == self.salary_max
        assert data["salary_currency"] == self.salary_currency

    def test_description_has_bullets(self, data) -> None:
        assert data["description"] == self.description


class TestLinkedinJobMain(TestPage):

    title = "Controls Engineer (Highly Technical Manufacturing) - to £65k - ID45697"
    company = "Humand Talent"
    platform = "linkedin"
    location = "Witney, England, United Kingdom"
    attendance_type = "hybrid"
    salary_min = 50_000
    salary_max = 65_000
    salary_currency = "GBP"
    description = (
        "Do you love designing elegant control systems for complex, real-world "
        "challenges?\n"
        "\n"
        "Are you looking to apply your expertise to next-generation, high-precision "
        "technology?\n"
        "\n"
        "Ready to take the technical lead on innovations used by major global "
        "manufacturers?\n"
        "\n"
        "Our client, a growing high-tech engineering company based in the Oxfordshire "
        "area, is seeking a Senior Controls Engineer to drive development across a "
        "suite of highly technical products. This is a chance to lead technically "
        "challenging projects at the cutting edge of automation, measurement, and "
        "systems integration, all in a collaborative and fast-paced R&D environment.\n"
        "\n"
        "You’ll join a multidisciplinary team working on solutions that push the "
        "boundaries of speed and precision, supporting technologies used in advanced "
        "manufacturing and research worldwide.\n"
        "\n"
        "Why This Role is Great:\n"
        "\n"
        "- Lead the design, development, and optimisation of precision control "
        "systems used in highly specialised equipment.\n"
        "- Take ownership of system performance - from concept through to validation "
        "and troubleshooting.\n"
        "- Work at the sub-nanometre scale, helping to solve complex control and "
        "noise challenges.\n"
        "- Act as the technical authority for controls across multiple modules and "
        "system stages.\n"
        "- Collaborate with electronics, software, and mechanical teams in a "
        "hands-on, innovation-focused environment.\n"
        "- Influence future system architecture through continuous learning, "
        "analysis, and design evolution.\n"
        "- Contribute to the company’s reputation for technical excellence and "
        "cutting-edge product development.\n"
        "\n"
        "About You:\n"
        "You might come from a background in engineering, physics, mechatronics or "
        "applied systems, with a proven track record in developing complex control "
        "systems. Whether your experience comes from high-end manufacturing, "
        "automation, scientific instrumentation, or another precision field, we’re "
        "open to transferable skills.\n"
        "\n"
        "You’ll be comfortable leading technical discussions, validating performance "
        "through testing, and translating complex theory into practical design.\n"
        "\n"
        "Skills & Experience That Would Be a Great Match:\n"
        "\n"
        "We’re especially keen to hear from people with:\n"
        "\n"
        "- Strong understanding of control theory, feedback and feedforward loops\n"
        "- Experience acting as a technical lead on controls or automation systems\n"
        "- A hands-on approach to experimental setup, testing, and troubleshooting\n"
        "- Solid communication skills, able to work with diverse stakeholders\n"
        "- Proven experience (5+ years) in relevant engineering roles\n"
        "\n"
        "Desirable experience includes:\n"
        "\n"
        "- Knowledge of digital filtering, ideally in FPGAs\n"
        "- Familiarity with piezo systems and control challenges like hysteresis\n"
        "- Exposure to metrology, motion systems, or instrumentation\n"
        "- Experience guiding systems through EMC or regulatory testing\n"
        "- Understanding of PLC programming or automation controls\n"
        "\n"
        "What’s in It for You:\n"
        "\n"
        "- £60,000-£65,000 salary\n"
        "- Annual bonus\n"
        "- EMI Share Scheme\n"
        "- Flexible working hours\n"
        "- 25 days’ holiday + bank holidays\n"
        "- Pension scheme\n"
        "- An exciting, supportive environment where your technical leadership is "
        "truly valued\n"
        "\n"
        "Inclusion & Diversity Statement:\n"
        "We and our client are committed to creating an inclusive, respectful, and "
        "diverse working environment. We strongly encourage applications from "
        "candidates of all backgrounds and identities. If you don’t meet every "
        "requirement but believe you have skills or experience that align with the "
        "role, we’d still love to hear from you.\n"
        "\n"
        "Excited by the opportunity to shape high-precision systems of the future?\n"
        "\n"
        "Apply now to learn more about this unique Senior Controls Engineer "
        "opportunity."
    )
    file = "Linkedin_main.html"


class TestIndeedJobView(TestPage):

    title = "Data Scientist"
    company = "Indeed"
    platform = "indeed"
    location = "Manchester, England"
    attendance_type = "remote"
    salary_min = 100_000
    salary_max = 150_000
    salary_currency = "GBP"
    description = "We are looking for a Data Scientist to join our team."
    file = "Indeed_view.html"


class TestIndeedJobMain(TestPage):

    title = "Data Scientist"
    company = "Indeed"
    platform = "indeed"
    location = "Manchester, England"
    attendance_type = "remote"
    salary_min = 100_000
    salary_max = 150_000
    salary_currency = "GBP"
    description = "We are looking for a Data Scientist to join our team."
    file = "Indeed_main.html"
