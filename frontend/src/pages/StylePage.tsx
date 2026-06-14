import React from "react";
import {
	Accordion,
	Badge,
	Button,
	Card,
	Col,
	Container,
	Form,
	ProgressBar,
	Row,
	Spinner,
	Stack,
} from "react-bootstrap";
import { ModalFormField } from "../components/rendering/form/FormRenders";
import { Checkbox } from "../components/rendering/widgets/Checkbox";
import { HelpBubble } from "../components/HelpBubble/HelpBubble";
import { PasswordInput } from "../components/rendering/widgets/PasswordInput";
import { SalaryInput } from "../components/rendering/widgets/SalaryInput";
import { LocalDatetimeInput } from "../components/rendering/widgets/Datetime";
import { StarRating } from "../components/rendering/widgets/StarRating";
import { SelectInput } from "../components/rendering/widgets/SelectWidget";
import { Textarea } from "../components/rendering/widgets/TextArea";
import { Toggle } from "../components/rendering/widgets/Toggle";
import { UrlInput } from "../components/rendering/widgets/UrlInput";

/* -------------------------------- THEME TOGGLE -------------------------------- */

const ThemeToggle: React.FC = () => {
	const [isDark, setIsDark] = React.useState<boolean>(document.body.dataset.mode === "dark");

	const toggleTheme = () => {
		setIsDark(!isDark);
		if (!isDark) {
			document.body.dataset.mode = "dark";
		} else {
			document.body.dataset.mode = "light";
		}
	};

	return (
		<Form.Check
			type="switch"
			id="theme-switch"
			label={isDark ? "Dark mode" : "Light mode"}
			checked={isDark}
			onChange={toggleTheme}
		/>
	);
};

/* ------------------------------- SECTION WRAPPER ------------------------------- */

const Section: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
	<Card className="mb-4 shadow-sm border-0">
		<Card.Body>
			<h5 className="mb-3">{title}</h5>
			{children}
		</Card.Body>
	</Card>
);

/* ---------------------------------- PAGE ---------------------------------- */

export const StyleGuidePage: React.FC = () => {
	const [formData, setFormData] = React.useState<any>({
		checkbox: false,
		password: "",
		salary: "",
		rating: 0,
		datetime: "",
		date: "",
		select: "",
		textarea: "",
	});

	const handleChange = (event: any) => {
		const { name, value, checked, type } = event.target;
		setFormData((prev: any) => ({
			...prev,
			[name]: type === "checkbox" ? checked : value,
		}));
	};

	// Mock field definitions for custom widgets
	const checkboxField: ModalFormField = {
		key: "checkbox",
		label: "Custom Checkbox",
		type: "checkbox",
	};

	const passwordField: ModalFormField = {
		key: "password",
		label: "Password Input",
		type: "password",
		helpText: "Enter a secure password",
	};

	const salaryField: ModalFormField = {
		key: "salary",
		label: "Salary Input",
		type: "salary",
		placeholder: "Enter salary amount",
	};

	const ratingField: ModalFormField = {
		key: "rating",
		label: "Star Rating",
		type: "rating",
		maxRating: 5,
	};

	const datetimeField: ModalFormField = {
		key: "datetime",
		label: "DateTime Picker",
		type: "datetime-local",
	};

	const dateField: ModalFormField = {
		key: "date",
		label: "Date Picker",
		type: "date",
	};

	const selectField: ModalFormField = {
		key: "select",
		label: "Select Widget",
		type: "select",
		options: [
			{ value: "option1", label: "Option 1" },
			{ value: "option2", label: "Option 2" },
			{ value: "option3", label: "Option 3" },
		],
	};

	const textareaField: ModalFormField = {
		key: "textarea",
		label: "Text Area",
		type: "textarea",
		placeholder: "Enter multiple lines of text here...",
	};

	const urlField: ModalFormField = {
		key: "url",
		label: "URL Input",
		type: "url",
		placeholder: "Enter a valid URL",
	};

	return (
		<Container fluid className="py-4 main-content">
			<div className="d-flex justify-content-between align-items-center mb-4">
				<h2 className="mb-0">Design System / Style Guide</h2>
				<ThemeToggle />
			</div>

			{/* -------------------------------- BUTTONS -------------------------------- */}
			<Section title="Buttons">
				<Stack direction="horizontal" gap={3}>
					<Button variant="primary">Primary</Button>
					<Button variant="secondary">Secondary</Button>
					<Button variant="danger">Danger</Button>
					<Button variant="outline-primary">Outline</Button>
					<Button disabled>Disabled</Button>
				</Stack>
			</Section>

			{/* -------------------------------- BADGES -------------------------------- */}
			<Section title="Badges">
				<Stack direction="horizontal" gap={2}>
					<Badge bg="primary">Primary</Badge>
					<Badge bg="success">Success</Badge>
					<Badge bg="warning">Warning</Badge>
					<Badge bg="danger">Danger</Badge>
					<Badge bg="secondary">Secondary</Badge>
					<Badge bg="dark">Dark</Badge>
				</Stack>
			</Section>

			{/* -------------------------------- FORMS -------------------------------- */}
			<Section title="Forms">
				<Form>
					<Row className="g-3">
						<Col md={6}>
							<Form.Group>
								<Form.Label>Text input</Form.Label>
								<Form.Control placeholder="Placeholder text" />
							</Form.Group>
						</Col>

						<Col md={6}>
							<Form.Group>
								<Form.Label>Invalid input</Form.Label>
								<Form.Control isInvalid defaultValue="Invalid value" />
								<Form.Control.Feedback type="invalid">This field is invalid</Form.Control.Feedback>
							</Form.Group>
						</Col>
					</Row>
				</Form>
			</Section>

			{/* --------------------------- CUSTOM WIDGETS --------------------------- */}
			<Section title="Custom Widgets">
				<Form>
					<Row className="g-3">
						<Col md={4}>
							<Checkbox field={checkboxField} value={formData.checkbox} handleChange={handleChange} />
						</Col>
						<Col md={4}>
							<Toggle field={checkboxField} value={formData.checkbox} handleChange={handleChange} />
						</Col>

						<Col md={4}>
							<Form.Group>
								<Form.Label>
									Help Bubble
									<HelpBubble helpText="This is a helpful tooltip that explains the feature" />
								</Form.Label>
								<Form.Control placeholder="Input with help bubble" />
							</Form.Group>
						</Col>

						<Col md={6}>
							<PasswordInput
								field={passwordField}
								value={formData.password}
								handleChange={handleChange}
							/>
						</Col>

						<Col md={6}>
							<SalaryInput
								field={salaryField}
								value={formData.salary}
								handleChange={handleChange}
								secondaryValue="USD"
							/>
						</Col>

						<Col md={6}>
							<Form.Group>
								<Form.Label>{ratingField.label}</Form.Label>
								<StarRating field={ratingField} value={formData.rating} handleChange={handleChange} />
							</Form.Group>
						</Col>

						<Col md={6}>
							<LocalDatetimeInput
								value={null}
								field={datetimeField}
								handleChange={handleChange}
								inputType="datetime-local"
							/>
						</Col>

						<Col md={6}>
							<LocalDatetimeInput
								value={null}
								field={dateField}
								handleChange={handleChange}
								inputType="date"
							/>
						</Col>

						<Col md={6}>
							<SelectInput field={selectField} value={formData.select} handleChange={handleChange} />
						</Col>

						<Col md={12}>
							<Textarea field={textareaField} value={formData.textarea} handleChange={handleChange} />
						</Col>

						<Col md={12}>
							<UrlInput field={urlField} value={"vsdv"} handleChange={handleChange}></UrlInput>
						</Col>
					</Row>
				</Form>
			</Section>

			{/* ------------------------------ PROGRESS BAR ------------------------------ */}
			<Section title="Progress">
				<div style={{ maxWidth: 400 }}>
					<ProgressBar now={60} label="60%" />
				</div>
			</Section>

			{/* -------------------------------- SPINNERS -------------------------------- */}
			<Section title="Spinners">
				<Stack direction="horizontal" gap={3}>
					<Spinner animation="border" size="sm" />
					<Spinner animation="border" />
				</Stack>
			</Section>

			{/* -------------------------------- ACCORDION -------------------------------- */}
			<Section title="Accordion">
				<Accordion defaultActiveKey="0">
					<Accordion.Item eventKey="0">
						<Accordion.Header>Accordion item</Accordion.Header>
						<Accordion.Body>
							This is what your accordion content looks like in the current theme.
						</Accordion.Body>
					</Accordion.Item>
				</Accordion>
			</Section>

			{/* ----------------------------- BACKGROUND CARDS ---------------------------- */}
			<Section title="Backgrounds">
				<div className="bg-light">
					<h6>Light background panel</h6>
					This shows your background gradients, borders and text colours.
				</div>
			</Section>
		</Container>
	);
};
