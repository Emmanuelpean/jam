export const formatDateTime = (datetime?: string | Date): string => {
	if (!datetime) {
		datetime = new Date();
	} else {
		datetime = new Date(datetime);
	}
	const year = datetime.getFullYear();
	const month = String(datetime.getMonth() + 1).padStart(2, "0");
	const day = String(datetime.getDate()).padStart(2, "0");
	const hours = String(datetime.getHours()).padStart(2, "0");
	const minutes = String(datetime.getMinutes()).padStart(2, "0");
	return `${year}-${month}-${day}T${hours}:${minutes}`;
};

export const localeDateOnly = (dateString: string): string => {
	if (!dateString) return "";
	const date = new Date(dateString);
	return date.toLocaleDateString();
};

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

export const formatDate = (datetime?: string | Date): string => {
	if (!datetime) {
		datetime = new Date();
	} else {
		datetime = new Date(datetime);
	}
	const year = datetime.getFullYear();
	const month = String(datetime.getMonth() + 1).padStart(2, "0");
	const day = String(datetime.getDate()).padStart(2, "0");
	return `${year}-${month}-${day}`;
};
