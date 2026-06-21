import React, { createContext, JSX, ReactNode, useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { DataProvider } from "./contexts/DataContext";
import Login from "./pages/Auth/AuthPage";
import CompaniesPage from "./pages/DataTablePages/CompaniesPage";
import JobsPage from "./pages/DataTablePages/JobsPage";
import PersonPage from "./pages/DataTablePages/PersonPage";
import KeywordsPage from "./pages/DataTablePages/KeywordsPage";
import InterviewsPage from "./pages/DataTablePages/InterviewsPage";
import AggregatorsPage from "./pages/DataTablePages/AggregatorsPage";
import { NotAuthorisedPage, NotFoundPage } from "./pages/NotFoundPage";
import { Sidebar } from "./components/Sidebar/Sidebar";
import JobApplicationUpdatesPage from "./pages/DataTablePages/JobApplicationUpdatesPage";
import Dashboard from "./pages/Dashboard/DashboardPage";
import { LoadingProvider, useLoading } from "./contexts/LoadingContext";
import { useViewport, ViewportProvider } from "./contexts/ViewportContext";
import UserSettingsPage from "./pages/UserSettings/UserSettingsPage";
import { useToast, UseToastReturn } from "./hooks/useNotificationToast";
import { ToastStack } from "./components/Toasts/Toast";
import TermsPage from "./pages/Auth/TermsPage";
import PrivacyPolicyPage from "./pages/Auth/PrivacyPolicyPage";
import AboutPage from "./pages/About/AboutPage";
import ExtensionPage from "./pages/About/ExtensionPage";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.scss";
import "./Themes.scss";
import { AlertProvider, useAlert } from "./contexts/AlertContext";
import SpeculativeApplicationsPage from "./pages/DataTablePages/SpeculativeApplicationsPage";
import { ContextMenuProvider } from "./contexts/ContextMenuContext";
import { ThemeProvider } from "./contexts/ThemeContext";
import { ProgressOverlayProvider } from "./contexts/useProgressOverlayContext";
import { ScrapedJobsPage } from "./pages/DataTablePages/ScrapedJobsPage";
import { ConfigProvider } from "./contexts/ConfigContext";
import { StatusProvider } from "./contexts/StatusContext";
import { MaintenanceBanner } from "./components/AppBanner/MaintenanceBanner";
import { DemoBanner } from "./components/AppBanner/DemoBanner";
import { WhatsNewProvider } from "./contexts/WhatsNewContext";
import AdminPage from "./pages/Admin/AdminPage";
import FilesPage from "./pages/FilesPage/FilesPage";
import CommandPalette from "./components/CommandPalette/CommandPalette";
import { useCommandPalette } from "./components/CommandPalette/useCommandPalette";
import { CommandPaletteProvider } from "./contexts/CommandPaletteContext";
import { TourProvider } from "./contexts/TourContext";
import { GuidedTour } from "./components/GuidedTour/GuidedTour";
import { TourSelectPanel } from "./components/Tours/TourSelectPanel";
import { StaticDataProvider } from "./contexts/StaticDataContext";

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
	const { isOpen: isCommandPaletteOpen, close: closeCommandPalette } = useCommandPalette();
	const { hideAlert } = useAlert();
	const { isMobile } = useViewport();
	useSwetrixPageViews();

	useEffect(() => {
		hideAlert();
	}, [location.pathname]);

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
			<CommandPalette isOpen={isCommandPaletteOpen} onClose={closeCommandPalette} />
			{isAuthenticated && <GuidedTour />}
			{isAuthenticated && <TourSelectPanel />}
			<MaintenanceBanner />
			<DemoBanner />
			<div style={{ display: "flex", flex: 1, minHeight: 0 }}>
				{isAuthenticated && currentUser && !isMobile && <Sidebar />}
				<div
					className={isAuthenticated && currentUser ? "sidebar-content-offset" : ""}
					style={{
						flex: 1,
						minWidth: 0,
						overflowY: "auto",
						display: "flex",
						flexDirection: "column",
						position: "relative",
						zIndex: 1,
					}}
				>
					<div
						className={!isAuthPage ? `main-content` : ""}
						style={isAuthPage ? { height: "100%" } : undefined}
					>
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

	return (
		<DataProvider token={token}>
			<TourProvider>
				<WhatsNewProvider>{children}</WhatsNewProvider>
			</TourProvider>
		</DataProvider>
	);
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
	{ path: "/companies", element: <CompaniesPage />, protected: true },
	{ path: "/jobs", element: <JobsPage />, protected: true },
	{
		path: "/speculative-applications",
		element: <SpeculativeApplicationsPage />,
		protected: true,
	},
	{ path: "/contacts", element: <PersonPage />, protected: true },
	{ path: "/keywords", element: <KeywordsPage />, protected: true },
	{ path: "/interviews", element: <InterviewsPage />, protected: true },
	{ path: "/aggregators", element: <AggregatorsPage />, protected: true },
	{ path: "/job-application-updates", element: <JobApplicationUpdatesPage />, protected: true },
	{ path: "/files", element: <FilesPage />, protected: true },
	{ path: "/job-alerts/jobs", element: <ScrapedJobsPage />, protected: true },
	{ path: "/job-alerts/emails", element: <ScrapedJobsPage />, protected: true },
	{ path: "/dashboard", element: <Dashboard />, protected: true },
	{ path: "/settings/:tab", element: <UserSettingsPage />, protected: true },
	{ path: "/settings", element: <Navigate to="/settings/account" replace />, protected: true },
	{ path: "/admin", element: <AdminPage />, protected: true, adminOnly: true },
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

function ScreenTooSmall(): JSX.Element {
	return (
		<div className="screen-too-small">
			<i className="bi bi-phone screen-too-small-icon" />
			<p className="screen-too-small-title">Screen too small</p>
			<p className="screen-too-small-message">JAM requires a minimum screen width of 300px.</p>
		</div>
	);
}

function AppContent(): JSX.Element {
	const toastMethods: UseToastReturn = useToast();

	return (
		<>
			<ScreenTooSmall />
			<BrowserRouter basename="/jam">
				<StaticDataProvider>
					<AuthProvider>
						<LoadingProvider>
							<ViewportProvider>
								<ToastContext.Provider value={toastMethods}>
									<CommandPaletteProvider>
										<AlertProvider>
											<ProgressOverlayProvider>
												<ThemeProvider>
													<DataProviderWrapper>
														<ContextMenuProvider>
															<AppLayout>
																<AppRoutes />
															</AppLayout>
														</ContextMenuProvider>
													</DataProviderWrapper>
													<ToastStack
														toasts={toastMethods.toasts}
														onClose={toastMethods.hideToast}
														position="top-end"
													/>
												</ThemeProvider>
											</ProgressOverlayProvider>
										</AlertProvider>
									</CommandPaletteProvider>
								</ToastContext.Provider>
							</ViewportProvider>
						</LoadingProvider>
					</AuthProvider>
				</StaticDataProvider>
			</BrowserRouter>
		</>
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
