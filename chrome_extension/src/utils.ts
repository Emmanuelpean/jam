// ---------------------------------------------------------------------------
// Selector helpers
// ---------------------------------------------------------------------------

export function queryFirst(selectors: string[]): string | null {
	for (const sel of selectors) {
		const el: Element | null = document.querySelector(sel);
		if (el && el.textContent?.trim()) {
			return el.textContent!.trim();
		}
	}
	return null;
}

// ---------------------------------------------------------------------------
// Salary parsing
// ---------------------------------------------------------------------------

const SALARY_RE =
	/([£$€¥₹])\s*([\d,]+(?:\.\d+)?)\s*([kKmM]?)\s*(?:\/\w+)?\s*(?:[-–—]|to)\s*[£$€¥₹]?\s*([\d,]+(?:\.\d+)?)\s*([kKmM]?)/;

const CURRENCY_SYMBOLS: Record<string, string> = { "£": "GBP", $: "USD", "€": "EUR", "¥": "JPY", "₹": "INR" };

function parseNumber(raw: string): number {
	return parseFloat(raw.replace(/,/g, ""));
}

function applyMultiplier(num: number, suffix: string): number {
	const s = (suffix || "").toLowerCase();
	if (s === "k") return num * 1_000;
	if (s === "m") return num * 1_000_000;
	return num;
}

export function parseSalary(text: string | null): SalaryResult {
	if (!text) return {};
	const match: RegExpMatchArray | null = text.match(SALARY_RE);
	if (!match) return {};

	const currency: string = CURRENCY_SYMBOLS[match[1]] || match[1];
	const numA: number = applyMultiplier(parseNumber(match[2]), match[3]);
	const numB: number = applyMultiplier(parseNumber(match[4]), match[5]);

	return {
		salary_min: Math.min(numA, numB),
		salary_max: Math.max(numA, numB),
		salary_currency: currency,
	};
}

// ---------------------------------------------------------------------------
// Attendance type mapping
// ---------------------------------------------------------------------------

export const ATTENDANCE_MAP: AttendanceEntry[] = [
	{ re: /^remote$/i, value: "remote" },
	{ re: /^hybrid$/i, value: "hybrid" },
	{ re: /^on[\s-]?site$/i, value: "on-site" },
	{ re: /\bremote\b/i, value: "remote" },
	{ re: /\bhybrid\b/i, value: "hybrid" },
	{ re: /\bon[\s-]?site\b/i, value: "on-site" },
];

// ---------------------------------------------------------------------------
// Description extraction
// ---------------------------------------------------------------------------

const BLOCK_TAGS = new Set(["p", "div", "li", "br", "h1", "h2", "h3", "h4", "h5", "h6", "tr"]);
const LIST_TAGS = new Set(["ul", "ol"]);

export function descriptionToText(el: Element): string {
	let out: string = "";

	function walk(node: Node): void {
		if (node.nodeType === Node.TEXT_NODE) {
			out += node.textContent;
			return;
		}
		if (node.nodeType !== Node.ELEMENT_NODE) return;

		const elem = node as Element;
		const tag: string = elem.tagName.toLowerCase();

		if (tag === "br") {
			out += "\n";
			return;
		}

		// Skip LinkedIn's "About the job" section header
		if (/^h[1-6]$/.test(tag) && elem.textContent?.trim() === "About the job") return;

		if (tag === "li") out += "- ";
		if (LIST_TAGS.has(tag)) out += "\n";

		for (const child of elem.childNodes) walk(child);

		if (BLOCK_TAGS.has(tag)) out += "\n";
		if (LIST_TAGS.has(tag)) out += "\n";
	}

	walk(el);

	return out
		.replace(/[ \t]+/g, " ") // collapse inline whitespace
		.replace(/ *\n */g, "\n") // strip spaces around newlines (indentation artifacts)
		.replace(/\n{3,}/g, "\n\n") // max one blank line between blocks
		.replace(/^(- .+)\n\n+(?=- )/gm, "$1\n") // no blank lines between bullets
		.trim();
}
