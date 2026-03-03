import React, { JSX, useMemo } from "react";
import Select from "react-select";
import { ReferenceFilterConfig, ReferenceFilterValue } from "../FilterTypes";
import { DataContextValue } from "../../../contexts/DataContext";

interface Props {
	config: ReferenceFilterConfig;
	value: ReferenceFilterValue;
	onChange: (v: ReferenceFilterValue) => void;
	dataContext: DataContextValue;
}

const ReferenceFilter = ({ config, value, onChange, dataContext }: Props): JSX.Element => {
	const entities: any[] = useMemo(
		() => (dataContext as any)[config.entityKey] ?? [],
		[dataContext, config.entityKey]
	);

	const labelKey = config.labelKey ?? "name";

	const options = useMemo(
		() =>
			entities.map((e) => ({
				value: String(e.id),
				label: String(e[labelKey] ?? e.id),
			})),
		[entities, labelKey]
	);

	const selected = options.filter((o) => value.selectedIds.includes(o.value));

	return (
		<Select
			isMulti
			options={options}
			value={selected}
			onChange={(picked) =>
				onChange({ type: "reference", selectedIds: (picked ?? []).map((p) => p.value) })
			}
			className="react-select-container filter-reference-select"
			classNamePrefix="react-select"
			placeholder="Select..."
			menuPortalTarget={document.body}
			isClearable={false}
		/>
	);
};

export default ReferenceFilter;
