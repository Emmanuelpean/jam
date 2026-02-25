import { queryFirst, parseSalary, descriptionToText, ATTENDANCE_MAP } from "./utils";

// ---------------------------------------------------------------------------
// New LinkedIn layout (randomised/obfuscated class names)
// Detected via stable `data-view-name` and `data-testid` attributes.
// ---------------------------------------------------------------------------

interface NewLayoutResult {
	title: string | null;
	company: string | null;
	location: string | null;
	attendance_type: string | null;
	salaryText: string | null;
	description: string | null;
}

function scrapeLinkedInNewLayout(): NewLayoutResult | null {
	const container: Element | null = document.querySelector('[data-view-name="job-detail-page"]');
	const descSpan: Element | null = document.querySelector('[data-testid="expandable-text-box"]');
	if (!container && !descSpan) return null;

	// Title: first <p> inside the container that has no <a> child
	const allPs: Element[] = container ? Array.from(container.querySelectorAll("p")) : [];
	const titleP: Element | null = allPs.find((p) => !p.querySelector("a")) ?? null;
	const title: string | null = titleP?.textContent?.trim() ?? null;

	// Company: first link to a /company/ page. Chrome auto-closes the containing <p> when it
	// encounters a nested block element, leaving the <a> with no text content. Read the text
	// from the link's parent element instead and take the part before the first '|'.
	const companyLink: Element | null = container?.querySelector('a[href*="/company/"]') ?? null;
	const companyRaw: string = (companyLink?.parentElement ?? companyLink)?.textContent?.trim() ?? "";
	const company: string | null = companyRaw.split("|")[0]?.trim() || null;

	// Location: walk up from titleP until we find a sibling <p>, split by middle dot (U+00B7)
	let location: string | null = null;
	if (titleP && container) {
		let node: Element | null = titleP.parentElement;
		outer: while (node && node !== container) {
			let sib: Element | null = node.nextElementSibling;
			while (sib) {
				if (sib.tagName === "P") {
					location = sib.textContent?.split("\u00b7")[0]?.trim() || null;
					break outer;
				}
				sib = sib.nextElementSibling;
			}
			node = node.parentElement;
		}
	}

	// Attendance: scan buttons inside the container for known keywords
	let attendance_type: string | null = null;
	if (container) {
		for (const btn of container.querySelectorAll("button")) {
			const text: string = btn.textContent?.trim() ?? "";
			for (const entry of ATTENDANCE_MAP) {
				if (entry.re.test(text)) {
					attendance_type = entry.value;
					break;
				}
			}
			if (attendance_type) break;
		}
	}

	// Salary: spans with a currency symbol + range/rate pattern, brief text only
	let salaryText: string | null = null;
	if (container) {
		for (const span of container.querySelectorAll("span")) {
			const text: string = span.textContent?.trim() ?? "";
			if (/[£$€¥₹]/.test(text) && /[-\u2013\u2014]|to|\/yr/.test(text) && text.length < 50) {
				salaryText = text;
				break;
			}
		}
	}

	// Description: Chrome's HTML parser breaks nested <p> elements out of the expandable-text-box
	// span, so the span ends up empty. Instead, use the grandparent of the "About the job" h2 —
	// that element contains all the description <p>/<ul>/<li> siblings as direct children.
	let descEl: Element | null = null;
	for (const h2 of document.querySelectorAll("h2")) {
		if (h2.textContent?.trim() === "About the job") {
			descEl = h2.parentElement?.parentElement ?? null;
			break;
		}
	}
	const description: string | null = descEl ? descriptionToText(descEl) : null;

	return { title, company, location, attendance_type, salaryText, description };
}

// ---------------------------------------------------------------------------

function getFitLevelTexts(): string[] {
	const container: Element | null = document.querySelector("div.job-details-fit-level-preferences");
	if (!container) return [];
	return Array.from(
		container.querySelectorAll("button.artdeco-button.artdeco-button--secondary.artdeco-button--muted")
	).map((btn: Element): string => btn.textContent?.trim() ?? "");
}

function findSalaryText(): string | null {
	// Salary may appear in the tertiary description or insight items
	const salarySelectors: string[] = [
		".compensation__salary",
		"[class*='salary']",
		".job-details-jobs-unified-top-card__job-insight--highlight span",
		".job-details-jobs-unified-top-card__salary-main-rail",
		"button.artdeco-button--secondary.artdeco-button--muted span.tvm__text--low-emphasis strong",
	];
	for (const sel of salarySelectors) {
		const el: Element | null = document.querySelector(sel);
		if (el) {
			const text: string = el.textContent?.trim();
			if (text) return text;
		}
	}
	// Fall back: any element whose text looks like a salary range
	const allText = document.querySelectorAll(
		".job-details-jobs-unified-top-card__tertiary-description-container span"
	);
	for (const el of allText) {
		const text = el.textContent?.trim();
		if (text && /[£$€¥₹]/.test(text) && /[-–—]|to/.test(text)) return text;
	}
	return null;
}

function getTopCardChips(): string[] {
	return Array.from(
		document.querySelectorAll(
			".job-details-jobs-unified-top-card__tertiary-description-container .job-details-jobs-unified-top-card__job-insight-view-model-secondary"
		)
	).map((el: Element): string => el.textContent?.trim() ?? "");
}

function parseLinkedInLocationAndAttendance(): { location: string | null; attendance_type: string | null } {
	// Location: first span.tvm__text--low-emphasis inside the tertiary container
	let location: string | null = null;
	const locEl: Element | null = document.querySelector(
		"div.t-black--light.mt2.job-details-jobs-unified-top-card__tertiary-description-container span.tvm__text.tvm__text--low-emphasis"
	);
	if (locEl) location = locEl.textContent?.trim() || null;

	// Attendance: buttons inside .job-details-fit-level-preferences
	let attendance_type: string | null = null;
	const fitTexts: string[] = getFitLevelTexts();
	for (const text of fitTexts) {
		for (const entry of ATTENDANCE_MAP) {
			if (entry.re.test(text)) {
				attendance_type = entry.value;
				break;
			}
		}
		if (attendance_type) break;
	}

	// Fallback: scan tertiary chips for attendance keywords
	if (!attendance_type) {
		for (const chip of getTopCardChips()) {
			for (const entry of ATTENDANCE_MAP) {
				if (entry.re.test(chip)) {
					attendance_type = entry.value;
					break;
				}
			}
			if (attendance_type) break;
		}
	}

	return { location, attendance_type };
}

function cleanLinkedInUrl(): string {
	try {
		const u = new URL(window.location.href);
		// /jobs/view/<id>/... → keep only the canonical path
		const match: RegExpMatchArray | null = u.pathname.match(/\/jobs\/view\/(\d+)/);
		if (match) return `https://www.linkedin.com/jobs/view/${match[1]}/`;

		// /jobs/collections/...?currentJobId=<id>
		const jobId: string | null = u.searchParams.get("currentJobId");
		if (jobId) return `https://www.linkedin.com/jobs/view/${jobId}/`;
	} catch (_) {}
	return window.location.href;
}

function detectApplicationStatus(): string | null {
	const text: string = document.body.innerText;
	if (text.includes("Application status") && text.includes("Application submitted")) {
		return "Applied";
	}
	return null;
}

export function scrapeLinkedInJob(): ScrapedJob {
	// Title — old layout (stable class names)
	const titleOld: string | null = queryFirst([
		".job-details-jobs-unified-top-card__job-title",
		".jobs-unified-top-card__job-title h1",
		".t-24.t-bold.inline h1",
		"h1.t-24",
		"h1",
	]);

	// Company — old layout
	const companyOld: string | null = queryFirst([
		".job-details-jobs-unified-top-card__company-name a",
		".job-details-jobs-unified-top-card__company-name",
		".jobs-unified-top-card__company-name a",
		".jobs-unified-top-card__company-name",
		".topcard__org-name-link",
		".topcard__flavor--black-link",
	]);

	// Description — old layout
	const descEl: Element | null = document.querySelector(
		"div.jobs-description-content__text, div.jobs-box__html-content, div#job-details"
	);
	const descriptionOld: string | null = descEl ? descriptionToText(descEl) : null;

	// Location and attendance type — old layout
	const { location: locationOld, attendance_type: attendanceOld } = parseLinkedInLocationAndAttendance();

	// Salary — old layout
	const salaryTextOld: string | null = findSalaryText();

	// New layout fallback (randomised class names): only used when old selectors all failed
	const newLayout: NewLayoutResult | null = titleOld == null ? scrapeLinkedInNewLayout() : null;

	const title: string | null = titleOld ?? newLayout?.title ?? null;
	const company: string | null = companyOld ?? newLayout?.company ?? null;
	const description: string | null = descriptionOld ?? newLayout?.description ?? null;
	const location: string | null = locationOld ?? newLayout?.location ?? null;
	const attendance_type: string | null = attendanceOld ?? newLayout?.attendance_type ?? null;
	const salary: SalaryResult = parseSalary(salaryTextOld ?? newLayout?.salaryText ?? null);

	return {
		title,
		company,
		description,
		url: cleanLinkedInUrl(),
		platform: "linkedin",
		location,
		attendance_type,
		application_status: detectApplicationStatus(),
		...salary,
	};
}
