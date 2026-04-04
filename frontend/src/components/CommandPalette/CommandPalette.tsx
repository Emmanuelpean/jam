import React, { JSX, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getEntityIcon, getTableIcon } from "../rendering/view/Icons";
import "./CommandPalette.scss";

interface CommandItem {
	id: string;
	label: string;
	icon: string;
	group: "Actions" | "Pages";
	shortcut?: string[];
	action: () => void;
}

interface CommandPaletteProps {
	isOpen: boolean;
	onClose: () => void;
}

const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose }: CommandPaletteProps): JSX.Element | null => {
	const navigate = useNavigate();
	const [query, setQuery] = useState("");
	const [activeIndex, setActiveIndex] = useState(0);
	const [isRendered, setIsRendered] = useState(isOpen);
	const [isClosing, setIsClosing] = useState(false);
	const inputRef = useRef<HTMLInputElement>(null);
	const listRef = useRef<HTMLUListElement>(null);

	useEffect(() => {
		if (isOpen) {
			setIsRendered(true);
			setIsClosing(false);
			setQuery("");
			setActiveIndex(0);
		} else if (isRendered) {
			setIsClosing(true);
		}
	}, [isOpen]);

	const handleAnimationEnd = (): void => {
		if (isClosing) {
			setIsRendered(false);
			setIsClosing(false);
		}
	};

	const goTo = (path: string, state?: object): void => {
		navigate(path, state ? { state } : undefined);
		onClose();
	};

	const items = useMemo<CommandItem[]>(
		() => [
			{
				id: "add-job",
				label: "Add Job",
				icon: getEntityIcon("job"),
				group: "Actions",
				shortcut: ["J", "N"],
				action: () => goTo("/jobs", { quickAdd: true }),
			},
			{
				id: "goto-dashboard",
				label: "Dashboard",
				icon: getTableIcon("Dashboard"),
				group: "Pages",
				shortcut: ["J","D"],
				action: () => goTo("/dashboard"),
			},
			{
				id: "goto-jobs",
				label: "Jobs",
				icon: getTableIcon("Jobs"),
				group: "Pages",
				shortcut: ["J","J"],
				action: () => goTo("/jobs"),
			},
			{
				id: "goto-persons",
				label: "People",
				icon: getTableIcon("People"),
				group: "Pages",
				shortcut: ["J","P"],
				action: () => goTo("/persons"),
			},
			{
				id: "goto-companies",
				label: "Companies",
				icon: getTableIcon("Companies"),
				group: "Pages",
				shortcut: ["J","C"],
				action: () => goTo("/companies"),
			},
			{
				id: "goto-interviews",
				label: "Interviews",
				icon: getTableIcon("Interviews"),
				group: "Pages",
				shortcut: ["J","I"],
				action: () => goTo("/interviews"),
			},
			{
				id: "goto-speculative",
				label: "Speculative Applications",
				icon: getTableIcon("Speculative Applications"),
				group: "Pages",
				shortcut: ["J", "V"],
				action: () => goTo("/speculative-applications"),
			},
			{
				id: "goto-updates",
				label: "Job Application Updates",
				icon: getTableIcon("Job Application Updates"),
				group: "Pages",
				shortcut: ["J", "U"],
				action: () => goTo("/job-application-updates"),
			},
			{
				id: "goto-locations",
				label: "Locations",
				icon: getTableIcon("Locations"),
				group: "Pages",
				shortcut: ["J","L"],
				action: () => goTo("/locations"),
			},
			{
				id: "goto-aggregators",
				label: "Job Aggregators",
				icon: getTableIcon("Job Aggregators"),
				group: "Pages",
				shortcut: ["J","A"],
				action: () => goTo("/aggregators"),
			},
			{
				id: "goto-keywords",
				label: "Keywords",
				icon: getEntityIcon("keyword"),
				group: "Pages",
				shortcut: ["J","K"],
				action: () => goTo("/keywords"),
			},
			{
				id: "goto-settings",
				label: "Settings",
				icon: getTableIcon("User Settings"),
				group: "Pages",
				shortcut: ["J","S"],
				action: () => goTo("/settings"),
			},
		],
		[navigate, onClose]
	);

	const filtered = useMemo<CommandItem[]>(() => {
		if (!query.trim()) return items;
		const q = query.toLowerCase();
		return items.filter((item) => item.label.toLowerCase().includes(q));
	}, [items, query]);

	const groups = useMemo<string[]>(() => {
		const seen = new Set<string>();
		for (const item of filtered) {
			seen.add(item.group);
		}
		return Array.from(seen);
	}, [filtered]);

	useEffect(() => {
		setActiveIndex(0);
	}, [query]);

	useEffect(() => {
		if (isOpen) {
			setTimeout(() => inputRef.current?.focus(), 50);
		}
	}, [isOpen]);

	useEffect(() => {
		const active = listRef.current?.querySelector<HTMLLIElement>(`[data-index="${activeIndex}"]`);
		active?.scrollIntoView({ block: "nearest" });
	}, [activeIndex]);

	const handleKeyDown = (e: React.KeyboardEvent): void => {
		if (e.key === "Escape") {
			onClose();
		} else if (e.key === "ArrowDown") {
			e.preventDefault();
			setActiveIndex((i) => Math.min(i + 1, filtered.length - 1));
		} else if (e.key === "ArrowUp") {
			e.preventDefault();
			setActiveIndex((i) => Math.max(i - 1, 0));
		} else if (e.key === "Enter") {
			filtered[activeIndex]?.action();
		}
	};

	if (!isRendered) return null;

	let globalIndex = -1;

	return (
		<div
			id="cp-backdrop"
			className={`cp-backdrop ${isClosing ? "closing" : "opening"}`}
			onAnimationEnd={handleAnimationEnd}
			onMouseDown={(e) => {
				if (e.target === e.currentTarget) onClose();
			}}
		>
			<div className={`cp-card ${isClosing ? "closing" : "opening"}`}>
				<div className="cp-search">
					<i className="bi bi-search cp-search-icon" />
					<input
						ref={inputRef}
						id="cp-input"
						className="cp-input"
						placeholder="Search pages and actions..."
						value={query}
						onChange={(e) => setQuery(e.target.value)}
						onKeyDown={handleKeyDown}
					/>
					<span className="cp-esc-hint">Esc</span>
				</div>
				<ul className="cp-list" ref={listRef}>
					{filtered.length === 0 && <li id="cp-empty" className="cp-empty">No results for "{query}"</li>}
					{groups.map((group) => (
						<React.Fragment key={group}>
							<li id={`cp-group-${group.toLowerCase()}`} className="cp-group-header">{group}</li>
							{filtered
								.filter((item) => item.group === group)
								.map((item) => {
									globalIndex++;
									const idx = globalIndex;
									return (
										<li
											key={item.id}
											id={`cp-item-${item.id}`}
											data-index={idx}
											className={`cp-item ${activeIndex === idx ? "active" : ""}`}
											onMouseEnter={() => setActiveIndex(idx)}
											onMouseDown={() => item.action()}
										>
											<div className="cp-item-icon-wrapper">
												<i className={`bi bi-${item.icon} cp-item-icon`} />
											</div>
											<span className="cp-item-label">{item.label}</span>
											{item.shortcut && (
												<span className="cp-shortcut">
													{item.shortcut.map((key) => (
														<kbd key={key}>{key}</kbd>
													))}
												</span>
											)}
										</li>
									);
								})}
						</React.Fragment>
					))}
				</ul>
				<div className="cp-footer">
					<span style={{ marginLeft: "auto" }}><kbd>⇧⇧</kbd> or <kbd>Ctrl</kbd><kbd>K</kbd> to open</span>
				</div>
			</div>
		</div>
	);
};

export default CommandPalette;
