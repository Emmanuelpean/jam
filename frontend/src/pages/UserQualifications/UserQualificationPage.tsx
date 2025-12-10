import React, { useState, useEffect } from "react";
import { Container, Row, Col, Form, Button, Card } from "react-bootstrap";
import { jobQualificationApi } from "../../services/Api";

const UserQualifications = () => {
	const [qualifications, setQualifications] = useState({
		experience: "",
		skills: "",
		qualities: "",
		education: "",
	});

	const [savedQualifications, setSavedQualifications] = useState(null);
	const [loading, setLoading] = useState(false);

	// Fetch existing qualifications on component mount
	useEffect(() => {
		fetchQualifications();
	}, []);

	const fetchQualifications = async () => {
		try {
			const response = await fetch("/api/user/qualifications", {
				headers: {
					Authorization: `Bearer ${localStorage.getItem("token")}`,
				},
			});
			if (response.ok) {
				const data = await response.json();
				setSavedQualifications(data);
				setQualifications({
					experience: data.experience || "",
					skills: data.skills || "",
					qualities: data.qualities || "",
					education: data.education || "",
				});
			}
		} catch (error) {
			console.error("Error fetching qualifications:", error);
		}
	};

	const handleChange = (e) => {
		const { name, value } = e.target;
		setQualifications((prev) => ({
			...prev,
			[name]: value,
		}));
	};

	const handleSubmit = async (e) => {
		e.preventDefault();
		setLoading(true);

		try {
			const response = await jobQualificationApi.upsert();

			if (response.ok) {
				const data = await response.json();
				setSavedQualifications(data);
				alert("Qualifications saved successfully!");
			}
		} catch (error) {
			console.error("Error saving qualifications:", error);
			alert("Failed to save qualifications");
		} finally {
			setLoading(false);
		}
	};

	return (
		<Container className="mt-4">
			<h2 className="mb-4">User Qualifications</h2>

			<Row>
				{/* Left side - Saved qualifications */}
				<Col md={6}>
					<Card>
						<Card.Header>
							<h5>Current Qualifications</h5>
						</Card.Header>
						<Card.Body>
							{savedQualifications ? (
								<>
									<div className="mb-3">
										<strong>Experience:</strong>
										<p className="mt-1">{savedQualifications.experience || "Not provided"}</p>
									</div>

									<div className="mb-3">
										<strong>Skills:</strong>
										<p className="mt-1">{savedQualifications.skills || "Not provided"}</p>
									</div>

									<div className="mb-3">
										<strong>Qualities:</strong>
										<p className="mt-1">{savedQualifications.qualities || "Not provided"}</p>
									</div>

									<div className="mb-3">
										<strong>Education:</strong>
										<p className="mt-1">{savedQualifications.education || "Not provided"}</p>
									</div>

									{savedQualifications.updated_at && (
										<small className="text-muted">
											Last updated: {new Date(savedQualifications.updated_at).toLocaleString()}
										</small>
									)}
								</>
							) : (
								<p className="text-muted">No qualifications saved yet</p>
							)}
						</Card.Body>
					</Card>
				</Col>

				{/* Right side - Input form */}
				<Col md={6}>
					<Card>
						<Card.Header>
							<h5>Edit Qualifications</h5>
						</Card.Header>
						<Card.Body>
							<Form onSubmit={handleSubmit}>
								<Form.Group className="mb-3">
									<Form.Label>Experience</Form.Label>
									<Form.Control
										as="textarea"
										rows={3}
										name="experience"
										value={qualifications.experience}
										onChange={handleChange}
										placeholder="Describe your work experience..."
										required
									/>
								</Form.Group>

								<Form.Group className="mb-3">
									<Form.Label>Skills</Form.Label>
									<Form.Control
										as="textarea"
										rows={3}
										name="skills"
										value={qualifications.skills}
										onChange={handleChange}
										placeholder="List your technical skills..."
										required
									/>
								</Form.Group>

								<Form.Group className="mb-3">
									<Form.Label>Qualities</Form.Label>
									<Form.Control
										as="textarea"
										rows={3}
										name="qualities"
										value={qualifications.qualities}
										onChange={handleChange}
										placeholder="Describe your professional qualities..."
										required
									/>
								</Form.Group>

								<Form.Group className="mb-3">
									<Form.Label>Education</Form.Label>
									<Form.Control
										as="textarea"
										rows={3}
										name="education"
										value={qualifications.education}
										onChange={handleChange}
										placeholder="Describe your educational background..."
										required
									/>
								</Form.Group>

								<Button variant="primary" type="submit" disabled={loading} className="w-100">
									{loading ? "Saving..." : "Save Qualifications"}
								</Button>
							</Form>
						</Card.Body>
					</Card>
				</Col>
			</Row>
		</Container>
	);
};

export default UserQualifications;
