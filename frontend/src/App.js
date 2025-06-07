import React from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import Login from "./components/Auth/Login";
import Register from "./components/Auth/Register";
import LocationsPage from "./pages/LocationsPage";
import StyleShowcase from "./pages/TestPage";
import Header from "./components/Header";
import "bootstrap/dist/css/bootstrap.min.css"; // Bootstrap first
import "./App.css";
import CompaniesPage from "./pages/CompaniesPage";
import JobsPage from "./pages/JobsPage";
import PersonPage from "./pages/PersonPage";
import KeywordsPage from "./pages/KeywordsPage";

// Layout wrapper component to conditionally show header
function AppLayout({ children }) {
	const location = useLocation();
	const { currentUser, logout } = useAuth();

	// Don't show header on auth pages
	const isAuthPage = location.pathname === "/login" || location.pathname === "/register";

	return (
		<>
			{!isAuthPage && currentUser && <Header onLogout={logout} />}
			{children}
		</>
	);
}

// Protected route wrapper
function ProtectedRoute({ children }) {
	const { isAuthenticated } = useAuth();

	return isAuthenticated ? children : <Navigate to="/login" />;
}

function App() {
	return (
		<BrowserRouter>
			<AuthProvider>
				<AppLayout>
					<Routes>
						<Route path="/login" element={<Login />} />
						<Route path="/register" element={<Register />} />
						<Route path="/" element={<Navigate to="/login" />} />
						<Route
							path="/locations"
							element={
								<ProtectedRoute>
									<LocationsPage />
								</ProtectedRoute>
							}
						/>
						<Route
							path="/companies"
							element={
								<ProtectedRoute>
									<CompaniesPage />
								</ProtectedRoute>
							}
						/>
						<Route
							path="/jobs"
							element={
								<ProtectedRoute>
									<JobsPage />
								</ProtectedRoute>
							}
						/>
						<Route
							path="/showcase"
							element={
								<ProtectedRoute>
									<StyleShowcase />
								</ProtectedRoute>
							}
						/>
						<Route
							path="/persons"
							element={
								<ProtectedRoute>
									<PersonPage />
								</ProtectedRoute>
							}
						/>
						<Route
							path="/keywords"
							element={
								<ProtectedRoute>
									<KeywordsPage />
								</ProtectedRoute>
							}
						/>
						<Route
							path="/users"
							element={
								<ProtectedRoute>
									<LocationsPage />
								</ProtectedRoute>
							}
						/>
					</Routes>
				</AppLayout>
			</AuthProvider>
		</BrowserRouter>
	);
}

export default App;
