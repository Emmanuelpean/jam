import React, { useEffect, useState } from "react";
import "./TimeSelection.scss";
import { DateRange, getDateRange, TimeUnit } from "../../utils/TimeUtils";
import { SelectInput } from "../rendering/widgets/SelectWidget";
import { ModalFormField } from "../rendering/form/FormRenders";

type SelectionMode = "period" | "dateRange";

interface TimeSelectionProps {
	onDateRangeChange?: (dateRange: DateRange) => void;
	defaultMode?: SelectionMode;
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

const TimeSelection: React.FC<TimeSelectionProps> = ({ onDateRangeChange, defaultMode = "period" }) => {
	const [mode, setMode] = useState<SelectionMode>(defaultMode);
	const [amount, setAmount] = useState<number>(1);
	const [unit, setUnit] = useState<TimeUnit>("weeks");
	const [startDate, setStartDate] = useState<string>("");
	const [endDate, setEndDate] = useState<string>("");

	const updateDateRange = (): void => {
		const range: DateRange = getDateRange(amount, unit);
		setStartDate(new Date(range.start).toISOString().slice(0, 16));
		setEndDate(new Date(range.end).toISOString().slice(0, 16));
		onDateRangeChange?.(range);
	};

	// Update every minute when in period mode
	useEffect(() => {
		if (mode === "period") {
			updateDateRange();
			const intervalId = setInterval(updateDateRange, 60000);
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
		name: "timeUnit",
		type: "select",
		label: "Unit",
		options: timeUnitOptions,
		placeholder: "Select unit",
		isClearable: false,
	};

	return (
		<div className="time-selection-container">
			<div className="d-flex align-items-center gap-3 flex-wrap">
				<div className="radio-group">
					<label className="custom-radio">
						<input
							type="radio"
							name="selectionMode"
							value="period"
							checked={mode === "period"}
							onChange={() => handleModeChange("period")}
						/>
						<span className="radio-label">Time Period</span>
					</label>
					<label className="custom-radio">
						<input
							type="radio"
							name="selectionMode"
							value="dateRange"
							checked={mode === "dateRange"}
							onChange={() => handleModeChange("dateRange")}
						/>
						<span className="radio-label">Date Range</span>
					</label>
				</div>

				{mode === "period" && (
					<>
						<input
							type="number"
							className="form-control"
							style={{ width: "100px", height: "52px" }}
							min="1"
							value={amount}
							onChange={handleAmountChange}
							placeholder="Amount"
						/>
						<div style={{ minWidth: "150px" }}>
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
							className="form-control"
							style={{ width: "200px", height: "52px" }}
							value={startDate}
							onChange={handleStartDateChange}
						/>
						<span className="text-muted fw-bold">to</span>
						<input
							type="datetime-local"
							className="form-control"
							style={{ width: "200px", height: "52px" }}
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
