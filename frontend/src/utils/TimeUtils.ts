export function formatActivityDate(date: Date, dateOnly = false): string {
	const now = new Date();

	const options: Intl.DateTimeFormatOptions = {
		weekday: "long",
		month: "short",
		day: "numeric",
		...(!dateOnly && { hour: "2-digit", minute: "2-digit", hour12: false }),
		...(now.getFullYear() !== date.getFullYear() && { year: "numeric" }),
	};

	return new Intl.DateTimeFormat("en-GB", options).format(date);
}

export function formatTimedelta(seconds: number): string {
	const days: number = Math.floor(seconds / (24 * 3600));
	if (days >= 1) {
		return `${days} day${days > 1 ? "s" : ""}`;
	}
	const hours: number = Math.floor(seconds / 3600);
	return `${hours} hour${hours !== 1 ? "s" : ""}`;
}

export function convertToEndOfDay(date: Date): Date {
	const endDate = new Date(date);
	endDate.setHours(23, 59, 59, 0);
	return endDate;
}

export function toDdMmYyyy(date: Date): string {
	const dateObj: Date = new Date(date);
	const day: string = String(dateObj.getDate()).padStart(2, "0");
	const month: string = String(dateObj.getMonth() + 1).padStart(2, "0");
	const year: string = dateObj.getFullYear().toString();
	return `${day}/${month}/${year}`;
}

export function toDdMmYyyyHhMm(date: Date): string {
	const datePart: string = new Intl.DateTimeFormat(undefined, {
		day: "2-digit",
		month: "2-digit",
		year: "numeric",
	}).format(date);
	const timePart: string = new Intl.DateTimeFormat(undefined, {
		hour: "2-digit",
		minute: "2-digit",
		hour12: false,
	}).format(date);
	return `${datePart} ${timePart}`;
}

export const formatDuration = (seconds: number | null): string => {
	if (!seconds) return "N/A";
	const hours: number = Math.floor(seconds / 3600);
	if (hours > 0) {
		const mins: number = Math.floor((seconds % 3600) / 60);
		return `${hours}h ${mins}m`;
	} else {
		const mins: number = Math.floor(seconds / 60);
		const secs: number = Math.floor(seconds % 60);
		return `${mins}m ${secs}s`;
	}
};

export const periodToDays = (amount: number, unit: TimeUnit): number => {
	switch (unit) {
		case "days":
			return amount;
		case "weeks":
			return amount * 7;
		case "months":
			return amount * 30;
		case "years":
			return amount * 365;
		default:
			return amount;
	}
};

export interface DateRange {
	start: Date | string;
	end: Date | string;
}

export const toDateTimeLocalString = (date: Date): string => {
	const pad = (n: number): string => String(n).padStart(2, "0");
	return (
		`${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` +
		`T${pad(date.getHours())}:${pad(date.getMinutes())}`
	);
};

export const getDateRange = (amount: number, unit: TimeUnit): DateRange => {
	const days: number = periodToDays(amount, unit);

	const end = new Date();
	const start = new Date();
	start.setDate(start.getDate() - days);

	return { start, end };
};

export type TimeUnit = "days" | "weeks" | "months" | "years";

export const ONE_HOUR_IN_SECONDS = 3600;

export const formatScheduledTime = (date: Date): string => {
	return date.toLocaleDateString("en-GB", {
		weekday: "long",
		day: "numeric",
		month: "long",
		hour: "2-digit",
		minute: "2-digit",
	});
};

const isIsoDateString = (value: any): boolean => {
	return typeof value === "string" && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(value);
};

export const parseDates = (data: any): any => {
	if (Array.isArray(data)) {
		return data.map(parseDates);
	}

	if (data && typeof data === "object") {
		const parsed: any = {};
		for (const key in data) {
			const value = data[key];

			if (isIsoDateString(value)) {
				parsed[key] = new Date(value);
			} else {
				parsed[key] = parseDates(value);
			}
		}
		return parsed;
	}

	return data;
};
