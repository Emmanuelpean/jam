"use strict";

const API_URL = "http://localhost:8000";
const FRONTEND_URL = "http://localhost:3000/jam";

const DEFAULT_EMAIL = "regular@example.com";
const DEFAULT_PASSWORD = "password1";

// ---------------------------------------------------------------------------
// Element refs
// ---------------------------------------------------------------------------
const mainView = document.getElementById("mainView");
const loginView = document.getElementById("loginView");

const addBtn = document.getElementById("addBtn");
const addBtnLabel = document.getElementById("addBtnLabel");
const addSpinner = document.getElementById("addSpinner");
const statusDiv = document.getElementById("status");
const sessionEmail = document.getElementById("sessionEmail");
const logoutBtn = document.getElementById("logoutBtn");

const emailInput = document.getElementById("emailInput");
const passwordInput = document.getElementById("passwordInput");
const loginBtn = document.getElementById("loginBtn");
const loginBtnLabel = document.getElementById("loginBtnLabel");
const loginSpinner = document.getElementById("loginSpinner");
const loginStatus = document.getElementById("loginStatus");

const detectingRow = document.getElementById("detectingRow");
const noJobMsg = document.getElementById("noJobMsg");
const jobCard = document.getElementById("jobCard");
const jobTitle = document.getElementById("jobTitle");
const jobCompany = document.getElementById("jobCompany");
const platformBadge = document.getElementById("platformBadge");

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function setStatus(msg, type) {
	statusDiv.textContent = msg;
	statusDiv.className = type || "";
}

function setLoginStatus(msg, type) {
	loginStatus.textContent = msg;
	loginStatus.className = type || "";
}

function trimSlash(url) {
	return (url || "").replace(/\/$/, "");
}

function spinOn(spinner, btn, label, labelText) {
	spinner.classList.remove("hidden");
	btn.disabled = true;
	if (label) label.textContent = labelText;
}

function spinOff(spinner, btn, label, labelText) {
	spinner.classList.add("hidden");
	btn.disabled = false;
	if (label) label.textContent = labelText;
}

// ---------------------------------------------------------------------------
// Job detection state
// ---------------------------------------------------------------------------
function showDetecting() {
	detectingRow.classList.remove("hidden");
	noJobMsg.classList.add("hidden");
	jobCard.classList.add("hidden");
	addBtn.classList.add("hidden");
}

function showNoJob() {
	detectingRow.classList.add("hidden");
	noJobMsg.classList.remove("hidden");
	jobCard.classList.add("hidden");
	addBtn.classList.add("hidden");
}

function showJob(title, company, platform) {
	detectingRow.classList.add("hidden");
	noJobMsg.classList.add("hidden");
	jobCard.classList.remove("hidden");
	jobTitle.textContent = title || "—";
	jobCompany.textContent = company || "";
	const badge = getBadgeContent(platform);
	platformBadge.innerHTML = badge.html;
	platformBadge.style.background = badge.bg;
	addBtn.classList.remove("hidden");
}

// ---------------------------------------------------------------------------
// UI state
// ---------------------------------------------------------------------------
function showLoggedIn(email) {
	loginView.style.display = "none";
	mainView.style.display = "flex";
	sessionEmail.textContent = email || "";
	detectJob();
}

function showLoggedOut() {
	mainView.style.display = "none";
	loginView.style.display = "flex";
	if (!emailInput.value) emailInput.value = DEFAULT_EMAIL;
	if (!passwordInput.value) passwordInput.value = DEFAULT_PASSWORD;
	setLoginStatus("");
}

// ---------------------------------------------------------------------------
// Auto-detect job on popup open
// ---------------------------------------------------------------------------
function detectPlatform(url) {
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
	} catch (_) {}
	return null;
}

const LINKEDIN_ICON =
	'<svg width="10" height="10" viewBox="0 0 24 24" fill="white"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>';

function getBadgeContent(platform) {
	if (platform === "linkedin") return { html: LINKEDIN_ICON + "LinkedIn", bg: "#0a66c2" };
	if (platform === "indeed") return { html: "Indeed", bg: "#2557a7" };
	return { html: platform || "", bg: "#555" };
}

function detectJob() {
	showDetecting();
	setStatus("");

	chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
		const tab = tabs[0];
		if (!detectPlatform(tab?.url)) {
			showNoJob();
			return;
		}

		chrome.scripting.executeScript(
			{ target: { tabId: tab.id }, files: ["content.js", "linkedin.js", "indeed.js"] },
			() => {
				const injectErr = chrome.runtime.lastError;
				if (injectErr) {
					showNoJob();
					setStatus(`Inject: ${injectErr.message}`, "error");
					return;
				}

				chrome.tabs.sendMessage(tab.id, { action: "scrapeJob" }, (response) => {
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
			}
		);
	});
}

// Initialise on popup open
chrome.storage.local.get(["jamApiToken", "jamUserEmail"], (r) => {
	if (r.jamApiToken) showLoggedIn(r.jamUserEmail);
	else showLoggedOut();
});

// ---------------------------------------------------------------------------
// Login
// ---------------------------------------------------------------------------
loginBtn.addEventListener("click", () => {
	const email = emailInput.value.trim();
	const password = passwordInput.value;

	if (!email || !password) {
		setLoginStatus("Email and password are required.", "error");
		return;
	}

	spinOn(loginSpinner, loginBtn, loginBtnLabel, "Logging in…");
	setLoginStatus("");

	const body = new URLSearchParams({ username: email, password });

	fetch(`${trimSlash(API_URL)}/login/`, {
		method: "POST",
		headers: { "Content-Type": "application/x-www-form-urlencoded" },
		body: body.toString(),
	})
		.then(async (res) => {
			const text = await res.text();
			let data = null;
			try {
				data = JSON.parse(text);
			} catch (_) {
				/* non-JSON */
			}

			if (res.ok && data?.access_token) {
				chrome.storage.local.set({ jamApiToken: data.access_token, jamUserEmail: email }, () =>
					showLoggedIn(email)
				);
			} else {
				setLoginStatus(data?.detail || `Login failed (HTTP ${res.status})`, "error");
			}
		})
		.catch((e) => setLoginStatus(`Request failed: ${e.message}`, "error"))
		.finally(() => spinOff(loginSpinner, loginBtn, loginBtnLabel, "Log in"));
});

passwordInput.addEventListener("keydown", (e) => {
	if (e.key === "Enter") loginBtn.click();
});

// ---------------------------------------------------------------------------
// Logout
// ---------------------------------------------------------------------------
logoutBtn.addEventListener("click", () => {
	chrome.storage.local.remove(["jamApiToken", "jamUserEmail"], () => showLoggedOut());
});

// ---------------------------------------------------------------------------
// Save to JAM — scrape full job data and open the frontend with URL params
// ---------------------------------------------------------------------------
addBtn.addEventListener("click", () => {
	setStatus("");
	spinOn(addSpinner, addBtn, addBtnLabel, "Scraping…");

	chrome.storage.local.get(["jamApiToken"], (result) => {
		if (!result.jamApiToken) {
			setStatus("Please log in first.", "error");
			spinOff(addSpinner, addBtn, addBtnLabel, "Save to JAM");
			return;
		}

		chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
			const tab = tabs[0];

			chrome.scripting.executeScript(
				{ target: { tabId: tab.id }, files: ["content.js", "linkedin.js", "indeed.js"] },
				() => {
					if (chrome.runtime.lastError) {
						setStatus(`Injection failed: ${chrome.runtime.lastError.message}`, "error");
						spinOff(addSpinner, addBtn, addBtnLabel, "Save to JAM");
						return;
					}

					chrome.tabs.sendMessage(tab.id, { action: "scrapeJob" }, (response) => {
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

						const job = response.data;
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

						const base = trimSlash(FRONTEND_URL);
						const targetUrl = `${base}/jobs?${params.toString()}`;

						chrome.tabs.query({ url: `${base}/*` }, (jamTabs) => {
							if (jamTabs.length > 0) {
								// Post job data directly — no URL change, no full reload
								chrome.scripting.executeScript({
									target: { tabId: jamTabs[0].id },
									func: (jobData) => window.postMessage({ type: "JAM_EXT_JOB", data: jobData }, "*"),
									args: [job],
								});
								chrome.tabs.update(jamTabs[0].id, { active: true });
								chrome.windows.update(jamTabs[0].windowId, { focused: true });
							} else {
								chrome.tabs.create({ url: targetUrl });
							}
							setStatus(`Saved: ${job.title}`, "success");
							spinOff(addSpinner, addBtn, addBtnLabel, "Save to JAM");
						});
					}); // sendMessage
				}
			); // executeScript
		}); // tabs.query
	}); // storage.get
}); // addBtn click
