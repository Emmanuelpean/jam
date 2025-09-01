export type SelectOption = {
	value: string;
	label: string;
};

export interface Progress {
	current: number;
	total: number;
}

export const accessAttribute = (item: any, key: string) => {
	const parts = key.split(".");
	let obj = item;
	for (const part of parts) {
		obj = obj?.[part];
		if (obj === null || obj === undefined) break;
	}
	return obj;
};

export const toSelectOptions = (data: [], valueKey = "id", labelKey = "name"): SelectOption[] => {
	return data.map((item: any) => ({
		value: accessAttribute(item, valueKey),
		label: accessAttribute(item, labelKey),
		data: item,
	}));
};
