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

export const findItemByKey = <T extends { key: V }, V>(objects: T[], key: V): T | null => {
	const found = objects.find((object) => object.key === key);
	return found === undefined ? null : found;
};

export const findItemById = <T extends { id: number }>(objects: T[], key: number): T | null => {
	const found = objects.find((object) => object.id === key);
	return found === undefined ? null : found;
};

export const getColumnClass = (count: number): string => {
	switch (count) {
		case 1:
			return "col-sm-12";
		case 2:
			return "col-sm-6";
		case 3:
			return "col-sm-4";
		case 4:
			return "col-sm-3";
		default:
			return "col-sm-6";
	}
};

export const sortByKey = <T extends Record<string, any>>(array: T[], key: keyof T, ascending: boolean = true): T[] => {
	return array.sort((a: T, b: T) => {
		const valueA = a[key];
		const valueB = b[key];

		if (valueA < valueB) return ascending ? -1 : 1;
		if (valueA > valueB) return ascending ? 1 : -1;
		return 0;
	});
};

export const normaliseArray = <T>(item: T | T[] | null | undefined): T[] => {
	return Array.isArray(item) ? item : item ? [item] : [];
};
