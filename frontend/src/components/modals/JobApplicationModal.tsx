import React, { useCallback, useMemo, useState } from "react";
import GenericModal from "./GenericModal/GenericModal";
import { formFields, useFormOptions } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { DataModalProps } from "./AggregatorModal";
import { ApplicationData } from "../../services/Schemas";

interface JobApplicationModalProps extends DataModalProps {
	jobId?: string | number | null;
}

export const JobApplicationModal: React.FC<JobApplicationModalProps> = ({
	show,
	onHide,
	data,
	id,
	onSuccess,
	onDelete,
	submode = "view",
	size = "lg",
	jobId = null,
}) => {
	// Track job options for the dropdown
	const { jobs, aggregators, openAggregatorModal, renderAggregatorModal } = useFormOptions(["jobs", "aggregators"]);
	const filteredJobs = jobs.filter(
		(job: any) => !job.data.job_application || job.data.job_application.id === data?.id,
	);

	// Add state to track current form data for conditional fields
	const [currentFormData, setCurrentFormData] = useState<Record<string, any>>({});

	// Handler for form data changes
	const handleFormDataChange = useCallback((newFormData: Record<string, any>) => {
		setCurrentFormData((prev) => ({
			...prev,
			...newFormData,
		}));
	}, []);

	const formFieldsArray = useMemo(() => {
		return [
			[formFields.applicationDate(), formFields.applicationStatus()],
			...(!jobId ? [formFields.job(filteredJobs)] : []),
			[
				formFields.applicationVia(),
				...(currentFormData?.applied_via === "aggregator"
					? [formFields.aggregator(aggregators, openAggregatorModal, { required: true })]
					: []),
			],
			formFields.url(),
			formFields.note({
				placeholder: "Add notes about your application process, interview details, etc...",
			}),
		];
	}, [currentFormData.applied_via, openAggregatorModal, jobId, filteredJobs, aggregators]);

	const viewFieldsArray = [
		[viewFields.date(), viewFields.status()],
		[viewFields.job(), viewFields.appliedVia()],
		[viewFields.url({ label: "Application URL" })],
		viewFields.note(),
		viewFields.interviews(),
		viewFields.updates(),
	];

	const fields = useMemo(
		() => ({
			form: formFieldsArray,
			view: viewFieldsArray,
		}),
		[formFieldsArray],
	);

	const transformFormData = (data: ApplicationData) => {
		return {
			date: new Date(data.date).toISOString(),
			url: data.url?.trim() || null,
			status: data.status,
			job_id: data.job_id,
			applied_via: data.applied_via,
			aggregator_id: data.aggregator_id,
			note: data.note?.trim() || null,
		};
	};

	return (
		<>
			<GenericModal
				show={show}
				onHide={onHide}
				submode={submode}
				itemName="Job Application"
				size={size}
				data={data || {}}
				id={id}
				fields={fields}
				endpoint="jobapplications"
				onSuccess={onSuccess}
				onDelete={onDelete}
				transformFormData={transformFormData}
				onFormDataChange={handleFormDataChange}
			/>

			{renderAggregatorModal()}
		</>
	);
};
