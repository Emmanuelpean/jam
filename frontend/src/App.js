import React, { useState } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import Login from "./components/Auth/Login";
import LocationsPage from "./pages/LocationsPage";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";
import CompaniesPage from "./pages/CompaniesPage";
import JobsPage from "./pages/JobsPage";
import PersonPage from "./pages/PersonPage";
import KeywordsPage from "./pages/KeywordsPage";
import InterviewsPage from "./pages/InterviewsPage";
import JobApplicationPage from "./pages/JobApplicationsPage";
import "./Themes.css";
import DashboardPage from "./pages/EISDashboardPage";
import AggregatorsPage from "./pages/AggregatorsPage";
import NotFoundPage from "./pages/NotFoundPage";
import { Sidebar } from "./Sidebar";
import JobApplicationUpdatesPage from "./pages/JobApplicationUpdatesPage";
import JobSearchDashboard from "./pages/DashboardPage";
import { LoadingProvider, useLoading } from "./contexts/LoadingContext";
import { UserManagementPage } from "./pages/UserManagementPage";
import UserSettingsPage from "./pages/UserSettingsPage";

function AppLayout({ children }) {
	const { isLoading, loadingMessage } = useLoading();
	const location = useLocation();
	const { currentUser } = useAuth();
	const [sidebarExpanded, setSidebarExpanded] = useState(false);

	// Don't show sidebar on auth pages
	const isAuthPage = location.pathname === "/login" || location.pathname === "/register";

	const handleSidebarHoverChange = (isHovering) => {
		setSidebarExpanded(isHovering);
	};

	return (
		<div style={{ display: "flex", height: "100vh" }}>
			{!isAuthPage && currentUser && <Sidebar onHoverChange={handleSidebarHoverChange} />}
			<div
				className={!isAuthPage ? `main-content ${sidebarExpanded ? "sidebar-expanded" : ""}` : ""}
				style={{ flex: 1, overflow: "auto" }}
			>
				<div
					className="content-wrapper"
					style={{
						maxWidth: "95%",
						margin: "0 auto",
						paddingBottom: "20px",
						paddingTop: "10px",
					}}
				>
					{isLoading && (
						<div className="global-loading-overlay">
							<div className="d-flex flex-column justify-content-center align-items-center h-100">
								<div className="spinner-border mb-3" role="status">
									<span className="visually-hidden">Loading...</span>
								</div>
								<p className="text-muted">{loadingMessage}</p>
							</div>
						</div>
					)}
					<div style={{ display: isLoading ? "none" : "block" }}>{children}</div>
				</div>
			</div>
		</div>
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
				<LoadingProvider>
					<AppLayout>
						<Routes>
							<Route path="/login" element={<Login />} />
							<Route path="/register" element={<Login />} />
							<Route path="/" element={<Navigate to="/dashboard" />} />
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
								path="/interviews"
								element={
									<ProtectedRoute>
										<InterviewsPage />
									</ProtectedRoute>
								}
							/>
							<Route
								path="/jobapplications"
								element={
									<ProtectedRoute>
										<JobApplicationPage />
									</ProtectedRoute>
								}
							/>
							<Route
								path="/eis_dashboard"
								element={
									<ProtectedRoute>
										<DashboardPage />
									</ProtectedRoute>
								}
							/>
							<Route
								path="/aggregators"
								element={
									<ProtectedRoute>
										<AggregatorsPage />
									</ProtectedRoute>
								}
							/>
							<Route
								path="/jobapplicationupdates"
								element={
									<ProtectedRoute>
										<JobApplicationUpdatesPage />
									</ProtectedRoute>
								}
							/>
							<Route
								path="/dashboard"
								element={
									<ProtectedRoute>
										<JobSearchDashboard />
									</ProtectedRoute>
								}
							/>
							<Route
								path="/users"
								element={
									<ProtectedRoute>
										<UserManagementPage />
									</ProtectedRoute>
								}
							/>
							<Route
								path="/settings"
								element={
									<ProtectedRoute>
										<UserSettingsPage />
									</ProtectedRoute>
								}
							/>
							<Route path="*" element={<NotFoundPage />} />
						</Routes>
					</AppLayout>
				</LoadingProvider>
			</AuthProvider>
		</BrowserRouter>
	);
}

export default App;
