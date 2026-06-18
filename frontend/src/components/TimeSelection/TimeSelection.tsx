import React, { useEffect, useState } from "react";
import "./TimeSelection.scss";
import { DateRange, getDateRange, TimeUnit } from "../../utils/TimeUtils";
import { SelectInput } from "../rendering/widgets/SelectWidget";
import { ModalFormField } from "../rendering/form/FormRenders";

type SelectionMode = "period" | "dateRange";

interface TimeSelectionProps {
	onDateRangeChange?: (dateRange: DateRange) => void;
	defaultMode?: SelectionMode;
	defaultAmount?: number;
	defaultUnit?: TimeUnit;
	defaultIntervalSeconds?: number;
}

interface SelectOption {
	value: TimeUnit;
	label: string;
}

const timeUnitOptions: SelectOption[] = [
	{ value: "days", label: "Days" },
	{ value: "weeks", label: "Weeks" },
	{ value: "months", label: "Months" },
	{ value: "years", label: "Years" },
];

const TimeSelection: React.FC<TimeSelectionProps> = ({
	onDateRangeChange,
	defaultMode = "period",
	defaultAmount = 1,
	defaultUnit = "weeks",
	defaultIntervalSeconds = 60,
}) => {
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

	// Refresh the range on the configured interval while in period mode
	useEffect(() => {
		if (mode === "period") {
			updateDateRange();
			const intervalId = setInterval(updateDateRange, defaultIntervalSeconds * 1000);
			return () => clearInterval(intervalId);
		}
	}, [mode, amount, unit]);

	const handleModeChange = (newMode: SelectionMode): void => {
		setMode(newMode);
		if (newMode === "period") {
			updateDateRange();
		} else if (newMode === "dateRange") {
			onDateRangeChange?.({ start: startDate, end: endDate });
		}
	};

	const handleAmountChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
		const value: number = parseInt(e.target.value, 10);
		if (!isNaN(value) && value > 0) {
			setAmount(value);
		}
	};

	const handleStartDateChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
		const newStartDate: string = e.target.value;
		setStartDate(newStartDate);
		if (newStartDate && endDate) {
			onDateRangeChange?.({ start: newStartDate, end: endDate });
		}
	};

	const handleEndDateChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
		const newEndDate: string = e.target.value;
		setEndDate(newEndDate);
		if (startDate && newEndDate) {
			onDateRangeChange?.({ start: startDate, end: newEndDate });
		}
	};

	const timeUnitField: ModalFormField = {
		key: "timeUnit",
		type: "select",
		label: "Unit",
		options: timeUnitOptions,
		placeholder: "Select unit",
		isClearable: false,
		size: "sm",
	};

	return (
		<div className="time-selection-container">
			<div className="d-flex align-items-center gap-3 flex-wrap">
				<div className="btn-group btn-group-sm" role="group" aria-label="Selection mode">
					<button
						type="button"
						className={`btn ${mode === "period" ? "btn-primary" : "btn-outline-secondary"}`}
						onClick={() => handleModeChange("period")}
					>
						Time Period
					</button>
					<button
						type="button"
						className={`btn ${mode === "dateRange" ? "btn-primary" : "btn-outline-secondary"}`}
						onClick={() => handleModeChange("dateRange")}
					>
						Date Range
					</button>
				</div>

				{mode === "period" && (
					<>
						<input
							type="number"
							className="form-control form-control-sm"
							style={{ width: "70px" }}
							min="1"
							value={amount}
							onChange={handleAmountChange}
							placeholder="Amount"
						/>
						<div style={{ minWidth: "120px" }}>
							<SelectInput
								field={timeUnitField}
								value={unit}
								error={null}
								handleChange={(event: any) => {
									// SelectInput emits SyntheticEvent with target.value being the selected option's value
									if (event?.target?.value) setUnit(event.target.value as TimeUnit);
								}}
							/>
						</div>
					</>
				)}

				{mode === "dateRange" && (
					<>
						<input
							type="datetime-local"
							className="form-control form-control-sm"
							style={{ width: "165px" }}
							value={startDate}
							onChange={handleStartDateChange}
						/>
						<span className="text-muted fw-bold">to</span>
						<input
							type="datetime-local"
							className="form-control form-control-sm"
							style={{ width: "165px" }}
							value={endDate}
							onChange={handleEndDateChange}
						/>
					</>
				)}
			</div>
		</div>
	);
};

export default TimeSelection;
