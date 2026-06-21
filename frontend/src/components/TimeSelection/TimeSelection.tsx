import React from "react";
import "./TimeSelection.scss";
import { TimeUnit } from "../../utils/TimeUtils";
import { SelectInput } from "../rendering/widgets/SelectWidget";
import { ModalFormField } from "../rendering/form/FormRenders";

export type SelectionMode = "period" | "dateRange";

interface TimeSelectionProps {
	mode: SelectionMode;
	amount: number;
	unit: TimeUnit;
	startDate: string;
	endDate: string;
	/** Restrict the selectable time units; defaults to all units. */
	availableUnits?: TimeUnit[];
	onModeChange: (mode: SelectionMode) => void;
	onAmountChange: (amount: number) => void;
	onUnitChange: (unit: TimeUnit) => void;
	onStartDateChange: (value: string) => void;
	onEndDateChange: (value: string) => void;
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
	mode,
	amount,
	unit,
	startDate,
	endDate,
	availableUnits,
	onModeChange,
	onAmountChange,
	onUnitChange,
	onStartDateChange,
	onEndDateChange,
}) => {
	const options: SelectOption[] = availableUnits
		? timeUnitOptions.filter((o) => availableUnits.includes(o.value))
		: timeUnitOptions;

	const timeUnitField: ModalFormField = {
		key: "timeUnit",
		type: "select",
		label: "Unit",
		options,
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
						onClick={() => onModeChange("period")}
					>
						Time Period
					</button>
					<button
						type="button"
						className={`btn ${mode === "dateRange" ? "btn-primary" : "btn-outline-secondary"}`}
						onClick={() => onModeChange("dateRange")}
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
							onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
								onAmountChange(parseInt(e.target.value, 10))
							}
							placeholder="Amount"
						/>
						<div className="time-unit-select">
							<SelectInput
								field={timeUnitField}
								value={unit}
								error={null}
								handleChange={(event: any) => {
									// SelectInput emits SyntheticEvent with target.value being the selected option's value
									if (event?.target?.value) onUnitChange(event.target.value as TimeUnit);
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
							onChange={(e: React.ChangeEvent<HTMLInputElement>) => onStartDateChange(e.target.value)}
						/>
						<span className="text-muted fw-bold">to</span>
						<input
							type="datetime-local"
							className="form-control form-control-sm"
							style={{ width: "165px" }}
							value={endDate}
							onChange={(e: React.ChangeEvent<HTMLInputElement>) => onEndDateChange(e.target.value)}
						/>
					</>
				)}
			</div>
		</div>
	);
};

export default TimeSelection;
