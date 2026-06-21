import React, { JSX, useEffect, useRef, useState } from "react";
import "./PageHeader.scss";
import { Card } from "react-bootstrap";
import { useViewport } from "../../contexts/ViewportContext";
import { MobileNavMenu } from "../../components/Sidebar/MobileNavMenu";

interface TableHeaderProps {
	title: string;
	count?: number;
	icon: string;
	className?: string;
	id?: string;
	onClick?: () => void;
	active?: boolean;
	statusContent?: React.ReactNode;
}

const PageHeader: React.FC<TableHeaderProps> = ({
	title,
	count,
	icon,
	className = "",
	id,
	onClick,
	active = false,
	statusContent,
}: TableHeaderProps): JSX.Element => {
	const { isMobile } = useViewport();
	const [menuOpen, setMenuOpen] = useState<boolean>(false);
	const wrapperRef = useRef<HTMLDivElement | null>(null);

	useEffect(() => {
		if (!menuOpen) return;
		const handleClickOutside = (event: MouseEvent): void => {
			if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
				setMenuOpen(false);
			}
		};
		document.addEventListener("mousedown", handleClickOutside);
		return () => document.removeEventListener("mousedown", handleClickOutside);
	}, [menuOpen]);

	const toggleMenu = (): void => setMenuOpen((prev: boolean): boolean => !prev);

	const headerOpensMenu: boolean = isMobile && !onClick;

	const handleHeaderClick = (): void => {
		if (headerOpensMenu) {
			toggleMenu();
		} else {
			onClick?.();
		}
	};

	const clickable: boolean = Boolean(onClick) || headerOpensMenu;

	return (
		<div
			ref={wrapperRef}
			id={id}
			className={`mb-4 page-header ${clickable ? "page-header-clickable" : ""} ${onClick && active ? "page-header-active" : ""} ${isMobile ? "page-header-mobile" : ""} ${className}`}
			onClick={clickable ? handleHeaderClick : undefined}
		>
			<Card className="h-100 shadow-sm border-0 rounded-3">
				<div className="d-flex align-items-center justify-content-between" style={{ padding: "0.8rem 1.5rem" }}>
					<div className="d-flex align-items-center">
						<div className="header-icon-wrapper me-2">
							<i className={`bi bi-${icon}`}></i>
						</div>
						<div>
							<h4 className="mb-0 fw-bold mx-2 me-3">{title}</h4>
						</div>
						{isMobile && (
							<button
								type="button"
								className={`page-header-menu-toggle ${menuOpen ? "open" : ""}`}
								aria-label="Open navigation menu"
								aria-expanded={menuOpen}
								onClick={(e: React.MouseEvent): void => {
									e.stopPropagation();
									toggleMenu();
								}}
							>
								<i className="bi bi-chevron-right"></i>
							</button>
						)}
					</div>
					{count !== undefined && <div className="table-count-badge">{count}</div>}
					{statusContent}
				</div>
			</Card>
			{isMobile && <MobileNavMenu open={menuOpen} onClose={() => setMenuOpen(false)} />}
		</div>
	);
};

export default PageHeader;
