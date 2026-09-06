import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "../contexts/AuthContext";

export const FIT_TO_SCREEN = "fit";

const RESIZE_DEBOUNCE_MS = 200;

export interface TablePageSize {
	pageSize: number;
	selectedValue: string;
	setPageSizeChoice: (value: string) => Promise<void>;
	tableRef: (element: HTMLElement | null) => void;
}

/** Resolve the number of entries a table shows per page: the size the user picked for that table,
 * persisted in their preferences, or as many rows as fit the available height while they have not
 * picked one. The fitted size never goes below the table default, so short viewports keep scrolling
 * inside the table rather than paginating more often.
 * :param entityType: The table the page size applies to.
 * :param defaultPageSize: The page size used when nothing is stored and nothing has been measured.
 * :param pageSizeOptions: The sizes offered by the table; a stored size outside them is ignored.
 * :param autoFit: Whether the table fills a fixed height and can therefore be measured. */
export function useTablePageSize(
	entityType: string,
	defaultPageSize: number,
	pageSizeOptions: number[],
	autoFit: boolean
): TablePageSize {
	const { currentUser, updateCurrentUser } = useAuth();
	const [container, setContainer] = useState<HTMLElement | null>(null);
	const [fittedPageSize, setFittedPageSize] = useState<number | null>(null);
	const [pendingChoice, setPendingChoice] = useState<number | null | undefined>(undefined);
	const measuredHeightRef = useRef<number>(0);

	const stored: number | undefined = currentUser?.preferences?.table_page_size?.[entityType];
	const storedPageSize: number | null = stored !== undefined && pageSizeOptions.includes(stored) ? stored : null;
	const chosen: number | null = pendingChoice !== undefined ? pendingChoice : storedPageSize;
	const isFitted: boolean = autoFit && chosen === null;

	const measure = useCallback((): void => {
		if (!container) return;
		const height: number = container.clientHeight;
		// Row heights differ from page to page, so only remeasure when the space itself changed
		if (height <= 0 || height === measuredHeightRef.current) return;
		const row: HTMLElement | null = container.querySelector("tbody tr");
		const rowHeight: number = row?.getBoundingClientRect().height ?? 0;
		if (rowHeight <= 0) return;
		const header: HTMLElement | null = container.querySelector("thead tr");
		const available: number = height - (header?.getBoundingClientRect().height ?? 0);
		measuredHeightRef.current = height;
		setFittedPageSize(Math.max(1, Math.floor(available / rowHeight)));
	}, [container]);

	useEffect(() => {
		if (!isFitted || !container) return;
		let timer: number = 0;
		const scheduleMeasure = (): void => {
			window.clearTimeout(timer);
			timer = window.setTimeout(measure, RESIZE_DEBOUNCE_MS);
		};
		const observer = new ResizeObserver(scheduleMeasure);
		observer.observe(container);
		const table: HTMLElement | null = container.querySelector("table");
		if (table) observer.observe(table);
		measure();
		return (): void => {
			window.clearTimeout(timer);
			observer.disconnect();
		};
	}, [container, isFitted, measure]);

	const setPageSizeChoice = useCallback(
		async (value: string): Promise<void> => {
			const size: number | null = value === FIT_TO_SCREEN ? null : Number(value);
			setPendingChoice(size);
			const existing: Record<string, number> = currentUser?.preferences?.table_page_size ?? {};
			const updated: Record<string, number> = { ...existing };
			if (size === null) {
				delete updated[entityType];
			} else {
				updated[entityType] = size;
			}
			await updateCurrentUser({
				preferences: { table_page_size: Object.keys(updated).length > 0 ? updated : null },
			});
		},
		[currentUser, entityType, updateCurrentUser]
	);

	const fittedOrDefault: number = isFitted && fittedPageSize ? fittedPageSize : defaultPageSize;

	return {
		pageSize: chosen ?? Math.max(defaultPageSize, fittedOrDefault),
		selectedValue: chosen !== null ? String(chosen) : autoFit ? FIT_TO_SCREEN : String(defaultPageSize),
		setPageSizeChoice,
		tableRef: setContainer,
	};
}
