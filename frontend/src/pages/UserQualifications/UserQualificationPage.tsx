import React, { JSX, useEffect, useState } from "react";
import { Card, Col, Container, Form, Row } from "react-bootstrap";
import { userQualificationApi } from "../../services/api/Users";
import { UserQualification, UserQualificationDataTransform } from "../../services/Schemas";
import { useAuth } from "../../contexts/AuthContext";
import { SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { ActionButton } from "../../components/rendering/form/ActionButton";

const defaultUserQualification: UserQualificationDataTransform = {
	id: null,
	experience: "",
	skills: "",
	qualities: "",
	education: "",
	modified_at: null,
	created_at: null,
};

const UserQualifications = (): JSX.Element => {
	const { token } = useAuth();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const [userQualification, setUserQualification] =
		useState<UserQualificationDataTransform>(defaultUserQualification);
	const [loading, setLoading] = useState(false);

	const fetchLatestQualification = async (): Promise<void> => {
		if (!token) return;

		try {
			const data: UserQualification = await userQualificationApi.getLatest(token);

			if (data) {
				setUserQualification({
					id: data.id,
					experience: data.experience || "",
					skills: data.skills || "",
					qualities: data.qualities || "",
					education: data.education || "",
					modified_at: data.modified_at || null,
					created_at: data.created_at || null,
				});
			} else {
				setUserQualification(defaultUserQualification);
			}
		} catch (error) {
			console.error("Error fetching qualification:", error);
			setUserQualification(defaultUserQualification);
		}
	};

	useEffect((): void => {
		fetchLatestQualification().then((_): void => {});
	}, [token]);

	const handleChange = (e: SyntheticEvent) => {
		const { name, value } = e.target;
		setUserQualification((prev) => ({
			...prev,
			[name]: value,
		}));
	};

	const handleSubmit = async (e: any) => {
		if (!token) return;
		e.preventDefault();
		setLoading(true);

		try {
			const userQualificationToSave = {
				id: userQualification.id,
				experience: userQualification.experience || "",
				skills: userQualification.skills || "",
				qualities: userQualification.qualities || "",
				education: userQualification.education || "",
			};
			await userQualificationApi.upsert(userQualificationToSave, token);
			showToastSuccess("Qualifications saved successfully.");
		} catch (error) {
			console.error("Error saving qualifications:", error);
			showToastError("Failed to save qualifications.");
		} finally {
			setLoading(false);
		}
	};

	return (
		<Container className="mt-4">
			<h2 className="mb-4">User Qualifications</h2>

			<Row>
				{/* Main form */}
				<Col md={12}>
					<Card>
						<Card.Body>
							<Form onSubmit={handleSubmit}>
								<Form.Group className="mb-3">
									<Form.Label>Experience</Form.Label>
									<Form.Control
										as="textarea"
										rows={3}
										name="experience"
										value={userQualification.experience}
										onChange={handleChange}
										placeholder="Describe your work experience..."
									/>
								</Form.Group>

								<Form.Group className="mb-3">
									<Form.Label>Skills</Form.Label>
									<Form.Control
										as="textarea"
										rows={3}
										name="skills"
										value={userQualification.skills}
										onChange={handleChange}
										placeholder="List your technical skills..."
									/>
								</Form.Group>

								<Form.Group className="mb-3">
									<Form.Label>Qualities</Form.Label>
									<Form.Control
										as="textarea"
										rows={3}
										name="qualities"
										value={userQualification.qualities}
										onChange={handleChange}
										placeholder="Describe your professional qualities..."
									/>
								</Form.Group>

								<Form.Group className="mb-3">
									<Form.Label>Education</Form.Label>
									<Form.Control
										as="textarea"
										rows={3}
										name="education"
										value={userQualification.education}
										onChange={handleChange}
										placeholder="Describe your educational background..."
									/>
								</Form.Group>

								<div className="d-flex justify-content-between align-items-center mb-3">
									{userQualification.modified_at && (
										<small className="text-muted">
											Last updated: {new Date(userQualification.modified_at).toLocaleString()}
										</small>
									)}
								</div>

								<ActionButton
									variant="primary"
									type="submit"
									disabled={loading}
									className="w-100"
									loadingText={"Saving..."}
									defaultText={"Save Qualifications"}
								></ActionButton>
							</Form>
						</Card.Body>
					</Card>
				</Col>
			</Row>
		</Container>
	);
};

export default UserQualifications;
