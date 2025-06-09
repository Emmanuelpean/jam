export const formatDateWithTimezone = (date) => {
	const dateObj = new Date(date);

	// Get date parts
	const day = String(dateObj.getDate()).padStart(2, "0");
	const month = String(dateObj.getMonth() + 1).padStart(2, "0");
	const year = dateObj.getFullYear();

	// Get time parts
	const hours = String(dateObj.getHours()).padStart(2, "0");
	const minutes = String(dateObj.getMinutes()).padStart(2, "0");
	const seconds = String(dateObj.getSeconds()).padStart(2, "0");

	// Get timezone offset
	const timezoneOffset = -dateObj.getTimezoneOffset();
	const offsetHours = Math.floor(Math.abs(timezoneOffset) / 60);
	const offsetMinutes = Math.abs(timezoneOffset) % 60;
	const offsetSign = timezoneOffset >= 0 ? "+" : "-";

	// Only include minutes if they're not zero
	const timezone =
		offsetMinutes === 0
			? `GMT${offsetSign}${String(offsetHours)}`
			: `GMT${offsetSign}${String(offsetHours)}:${String(offsetMinutes).padStart(2, "0")}`;

	return `${day}/${month}/${year} ${hours}:${minutes}:${seconds} ${timezone}`;
};
