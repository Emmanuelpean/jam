export const formatFileSize = (bytes) => {
	if (!bytes || bytes === 0) return "";
	if (bytes < 1024) return `${bytes} B`;
	if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
	return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

export const parseSizeText = (sizeText) => {
	const defaultSize = 10 * 1024 * 1024; // 10MB
	if (!sizeText) return defaultSize;

	const match = sizeText.match(/^(\d+(?:\.\d+)?)\s*(KB|MB|GB)$/i);
	if (!match) return defaultSize;

	const value = parseFloat(match[1]);
	const unit = match[2].toUpperCase();

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

export const fileToBase64 = (file) => {
	return new Promise((resolve, reject) => {
		const reader = new FileReader();
		reader.readAsDataURL(file);
		reader.onload = () => resolve(reader.result);
		reader.onerror = (error) => reject(error);
	});
};
