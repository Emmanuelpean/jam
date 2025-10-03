import React, { createContext, JSX, ReactNode } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { DataProvider } from "./contexts/DataContext";
import Login from "./pages/Auth/Auth";
import LocationsPage from "./pages/LocationsPage";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";
import CompaniesPage from "./pages/CompaniesPage";
import JobsPage from "./pages/JobsPage";
import PersonPage from "./pages/PersonPage";
import KeywordsPage from "./pages/KeywordsPage";
import InterviewsPage from "./pages/InterviewsPage";
import "./Themes.css";
import DashboardPage from "./pages/EISDashboardPage";
import AggregatorsPage from "./pages/AggregatorsPage";
import { NotAuthorisedPage, NotFoundPage } from "./pages/NotFoundPage";
import { Sidebar } from "./components/sidebar/Sidebar";
import JobApplicationUpdatesPage from "./pages/JobApplicationUpdatesPage";
import JobSearchDashboard from "./pages/Dashboard/DashboardPage";
import { LoadingProvider, useLoading } from "./contexts/LoadingContext";
import { UserManagementPage } from "./pages/UserManagementPage";
import UserSettingsPage from "./pages/UserSettings/UserSettingsPage";
import { useToast, UseToastReturn } from "./hooks/useNotificationToast";
import { ToastStack } from "./components/toasts/Toast";
import SettingsPage from "./pages/SettingsPage";
import AboutPage from "./pages/AboutPage";

export const ToastContext = createContext<UseToastReturn | undefined>(undefined);

interface AppLayoutProps {
	children: ReactNode;
}

function AppLayout({ children }: AppLayoutProps): JSX.Element {
	const { isLoading, loadingMessage } = useLoading();
	const location = useLocation();
	const { currentUser } = useAuth();

	const isAuthPage = location.pathname === "/login" || location.pathname === "/register";

	return (
		<div style={{ display: "flex", minHeight: "100vh" }}>
			{currentUser && <Sidebar />}
			<div style={{ width: "100%" }}>
				<div className={!isAuthPage ? `main-content` : ""}>
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

interface ProtectedRouteProps {
	children: ReactNode;
}

function ProtectedRoute({ children }: ProtectedRouteProps): JSX.Element {
	const { isAuthenticated } = useAuth();

	return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

function AdminProtectedRoute({ children }: ProtectedRouteProps): JSX.Element {
	const { isAuthenticated, is_admin } = useAuth();

	return isAuthenticated && is_admin ? <>{children}</> : <NotAuthorisedPage />;
}

// New component to wrap DataProvider with token
function DataProviderWrapper({ children }: { children: ReactNode }): JSX.Element {
	const { token } = useAuth();

	// Only provide data context when authenticated
	if (!token) {
		return <>{children}</>;
	}

	return <DataProvider token={token}>{children}</DataProvider>;
}

function App(): JSX.Element {
	const { toasts, showToastSuccess, showToastError, showToastWarning, showToastInfo, hideToast } = useToast();

	return (
		<BrowserRouter basename="/jam">
			<AuthProvider>
				<DataProviderWrapper>
					<LoadingProvider>
						<ToastContext.Provider
							// @ts-ignore
							value={{
								showToastSuccess,
								showToastError,
								showToastWarning,
								showToastInfo,
							}}
						>
							<AppLayout>
								<Routes>
									<Route path="/login" element={<Login />} />
									<Route path="/register" element={<Login />} />
									<Route path="/" element={<Navigate to="/dashboard" />} />
									<Route
										path="/about"
										element={
											<ProtectedRoute>
												<AboutPage />
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
										path="/eis_dashboard"
										element={
											<AdminProtectedRoute>
												<DashboardPage />
											</AdminProtectedRoute>
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
											<AdminProtectedRoute>
												<UserManagementPage />
											</AdminProtectedRoute>
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
									<Route
										path="/app_settings"
										element={
											<AdminProtectedRoute>
												<SettingsPage />
											</AdminProtectedRoute>
										}
									/>
									<Route path="*" element={<NotFoundPage />} />
								</Routes>
							</AppLayout>
							<ToastStack toasts={toasts} onClose={hideToast} position="top-end" />
						</ToastContext.Provider>
					</LoadingProvider>
				</DataProviderWrapper>
			</AuthProvider>
		</BrowserRouter>
	);
}

export default App;
