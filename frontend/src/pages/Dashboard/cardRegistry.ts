import { LayoutItem } from "react-grid-layout";

export interface CardDefinition {
	id: string;
	label: string;
	icon: string;
	premiumOnly: boolean;
	layouts: {
		lg: LayoutItem;
		md: LayoutItem;
		sm: LayoutItem;
	};
}

export const CARD_REGISTRY: CardDefinition[] = [
	{
		id: "stat-total-jobs",
		label: "Total Jobs",
		icon: "briefcase",
		premiumOnly: false,
		layouts: {
			lg: { i: "stat-total-jobs", x: 0, y: 0, w: 3, h: 4, minW: 2, minH: 2 },
			md: { i: "stat-total-jobs", x: 0, y: 0, w: 3, h: 4, minW: 2, minH: 2 },
			sm: { i: "stat-total-jobs", x: 0, y: 0, w: 6, h: 4, minW: 3, minH: 2 },
		},
	},
	{
		id: "stat-applications",
		label: "Applications",
		icon: "send",
		premiumOnly: false,
		layouts: {
			lg: { i: "stat-applications", x: 3, y: 0, w: 3, h: 4, minW: 2, minH: 4 },
			md: { i: "stat-applications", x: 3, y: 0, w: 3, h: 4, minW: 2, minH: 4 },
			sm: { i: "stat-applications", x: 6, y: 0, w: 6, h: 4, minW: 3, minH: 4 },
		},
	},
	{
		id: "stat-pending",
		label: "Pending",
		icon: "clock",
		premiumOnly: false,
		layouts: {
			lg: { i: "stat-pending", x: 6, y: 0, w: 3, h: 4, minW: 2, minH: 4 },
			md: { i: "stat-pending", x: 6, y: 0, w: 3, h: 4, minW: 2, minH: 4 },
			sm: { i: "stat-pending", x: 0, y: 4, w: 6, h: 4, minW: 3, minH: 4 },
		},
	},
	{
		id: "stat-follow-up",
		label: "Need Follow-up",
		icon: "telephone",
		premiumOnly: false,
		layouts: {
			lg: { i: "stat-follow-up", x: 9, y: 0, w: 3, h: 4, minW: 2, minH: 4 },
			md: { i: "stat-follow-up", x: 9, y: 0, w: 3, h: 4, minW: 2, minH: 4 },
			sm: { i: "stat-follow-up", x: 6, y: 4, w: 6, h: 4, minW: 3, minH: 4 },
		},
	},
	{
		id: "recent-activity",
		label: "Recent Activity",
		icon: "clock-history",
		premiumOnly: false,
		layouts: {
			lg: { i: "recent-activity", x: 0, y: 4, w: 4, h: 6, minW: 3, minH: 4 },
			md: { i: "recent-activity", x: 0, y: 4, w: 4, h: 6, minW: 3, minH: 4 },
			sm: { i: "recent-activity", x: 0, y: 8, w: 12, h: 6, minW: 6, minH: 4 },
		},
	},
	{
		id: "follow-up-table",
		label: "Applications Requiring Follow-up",
		icon: "telephone",
		premiumOnly: false,
		layouts: {
			lg: { i: "follow-up-table", x: 4, y: 4, w: 8, h: 6, minW: 4, minH: 4 },
			md: { i: "follow-up-table", x: 4, y: 4, w: 8, h: 6, minW: 4, minH: 4 },
			sm: { i: "follow-up-table", x: 0, y: 14, w: 12, h: 6, minW: 6, minH: 4 },
		},
	},
	{
		id: "upcoming-deadlines",
		label: "Upcoming Deadlines",
		icon: "clock",
		premiumOnly: false,
		layouts: {
			lg: { i: "upcoming-deadlines", x: 0, y: 10, w: 8, h: 6, minW: 4, minH: 4 },
			md: { i: "upcoming-deadlines", x: 0, y: 10, w: 8, h: 6, minW: 4, minH: 4 },
			sm: { i: "upcoming-deadlines", x: 0, y: 20, w: 12, h: 6, minW: 6, minH: 4 },
		},
	},
	{
		id: "upcoming-interviews",
		label: "Upcoming Interviews",
		icon: "calendar-event",
		premiumOnly: false,
		layouts: {
			lg: { i: "upcoming-interviews", x: 8, y: 10, w: 4, h: 6, minW: 3, minH: 4 },
			md: { i: "upcoming-interviews", x: 8, y: 10, w: 4, h: 6, minW: 3, minH: 4 },
			sm: { i: "upcoming-interviews", x: 0, y: 26, w: 12, h: 6, minW: 6, minH: 4 },
		},
	},
	{
		id: "job-alerts",
		label: "Job Alerts",
		icon: "bell",
		premiumOnly: true,
		layouts: {
			lg: { i: "job-alerts", x: 0, y: 16, w: 12, h: 6, minW: 6, minH: 4 },
			md: { i: "job-alerts", x: 0, y: 16, w: 12, h: 6, minW: 6, minH: 4 },
			sm: { i: "job-alerts", x: 0, y: 32, w: 12, h: 6, minW: 6, minH: 4 },
		},
	},
];

export interface DashboardLayoutData {
	version: number;
	visibleCards: string[];
	layouts: {
		lg: LayoutItem[];
		md: LayoutItem[];
		sm: LayoutItem[];
	};
}

export function getDefaultLayout(isPremium: boolean): DashboardLayoutData {
	const cards = CARD_REGISTRY.filter((c) => !c.premiumOnly || isPremium);
	return {
		version: 1,
		visibleCards: cards.map((c) => c.id),
		layouts: {
			lg: cards.map((c) => c.layouts.lg),
			md: cards.map((c) => c.layouts.md),
			sm: cards.map((c) => c.layouts.sm),
		},
	};
}

export function parseLayoutData(json: string | null, isPremium: boolean): DashboardLayoutData {
	if (!json) return getDefaultLayout(isPremium);
	try {
		const parsed = JSON.parse(json) as DashboardLayoutData;
		if (parsed.version !== 1 || !parsed.layouts || !parsed.visibleCards) {
			return getDefaultLayout(isPremium);
		}
		// Filter out premium cards if user is not premium
		if (!isPremium) {
			const premiumIds = new Set(CARD_REGISTRY.filter((c) => c.premiumOnly).map((c) => c.id));
			parsed.visibleCards = parsed.visibleCards.filter((id) => !premiumIds.has(id));
			for (const bp of ["lg", "md", "sm"] as const) {
				parsed.layouts[bp] = parsed.layouts[bp].filter((l) => !premiumIds.has(l.i));
			}
		}
		return parsed;
	} catch {
		return getDefaultLayout(isPremium);
	}
}
