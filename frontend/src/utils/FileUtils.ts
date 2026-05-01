const UNPREVIEWABLE_MIME_TYPES = new Set([
	"application/msword",
	"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
	"application/vnd.ms-excel",
	"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
	"application/vnd.ms-powerpoint",
	"application/vnd.openxmlformats-officedocument.presentationml.presentation",
]);

export const canPreviewFile = (mimeType: string): boolean => !UNPREVIEWABLE_MIME_TYPES.has(mimeType);

export const formatFileSize = (bytes: number): string => {
	if (!bytes || bytes === 0) return "";
	if (bytes < 1024) return `${bytes} B`;
	if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
	return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

export const parseSizeText = (sizeText: string | null): number => {
	const defaultSize: number = 10 * 1024 * 1024; // 10MB
	if (!sizeText) return defaultSize;

	const match = sizeText.match(/^(\d+(?:\.\d+)?)\s*(KB|MB|GB)$/i);
	if (!match || !match[1] || !match[2]) return defaultSize;

	const value = parseFloat(match[1]);
	const unit = match[2].toUpperCase() as "KB" | "MB" | "GB";

	switch (unit) {
		case "KB":
			return value * 1024;
		case "MB":
			return value * 1024 * 1024;
		case "GB":
			return value * 1024 * 1024 * 1024;
		default:
			return defaultSize;
	}
};

export const fileToBase64 = (file: File): Promise<string | ArrayBuffer | null> => {
	return new Promise((resolve, reject) => {
		const reader = new FileReader();
		reader.readAsDataURL(file);
		reader.onload = () => resolve(reader.result);
		reader.onerror = (error) => reject(error);
	});
};
