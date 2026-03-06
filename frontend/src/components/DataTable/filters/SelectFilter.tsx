import React, { JSX } from "react";
import Select from "react-select";
import { SelectFilterConfig, SelectFilterValue } from "../FilterTypes";

interface Props {
	config: SelectFilterConfig;
	value: SelectFilterValue;
	onChange: (v: SelectFilterValue) => void;
}

const SelectFilter = ({ config, value, onChange }: Props): JSX.Element => {
	const options = config.options.map((opt) => ({ value: String(opt.value), label: opt.label }));
	const selected = options.filter((o) => value.selected.includes(o.value));

	return (
		<Select
			isMulti
			closeMenuOnSelect={false}
			options={options}
			value={selected}
			onChange={(picked) =>
				onChange({ type: "select", selected: (picked ?? []).map((p) => p.value) })
			}
			className="react-select-container react-select-container--sm"
			classNamePrefix="react-select"
			placeholder="Select..."
			menuPortalTarget={document.body}
			isClearable={false}
			styles={{
				menuPortal: (base) => ({ ...base, zIndex: 9999 }),
			}}
			classNames={{
				menuPortal: () => "react-select--sm-menu",
			}}
		/>
	);
};

export default SelectFilter;
