export const formatTimeAgo = (dateString: string): string => {
	const now = new Date();
	const date = new Date(dateString);
	const diffTime = Math.abs(now.getTime() - date.getTime());
	const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
	const diffDays = Math.floor(diffHours / 24);

	if (diffHours < 1) return "Just now";
	if (diffHours < 24) return `${diffHours}h ago`;
	if (diffDays === 1) return "1 day ago";
	return `${diffDays} days ago`;
};

export function formatActivityDate(dateString: string | Date): string {
	const date = new Date(dateString);
	const now = new Date();
	const options: Intl.DateTimeFormatOptions = {
		weekday: "long",
		month: "short",
		day: "numeric",
		...(now.getFullYear() !== date.getFullYear() && { year: "numeric" }),
	};
	return date.toLocaleDateString("en-UK", options);
}

export function formatTimedelta(seconds: number): string {
	const days = Math.floor(seconds / (24 * 3600));
	if (days >= 1) {
		return `${days} day${days > 1 ? "s" : ""}`;
	}
	const hours = Math.floor(seconds / 3600);
	return `${hours} hour${hours !== 1 ? "s" : ""}`;
}

export function convertToEndOfDay(date: Date): Date {
	// Create a copy to avoid mutating the original
	const endDate = new Date(date);

	// Set to end of day
	endDate.setHours(23, 59, 59, 0);

	return endDate;
}

export function toDdMmYyyy(date: Date): string {
	const dateObj: Date = new Date(date);
	const day = String(dateObj.getUTCDate()).padStart(2, "0");
	const month = String(dateObj.getUTCMonth() + 1).padStart(2, "0");
	const year = dateObj.getUTCFullYear();
	return `${day}/${month}/${year}`;
}

export function toDdMmYyyyHhMm(date: Date): string {
	const dateObj: Date = new Date(date);
	const dd = String(dateObj.getDate()).padStart(2, "0");
	const MM = String(dateObj.getMonth() + 1).padStart(2, "0");
	const yyyy = dateObj.getFullYear();
	const hh = String(dateObj.getHours()).padStart(2, "0");
	const mm = String(dateObj.getMinutes()).padStart(2, "0");

	return `${dd}/${MM}/${yyyy} ${hh}:${mm}`;
}
