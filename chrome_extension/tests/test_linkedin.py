import pytest


class ScraperTestBase:

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


class TestLinkedinJobMain(ScraperTestBase):

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


class TestIndeedJobView(ScraperTestBase):

    title = "Embedded Software Engineer (UAV's)"
    company = "Archangel Aerospace Group"
    platform = "indeed"
    location = "1 Osney Mead, Oxford"
    attendance_type = None
    salary_min = 55_000
    salary_max = 65_000
    salary_currency = "GBP"
    description = (
        "Embedded Software Engineer\n"
        "\n"
        "We are looking for an experienced Embedded Software Engineer who combines "
        "practical software skills with a very strong academic background\n"
        "\n"
        "At Archangel Imaging, you will be working alongside a fun, experienced and "
        "forward-thinking team to deliver transformative AI solutions that help "
        "organisations like Network Rail, Nuclear Decommissioning Authority and "
        "Ministry of Defence better protect our service personnel, critical "
        "infrastructure and first responders over large, remote areas. But that’s not "
        "all! We work extensively with industry drones and robotics partners to "
        "create turn-key solutions, so you will have exposure to the latest "
        "cutting-edge technologies.\n"
        "\n"
        "You will be joining a company that is enjoying great success. We have "
        "recently won the GENIUS NY program in New York (the largest accelerator "
        "program for unmanned systems in the world). In addition, we have won several "
        "exciting development projects with key defence customers.\n"
        "\n"
        "You must have these to apply:\n"
        "\n"
        "- BSc or MSc degree in Electrical Engineering, Computer Science, Computer "
        "Engineering, or related engineering field\n"
        "- 4+ Years of experience delivering functioning commercial embedded "
        "software\n"
        "- Excellent C/C++ skills\n"
        "- Familiarity with Python\n"
        "- Deep understanding of Linux internals, kernel programming, device trees\n"
        "- Experience writing and debugging drivers for novel hardware in Linux\n"
        "- Experience in debugging various interfaces (SPI, UART, CAN, USB etc.)\n"
        "- Practical skills in directly working with hardware\n"
        "- Ability to be on site in Oxford regularly during the week\n"
        "\n"
        "Nice to have:\n"
        "\n"
        "- Experience with Nvidia Jetson systems\n"
        "- Experience of kernel mode and bare-metal programming on ARM\n"
        "- Deep knowledge of camera systems to the sensor level\n"
        "- RTOS programming experience\n"
        "- Understanding of filesystems, networking, interprocess communication\n"
        "- Sound knowledge of control theory\n"
        "- Interest and experience in the Drone/UAS space\n"
        "- Knowledge of wireless communication systems\n"
        "- Interest in machine learning\n"
        "- Familiarity with GPS/GNSS positioning\n"
        "- Hardware and electronics rapid prototyping skills\n"
        "- Able to travel for events and field tests in the UK and abroad\n"
        "\n"
        "By joining us, you'll have:\n"
        "\n"
        "- The ability to make a measurable difference in a small company building "
        "cutting edge technology with big vision\n"
        "- Fast-paced environment with a positive, talented team\n"
        "- Forward-thinking, supportive culture with Monday paid lunch, quarterly "
        "company retreats and strategic alignment, flexible working hours, working "
        "from home and custom arrangements that matter to you\n"
        "- Exciting growth opportunities and training resources Including training to "
        "be a UAV pilot\n"
        "- Merit-based compensation\n"
        "- 5% employer pension contribution\n"
        "- 25 days holiday + UK bank holidays\n"
        "- Employee equity options scheme upon passing probation\n"
        "- A variety of perks: Gym discounts, Cycle2work, shopping, and supermarket "
        "discounts plus many more!\n"
        "- VR headset / DJI drone upon passing probation\n"
        "\n"
        "Interested?\n"
        "\n"
        "Apply now and someone from our HR team will get back to you ASAP. The usual "
        "process includes a screening call, a quick live coding test and then a "
        "meeting with more of the team to get to know each other. That’s it!\n"
        "\n"
        "Sound interesting? Apply now and join us making the future\n"
        "\n"
        "Job Type: Full-time\n"
        "\n"
        "Pay: £55,000.00-£65,000.00 per year\n"
        "\n"
        "Schedule:\n"
        "\n"
        "- Monday to Friday\n"
        "\n"
        "Work Location: In person"
    )
    file = "Indeed_view.html"


class TestIndeedJobMain(ScraperTestBase):

    title = "Embedded Software Engineer (UAV's)"
    company = "Archangel Aerospace Group"
    platform = "indeed"
    location = "1 Osney Mead, Oxford"
    attendance_type = None
    salary_min = 55_000
    salary_max = 65_000
    salary_currency = "GBP"
    description = (
        "Embedded Software Engineer\n"
        "\n"
        "We are looking for an experienced Embedded Software Engineer who combines "
        "practical software skills with a very strong academic background\n"
        "\n"
        "At Archangel Imaging, you will be working alongside a fun, experienced and "
        "forward-thinking team to deliver transformative AI solutions that help "
        "organisations like Network Rail, Nuclear Decommissioning Authority and "
        "Ministry of Defence better protect our service personnel, critical "
        "infrastructure and first responders over large, remote areas. But that’s not "
        "all! We work extensively with industry drones and robotics partners to "
        "create turn-key solutions, so you will have exposure to the latest "
        "cutting-edge technologies.\n"
        "\n"
        "You will be joining a company that is enjoying great success. We have "
        "recently won the GENIUS NY program in New York (the largest accelerator "
        "program for unmanned systems in the world). In addition, we have won several "
        "exciting development projects with key defence customers.\n"
        "\n"
        "You must have these to apply:\n"
        "\n"
        "- BSc or MSc degree in Electrical Engineering, Computer Science, Computer "
        "Engineering, or related engineering field\n"
        "- 4+ Years of experience delivering functioning commercial embedded "
        "software\n"
        "- Excellent C/C++ skills\n"
        "- Familiarity with Python\n"
        "- Deep understanding of Linux internals, kernel programming, device trees\n"
        "- Experience writing and debugging drivers for novel hardware in Linux\n"
        "- Experience in debugging various interfaces (SPI, UART, CAN, USB etc.)\n"
        "- Practical skills in directly working with hardware\n"
        "- Ability to be on site in Oxford regularly during the week\n"
        "\n"
        "Nice to have:\n"
        "\n"
        "- Experience with Nvidia Jetson systems\n"
        "- Experience of kernel mode and bare-metal programming on ARM\n"
        "- Deep knowledge of camera systems to the sensor level\n"
        "- RTOS programming experience\n"
        "- Understanding of filesystems, networking, interprocess communication\n"
        "- Sound knowledge of control theory\n"
        "- Interest and experience in the Drone/UAS space\n"
        "- Knowledge of wireless communication systems\n"
        "- Interest in machine learning\n"
        "- Familiarity with GPS/GNSS positioning\n"
        "- Hardware and electronics rapid prototyping skills\n"
        "- Able to travel for events and field tests in the UK and abroad\n"
        "\n"
        "By joining us, you'll have:\n"
        "\n"
        "- The ability to make a measurable difference in a small company building "
        "cutting edge technology with big vision\n"
        "- Fast-paced environment with a positive, talented team\n"
        "- Forward-thinking, supportive culture with Monday paid lunch, quarterly "
        "company retreats and strategic alignment, flexible working hours, working "
        "from home and custom arrangements that matter to you\n"
        "- Exciting growth opportunities and training resources Including training to "
        "be a UAV pilot\n"
        "- Merit-based compensation\n"
        "- 5% employer pension contribution\n"
        "- 25 days holiday + UK bank holidays\n"
        "- Employee equity options scheme upon passing probation\n"
        "- A variety of perks: Gym discounts, Cycle2work, shopping, and supermarket "
        "discounts plus many more!\n"
        "- VR headset / DJI drone upon passing probation\n"
        "\n"
        "Interested?\n"
        "\n"
        "Apply now and someone from our HR team will get back to you ASAP. The usual "
        "process includes a screening call, a quick live coding test and then a "
        "meeting with more of the team to get to know each other. That’s it!\n"
        "\n"
        "Sound interesting? Apply now and join us making the future\n"
        "\n"
        "Job Type: Full-time\n"
        "\n"
        "Pay: £55,000.00-£65,000.00 per year\n"
        "\n"
        "Schedule:\n"
        "\n"
        "- Monday to Friday\n"
        "\n"
        "Work Location: In person"
    )
    file = "Indeed_main.html"
