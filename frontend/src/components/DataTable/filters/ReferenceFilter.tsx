import React, { JSX, useMemo } from "react";
import { CustomSelect } from "../../rendering/widgets/CustomSelect";
import { ReferenceFilterConfig, ReferenceFilterValue } from "../FilterTypes";
import { DataContextValue } from "../../../contexts/DataContext";

interface Props {
	columnKey: string;
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
		<CustomSelect
			id="reference-filter"
			isMulti
			closeMenuOnSelect={false}
			options={options}
			value={selected}
			onChange={(picked) =>
				onChange({ type: "reference", selectedIds: ((picked as typeof selected) ?? []).map((p) => p.value) })
			}
			size="sm"
			placeholder="Select..."
			isClearable={false}
		/>
	);
};

export default ReferenceFilter;
