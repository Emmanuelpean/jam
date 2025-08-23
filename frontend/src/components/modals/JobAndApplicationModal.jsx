import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import GenericModal from "./GenericModal/GenericModal";
import useGenericAlert from "../../hooks/useGenericAlert.ts";
import { filesApi } from "../../services/Api.ts";
import { fileToBase64 } from "../../utils/FileUtils.ts";
import { formFields, useFormOptions } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { useAuth } from "../../contexts/AuthContext.tsx";
import AlertModal from "./AlertModal";
import { InterviewModal } from "./InterviewModal";
import { getApplicationStatusBadgeClass } from "../rendering/view/ViewRenders";

export const JobAndApplicationModal = ({
	show,
	onHide,
	data,
	onJobSuccess,
	onApplicationSuccess,
	onJobDelete,
	onApplicationDelete,
	submode = "view",
	size = "xl",
}) => {
	const { token } = useAuth();
	const { alertState, showError, hideAlert } = useGenericAlert();
	console.log("JobAndApplicationModal: ", data, data?.job_application);

	// File states for job application
	const [fileStates, setFileStates] = useState({
		cv: null,
		cover_letter: null,
	});

	// Track current form data for conditional fields
	const [currentApplicationFormData, setCurrentApplicationFormData] = useState({});

	// Create a ref to store the original file states
	const originalFileStatesRef = useRef({
		cv: null,
		cover_letter: null,
	});

	// Get form options for both job and application
	const {
		companies,
		locations,
		keywords,
		persons,
		jobs,
		aggregators,
		openCompanyModal,
		openLocationModal,
		openKeywordModal,
		openPersonModal,
		openAggregatorModal,
		renderCompanyModal,
		renderLocationModal,
		renderKeywordModal,
		renderPersonModal,
		renderAggregatorModal,
	} = useFormOptions(["companies", "locations", "keywords", "persons", "jobs", "aggregators"]);

	// Initialize file states when modal opens or data changes
	useEffect(() => {
		if (show) {
			const initialFileStates = {
				cv: data?.job_application?.cv || null,
				cover_letter: data?.job_application?.cover_letter || null,
			};
			setFileStates(initialFileStates);
			originalFileStatesRef.current = { ...initialFileStates };
			setCurrentApplicationFormData(data?.job_application || {});
		}
	}, [show, data?.job_application?.cv, data?.job_application?.cover_letter, data?.job_application]);

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

	// Handler for application form data changes
	const handleApplicationFormDataChange = useCallback(
		(newFormData) => {
			setCurrentApplicationFormData((prev) => ({
				...prev,
				...newFormData,
			}));

			// Check if the form data has been reset to original data (indicating a cancel operation)
			if (data?.job_application && newFormData) {
				const formDataKeys = Object.keys(newFormData);
				const isFormReset =
					formDataKeys.length > 0 &&
					formDataKeys.every((key) => {
						const newValue = newFormData[key];
						const originalValue = data?.job_application[key];

						// Handle different data types appropriately
						if (newValue === originalValue) return true;
						if (newValue === "" && (originalValue === null || originalValue === undefined)) return true;
						if ((newValue === null || newValue === undefined) && originalValue === "") return true;

						// For dates, convert to comparable format
						if (key.includes("date") || key.includes("Date")) {
							try {
								const newDate = new Date(newValue).getTime();
								const origDate = new Date(originalValue).getTime();
								return newDate === origDate;
							} catch {
								return false;
							}
						}

						return false;
					});

				if (isFormReset) {
					console.log("Form reset detected - restoring original file states:", originalFileStatesRef.current);
					setFileStates({ ...originalFileStatesRef.current });
				}
			}
		},
		[data?.job_application],
	);

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

	// Job form fields
	const jobFormFieldsArray = [
		formFields.jobTitle(),
		[formFields.company(companies, openCompanyModal), formFields.location(locations, openLocationModal)],
		[formFields.keywords(keywords, openKeywordModal), formFields.contacts(persons, openPersonModal)],
		[formFields.attendanceType(), formFields.url({ label: "Job URL" })],
		[formFields.salaryMin(), formFields.salaryMax(), formFields.personalRating()],
		formFields.description(),
		formFields.note(),
	];

	const jobViewFieldsArray = [
		[viewFields.title({ isTitle: true })],
		[viewFields.company(), viewFields.location()],
		viewFields.description(),
		[viewFields.salaryRange(), viewFields.personalRating()],
		viewFields.url({ label: "Job URL" }),
		[viewFields.keywords(), viewFields.persons()],
	];

	// Job application form fields
	const filteredJobs = jobs.filter(
		(job) =>
			!job.data?.job_application ||
			job.data?.job_application?.id === data?.job_application?.id ||
			job.data.id === data?.id,
	);

	const applicationFormFieldsArray = useMemo(() => {
		return [
			[formFields.applicationDate(), formFields.applicationStatus()],
			// Only show job selector if we don't have data (i.e., not created from a specific job)
			...(data ? [] : [formFields.job(filteredJobs)]),
			[
				formFields.applicationVia(),
				...(currentApplicationFormData?.applied_via === "aggregator"
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
	}, [
		currentApplicationFormData.applied_via,
		fileStates.cv,
		fileStates.cover_letter,
		handleFileChange,
		handleFileRemove,
		openAggregatorModal,
		data,
		filteredJobs,
		aggregators,
	]);

	const applicationViewFieldsArray = useMemo(() => {
		const baseFields = [
			[viewFields.date(), viewFields.status()],
			[viewFields.appliedVia(), viewFields.files()],
			[viewFields.url({ label: "Application URL" })],
			viewFields.note(),
		];

		if (data?.job_application?.id) {
			baseFields.push(viewFields.interviews());
			baseFields.push(viewFields.updates());
		}

		return baseFields;
	}, [data?.job_application?.id]);

	// Custom submit handler for job application to process files
	const handleApplicationCustomSubmit = async (formElement, submitCallback) => {
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

			// If we have data, set the job_id automatically
			if (data?.id) {
				transformedData.job_id = data.id;
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
						transformedData[idFieldName] = await processFile(currentFile);
					} catch (fileError) {
						console.error(`Error processing file ${fieldName}:`, fileError);
						throw new Error(`Failed to process ${fieldName}: ${fileError.message}`);
					}
				} else if (currentFile && typeof currentFile === "object" && currentFile.id) {
					// Existing file from database - keep the ID
					transformedData[idFieldName] = currentFile.id;
				} else {
					// No file state for this field - explicitly set to null for updates
					if (submode === "edit" && data?.job_application) {
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

	// Transform functions
	const transformJobData = (data) => {
		return {
			title: data.title.trim(),
			description: data.description?.trim() || null,
			note: data.note?.trim() || null,
			url: data.url?.trim() || null,
			salary_min: data.salary_min || null,
			salary_max: data.salary_max || null,
			personal_rating: data.personal_rating || null,
			company_id: data.company_id || null,
			location_id: data.location_id || null,
			keywords: data.keywords?.map((item) => item.id || item) || [],
			contacts: data.contacts?.map((item) => item.id || item) || [],
		};
	};

	const transformApplicationData = (data) => {
		return {
			date: new Date(data.date).toISOString(),
			url: data.url?.trim() || null,
			status: data.status,
			job_id: data.job_id || data?.id, // Use data.id if available
			applied_via: data.applied_via,
			aggregator_id: data.aggregator_id,
			note: data.note?.trim() || null,
			cv_id: data.cv_id,
			cover_letter_id: data.cover_letter_id,
		};
	};

	// Determine application tab title and submode
	const applicationTabTitle = data?.job_application ? (
		<>
			Job Application{" "}
			<span className={`badge ${getApplicationStatusBadgeClass(data.job_application.status)} badge`}>
				{data.job_application.status}
			</span>
		</>
	) : (
		"Create Job Application"
	);
	const applicationSubmode = data?.job_application ? submode : "add";

	// Define tabs
	const tabs = [
		{
			key: "job",
			title: "Job Details",
			mode: "formview",
			submode: submode,
			data: data || {},
			fields: {
				form: jobFormFieldsArray,
				view: jobViewFieldsArray,
			},
			endpoint: "jobs",
			onSuccess: onJobSuccess,
			onDelete: onJobDelete,
			transformFormData: transformJobData,
		},
		{
			key: "application",
			title: applicationTabTitle,
			mode: "formview",
			submode: applicationSubmode,
			data: data?.job_application || {},
			fields: {
				form: applicationFormFieldsArray,
				view: applicationViewFieldsArray,
			},
			endpoint: "jobapplications",
			onSuccess: onApplicationSuccess,
			onDelete: onApplicationDelete,
			transformFormData: transformApplicationData,
			customSubmitHandler: handleApplicationCustomSubmit,
			onFormDataChange: handleApplicationFormDataChange,
		},
	];

	return (
		<>
			<GenericModal
				show={show}
				onHide={onHide}
				itemName="Job & Application"
				size={size}
				tabs={tabs}
				defaultActiveTab="job"
			/>

			{/* Alert Modal for error messages */}
			<AlertModal alertState={alertState} hideAlert={hideAlert} />

			{renderCompanyModal()}
			{renderLocationModal()}
			{renderKeywordModal()}
			{renderPersonModal()}
			{renderAggregatorModal()}
		</>
	);
};

export const JobAndApplicationFormModal = (props) => {
	const submode = props.isEdit || props.interview?.id ? "edit" : "add";
	return <JobAndApplicationModal {...props} submode={submode} />;
};

export const JobAndApplicationViewModal = (props) => (
	<JobAndApplicationModal {...props} interview={props.item} submode="view" />
);
