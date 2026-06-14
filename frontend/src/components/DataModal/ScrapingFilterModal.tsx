import React, { forwardRef, JSX, useImperativeHandle, useRef, useState } from "react";
import { Button } from "react-bootstrap";
import DataModal, { DataModalHandle, Fields, GenericFormData, JamDataModalProps, ValidationErrors } from "./DataModal";
import { useFormFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { FilterVariant, ScrapingFilterData, ScrapingFilterTransform } from "../../services/schemas/Services";
import ScrapedJobsTable from "../DataTable/ScrapedJobTable";

interface ScrapingFilterModalProps extends JamDataModalProps {
	variant?: FilterVariant;
}

export const ScrapingFilterModal = forwardRef<DataModalHandle<ScrapingFilterData>, ScrapingFilterModalProps>(
	({ size = "lg", variant = "exclusion" }: ScrapingFilterModalProps, ref): JSX.Element => {
		const dataContext: DataContextValue = useDataContext();
		const isExclusion: boolean = variant === "exclusion";
		const ff = useFormFields();

		const internalRef = useRef<DataModalHandle<ScrapingFilterData>>(null);
		useImperativeHandle(ref, () => ({
			showView: (data: ScrapingFilterData): void | undefined => internalRef.current?.showView(data),
			showEdit: (data: ScrapingFilterData): void | undefined => internalRef.current?.showEdit(data),
			showAdd: (data: any): void | undefined => internalRef.current?.showAdd(data),
			showImport: (data: ScrapingFilterData): void | undefined => internalRef.current?.showImport(data),
		}));

		const [queryParams, setQueryParams] = useState<Record<string, string> | null>(null);
		const [reloadTrigger, setReloadTrigger] = useState(0);

		const formFieldsArray: Fields = [
			ff.scrapingFilterTypeField(),
			ff.scrapingFilterOperatorField(),
			ff.valueField({ type: "input", placeholder: "Enter a value" }),
			ff.caseSensitiveField(),
		];

		const viewFieldsArray: Fields = [
			modalViewFields.scrapingFilterName({ isTitle: true }),
			modalViewFields.caseSensitive(),
		];

		const fields = { form: formFieldsArray, view: viewFieldsArray };

		const customValidation = (formData: ScrapingFilterData): ValidationErrors => {
			const errors: ValidationErrors = {};
			const filters: ScrapingFilterData[] = isExclusion
				? dataContext.scrapingExclusionFilters
				: dataContext.scrapingFavouriteFilters;
			const duplicates: ScrapingFilterData[] = filters.filter(
				(filter: ScrapingFilterData): boolean =>
					filter.type === formData.type &&
					filter.operator === formData.operator &&
					filter.value.trim().toLowerCase() === formData.value.trim().toLowerCase() &&
					filter.case_sensitive === formData.case_sensitive &&
					filter.id !== formData?.id
			);
			if (duplicates.length > 0) {
				errors.type = errors.operator = errors.value = `A filter with these values already exists`;
			}
			return errors;
		};

		const canEdit = isExclusion
			? (formData: ScrapingFilterData): string =>
					formData?.filtered_jobs?.length > 0
						? "Filters that have been applied to scraped jobs cannot be edited."
						: ""
			: undefined;

		const canDelete = isExclusion
			? (formData: ScrapingFilterData): string =>
					formData?.filtered_jobs?.length > 0
						? "Filters that have been applied to scraped jobs cannot be deleted."
						: ""
			: undefined;

		const transformFormData = (formData: ScrapingFilterData): ScrapingFilterTransform => ({
			type: formData.type,
			operator: formData.operator,
			value: formData.value.trim(),
			case_sensitive: formData.case_sensitive,
		});

		return (
			<DataModal<ScrapingFilterData>
				ref={internalRef}
				size={size}
				fields={fields}
				entityType={isExclusion ? "scrapingExclusionFilter" : "scrapingFavouriteFilter"}
				validation={customValidation}
				transformFormData={transformFormData}
				formExtraContent={(formData: GenericFormData): JSX.Element | null => {
					const canTest: boolean =
						formData?.type && formData?.operator && (formData?.value ?? "").trim().length > 0;
					const handleTest = (): void => {
						if (!canTest) return;
						setQueryParams({
							filter_type: formData.type,
							filter_operator: formData.operator,
							filter_value: formData.value.trim(),
							case_sensitive: String(formData.case_sensitive ?? false),
						});
						setReloadTrigger((prev: number): number => prev + 1);
					};
					return (
						<div className="mt-3">
							<Button
								id="scraping-filter-test-btn"
								size="sm"
								variant="outline-primary"
								style={{ width: "100%", marginBottom: "10px" }}
								onClick={handleTest}
								disabled={!canTest}
							>
								<i className="bi bi-play-fill me-1" />
								Test
							</Button>
							{queryParams && (
								<ScrapedJobsTable
									endpoint={"scraping-exclusion-filters/preview"}
									queryParamsOverride={queryParams}
									reloadTrigger={reloadTrigger}
								/>
							)}
						</div>
					);
				}}
				{...(isExclusion && {
					additionalFields: [modalViewFields.accordionScrapedJobTable()],
					canEdit,
					canDelete,
				})}
				showDeactivate={true}
			/>
		);
	}
);
