export interface BaseOut {
	id: number;
	created_at: Date | string;
	modified_at: Date | string;
}

export interface OwnedOut extends BaseOut {
	owner_id: number;
}

export interface GeoLocation {
	latitude: number | null;
	longitude: number | null;
	city: string | null;
	postcode: string | null;
	country: string | null;
}
