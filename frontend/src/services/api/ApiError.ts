export const errorToString = (error: unknown): string => {
	if (error instanceof Error) {
		return `${error.name}: ${error.message}\n${error.stack ?? ""}`;
	}

	if (typeof error === "string") {
		return error;
	}

	try {
		return JSON.stringify(error, null, 2);
	} catch {
		return String(error);
	}
};

export class ApiError extends Error {
	readonly status: number;
	readonly data: unknown;

	constructor(message: string, status: number, data?: unknown) {
		super(message);
		this.name = "ApiError";
		this.status = status;
		this.data = data;
	}
}

export const handleApiError = (error: unknown, fallbackMessage = "Something went wrong") => {
	if (error instanceof ApiError) {
		return {
			message: error.message,
			status: error.status,
		};
	}

	return {
		message: fallbackMessage,
		status: 0,
	};
};
