import React, { JSX } from "react";
import { CustomSelect } from "../../rendering/widgets/CustomSelect";
import { SelectFilterConfig, SelectFilterValue } from "../FilterTypes";

interface Props {
	columnKey?: string;
	config: SelectFilterConfig;
	value: SelectFilterValue;
	onChange: (v: SelectFilterValue) => void;
}

const SelectFilter = ({ columnKey, config, value, onChange }: Props): JSX.Element => {
	const options = config.options.map((opt) => ({ value: String(opt.value), label: opt.label }));
	const selected = options.filter((o) => value.selected.includes(o.value));

	return (
		<CustomSelect
			id={columnKey ? `select-filter-${columnKey}` : "select-filter"}
			inputId={columnKey ? `filter-select-${columnKey}` : undefined}
			isMulti
			closeMenuOnSelect={false}
			options={options}
			value={selected}
			onChange={(picked) =>
				onChange({ type: "select", selected: ((picked as typeof selected) ?? []).map((p) => p.value) })
			}
			className="jam-select jam-select--sm"
			menuPortalClassName="jam-select--sm-menu"
			placeholder="Select..."
			isClearable={false}
		/>
	);
};

export default SelectFilter;
