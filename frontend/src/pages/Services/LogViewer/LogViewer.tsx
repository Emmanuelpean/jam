import React, { JSX, useEffect, useRef, useState } from "react";
import { BaseServiceApi, LogResponse, ServiceStatus } from "../../../services/api/Services";
import { useAuth } from "../../../contexts/AuthContext";
import LoadingSpinner from "../../../components/Spinner/Spinner";
import "./LogViewer.scss";
import { ApiResponse } from "../../../services/api/Base";

interface LogViewerProps {
	api: BaseServiceApi;
	isServiceRunning: boolean;
	serviceStatus: ServiceStatus | null;
	id?: string;
	/** Controlled expansion. When provided, internal state is bypassed. */
	expanded?: boolean;
	onExpandedChange?: (expanded: boolean) => void;
}

const LogViewer = ({
	api,
	isServiceRunning,
	serviceStatus,
	id,
	expanded,
	onExpandedChange,
}: LogViewerProps): JSX.Element => {
	const { token } = useAuth();
	const [logs, setLogs] = useState<LogResponse | null>(null);
	const [internalExpanded, setInternalExpanded] = useState<boolean>(false);
	const isControlled: boolean = expanded !== undefined;
	const logsExpanded: boolean = isControlled ? !!expanded : internalExpanded;
	const setLogsExpanded = (value: boolean): void => {
		if (!isControlled) setInternalExpanded(value);
		onExpandedChange?.(value);
	};
	const [logLines, setLogLines] = useState<number>(100);
	const logLinesRef = useRef<number>(100);
	const [error, setError] = useState<string | null>(null);

	// Update ref whenever logLines changes
	useEffect((): void => {
		logLinesRef.current = logLines;
	}, [logLines]);

	// Fetch logs using the ref
	const fetchLogs = async (): Promise<void> => {
		if (!token) return;
		setError(null);
		try {
			const data: ApiResponse<LogResponse> = await api.getLogs(logLinesRef.current, token);
			setLogs(data.data);
		} catch (err: any) {
			setError(err?.message || "Failed to fetch logs");
			console.error(err);
		}
	};

	useEffect(() => {
		void fetchLogs();
	}, []);

	const handleShowMoreLogs = (): void => {
		setLogLines((prev: number): number => Math.min(prev + 100, logs?.total_lines || prev));
	};

	useEffect(() => {
		if (!logsExpanded) return;

		void fetchLogs();

		const pollInterval: 3000 | null = isServiceRunning ? 3000 : null;
		if (pollInterval !== null) {
			const interval = setInterval(fetchLogs, pollInterval);
			return (): void => clearInterval(interval);
		}
	}, [logsExpanded, token, logLines, isServiceRunning]);

	return (
		<div className="log-section" id={id}>
			<button
				className="log-toggle"
				onClick={() => {
					setLogsExpanded(!logsExpanded);
					setError(null);
				}}
			>
				<span className={`log-caret ${logsExpanded ? "expanded" : ""}`}>
					<i className="bi bi-chevron-right" />
				</span>
				View Log File
				{logs && (
					<>
						<span className="log-count"> ({logs.total_lines} total lines)</span>
						{serviceStatus?.last_log && <span className="log-preview"> - {serviceStatus?.last_log}</span>}
					</>
				)}
			</button>

			<div className={`log-viewer-wrapper ${logsExpanded ? "open" : ""}`}>
				<div className="log-viewer-inner">
					<div className="log-viewer">
						{error && (
							<div className="log-error">
								<span className="log-error-message">{error}</span>
								<button
									className="log-retry"
									onClick={(): void => {
										setError(null);
										fetchLogs().then();
									}}
								>
									Retry
								</button>
							</div>
						)}

						{logs ? (
							<>
								<div className="log-header">
									<span>
										Showing last {logs.lines.length} of {logs.total_lines} lines
									</span>
									{logs.lines.length < logs.total_lines && (
										<button className="log-load-more" onClick={handleShowMoreLogs}>
											Load 100 More
										</button>
									)}
								</div>
								<pre className="log-content">
									{[...logs.lines].reverse().map((line: string, idx: number): JSX.Element => {
										const lineNumber: number = logs.total_lines - idx;
										return (
											<div key={idx} className="log-line">
												<span className="log-line-number">{lineNumber}</span>
												<span className="log-line-content">{line}</span>
											</div>
										);
									})}
								</pre>
							</>
						) : (
							!error && <LoadingSpinner text="Loading..." textColor="white" />
						)}
					</div>
				</div>
			</div>
		</div>
	);
};

export default LogViewer;
