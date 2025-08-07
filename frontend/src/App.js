import React from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import Login from "./components/Auth/Login";
import LocationsPage from "./pages/LocationsPage";
import Header from "./Header";
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
import { SidebarExample } from "./sidebar";

function AppLayout({ children }) {
	const location = useLocation();
	const { currentUser, logout } = useAuth();

	// Don't show header on auth pages
	const isAuthPage = location.pathname === "/login" || location.pathname === "/register";

	return (
		<>
			{!isAuthPage && currentUser && <Header onLogout={logout} />}
			<div className="main-content">
				<div
					className="content-wrapper"
					style={{
						maxWidth: "90%",
						margin: "0 auto",
						padding: "20px",
					}}
				>
					{children}
				</div>
			</div>
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
							path="/locations"
							element={
								<ProtectedRoute>
									<LocationsPage />
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
							path="/dashboard"
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
						<Route path="/sidebar" element={<SidebarExample />}></Route>

						<Route path="*" element={<NotFoundPage />} />
					</Routes>
				</AppLayout>
			</AuthProvider>
		</BrowserRouter>
	);
}

export default App;
