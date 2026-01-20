import React, { JSX, useEffect, useRef, useState } from "react";
import { BaseServiceApi, LogResponse } from "../../../services/api/Services";
import { useAuth } from "../../../contexts/AuthContext";
import LoadingSpinner from "../../../components/spinner/Spinner";
import "./LogViewer.scss";
import { ApiResponse } from "../../../services/api/Base";

interface LogViewerProps {
	api: BaseServiceApi;
	isServiceRunning: boolean;
}

const LogViewer = ({ api, isServiceRunning }: LogViewerProps): JSX.Element => {
	const { token } = useAuth();
	const [logs, setLogs] = useState<LogResponse | null>(null);
	const [logsExpanded, setLogsExpanded] = useState<boolean>(false);
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

	const handleShowMoreLogs = (): void => {
		setLogLines((prev: number): number => Math.min(prev + 100, logs?.total_lines || prev));
	};

	// This effect now doesn't need logLines in dependencies
	useEffect(() => {
		if (!logsExpanded) return;

		fetchLogs().then(); // Initial fetch

		const pollInterval: 3000 | null = isServiceRunning ? 3000 : null;
		if (pollInterval !== null) {
			const interval = setInterval(fetchLogs, pollInterval);
			return (): void => clearInterval(interval);
		}
	}, [logsExpanded, token, logLines, isServiceRunning]);

	return (
		<div className="log-section">
			<button
				className="log-toggle"
				onClick={() => {
					setLogsExpanded(!logsExpanded);
					setError(null);
				}}
			>
				{logsExpanded ? "▼" : "▶"} View Log File
				{logs && (
					<>
						<span className="log-count"> ({logs.total_lines} total lines)</span>
						{logs.lines.length > 0 && !logsExpanded && (
							<span className="log-preview">
								{" "}
								- {logs.lines[logs.lines.length - 1]}
							</span>
						)}
					</>
				)}
			</button>

			{logsExpanded && (
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
								{logs.lines.map((line: string, idx: number): JSX.Element => {
									const lineNumber: number =
										logs.total_lines - logs.lines.length + idx + 1;
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
			)}
		</div>
	);
};

export default LogViewer;
