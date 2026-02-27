export {};

declare const __FRONTEND_URL__: string;
const FRONTEND_URL = __FRONTEND_URL__;

// ---------------------------------------------------------------------------
// Element refs
// ---------------------------------------------------------------------------
const addBtn = document.getElementById("addBtn") as HTMLButtonElement;
const addBtnLabel = document.getElementById("addBtnLabel") as HTMLElement;
const addSpinner = document.getElementById("addSpinner") as HTMLElement;
const statusDiv = document.getElementById("status") as HTMLElement;

const actionArea = document.getElementById("actionArea") as HTMLElement;
const detectingRow = document.getElementById("detectingRow") as HTMLElement;
const noJobMsg = document.getElementById("noJobMsg") as HTMLElement;
const jobCard = document.getElementById("jobCard") as HTMLElement;
const jobTitle = document.getElementById("jobTitle") as HTMLElement;
const jobCompany = document.getElementById("jobCompany") as HTMLElement;
const platformBadge = document.getElementById("platformBadge") as HTMLElement;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function setStatus(msg: string, type?: string): void {
	statusDiv.textContent = msg;
	statusDiv.className = msg ? type || "" : "hidden";
}

function trimSlash(url: string): string {
	return (url || "").replace(/\/$/, "");
}

function spinOn(spinner: HTMLElement, btn: HTMLButtonElement, label: HTMLElement | null, labelText: string): void {
	spinner.classList.remove("hidden");
	btn.disabled = true;
	if (label) label.textContent = labelText;
}

function spinOff(spinner: HTMLElement, btn: HTMLButtonElement, label: HTMLElement | null, labelText: string): void {
	spinner.classList.add("hidden");
	btn.disabled = false;
	if (label) label.textContent = labelText;
}

// ---------------------------------------------------------------------------
// Job detection state
// ---------------------------------------------------------------------------
function showDetecting(): void {
	detectingRow.classList.remove("hidden");
	noJobMsg.classList.add("hidden");
	jobCard.classList.add("hidden");
	actionArea.classList.add("hidden");
}

function showNoJob(): void {
	detectingRow.classList.add("hidden");
	noJobMsg.classList.remove("hidden");
	jobCard.classList.add("hidden");
	actionArea.classList.add("hidden");
}

function showJob(title: string | null, company: string | null, platform: string): void {
	detectingRow.classList.add("hidden");
	noJobMsg.classList.add("hidden");
	jobCard.classList.remove("hidden");
	jobTitle.textContent = title || "—";
	jobCompany.textContent = company || "";
	const badge = getBadgeContent(platform);
	platformBadge.innerHTML = badge.html;
	platformBadge.style.background = badge.bg;
	actionArea.classList.remove("hidden");
}

// ---------------------------------------------------------------------------
// Auto-detect job on popup open
// ---------------------------------------------------------------------------
function detectPlatform(url: string | null | undefined): string | null {
	if (!url) return null;
	try {
		const u = new URL(url);
		const h = u.hostname;
		if (h.includes("linkedin.com")) {
			if (u.pathname.includes("/jobs/view")) return "linkedin";
			if (u.pathname.includes("/jobs/collections") && u.searchParams.has("currentJobId")) return "linkedin";
		}
		if (h.endsWith("indeed.com")) {
			if (u.pathname.includes("/viewjob")) return "indeed";
			if (u.searchParams.has("jk") || u.searchParams.has("vjk")) return "indeed";
		}
		if (h === "www.jobs.nhs.uk" && u.pathname.includes("/candidate/jobadvert/")) return "nhs";
		if (h === "veganjobs.com" && u.pathname.includes("/job/")) return "veganjobs";
	} catch (_) {}
	return null;
}

const LINKEDIN_ICON =
	'<svg width="10" height="10" viewBox="0 0 24 24" fill="white"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>';

const INDEED_ICON =
	'<svg width="10" height="10" viewBox="0 0 24 24" fill="white"><circle cx="12" cy="3.5" r="2.5"/><rect x="9.5" y="8" width="5" height="13" rx="2.5"/></svg>';

const NHS_ICON =
	'<svg width="10" height="10" viewBox="0 0 24 24" fill="white"><path d="M11 3h2v7h7v2h-7v7h-2v-7H4v-2h7z"/></svg>';

const VEGANJOBS_ICON =
	'<svg width="10" height="10" viewBox="0 0 24 24" fill="white"><path d="M17 8C8 10 5.9 16.17 3.82 21.34L5.71 22l1-2.3A4.49 4.49 0 008 20C19 20 22 3 22 3c-1 2-8 2-8 2-3.5 0-5.5 1.5-6.5 3.5C9 6 11 4 17 4z"/></svg>';

function getBadgeContent(platform: string): { html: string; bg: string } {
	if (platform === "linkedin") return { html: LINKEDIN_ICON + "LinkedIn", bg: "#0a66c2" };
	if (platform === "indeed") return { html: INDEED_ICON + "Indeed", bg: "#2557a7" };
	if (platform === "nhs") return { html: NHS_ICON + "NHS Jobs", bg: "#005eb8" };
	if (platform === "veganjobs") return { html: VEGANJOBS_ICON + "VeganJobs", bg: "#4caf50" };
	return { html: platform || "", bg: "#555" };
}

function detectJob(): void {
	showDetecting();
	setStatus("");

	chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
		const tab = tabs[0];
		if (!tab) return;
		if (!detectPlatform(tab.url)) {
			showNoJob();
			return;
		}

		chrome.scripting.executeScript({ target: { tabId: tab.id! }, files: ["content.js"] }, () => {
			const injectErr = chrome.runtime.lastError;
			if (injectErr) {
				showNoJob();
				setStatus(`Inject: ${injectErr.message}`, "error");
				return;
			}

			chrome.tabs.sendMessage(tab.id!, { action: "scrapeJob" }, (response: ScrapeResponse | undefined) => {
				const msgErr = chrome.runtime.lastError;
				if (msgErr) {
					showNoJob();
					setStatus(`Msg: ${msgErr.message}`, "error");
					return;
				}
				if (!response?.success || !response.data?.title) {
					showNoJob();
					setStatus(response?.error || "No title found", "error");
					return;
				}
				showJob(response.data.title, response.data.company, response.data.platform);
			});
		});
	});
}

// ---------------------------------------------------------------------------
// Initialise on popup open
// ---------------------------------------------------------------------------
detectJob();

// ---------------------------------------------------------------------------
// Save to JAM — scrape full job data and open the frontend with URL params
// ---------------------------------------------------------------------------
addBtn.addEventListener("click", () => {
	setStatus("");
	spinOn(addSpinner, addBtn, addBtnLabel, "Scraping…");

	chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
		const tab = tabs[0];
		if (!tab) return;

		chrome.scripting.executeScript({ target: { tabId: tab.id! }, files: ["content.js"] }, () => {
			if (chrome.runtime.lastError) {
				setStatus(`Injection failed: ${chrome.runtime.lastError.message}`, "error");
				spinOff(addSpinner, addBtn, addBtnLabel, "Save to JAM");
				return;
			}

			chrome.tabs.sendMessage(tab.id!, { action: "scrapeJob" }, (response: ScrapeResponse | undefined) => {
				if (chrome.runtime.lastError) {
					setStatus(`Script error: ${chrome.runtime.lastError.message}`, "error");
					spinOff(addSpinner, addBtn, addBtnLabel, "Save to JAM");
					return;
				}
				if (!response?.success) {
					setStatus(response?.error || "Unknown scraping error.", "error");
					spinOff(addSpinner, addBtn, addBtnLabel, "Save to JAM");
					return;
				}

				const job = response.data as ScrapedJob;
				const params = new URLSearchParams();
				if (job.title) params.set("ext_title", job.title);
				if (job.url) params.set("ext_url", job.url);
				if (job.description) params.set("ext_description", job.description);
				if (job.salary_min) params.set("ext_salary_min", String(job.salary_min));
				if (job.salary_max) params.set("ext_salary_max", String(job.salary_max));
				if (job.attendance_type) params.set("ext_attendance_type", job.attendance_type);
				if (job.company) params.set("ext_company", job.company);
				if (job.location) params.set("ext_location", job.location);
				if (job.platform) params.set("ext_platform", job.platform);
				if (job.application_status) params.set("ext_application_status", job.application_status);
				if (job.deadline) params.set("ext_deadline", job.deadline);

				const base = trimSlash(FRONTEND_URL);
				const targetUrl = `${base}/jobs?${params.toString()}`;

				chrome.tabs.query({ url: `${base}/*` }, (jamTabs) => {
					if (jamTabs.length > 0) {
						// Existing JAM tab — inject postMessage directly (no URL needed)
						chrome.scripting.executeScript({
							target: { tabId: jamTabs[0].id! },
							func: (jobData: ScrapedJob) =>
								window.postMessage({ type: "JAM_EXT_JOB", data: jobData }, "*"),
							args: [job],
						});
						chrome.tabs.update(jamTabs[0].id!, { active: true });
						chrome.windows.update(jamTabs[0].windowId!, { focused: true });
					} else {
						// New tab — store job in local storage; jam_bridge.ts picks it up on load
						chrome.storage.local.set({ pendingExtJob: job });
						chrome.tabs.create({ url: `${base}/jobs` });
					}
					spinOff(addSpinner, addBtn, addBtnLabel, "Save to JAM");
				});
			});
		});
	});
});
