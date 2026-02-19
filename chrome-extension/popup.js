'use strict';

const API_URL      = 'http://localhost:8000';
const FRONTEND_URL = 'http://localhost:3000/jam';

const DEFAULT_EMAIL    = 'regular@example.com';
const DEFAULT_PASSWORD = 'password1';

// ---------------------------------------------------------------------------
// Element refs
// ---------------------------------------------------------------------------
const mainView      = document.getElementById('mainView');
const loginView     = document.getElementById('loginView');

const addBtn        = document.getElementById('addBtn');
const addBtnLabel   = document.getElementById('addBtnLabel');
const addSpinner    = document.getElementById('addSpinner');
const statusDiv     = document.getElementById('status');
const sessionEmail  = document.getElementById('sessionEmail');
const logoutBtn     = document.getElementById('logoutBtn');

const emailInput    = document.getElementById('emailInput');
const passwordInput = document.getElementById('passwordInput');
const loginBtn      = document.getElementById('loginBtn');
const loginBtnLabel = document.getElementById('loginBtnLabel');
const loginSpinner  = document.getElementById('loginSpinner');
const loginStatus   = document.getElementById('loginStatus');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function setStatus(msg, type) {
  statusDiv.textContent = msg;
  statusDiv.className = type || '';
}

function setLoginStatus(msg, type) {
  loginStatus.textContent = msg;
  loginStatus.className = type || '';
}

function trimSlash(url) {
  return (url || '').replace(/\/$/, '');
}

function spinOn(spinner, btn, label, labelText) {
  spinner.classList.remove('hidden');
  btn.disabled = true;
  if (label) label.textContent = labelText;
}

function spinOff(spinner, btn, label, labelText) {
  spinner.classList.add('hidden');
  btn.disabled = false;
  if (label) label.textContent = labelText;
}

// ---------------------------------------------------------------------------
// UI state
// ---------------------------------------------------------------------------
function showLoggedIn(email) {
  loginView.style.display = 'none';
  mainView.style.display  = 'flex';
  sessionEmail.textContent = email || '';
}

function showLoggedOut() {
  mainView.style.display  = 'none';
  loginView.style.display = 'flex';
  if (!emailInput.value)    emailInput.value    = DEFAULT_EMAIL;
  if (!passwordInput.value) passwordInput.value = DEFAULT_PASSWORD;
  setLoginStatus('');
}

// Initialise on popup open
chrome.storage.local.get(['jamApiToken', 'jamUserEmail'], (r) => {
  if (r.jamApiToken) showLoggedIn(r.jamUserEmail);
  else showLoggedOut();
});

// ---------------------------------------------------------------------------
// Login
// ---------------------------------------------------------------------------
loginBtn.addEventListener('click', () => {
  const email    = emailInput.value.trim();
  const password = passwordInput.value;

  if (!email || !password) {
    setLoginStatus('Email and password are required.', 'error');
    return;
  }

  spinOn(loginSpinner, loginBtn, loginBtnLabel, 'Logging in…');
  setLoginStatus('');

  const body = new URLSearchParams({ username: email, password });

  fetch(`${trimSlash(API_URL)}/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  })
    .then(async (res) => {
      const text = await res.text();
      let data = null;
      try { data = JSON.parse(text); } catch (_) { /* non-JSON */ }

      if (res.ok && data?.access_token) {
        chrome.storage.local.set(
          { jamApiToken: data.access_token, jamUserEmail: email },
          () => showLoggedIn(email)
        );
      } else {
        setLoginStatus(data?.detail || `Login failed (HTTP ${res.status})`, 'error');
      }
    })
    .catch((e) => setLoginStatus(`Request failed: ${e.message}`, 'error'))
    .finally(() => spinOff(loginSpinner, loginBtn, loginBtnLabel, 'Log in'));
});

passwordInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') loginBtn.click();
});

// ---------------------------------------------------------------------------
// Logout
// ---------------------------------------------------------------------------
logoutBtn.addEventListener('click', () => {
  chrome.storage.local.remove(['jamApiToken', 'jamUserEmail'], () => showLoggedOut());
});

// ---------------------------------------------------------------------------
// Add to JAM — open the frontend with prefilled URL params
// ---------------------------------------------------------------------------
addBtn.addEventListener('click', () => {
  setStatus('');
  spinOn(addSpinner, addBtn, addBtnLabel, 'Scraping…');

  chrome.storage.local.get(['jamApiToken'], (result) => {
    if (!result.jamApiToken) {
      setStatus('Please log in first.', 'error');
      spinOff(addSpinner, addBtn, addBtnLabel, 'Add to JAM');
      return;
    }

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs[0];
      const isJobView        = tab?.url?.includes('linkedin.com/jobs/view');
      const isCollectionView = tab?.url?.includes('linkedin.com/jobs/collections') &&
                               new URL(tab.url).searchParams.has('currentJobId');

      if (!isJobView && !isCollectionView) {
        setStatus('Navigate to a LinkedIn job listing page first.', 'error');
        spinOff(addSpinner, addBtn, addBtnLabel, 'Add to JAM');
        return;
      }

      chrome.scripting.executeScript(
        { target: { tabId: tab.id }, files: ['content.js'] },
        () => {
          if (chrome.runtime.lastError) {
            setStatus(`Injection failed: ${chrome.runtime.lastError.message}`, 'error');
            spinOff(addSpinner, addBtn, addBtnLabel, 'Add to JAM');
            return;
          }

          chrome.tabs.sendMessage(tab.id, { action: 'scrapeJob' }, (response) => {
            if (chrome.runtime.lastError) {
              setStatus(`Script error: ${chrome.runtime.lastError.message}`, 'error');
              spinOff(addSpinner, addBtn, addBtnLabel, 'Add to JAM');
              return;
            }
            if (!response?.success) {
              setStatus(response?.error || 'Unknown scraping error.', 'error');
              spinOff(addSpinner, addBtn, addBtnLabel, 'Add to JAM');
              return;
            }

            const job = response.data;
            const params = new URLSearchParams();
            if (job.title)            params.set('ext_title',            job.title);
            if (job.url)              params.set('ext_url',              job.url);
            if (job.description)      params.set('ext_description',      job.description);
            if (job.salary_min)       params.set('ext_salary_min',       String(job.salary_min));
            if (job.salary_max)       params.set('ext_salary_max',       String(job.salary_max));
            if (job.attendance_type)  params.set('ext_attendance_type',  job.attendance_type);
            if (job.company_name)     params.set('ext_company_name',     job.company_name);
            if (job.location_city)    params.set('ext_location_city',    job.location_city);
            if (job.location_country) params.set('ext_location_country', job.location_country);

            const base      = trimSlash(FRONTEND_URL);
            const targetUrl = `${base}/jobs?${params.toString()}`;

            chrome.tabs.query({ url: `${base}/*` }, (jamTabs) => {
              if (jamTabs.length > 0) {
                chrome.tabs.update(jamTabs[0].id, { active: true, url: targetUrl });
                chrome.windows.update(jamTabs[0].windowId, { focused: true });
              } else {
                chrome.tabs.create({ url: targetUrl });
              }
              setStatus(`Opened: ${job.title}`, 'success');
              spinOff(addSpinner, addBtn, addBtnLabel, 'Add to JAM');
            });
          }); // sendMessage
        }
      ); // executeScript
    }); // tabs.query
  }); // storage.get
}); // addBtn click
