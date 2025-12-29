import React, { forwardRef, useImperativeHandle, useState } from "react";
import { Modal } from "react-bootstrap";
import { useAlert } from "../../contexts/AlertContext";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { getContactOptions, GroupedSelectOption } from "../rendering/form/FormOptions";
import { JobData, PersonData } from "../../services/Schemas";
import { useAuth } from "../../contexts/AuthContext";
import { Errors, FormField, SyntheticEvent } from "../rendering/widgets/WidgetRenders";
import { ModalFormField } from "../rendering/form/FormRenders";
import { areDifferent } from "../../utils/Utils";
import "./DataModal/DataModal.css";
import { ActionButton } from "../rendering/form/ActionButton";

export interface FollowUpModalHandle {
	show: (job: JobData) => void;
}

export interface FormData {
	body: string;
	contact: number;
	subject: string;
}

export function jobFollowUpEmail(hiringManager: string, jobTitle: string, yourName: string) {
	return `Hi ${hiringManager},

I hope you are well. I am writing to follow up on my application for the ${jobTitle} position and to kindly ask if there have been any updates regarding the recruitment process.

Thank you for your time and consideration.

Best regards,

${yourName}`;
}

const FollowUpModal = forwardRef<FollowUpModalHandle>((_, ref) => {
	const defaultFormData: FormData = {
		body: "",
		subject: "",
		contact: 0,
	};
	const [internalShow, setInternalShow] = useState(false);
	const [currentJob, setCurrentJob] = useState<JobData | null>(null);
	const [originalFormData, setOriginalFormData] = useState<FormData>(defaultFormData);
	const [formData, setFormData] = useState<FormData>(defaultFormData);
	const [contactOptions, setContactOptions] = useState<GroupedSelectOption[]>([]);
	const { showConfirm } = useAlert();
	const [errors, setErrors] = useState<Errors>({});
	const dataContext: DataContextValue = useDataContext();
	const { currentUser } = useAuth();

	useImperativeHandle(ref, () => ({
		show: (job: JobData): void => {
			setCurrentJob(job);
			setContactOptions(getContactOptions(dataContext, job));
			const formData: FormData = transformInputData(job);
			setFormData(formData);
			setOriginalFormData(formData);
			setInternalShow(true);
		},
	}));

	const generateEmailBody = (contact: PersonData | undefined, job: JobData): string => {
		return jobFollowUpEmail(contact?.first_name || "[Contact Name]", job?.title || "[Job Title]", "[Your Name]");
	};

	const generateEmailSubject = (job: JobData): string => {
		return `Follow Up on My Application for ${job?.title || "[Job Title]"}`;
	};

	const transformInputData = (data: JobData): FormData => {
		const contactOptions: GroupedSelectOption[] = getContactOptions(dataContext, data);
		const optionValue: string = contactOptions[0]?.options[0]?.value || "";
		const contact: PersonData | undefined = dataContext.persons.find(
			(person: PersonData): boolean => person.id === parseInt(optionValue),
		);
		return {
			contact: parseInt(optionValue || "0"),
			body: generateEmailBody(contact, data),
			subject: generateEmailSubject(data),
		};
	};

	const hasUnsavedChanges = (): boolean => {
		const keys: string[] = Object.keys(formData);
		return keys.some((key: string): boolean => {
			return areDifferent(formData[key as keyof FormData], originalFormData[key as keyof FormData]);
		});
	};

	const handleChange = (e: SyntheticEvent): void => {
		setFormData(
			(prev: FormData): FormData => ({
				...prev,
				[e.target.name]: e.target.value,
			}),
		);
		if (e.target.name === "contact" && currentJob) {
			const contact: PersonData | undefined = dataContext.persons.find(
				(person: PersonData): boolean => person.id === parseInt(e.target.value),
			);
			setFormData(
				(prev: FormData): FormData => ({
					...prev,
					body: generateEmailBody(contact, currentJob),
				}),
			);
		}
		if (errors[e.target.name]) {
			setErrors((prev: Errors) => ({ ...prev, [e.target.name]: "" }));
		}
	};

	const handleCloseWithConfirmation = async (): Promise<void> => {
		if (hasUnsavedChanges()) {
			const confirmed = await showConfirm({
				title: "Close Modal?",
				message: "Are you sure you want to close this modal?",
				confirmText: "Close",
				cancelText: "Cancel",
			});
			if (!confirmed) {
				return;
			}
		}
		setInternalShow(false);
	};

	const hide = (): void => {
		setInternalShow(false);
	};

	const selectField: ModalFormField = {
		type: "select",
		name: "contact",
		label: "Contact",
		options: contactOptions,
	};

	const bodyField: ModalFormField = {
		type: "textarea",
		name: "body",
		label: "Email Body",
		placeholder: "Enter your follow up email here...",
		rows: 10,
	};

	const subjectField: ModalFormField = {
		type: "text",
		name: "subject",
		label: "Email Subject",
		placeholder: "Enter the email subject here...",
	};

	const handleSend = (): void => {
		const contact: PersonData | undefined = dataContext.persons.find(
			(person: PersonData): boolean => person.id === formData.contact,
		);

		const emailAddress = contact?.email || "";
		const subject = encodeURIComponent(formData.subject);
		const body = encodeURIComponent(formData.body);

		window.location.href = `mailto:${emailAddress}?subject=${subject}&body=${body}`;
	};

	return (
		<Modal show={internalShow} onHide={handleCloseWithConfirmation} centered={true} size={"lg"}>
			<Modal.Header closeButton>
				<Modal.Title>Follow Up Email Generator</Modal.Title>
			</Modal.Header>
			<Modal.Body>
				{FormField(selectField, formData, handleChange, errors, currentUser)}
				{FormField(subjectField, formData, handleChange, errors, currentUser)}
				{FormField(bodyField, formData, handleChange, errors, currentUser)}
			</Modal.Body>
			<Modal.Footer>
				<div className="modal-buttons-container">
					<ActionButton variant="secondary" onClick={hide} defaultText={"Close"} fullWidth={true} />
					<ActionButton variant="primary" onClick={handleSend} defaultText={"Send"} fullWidth={true} />
				</div>
			</Modal.Footer>
		</Modal>
	);
});

export default FollowUpModal;
