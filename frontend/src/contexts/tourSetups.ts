import React from "react";
import { scrapedJobApi } from "../services/api/Services";
import { DataContextValue } from "./DataContext";
import { DemoIds, TourSnapshot } from "./tourTypes";
import { ApiResponse } from "../services/api/Base";
import { CompanyData, InterviewData, JobData } from "../services/schemas/DataTables";
import { ScrapedJobData } from "../services/schemas/Services";

export interface TourSetupDeps {
	addEntity: DataContextValue["addEntity"];
	jamCreatedIds: React.MutableRefObject<TourSnapshot>;
	demoIds: React.MutableRefObject<DemoIds>;
	token: string;
}

export async function runTourSetup(tourId: string, deps: TourSetupDeps): Promise<void> {
	const { addEntity, jamCreatedIds, demoIds, token } = deps;

	if (tourId === "follow-up-email") {
		const [personResult, interviewerResult] = await Promise.all([
			addEntity("person", {
				first_name: "Alex",
				last_name: "Johnson",
				email: "alex.johnson@novatech.io",
				phone: "+44 7911 123456",
				role: "Hiring Manager",
				linkedin_url: "https://www.linkedin.com/in/alex-johnson",
				is_tour: true,
			}),
			addEntity("person", {
				first_name: "Sarah",
				last_name: "Mitchell",
				email: "sarah.mitchell@novatech.io",
				phone: "+44 7911 234567",
				role: "Engineering Manager",
				linkedin_url: "https://www.linkedin.com/in/sarah-mitchell",
				is_tour: true,
			}),
		]);

		const personId: number = personResult.data.id;
		const interviewerId: number = interviewerResult.data.id;

		const jobResult: ApiResponse<JobData> = await addEntity("job", {
			title: "Software Engineer",
			url: "https://www.novatech.io/careers/software-engineer",
			application_date: new Date().toISOString(),
			application_status: "applied",
			is_tour: true,
			contacts: [personId],
		});

		const jobId: number = jobResult.data.id;
		demoIds.current.jobId = jobId;
		const interviewResult: ApiResponse<InterviewData> = await addEntity("interview", {
			job_id: jobId,
			type: "video",
			date: new Date().toISOString(),
			attendance_type: "remote",
			interviewers: [interviewerId],
			is_tour: true,
		});
		const interviewId: number = interviewResult.data.id;

		jamCreatedIds.current.personIds.add(personId);
		jamCreatedIds.current.personIds.add(interviewerId);
		jamCreatedIds.current.jobIds.add(jobId);
		jamCreatedIds.current.interviewIds.add(interviewId);
	}

	if (tourId === "import-scraped-job") {
		const scrapedResult: ApiResponse<ScrapedJobData> = await scrapedJobApi.createTourDemo(token);
		demoIds.current.scrapedJobId = scrapedResult.data.id;
		demoIds.current.jobEmailId = scrapedResult.data.emails[0] ?? null;
	}

	if (tourId === "log-interview" || tourId === "log-update") {
		const companyResult: ApiResponse<CompanyData> = await addEntity("company", {
			name: "Meridian Labs",
			url: "https://www.meridianlabs.com",
			description: "Product-led growth startup specialising in data analytics. ~80 employees.",
			is_tour: true,
		});
		const companyId: number = companyResult.data.id;
		jamCreatedIds.current.companyIds.add(companyId);

		const interviewerPromises = tourId === "log-interview"
			? [
				addEntity("person", {
					first_name: "James",
					last_name: "Carter",
					role: "Engineering Manager",
					email: "james.carter@meridianlabs.com",
					company_id: companyId,
					is_tour: true,
				}),
				addEntity("person", {
					first_name: "Priya",
					last_name: "Sharma",
					role: "Senior Software Engineer",
					email: "priya.sharma@meridianlabs.com",
					company_id: companyId,
					is_tour: true,
				}),
			]
			: [];

		const [jobResult, ...personResults] = await Promise.all([
			addEntity("job", {
				title: "Software Engineer",
				is_favourite: false,
				is_tour: true,
				url: "https://www.meridianlabs.com/jobs/software-engineer",
				salary_min: 65000,
				salary_max: 85000,
				salary_currency: "GBP",
				company_id: companyId,
				location: "London, UK",
				application_date: new Date().toISOString(),
				application_status: "applied",
				attendance_type: "hybrid",
			}),
			...interviewerPromises,
		]);
		demoIds.current.jobId = (jobResult as ApiResponse<JobData>).data.id;
		jamCreatedIds.current.jobIds.add((jobResult as ApiResponse<JobData>).data.id);
		for (const p of personResults) {
			jamCreatedIds.current.personIds.add(p.data.id);
		}
	}

	if (tourId === "first-job") {
		const [company1, company2] = await Promise.all([
			addEntity("company", {
				name: "Acme Corp",
				url: "https://www.acmecorp.com",
				description:
					"B2B SaaS company building HR tooling. Series B, ~200 employees, offices in London and Manchester.",
				is_tour: true,
			}),
			addEntity("company", {
				name: "Globex Inc",
				url: "https://www.globexinc.com",
				description:
					"Enterprise software solutions provider. Clients across finance and logistics in the UK and Europe.",
				is_tour: true,
			}),
		]);
		jamCreatedIds.current.companyIds.add(company1.data.id);
		jamCreatedIds.current.companyIds.add(company2.data.id);

		const [p1, p2, k1, k2, a1, a2] = await Promise.all([
			addEntity("person", {
				first_name: "Emma",
				last_name: "Williams",
				email: "emma.williams@acmecorp.com",
				phone: "+44 7700 900123",
				role: "Recruiter",
				linkedin_url: "https://www.linkedin.com/in/emma-williams",
				company_id: company1.data.id,
				is_recruiter: true,
				is_tour: true,
			}),
			addEntity("person", {
				first_name: "David",
				last_name: "Chen",
				email: "david.chen@acmecorp.com",
				phone: "+44 7700 900456",
				role: "Hiring Manager",
				linkedin_url: "https://www.linkedin.com/in/david-chen",
				company_id: company1.data.id,
				is_recruiter: false,
				is_tour: true,
			}),
			addEntity("keyword", { name: "TypeScript", is_tour: true }),
			addEntity("keyword", { name: "React.js", is_tour: true }),
			addEntity("aggregator", {
				name: "LinkedIn Jobs",
				url: "https://www.linkedin.com/jobs/jam-tour",
				is_tour: true,
			}),
			addEntity("aggregator", {
				name: "Indeed",
				url: "https://www.indeed.com/jam-tour",
				is_tour: true,
			}),
		]);
		jamCreatedIds.current.personIds.add(p1.data.id);
		jamCreatedIds.current.personIds.add(p2.data.id);
		jamCreatedIds.current.keywordIds.add(k1.data.id);
		jamCreatedIds.current.keywordIds.add(k2.data.id);
		jamCreatedIds.current.aggregatorIds.add(a1.data.id);
		jamCreatedIds.current.aggregatorIds.add(a2.data.id);
	}

	if (tourId === "add-contact") {
		const [c1, c2] = await Promise.all([
			addEntity("company", {
				name: "Sterling Digital",
				url: "https://www.sterlingdigital.com",
				description: "London-based digital agency specialising in product design and engineering. ~120 employees.",
				is_tour: true,
			}),
			addEntity("company", {
				name: "Vertex Consulting",
				url: "https://www.vertexconsulting.co.uk",
				description: "Management and technology consultancy. UK and European clients across finance and retail.",
				is_tour: true,
			}),
		]);
		jamCreatedIds.current.companyIds.add(c1.data.id);
		jamCreatedIds.current.companyIds.add(c2.data.id);
	}

	if (tourId === "speculative-applications") {
		const [companyResult1, companyResult2] = await Promise.all([
			addEntity("company", {
				name: "Anthropic",
				url: "https://www.anthropic.com",
				description:
					"AI safety company. Builds Claude. Based in San Francisco — remote-friendly for UK applicants.",
				is_tour: true,
			}),
			addEntity("company", {
				name: "DeepMind",
				url: "https://www.deepmind.com",
				description:
					"AI research lab, part of Google. Main office in London (King's Cross). World-class research team.",
				is_tour: true,
			}),
		]);
		jamCreatedIds.current.companyIds.add(companyResult1.data.id);
		jamCreatedIds.current.companyIds.add(companyResult2.data.id);

		const [p1, p2] = await Promise.all([
			addEntity("person", {
				first_name: "Sophie",
				last_name: "Clarke",
				role: "Talent Acquisition",
				email: "sophie.clarke@anthropic.com",
				company_id: companyResult1.data.id,
				is_recruiter: true,
				is_tour: true,
			}),
			addEntity("person", {
				first_name: "Liam",
				last_name: "Patel",
				role: "Recruiter",
				email: "liam.patel@deepmind.com",
				company_id: companyResult2.data.id,
				is_recruiter: true,
				is_tour: true,
			}),
		]);
		jamCreatedIds.current.personIds.add(p1.data.id);
		jamCreatedIds.current.personIds.add(p2.data.id);
	}

	if (tourId === "log-application") {
		const [companyResult, a1, a2] = await Promise.all([
			addEntity("company", {
				name: "Meridian Labs",
				url: "https://www.meridianlabs.com",
				description: "Product-led growth startup specialising in data analytics. ~80 employees.",
				is_tour: true,
			}),
			addEntity("aggregator", { name: "LinkedIn Jobs", url: "https://www.linkedin.com/jobs", is_tour: true }),
			addEntity("aggregator", { name: "Indeed", url: "https://www.indeed.com", is_tour: true }),
		]);
		const companyId: number = companyResult.data.id;
		jamCreatedIds.current.companyIds.add(companyId);
		jamCreatedIds.current.aggregatorIds.add(a1.data.id);
		jamCreatedIds.current.aggregatorIds.add(a2.data.id);

		const jobResult: ApiResponse<JobData> = await addEntity("job", {
			title: "Software Engineer",
			is_favourite: false,
			is_tour: true,
			url: "https://www.meridianlabs.com/jobs/software-engineer",
			salary_min: 65000,
			salary_max: 85000,
			salary_currency: "GBP",
			company_id: companyId,
			location: "London, UK",
			attendance_type: "hybrid",
			keywords: [],
			contacts: [],
		});
		demoIds.current.jobId = jobResult.data.id;
		const jobId: number = jobResult.data.id;
		jamCreatedIds.current.jobIds.add(jobId);
	}
}
