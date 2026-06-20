import React, { JSX, useEffect, useState } from "react";
import { Popover } from "../Popover/Popover";
import TimeSelection, { SelectionMode } from "./TimeSelection";
import { DateRange, getDateRange, TimeUnit } from "../../utils/TimeUtils";

interface TimeFilterPopoverProps {
	onDateRangeChange?: (dateRange: DateRange) => void;
	defaultMode?: SelectionMode;
	defaultAmount?: number;
	defaultUnit?: TimeUnit;
	defaultIntervalSeconds?: number;
	id?: string;
}

/**
 * Compact "Filters" button that reveals the time range controls in a popover.
 * Owns the range state and computation so the data range is emitted on page
 * load (and kept refreshed) even while the popover is closed.
 */
export const TimeFilterPopover = ({
	id,
	onDateRangeChange,
	defaultMode = "period",
	defaultAmount = 1,
	defaultUnit = "weeks",
	defaultIntervalSeconds = 60,
}: TimeFilterPopoverProps): JSX.Element => {
	const [mode, setMode] = useState<SelectionMode>(defaultMode);
	const [amount, setAmount] = useState<number>(defaultAmount);
	const [unit, setUnit] = useState<TimeUnit>(defaultUnit);
	const [startDate, setStartDate] = useState<string>("");
	const [endDate, setEndDate] = useState<string>("");

	const updateDateRange = (): void => {
		const range: DateRange = getDateRange(amount, unit);
		setStartDate(new Date(range.start).toISOString().slice(0, 16));
		setEndDate(new Date(range.end).toISOString().slice(0, 16));
		onDateRangeChange?.(range);
	};

	// Emit the range on mount (page load) and whenever the period selection
	// changes; refresh it on the configured interval while in period mode.
	useEffect(() => {
		if (mode !== "period") return;
		updateDateRange();
		const intervalId = setInterval(updateDateRange, defaultIntervalSeconds * 1000);
		return (): void => clearInterval(intervalId);
	}, [mode, amount, unit]);

	const handleModeChange = (newMode: SelectionMode): void => {
		// Switching to date-range keeps the current window (the date inputs are already
		// populated from period mode), so there is no need to re-emit and reload data.
		// Switching back to period recomputes a now-relative window via the effect below.
		setMode(newMode);
	};

	const handleAmountChange = (value: number): void => {
		if (!isNaN(value) && value > 0) setAmount(value);
	};

	const handleStartDateChange = (value: string): void => {
		setStartDate(value);
		if (value && endDate) onDateRangeChange?.({ start: value, end: endDate });
	};

	const handleEndDateChange = (value: string): void => {
		setEndDate(value);
		if (startDate && value) onDateRangeChange?.({ start: startDate, end: value });
	};

	return (
		<Popover
			className="time-filter-popover"
			ariaLabel="Time filters"
			trigger={
				<span id={id} className="btn btn-outline-secondary btn-sm time-filter-button">
					<i className="bi bi-funnel me-2" />
					Filters
				</span>
			}
		>
			<TimeSelection
				mode={mode}
				amount={amount}
				unit={unit}
				startDate={startDate}
				endDate={endDate}
				onModeChange={handleModeChange}
				onAmountChange={handleAmountChange}
				onUnitChange={setUnit}
				onStartDateChange={handleStartDateChange}
				onEndDateChange={handleEndDateChange}
			/>
		</Popover>
	);
};
