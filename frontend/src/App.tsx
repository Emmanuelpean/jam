import React, { createContext, JSX, ReactNode, useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { DataProvider } from "./contexts/DataContext";
import Login from "./pages/Auth/AuthPage";
import LocationsPage from "./pages/DataTablePages/LocationsPage";
import CompaniesPage from "./pages/DataTablePages/CompaniesPage";
import JobsPage from "./pages/DataTablePages/JobsPage";
import PersonPage from "./pages/DataTablePages/PersonPage";
import KeywordsPage from "./pages/DataTablePages/KeywordsPage";
import InterviewsPage from "./pages/DataTablePages/InterviewsPage";
import JobScraperDashboard from "./pages/Services/JobScrapingDashboard/JobScraperDashboardPage";
import AggregatorsPage from "./pages/DataTablePages/AggregatorsPage";
import { NotAuthorisedPage, NotFoundPage } from "./pages/NotFoundPage";
import { Sidebar } from "./components/Sidebar/Sidebar";
import JobApplicationUpdatesPage from "./pages/DataTablePages/JobApplicationUpdatesPage";
import Dashboard from "./pages/Dashboard/DashboardPage";
import { LoadingProvider, useLoading } from "./contexts/LoadingContext";
import { UserManagementPage } from "./pages/DataTablePages/UserManagementPage";
import UserSettingsPage from "./pages/UserSettings/UserSettingsPage";
import { useToast, UseToastReturn } from "./hooks/useNotificationToast";
import { ToastStack } from "./components/Toasts/Toast";
import SettingsPage from "./pages/DataTablePages/SettingsPage";
import TermsPage from "./pages/Auth/TermsPage";
import PrivacyPolicyPage from "./pages/Auth/PrivacyPolicyPage";
import AboutPage from "./pages/About/AboutPage";
import ExtensionPage from "./pages/About/ExtensionPage";
import ReleaseNotesPage from "./pages/About/ReleaseNotesPage";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.scss";
import "./Themes.scss";
import { AlertProvider } from "./contexts/AlertContext";
import JobRatingDashboard from "./pages/Services/JobRatingDashboard/JobRatingDashboardPage";
import SpeculativeApplicationsPage from "./pages/DataTablePages/SpeculativeApplicationsPage";
import { ContextMenuProvider } from "./contexts/ContextMenuContext";
import { ThemeProvider } from "./contexts/ThemeContext";
import { ProgressOverlayProvider } from "./contexts/useProgressOverlayContext";
import { ScrapedJobsPage } from "./pages/DataTablePages/ScrapedJobsPage";
import { StyleGuidePage } from "./pages/StylePage";
import { EmailTemplatesPage } from "./pages/Admin/EmailTemplatesPage";
import { ConfigProvider } from "./contexts/ConfigContext";
import { StatusProvider } from "./contexts/StatusContext";
import { MaintenanceBanner } from "./components/AppBanner/MaintenanceBanner";
import { DemoBanner } from "./components/AppBanner/DemoBanner";
import { WhatsNewProvider } from "./contexts/WhatsNewContext";

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

function AppLayout({ children }: AppLayoutProps): JSX.Element {
	const { isLoading, loadingMessage, progress } = useLoading();
	const location = useLocation();
	const { currentUser, isAuthenticated } = useAuth();
	const navigate = useNavigate();
	useSwetrixPageViews();

	useEffect(() => {
		if (!isAuthenticated) return;
		const handler = (event: MessageEvent): void => {
			if (event.data?.type !== "JAM_EXT_JOB") return;
			navigate("/jobs", { state: { extJob: event.data.data } });
		};
		window.addEventListener("message", handler);
		return () => window.removeEventListener("message", handler);
	}, [isAuthenticated, navigate]);

	const normalisedPathname: string =
		location.pathname !== "/" && location.pathname.endsWith("/")
			? location.pathname.slice(0, -1)
			: location.pathname;

	const isAuthPage: boolean = [
		"/login",
		"/register",
		"/forgot-password",
		"/verify-email",
		"/verify-new-email",
		"/reset-password",
	].includes(normalisedPathname);

	return (
		<div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
			<MaintenanceBanner />
			<DemoBanner />
			<div style={{ display: "flex", flex: 1, minHeight: 0 }}>
				{currentUser && <Sidebar />}
				<div style={{ flex: 1, minWidth: 0, overflowY: "auto", display: "flex", flexDirection: "column" }}>
					<div
						className={!isAuthPage ? `main-content` : ""}
						style={isAuthPage ? { height: "100%" } : undefined}
					>
						{isLoading && (
							<div className="global-loading-overlay">
								<div className="d-flex flex-column justify-content-center align-items-center h-100">
									<div className="spinner-border mb-3" role="status" id="loading-spinner">
										<span className="visually-hidden">Loading...</span>
									</div>
									<p className="mb-3">{loadingMessage}</p>
									{progress !== undefined && (
										<div className="progress" style={{ width: "315px" }}>
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
						{children}
					</div>
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
	{ path: "/terms", element: <TermsPage /> },
	{ path: "/privacy", element: <PrivacyPolicyPage /> },
	{ path: "/about", element: <AboutPage />, protected: true },
	{ path: "/browser-extension", element: <ExtensionPage />, protected: true },
	{ path: "/release-notes", element: <ReleaseNotesPage />, protected: true },
	{ path: "/locations", element: <LocationsPage />, protected: true },
	{ path: "/companies", element: <CompaniesPage />, protected: true },
	{ path: "/jobs", element: <JobsPage />, protected: true },
	{ path: "/style-guide", element: <StyleGuidePage />, protected: true, adminOnly: true },
	{
		path: "/speculative-applications",
		element: <SpeculativeApplicationsPage />,
		protected: true,
	},
	{ path: "/persons", element: <PersonPage />, protected: true },
	{ path: "/keywords", element: <KeywordsPage />, protected: true },
	{ path: "/interviews", element: <InterviewsPage />, protected: true },
	{ path: "/aggregators", element: <AggregatorsPage />, protected: true },
	{ path: "/job-application-updates", element: <JobApplicationUpdatesPage />, protected: true },
	{ path: "/scraped-jobs", element: <ScrapedJobsPage />, protected: true },
	{ path: "/dashboard", element: <Dashboard />, protected: true },
	{ path: "/settings/:tab", element: <UserSettingsPage />, protected: true },
	{ path: "/settings", element: <Navigate to="/settings/account" replace />, protected: true },
	{ path: "/users", element: <UserManagementPage />, protected: true, adminOnly: true },
	{
		path: "/job-scraping-dashboard",
		element: <JobScraperDashboard />,
		protected: true,
		adminOnly: true,
	},
	{
		path: "/job-rating-dashboard",
		element: <JobRatingDashboard />,
		protected: true,
		adminOnly: true,
	},
	{ path: "/app-settings", element: <SettingsPage />, protected: true, adminOnly: true },
	{ path: "/email-templates", element: <EmailTemplatesPage />, protected: true, adminOnly: true },
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

function AppContent(): JSX.Element {
	const toastMethods: UseToastReturn = useToast();

	return (
		<BrowserRouter basename="/jam">
			<AuthProvider>
				<LoadingProvider>
					<DataProviderWrapper>
						<ToastContext.Provider value={toastMethods}>
							<AlertProvider>
								<ProgressOverlayProvider>
									<ThemeProvider>
										<WhatsNewProvider>
											<ContextMenuProvider>
												<AppLayout>
													<AppRoutes />
												</AppLayout>
											</ContextMenuProvider>
										</WhatsNewProvider>
									</ThemeProvider>
									<ToastStack
										toasts={toastMethods.toasts}
										onClose={toastMethods.hideToast}
										position="top-end"
									/>
								</ProgressOverlayProvider>
							</AlertProvider>
						</ToastContext.Provider>
					</DataProviderWrapper>
				</LoadingProvider>
			</AuthProvider>
		</BrowserRouter>
	);
}

function App(): JSX.Element {
	return (
		<ConfigProvider>
			<StatusProvider>
				<AppContent />
			</StatusProvider>
		</ConfigProvider>
	);
}

export default App;
