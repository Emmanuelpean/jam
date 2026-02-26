// Runs on the JAM frontend at document_idle.
// By this point React has mounted and App.tsx's message listener is already set up
// (auth token is read synchronously from localStorage, so isAuthenticated is true on
// the first render and the useEffect runs before document_idle fires).

chrome.storage.local.get("pendingExtJob").then((result: { pendingExtJob?: ScrapedJob }) => {
	if (!result.pendingExtJob) return;
	window.postMessage({ type: "JAM_EXT_JOB", data: result.pendingExtJob }, "*");
	chrome.storage.local.remove("pendingExtJob");
});
