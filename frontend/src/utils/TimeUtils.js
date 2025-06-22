export const formDateTime = (datetime) => {
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
