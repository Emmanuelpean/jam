import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import GenericModal from "../GenericModal";
import useGenericAlert from "../../../hooks/useGenericAlert";
import { filesApi, jobApplicationsApi } from "../../../services/api";
import { fileToBase64 } from "../../../utils/FileUtils";
import { formFields, useFormOptions } from "../../rendering/FormRenders";
import { viewFields } from "../../rendering/ViewRenders";
import { useAuth } from "../../../contexts/AuthContext";
import AlertModal from "../alert/AlertModal";
import InterviewsTable from "../../tables/InterviewTable";
import { JobModal } from "../job/JobModal";

export const JobApplicationModal = ({
	show,
	onHide,
	data,
	onSuccess,
	onDelete,
	endpoint = "jobapplications",
	submode = "view",
	size = "lg",
}) => {
	console.log(data);
	const { token } = useAuth();
	const { alertState, showError, hideAlert } = useGenericAlert();
	const formRef = useRef();

	// Track file states independently
	const [fileStates, setFileStates] = useState({
		cv: null,
		cover_letter: null,
	});

	// Track interview data
	const [interviews, setInterviews] = useState([]);
	const [setRefreshInterviews] = useState(0);

	// Track job options for the dropdown
	const { jobs, aggregators, openAggregatorModal, renderAggregatorModal } = useFormOptions();
	const filteredJobs = jobs.filter((job) => !job.job_application || job.job_application.id === data?.id);

	// Add state to track current form data for conditional fields
	const [currentFormData, setCurrentFormData] = useState({});

	// Initialize file states when modal opens or data changes
	useEffect(() => {
		if (show) {
			setFileStates({
				cv: data?.cv || null,
				cover_letter: data?.cover_letter || null,
			});
			setInterviews(data?.interviews || []);
			// Initialize form data state
			setCurrentFormData(data);
		}
	}, [show, data?.cv, data?.cover_letter, data?.interviews, data]);

	const handleInterviewChange = () => {
		setRefreshInterviews((prev) => prev + 1);
	};

	const handleFileDownload = async (fileObject) => {
		await filesApi.download(fileObject.id, fileObject.filename, token);
	};

	// Custom file change handler that tracks file state
	const handleFileChange = useCallback((fieldName, file) => {
		console.log(`File changed for ${fieldName}:`, file);
		setFileStates((prev) => ({
			...prev,
			[fieldName]: file,
		}));
	}, []);

	// Custom file remove handler
	const handleFileRemove = useCallback((fieldName) => {
		console.log(`File removed for ${fieldName}`);
		setFileStates((prev) => ({
			...prev,
			[fieldName]: null,
		}));
	}, []);

	// Helper function to normalize content for comparison
	const normalizeFileContent = (content) => {
		if (!content) return "";

		if (content.startsWith("data:")) {
			const commaIndex = content.indexOf(",");
			return commaIndex !== -1 ? content.substring(commaIndex + 1) : content;
		}
		return content;
	};

	// Process a single file: check for existing or create new
	const processFile = async (file) => {
		console.log(`Processing file ${file.name}...`);
		if (!file || !(file instanceof File)) {
			return null;
		}

		try {
			const base64Content = await fileToBase64(file);
			const normalizedNewContent = normalizeFileContent(base64Content);

			// Check for existing files
			const files = await filesApi.getAll(token);
			const existingFile = files.find((f) => {
				const normalizedExistingContent = normalizeFileContent(f.content);
				return normalizedExistingContent === normalizedNewContent;
			});

			if (existingFile) {
				console.log(`File ${file.name} already exists, reusing ID: ${existingFile.id}`);
				return existingFile.id;
			} else {
				// Create new file entry
				console.log(`Creating new file entry for: ${file.name}`);
				const fileData = {
					filename: file.name,
					content: normalizedNewContent,
					type: file.type,
					size: file.size,
				};
				const newFile = await filesApi.create(fileData, token);
				console.log(`File created with ID: ${newFile.id}`);
				return newFile.id;
			}
		} catch (error) {
			console.error(`Error processing file ${file.name}:`, error);

			// Check if error has validation details
			if (error.data && error.data.detail) {
				if (Array.isArray(error.data.detail)) {
					const messages = error.data.detail.map((err) => err.msg || JSON.stringify(err)).join(", ");
					throw new Error(`File validation error: ${messages}`);
				} else if (typeof error.data.detail === "string") {
					throw new Error(error.data.detail);
				} else {
					throw new Error(`File processing failed: ${JSON.stringify(error.data.detail)}`);
				}
			}
			throw error;
		}
	};

	const createInterviewsTableField = () => {
		if (data?.id) {
			return {
				name: "interviews_table",
				key: "interviews_table",
				type: "table",
				columnClass: "col-12", // Full width
				render: () => (
					<InterviewsTable
						interviews={interviews}
						jobApplicationId={data.id}
						onInterviewChange={handleInterviewChange}
					/>
				),
			};
		}
		return null;
	};

	// Form fields for editing
	const formFieldsArray = useMemo(() => {
		const baseFields = [
			[formFields.applicationDate(), formFields.applicationStatus()],
			[formFields.job(filteredJobs)],
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

		if (data?.id) {
			baseFields.push(viewFields.interviews());
		}

		return baseFields;
	}, [
		currentFormData?.applied_via,
		fileStates.cv,
		fileStates.cover_letter,
		handleFileChange,
		handleFileRemove,
		openAggregatorModal,
		submode,
		data?.id,
		interviews,
		handleInterviewChange,
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
	}, [submode, data?.id, interviews, handleInterviewChange]);

	const fields = useMemo(
		() => ({
			form: formFieldsArray,
			view: viewFieldsArray,
		}),
		[formFieldsArray, viewFieldsArray],
	);

	// Add a handler to update currentFormData when form changes
	const handleFormDataChange = useCallback((newFormData) => {
		setCurrentFormData((prev) => ({
			...prev,
			...newFormData,
		}));
	}, []);

	// Custom submit handler to process files before form submission
	const handleCustomSubmit = async (formElement, submitCallback) => {
		try {
			// Get form data from the actual form element
			const formData = new FormData(formElement);
			const transformedData = {};

			// Process regular form fields first
			for (const [key, value] of formData.entries()) {
				if (typeof value === "string") {
					transformedData[key] = value;
				}
			}

			// Check for existing job application if creating new and job_id is provided
			if (submode === "add" && transformedData.job_id) {
				try {
					const { jobApplicationsApi } = await import("../../../services/api");
					const existingApps = await jobApplicationsApi.getAll(token, { job_id: transformedData.job_id });

					if (existingApps && existingApps.length > 0) {
						showError({
							title: "Job Application Already Exists",
							message:
								"You already have an application for this job. Please edit the existing application instead.",
							size: "md",
						});
						return; // Stop submission
					}
				} catch (checkError) {
					console.error("Error checking existing applications:", checkError);
				}
			}

			// Process file states instead of relying on form files
			const fileFields = ["cv", "cover_letter"];

			for (const fieldName of fileFields) {
				const currentFile = fileStates[fieldName];
				const idFieldName = `${fieldName}_id`;

				if (currentFile === null) {
					// File was explicitly removed - send null to backend
					transformedData[idFieldName] = null;
				} else if (currentFile instanceof File) {
					// New file uploaded
					try {
						const fileId = await processFile(currentFile);
						transformedData[idFieldName] = fileId;
					} catch (fileError) {
						console.error(`Error processing file ${fieldName}:`, fileError);
						throw new Error(`Failed to process ${fieldName}: ${fileError.message}`);
					}
				} else if (currentFile && typeof currentFile === "object" && currentFile.id) {
					// Existing file from database - keep the ID
					transformedData[idFieldName] = currentFile.id;
				} else {
					// No file state for this field - explicitly set to null for updates
					if (submode === "edit") {
						transformedData[idFieldName] = null;
					}
					// For new records, don't set the field at all
				}
			}

			// Now submit the form with file IDs
			await submitCallback(transformedData);
		} catch (error) {
			console.error("Error processing files:", error);

			// Extract meaningful error message
			let errorMessage = "Failed to process uploaded files. Please try again.";
			if (error.message) {
				errorMessage = error.message;
			}

			showError({
				title: "File Processing Error",
				message: errorMessage,
				size: "md",
			});
			throw error; // Re-throw to prevent form submission
		}
	};

	// Data transformation function (synchronous - files already processed)
	const transformFormData = (data) => {
		return {
			date: new Date(data.date).toISOString(),
			url: data.url?.trim() || null,
			status: data.status,
			job_id: data.job_id,
			applied_via: data.applied_via,
			aggregator_id: data.aggregator_id,
			note: data.note?.trim() || null,
			cv_id: data.cv_id,
			cover_letter_id: data.cover_letter_id,
		};
	};

	return (
		<>
			<GenericModal
				ref={formRef}
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
				transformFormData={transformFormData}
				customSubmitHandler={submode !== "view" ? handleCustomSubmit : undefined}
				onFormDataChange={handleFormDataChange} // Remove the condition - always pass this
			/>

			{/* Alert Modal for error messages */}
			<AlertModal alertState={alertState} hideAlert={hideAlert} />

			{renderAggregatorModal()}
		</>
	);
};

export const JobApplicationFormModal = (props) => {
	const submode = props.isEdit || props.job?.id ? "edit" : "add";
	return <JobApplicationModal {...props} submode={submode} />;
};

export const JobApplicationViewModal = (props) => <JobApplicationModal {...props} submode="view" />;
