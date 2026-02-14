export function formatActivityDate(dateString: string | Date): string {
	const date = new Date(dateString);
	const now = new Date();

	const options: Intl.DateTimeFormatOptions = {
		weekday: "long",
		month: "short",
		day: "numeric",
		hour: "2-digit",
		minute: "2-digit",
		hour12: false,
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

export function convertToEndOfDay(date: Date | string): Date {
	const endDate = new Date(date);
	endDate.setHours(23, 59, 59, 0);
	return endDate;
}

export function toDdMmYyyy(date: Date | string): string {
	const dateObj: Date = new Date(date);
	const day: string = String(dateObj.getDate()).padStart(2, "0");
	const month: string = String(dateObj.getMonth() + 1).padStart(2, "0");
	const year: string = dateObj.getFullYear().toString();
	return `${day}/${month}/${year}`;
}

export function toDdMmYyyyHhMm(date: Date | string): string {
	const dateObj = typeof date === "string" ? new Date(date) : date;

	const datePart = new Intl.DateTimeFormat(undefined, {
		day: "2-digit",
		month: "2-digit",
		year: "numeric",
	}).format(dateObj);

	const timePart = new Intl.DateTimeFormat(undefined, {
		hour: "2-digit",
		minute: "2-digit",
		hour12: false,
	}).format(dateObj);

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
