import React, { JSX, useCallback, useEffect, useRef, useState } from "react";
import { LogProvider, LogResponse } from "../../../services/api/Services";
import { useAuth } from "../../../contexts/AuthContext";
import LoadingSpinner from "../../../components/Spinner/Spinner";
import "./LogViewer.scss";
import { ApiResponse } from "../../../services/api/Base";

/**
 * Controls a (controlled) LogViewer: tracks its expanded state and exposes `open`, which
 * expands the viewer and scrolls it into view once the expand animation has finished.
 */
export const useLogViewerToggle = (
	logViewerId: string,
	initialExpanded: boolean = false
): { expanded: boolean; setExpanded: (value: boolean) => void; open: () => void } => {
	const [expanded, setExpanded] = useState<boolean>(initialExpanded);
	const open = useCallback((): void => {
		setExpanded(true);
		// Wait for the expand animation (0.25s) so the page has grown enough to scroll
		// the bottom widget fully into view.
		window.setTimeout(() => {
			document.getElementById(logViewerId)?.scrollIntoView({ behavior: "smooth", block: "start" });
		}, 300);
	}, [logViewerId]);
	return { expanded, setExpanded, open };
};

type LogLevel = "debug" | "info" | "warning" | "error" | "critical" | "";

interface ClassifiedLine {
	line: string;
	level: LogLevel;
}

const LEVEL_RE = /\s-\s(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s-\s/;
const TIMESTAMP_RE = /^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}/;

/**
 * Tag each log line with its level so it can be coloured. The backend file format is
 * `timestamp - name - LEVEL - func:line - message`. Multi-line tracebacks have no level
 * prefix, so a continuation line (no leading timestamp) inherits the preceding level.
 */
const classifyLogLines = (lines: string[]): ClassifiedLine[] => {
	let current: LogLevel = "";
	return lines.map((line: string): ClassifiedLine => {
		const match = line.match(LEVEL_RE);
		if (match) {
			current = match[1]!.toLowerCase() as LogLevel;
			return { line, level: current };
		}
		// A new timestamped line with an unrecognised level resets the context.
		if (TIMESTAMP_RE.test(line)) {
			current = "";
			return { line, level: "" };
		}
		// Continuation line (e.g. a traceback) inherits the current level.
		return { line, level: current };
	});
};

interface LogViewerProps {
	api: LogProvider;
	isServiceRunning: boolean;
	id?: string;
	/** Controlled expansion. When provided, internal state is bypassed. */
	expanded?: boolean;
	onExpandedChange?: (expanded: boolean) => void;
}

const LogViewer = ({ api, isServiceRunning, id, expanded, onExpandedChange }: LogViewerProps): JSX.Element => {
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
		<div className="log-section status-card" id={id}>
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
				{logs && logs.lines.length > 0 && (
					<span className="log-preview"> - {logs.lines[logs.lines.length - 1]}</span>
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
									{classifyLogLines(logs.lines)
										.reverse()
										.map((entry: ClassifiedLine, idx: number): JSX.Element => {
											const lineNumber: number = logs.total_lines - idx;
											return (
												<div
													key={idx}
													className={`log-line${entry.level ? ` log-line--${entry.level}` : ""}`}
												>
													<span className="log-line-number">{lineNumber}</span>
													<span className="log-line-content">{entry.line}</span>
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
