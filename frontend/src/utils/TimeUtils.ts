export function formatActivityDate(dateString: string | Date): string {
	const date = new Date(dateString);
	const now = new Date();
	const options: Intl.DateTimeFormatOptions = {
		weekday: "long",
		month: "short",
		day: "numeric",
		hour: "2-digit",
		minute: "2-digit",
		...(now.getFullYear() !== date.getFullYear() && { year: "numeric" }),
	};
	return date.toLocaleDateString("en-UK", options);
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
	const day: string = String(dateObj.getUTCDate()).padStart(2, "0");
	const month: string = String(dateObj.getUTCMonth() + 1).padStart(2, "0");
	const year: string = dateObj.getUTCFullYear().toString();
	return `${day}/${month}/${year}`;
}

export function toDdMmYyyyHhMm(date: Date | string): string {
	const ddMmYyyy: string = toDdMmYyyy(date);
	const dateObj: Date = new Date(date);
	const hh: string = String(dateObj.getHours()).padStart(2, "0");
	const mm: string = String(dateObj.getMinutes()).padStart(2, "0");
	return `${ddMmYyyy} ${hh}:${mm}`;
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
