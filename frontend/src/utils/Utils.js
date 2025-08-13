export const accessAttribute = (item, key) => {
	const parts = key.split(".");
	let obj = item;
	for (const part of parts) {
		obj = obj?.[part];
		if (obj === null || obj === undefined) break;
	}
	return obj;
};

export const toSelectOptions = (data, valueKey = "id", labelKey = "name") => {
	return data.map((item) => ({
		value: accessAttribute(item, valueKey),
		label: accessAttribute(item, labelKey),
		data: item,
	}));
};
