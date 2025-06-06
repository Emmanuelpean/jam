import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import "./AuthForm.css";
import "../Logo.css";
import logo from "../../assets/jam-jam.png";

function Login() {
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState("");
	const [loading, setLoading] = useState(false);
	const { login } = useAuth();
	const navigate = useNavigate();

	async function handleSubmit(e) {
		e.preventDefault();
		setError("");
		setLoading(true);

		try {
			const result = await login(email, password);
			if (result.success) {
				navigate("/users");
			} else {
				setError(result.error);
			}
		} catch (error) {
			setError("Failed to log in");
		}

		setLoading(false);
	}

	return (
		<div className="auth-container">
			<div className="auth-logo">
				<div className="logo-container logo-container-vertical">
					<img src={logo} alt="Logo" style={{ height: "175px" }} />
					<div className="logo-text logo-text-below">Job Application Manager</div>
				</div>
			</div>

			<div className="auth-card">
				<h1>Login</h1>
				{error && <div className="error-message active">{error}</div>}

				<form onSubmit={handleSubmit}>
					<div className="form-group">
						<label htmlFor="email">Email</label>
						<input
							type="email"
							id="email"
							value={email}
							onChange={(e) => setEmail(e.target.value)}
							required
						/>
					</div>

					<div className="form-group">
						<label htmlFor="password">Password</label>
						<input
							type="password"
							id="password"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							required
						/>
					</div>

					<button type="submit" className="btn-primary" disabled={loading}>
						{loading ? "Logging in..." : "Login"}
					</button>
				</form>

				<div className="auth-footer">
					<p>
						Don't have an account? <Link to="/register">Register</Link>
					</p>
				</div>
			</div>
		</div>
	);
}

export default Login;
