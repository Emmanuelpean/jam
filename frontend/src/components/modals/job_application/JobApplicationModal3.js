import React, { useCallback, useMemo, useState } from "react";
import GenericModal from "../GenericModal";
import { filesApi } from "../../../services/api";
import { formFields, useFormOptions } from "../../rendering/FormRenders";
import { viewFields } from "../../rendering/ViewRenders";
import { useAuth } from "../../../contexts/AuthContext";

export const JobApplicationModal = ({
	show,
	onHide,
	data,
	onSuccess,
	onDelete,
	endpoint = "job-applications", // or whatever your endpoint should be
	submode = "view",
	size = "lg",
}) => {
	const { token } = useAuth();
	const { jobs, aggregators, openAggregatorModal } = useFormOptions();
	const [currentFormData, setCurrentFormData] = useState({});
	const [fileStates, setFileStates] = useState({
		cv: null,
		cover_letter: null,
	});

	const handleFileDownload = async (fileObject) => {
		await filesApi.download(fileObject.id, fileObject.filename, token);
	};

	const handleFileChange = useCallback((fieldName, file) => {
		setFileStates((prev) => ({
			...prev,
			[fieldName]: file,
		}));
	}, []);

	const handleFileRemove = useCallback((fieldName) => {
		setFileStates((prev) => ({
			...prev,
			[fieldName]: null,
		}));
	}, []);

	const formFieldsArray = useMemo(() => {
		const baseFields = [
			[formFields.applicationDate(), formFields.applicationStatus()],
			[formFields.job(jobs)],
			[
				formFields.applicationVia(),
				...(currentFormData?.applied_via === "Aggregator"
					? [formFields.aggregator(aggregators, openAggregatorModal)]
					: []),
			],
			formFields.url(),
			formFields.note({
				placeholder: "Add notes about your application process, interview details, etc...",
			}),
			[
				{
					name: "cv",
					label: "CV/Resume",
					type: "drag-drop",
					value: fileStates.cv,
					onChange: (file) => handleFileChange("cv", file),
					onRemove: () => handleFileRemove("cv"),
					onOpenFile: handleFileDownload,
				},
				{
					name: "cover_letter",
					label: "Cover Letter",
					type: "drag-drop",
					value: fileStates.cover_letter,
					onChange: (file) => handleFileChange("cover_letter", file),
					onRemove: () => handleFileRemove("cover_letter"),
					onOpenFile: handleFileDownload,
				},
			],
		];

		return baseFields;
	}, [
		currentFormData?.applied_via,
		fileStates.cv,
		fileStates.cover_letter,
		handleFileChange,
		handleFileRemove,
		openAggregatorModal,
		jobs,
		aggregators,
	]);

	// View fields for display
	const viewFieldsArray = useMemo(() => {
		const baseFields = [
			[viewFields.date(), viewFields.status()],
			[viewFields.job(), viewFields.appliedVia()],
			[viewFields.url({ label: "Application URL" }), viewFields.files()],
			viewFields.note(),
		];

		if (data?.id) {
			baseFields.push(viewFields.interviews());
		}

		return baseFields;
	}, [data?.id]);

	const fields = useMemo(
		() => ({
			form: formFieldsArray,
			view: viewFieldsArray,
		}),
		[formFieldsArray, viewFieldsArray],
	);

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="formview"
			submode={submode}
			title="Job Application"
			size={size}
			data={data || {}}
			fields={fields}
			endpoint={endpoint}
			onSuccess={onSuccess}
			onDelete={onDelete}
		/>
	);
};

export const JobApplicationFormModal = (props) => {
	const submode = props.isEdit || props.data?.id ? "edit" : "add";
	return <JobApplicationModal {...props} submode={submode} />;
};

export const JobApplicationViewModal = (props) => {
	return <JobApplicationModal {...props} data={props.job} submode="view" />;
};
