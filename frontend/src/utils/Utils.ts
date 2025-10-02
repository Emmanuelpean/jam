export type SelectOption = {
	value: string;
	label: string;
	data?: any;
};

export interface Progress {
	current: number;
	total: number;
}

export const accessAttribute = (item: any, key: string | null | undefined) => {
	if (!key) return item;
	const parts = key.split(".");
	let obj = item;
	for (const part of parts) {
		obj = obj?.[part];
		if (obj === null || obj === undefined) break;
	}
	return obj;
};

export const toSelectOptions = (data: any[], valueKey = "id", labelKey = "name"): SelectOption[] => {
	return data.map((item: any) => ({
		value: accessAttribute(item, valueKey),
		label: accessAttribute(item, labelKey),
		data: item,
	}));
};

export const areDifferent = (value1: any, value2: any): boolean => {
	// Handle null/undefined/empty string equivalence
	const isEmptyValue = (val: any): boolean => val === null || val === undefined || val === "";

	if (isEmptyValue(value1) && isEmptyValue(value2)) {
		return false;
	}

	// Handle arrays (for multi-select fields)
	if (Array.isArray(value1) && Array.isArray(value2)) {
		if (value1.length !== value2.length) return true;
		return value1.some((val: any, index: number) => val !== value2[index]);
	}

	return value1 !== value2;
};

export const findByKey = (objects: any[], key: any): any => {
	return objects.find((object) => object.key === key);
};

export function flattenArray(arr: Array<any>): Array<any> {
	const result = [];
	for (const item of arr) {
		if (Array.isArray(item)) {
			result.push(...flattenArray(item));
		} else {
			result.push(item);
		}
	}
	return result;
}

export const normaliseList = <T>(variable: T | T[] | null | undefined): T[] => {
	if (variable === null || variable === undefined) return [];
	return Array.isArray(variable) ? variable : [variable];
};
