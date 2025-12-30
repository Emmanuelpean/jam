import React, { forwardRef, useImperativeHandle, useState } from "react";
import { Button, ButtonGroup, Dropdown, Modal } from "react-bootstrap";
import { useAlert } from "../../contexts/AlertContext";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { GroupedSelectOption, useFormOptions } from "../rendering/form/FormOptions";
import { CompanyData, JobData, PersonData } from "../../services/Schemas";
import { useAuth } from "../../contexts/AuthContext";
import { Errors, FormField, SyntheticEvent } from "../rendering/widgets/WidgetRenders";
import { ModalFormField } from "../rendering/form/FormRenders";
import { areDifferent } from "../../utils/Utils";
import "./FollowUpModal.css";

export interface FollowUpModalHandle {
	show: (job: JobData, person?: PersonData) => void;
}

export interface FormData {
	body: string;
	contactId: number;
	subject: string;
}

type mailClient = "default" | "gmail" | "outlook";

export function jobFollowUpEmail(
	hiringManager: string,
	jobTitle: string,
	yourName: string,
	company: string | null = null,
): string {
	company = company ? ` at ${company}` : "";
	return `Hi ${hiringManager},

I hope you are well. I am writing to follow up on my application for the ${jobTitle} position${company} and to kindly ask if there have been any updates regarding the recruitment process.

Thank you for your time and consideration.

Best regards,

${yourName}`;
}

const FollowUpModal = forwardRef<FollowUpModalHandle>((_, ref) => {
	const defaultFormData: FormData = {
		body: "",
		subject: "",
		contactId: 0,
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
	const { getContactOptions } = useFormOptions();

	useImperativeHandle(ref, () => ({
		show: (job: JobData, person?: PersonData): void => {
			setCurrentJob(job);
			setContactOptions(getContactOptions(job));
			const formData: FormData = transformInputData(job, person);
			setFormData(formData);
			setOriginalFormData(formData);
			setInternalShow(true);
		},
	}));

	const generateEmailBody = (contact: PersonData | undefined, job: JobData): string => {
		let companyString: string | null = null;
		if (contact?.is_recruiter && contact.company_id !== job.company_id) {
			companyString =
				dataContext.companies.find((c: CompanyData): boolean => c.id === contact?.company_id)?.name ||
				"[Company Name]";
		}
		return jobFollowUpEmail(
			contact?.first_name || "[Contact Name]",
			job?.title || "[Job Title]",
			currentUser?.name || "[Your Name]",
			companyString,
		);
	};

	const generateEmailSubject = (job: JobData): string => {
		return `Follow Up on My Application for the ${job?.title || "[Job Title]"} position`;
	};

	const transformInputData = (data: JobData, person?: PersonData): FormData => {
		const contactOptions: GroupedSelectOption[] = getContactOptions(data);

		// Use provided person if available, otherwise fall back to first option
		let contactId: number;
		let contact: PersonData | undefined;

		if (person) {
			contactId = person.id;
			contact = person;
		} else {
			const optionValue: string =
				contactOptions[0]?.options[0]?.value || contactOptions[1]?.options[0]?.value || "";
			contactId = parseInt(optionValue || "0");
			contact = dataContext.persons.find((p: PersonData): boolean => p.id === contactId);
		}

		return {
			contactId: contactId,
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
		if (e.target.name === "contactId" && currentJob) {
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
		name: "contactId",
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

	const buildEmailUrl = (service: mailClient): string => {
		const contact: PersonData | undefined = dataContext.persons.find(
			(person: PersonData): boolean => person.id === formData.contactId,
		);

		const emailAddress: string = contact?.email || "";
		const subject: string = encodeURIComponent(formData.subject);
		const body: string = encodeURIComponent(formData.body);

		switch (service) {
			case "gmail":
				return `https://mail.google.com/mail/?view=cm&fs=1&to=${emailAddress}&su=${subject}&body=${body}`;
			case "outlook":
				return `https://outlook.office.com/mail/deeplink/compose?to=${emailAddress}&subject=${subject}&body=${body}`;
			case "default":
			default:
				return `mailto:${emailAddress}?subject=${subject}&body=${body}`;
		}
	};

	const createUpdate = async (): Promise<void> => {
		const result: boolean = await showConfirm({
			title: "Create Update?",
			message: "Have you sent the follow up email? An update will be created for this job.",
			confirmText: "Yes",
			cancelText: "No",
		});
		if (result) {
			dataContext
				.addEntity("jobApplicationUpdate", {
					type: "sent",
					job_id: currentJob?.id,
					note: `Follow up email sent to ${formData.contactId}`,
					date: new Date().toISOString(),
				})
				.then((): void => {
					hide();
				});
		}
	};

	const handleSend = (service: mailClient): void => {
		window.open(buildEmailUrl(service), "_blank", "noopener,noreferrer");
		createUpdate().then((): void => {});
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
			<Modal.Footer className={"modal-footer"}>
				<div className={"modal-buttons-container"}>
					<div style={{ width: "100%" }}>
						<Button
							style={{ width: "100%" }}
							variant="secondary"
							onClick={handleCloseWithConfirmation}
							className="flex-fill"
						>
							Close
						</Button>
					</div>
					<div style={{ width: "100%" }}>
						<Dropdown
							as={ButtonGroup}
							className="email-service-dropdown flex-fill"
							style={{ width: "100%" }}
						>
							<Button variant="primary" onClick={() => handleSend("default")}>
								<i className="bi bi-send-fill me-2"></i>
								Send Email
							</Button>
							<Dropdown.Toggle split variant="primary" id="dropdown-split-email" />
							<Dropdown.Menu align="end" className="email-dropdown-menu">
								<Dropdown.Item onClick={() => handleSend("default")} className="email-dropdown-item">
									<i className="bi bi-envelope-fill me-2"></i>
									Default Email Client
								</Dropdown.Item>
								<Dropdown.Divider />
								<Dropdown.Item onClick={() => handleSend("gmail")} className="email-dropdown-item">
									<i className="bi bi-google me-2"></i>
									Send with Gmail
								</Dropdown.Item>
								<Dropdown.Item onClick={() => handleSend("outlook")} className="email-dropdown-item">
									<i className="bi bi-microsoft me-2"></i>
									Send with Outlook
								</Dropdown.Item>
							</Dropdown.Menu>
						</Dropdown>
					</div>
				</div>
			</Modal.Footer>
		</Modal>
	);
});

export default FollowUpModal;
