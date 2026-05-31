/** Expand step-definition placeholders to real DOM ids */
export function expandTargetId(
	targetId: string,
	demoJobId: number | null,
	demoScrapedJobId: number | null,
	demoScrapingFilterId: number | null,
	demoJobEmailId: number | null = null,
): string {
	if (targetId === "[demo-job-row]") return demoJobId !== null ? `table-row-job-${demoJobId}` : targetId;
	if (targetId === "[demo-scraped-job-row]")
		return demoScrapedJobId !== null ? `table-row-scrapedJob-${demoScrapedJobId}` : targetId;
	if (targetId === "[demo-scraping-filter-row]")
		return demoScrapingFilterId !== null ? `table-row-scrapingExclusionFilter-${demoScrapingFilterId}` : targetId;
	if (targetId === "[demo-job-email-row]")
		return demoJobEmailId !== null ? `table-row-jobEmail-${demoJobEmailId}` : targetId;
	return targetId;
}

/** Resolve a targetId to a DOM element — supports plain IDs and CSS selectors */
export function resolveTarget(targetId: string): Element | null {
	return targetId.startsWith("#") || targetId.startsWith(".") || targetId.startsWith("[") || targetId.includes(" ")
		? document.querySelector(targetId)
		: document.getElementById(targetId);
}

/** Returns true if the element is hidden by any scrollable ancestor (including the window) */
export function isClippedByScroll(el: Element): boolean {
	const r = el.getBoundingClientRect();
	if (r.bottom < 0 || r.top > window.innerHeight || r.right < 0 || r.left > window.innerWidth) return true;
	let parent = el.parentElement;
	while (parent && parent !== document.documentElement) {
		const { overflowY, overflow } = window.getComputedStyle(parent);
		if (/(auto|scroll)/.test(overflowY + overflow)) {
			const pr = parent.getBoundingClientRect();
			if (r.top < pr.top || r.bottom > pr.bottom) return true;
		}
		parent = parent.parentElement;
	}
	return false;
}

/** Force a value into a React-controlled input */
export function setNativeInputValue(el: HTMLInputElement, value: string): void {
	const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value")?.set;
	if (nativeSetter) {
		nativeSetter.call(el, value);
		el.dispatchEvent(new Event("input", { bubbles: true }));
		el.dispatchEvent(new Event("change", { bubbles: true }));
	}
}

export function rectEqual(a: DOMRect, b: DOMRect): boolean {
	return a.top === b.top && a.left === b.left && a.width === b.width && a.height === b.height;
}
