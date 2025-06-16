import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import "./AuthForm.css";
import "../Logo.css";
import { ReactComponent as JamLogo } from "../../assets/Logo.svg";

function Login() {
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState("");
	const [loading, setLoading] = useState(false);
	const { login } = useAuth();
	const navigate = useNavigate();

	const themes = ["strawberry", "blueberry", "raspberry", "mixed-berry", "forest-berry", "blackberry"];

	// Randomly pick a theme when component mounts
	useEffect(() => {
		const randomTheme = themes[Math.floor(Math.random() * themes.length)];
		document.documentElement.setAttribute("data-theme", randomTheme);
	}, []);

	async function handleSubmit(e) {
		e.preventDefault();
		setError("");
		setLoading(true);

		try {
			const result = await login(email, password);
			if (result.success) {
				navigate("/dashboard");
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
					<JamLogo style={{ height: "175px", width: "auto" }} alt="Logo" />
					<div className="logo-text logo-text-below text-gradient-primary">Job Application Manager</div>
				</div>
			</div>

			<div className="auth-card">
				<h1>Login</h1>
				{error && <div className="error-message active">{error}</div>}

				<form onSubmit={handleSubmit}>
					<div className="auth-form-group">
						<label htmlFor="email">Email</label>
						<input
							type="email"
							id="email"
							value={email}
							onChange={(e) => setEmail(e.target.value)}
							required
						/>
					</div>

					<div className="auth-form-group">
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
