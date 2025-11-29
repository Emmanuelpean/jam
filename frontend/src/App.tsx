import React, { createContext, JSX, ReactNode, useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { DataProvider } from "./contexts/DataContext";
import Login from "./pages/Auth/Auth";
import LocationsPage from "./pages/LocationsPage";
import CompaniesPage from "./pages/CompaniesPage";
import JobsPage from "./pages/JobsPage";
import PersonPage from "./pages/PersonPage";
import KeywordsPage from "./pages/KeywordsPage";
import InterviewsPage from "./pages/InterviewsPage";
import DashboardPage from "./pages/EISDashboard/EISDashboardPage";
import AggregatorsPage from "./pages/AggregatorsPage";
import { NotAuthorisedPage, NotFoundPage } from "./pages/NotFoundPage";
import { Sidebar } from "./components/sidebar/Sidebar";
import JobApplicationUpdatesPage from "./pages/JobApplicationUpdatesPage";
import Dashboard from "./pages/Dashboard/DashboardPage";
import { LoadingProvider, useLoading } from "./contexts/LoadingContext";
import { UserManagementPage } from "./pages/UserManagementPage";
import UserSettingsPage from "./pages/UserSettings/UserSettingsPage";
import { useToast, UseToastReturn } from "./hooks/useNotificationToast";
import { ToastStack } from "./components/toasts/Toast";
import SettingsPage from "./pages/SettingsPage";
import AboutPage from "./pages/AboutPage/AboutPage";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";
import "./Themes.css";

export function useSwetrixPageViews() {
	const location = useLocation();

	useEffect(() => {
		//@ts-ignore
		window.swetrix?.trackViews();
	}, [location]);
}

export const ToastContext = createContext<UseToastReturn | undefined>(undefined);

interface AppLayoutProps {
	children: ReactNode;
}

function composeProviders(...providers: React.ComponentType<{ children: ReactNode }>[]) {
	return ({ children }: { children: ReactNode }): ReactNode =>
		providers.reduceRight((acc: ReactNode, Provider) => <Provider>{acc}</Provider>, children);
}

function AppLayout({ children }: AppLayoutProps): JSX.Element {
	const { isLoading, loadingMessage, progress } = useLoading();
	const location = useLocation();
	const { currentUser } = useAuth();
	useSwetrixPageViews();

	const isAuthPage: boolean = location.pathname === "/login" || location.pathname === "/register";

	return (
		<div style={{ display: "flex", minHeight: "100vh" }}>
			{currentUser && <Sidebar />}
			<div style={{ flex: 1 }}>
				<div className={!isAuthPage ? `main-content` : ""}>
					{isLoading && (
						<div className="global-loading-overlay">
							<div className="d-flex flex-column justify-content-center align-items-center h-100">
								<div className="spinner-border mb-3" role="status" id="loading-spinner">
									<span className="visually-hidden">Loading...</span>
								</div>
								<p className="text-muted mb-3">{loadingMessage}</p>
								{progress !== undefined && (
									<div className="progress" style={{ width: "350px" }}>
										<div
											className="progress-bar progress-bar-striped progress-bar-animated"
											role="progressbar"
											style={{ width: `${progress}%` }}
											aria-valuenow={progress}
											aria-valuemin={0}
											aria-valuemax={100}
										/>
										<span className="progress-text">{progress}%</span>
									</div>
								)}
							</div>
						</div>
					)}
					{!isLoading && <div>{children}</div>}
				</div>
			</div>
		</div>
	);
}

function ProtectedRoute({ children }: AppLayoutProps): JSX.Element {
	const { isAuthenticated } = useAuth();
	return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

function AdminProtectedRoute({ children }: AppLayoutProps): JSX.Element {
	const { currentUser } = useAuth();
	return currentUser?.is_admin ? <>{children}</> : <NotAuthorisedPage />;
}

function DataProviderWrapper({ children }: { children: ReactNode }): JSX.Element {
	const { token } = useAuth();

	if (!token) {
		return <>{children}</>;
	}

	return <DataProvider token={token}>{children}</DataProvider>;
}

interface RouteConfig {
	path: string;
	element: JSX.Element;
	protected?: boolean;
	adminOnly?: boolean;
}

const routeConfigs: RouteConfig[] = [
	{ path: "/login", element: <Login /> },
	{ path: "/register", element: <Login /> },
	{ path: "/forgot-password", element: <Login /> },
	{ path: "/reset-password", element: <Login /> },
	{ path: "/verify-email", element: <Login /> },
	{ path: "/verify-new-email", element: <Login /> },
	{ path: "/", element: <Navigate to="/dashboard" replace /> },
	{ path: "/about", element: <AboutPage />, protected: true },
	{ path: "/locations", element: <LocationsPage />, protected: true },
	{ path: "/companies", element: <CompaniesPage />, protected: true },
	{ path: "/jobs", element: <JobsPage />, protected: true },
	{ path: "/persons", element: <PersonPage />, protected: true },
	{ path: "/keywords", element: <KeywordsPage />, protected: true },
	{ path: "/interviews", element: <InterviewsPage />, protected: true },
	{ path: "/aggregators", element: <AggregatorsPage />, protected: true },
	{ path: "/jobapplicationupdates", element: <JobApplicationUpdatesPage />, protected: true },
	{ path: "/dashboard", element: <Dashboard />, protected: true },
	{ path: "/settings", element: <UserSettingsPage />, protected: true },
	{ path: "/users", element: <UserManagementPage />, protected: true, adminOnly: true },
	{ path: "/eis_dashboard", element: <DashboardPage />, protected: true, adminOnly: true },
	{ path: "/app_settings", element: <SettingsPage />, protected: true, adminOnly: true },
	{ path: "*", element: <NotFoundPage /> },
];

function AppRoutes(): JSX.Element {
	return (
		<Routes>
			{routeConfigs.map(({ path, element, protected: isProtected, adminOnly }: RouteConfig): JSX.Element => {
				let routeElement: JSX.Element = element;

				if (isProtected && adminOnly) {
					routeElement = (
						<ProtectedRoute>
							<AdminProtectedRoute>{element}</AdminProtectedRoute>
						</ProtectedRoute>
					);
				} else if (isProtected) {
					routeElement = <ProtectedRoute>{element}</ProtectedRoute>;
				}

				return <Route key={path} path={path} element={routeElement} />;
			})}
		</Routes>
	);
}

function App(): JSX.Element {
	const toastMethods: UseToastReturn = useToast();

	// Compose all providers in a clean, readable way
	const AllProviders = React.useMemo(() => composeProviders(AuthProvider, LoadingProvider, DataProviderWrapper), []);

	return (
		<BrowserRouter basename="/jam">
			<AllProviders>
				<ToastContext.Provider value={toastMethods}>
					<AppLayout>
						<AppRoutes />
					</AppLayout>
					<ToastStack toasts={toastMethods.toasts} onClose={toastMethods.hideToast} position="top-end" />
				</ToastContext.Provider>
			</AllProviders>
		</BrowserRouter>
	);
}

export default App;
