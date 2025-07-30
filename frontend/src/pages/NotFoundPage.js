import React from "react";
import { Link, useNavigate } from "react-router-dom";

const NotFound = () => {
	const navigate = useNavigate();

	const goBack = () => {
		navigate(-1);
	};

	return (
		<div
			className="container-fluid d-flex flex-column justify-content-center align-items-center text-center"
			style={{ minHeight: "calc(100vh - 100px)" }}
		>
			<div className="col-12 col-md-8 col-lg-6" style={{ maxWidth: "700px" }}>
				<div className="error-content">
					<h1 className="display-1 fw-bold text-primary mb-3">404</h1>
					<h2 className="h3 mb-3">Oops! Something Is Jamming Our Radars</h2>
					<p className="lead text-muted mb-4">
						The page you're looking for might have been removed, had its name changed, or is temporarily
						unavailable.
					</p>
					<div className="d-flex gap-3 justify-content-center flex-wrap">
						<Link to="/dashboard" className="btn btn-primary">
							<i className="bi bi-house-fill me-2"></i>
							Go Home
						</Link>
						<button onClick={goBack} className="btn btn-outline-secondary" type="button">
							<i className="bi bi-arrow-left me-2"></i>
							Go Back
						</button>
					</div>
				</div>
			</div>
		</div>
	);
};

export default NotFound;
