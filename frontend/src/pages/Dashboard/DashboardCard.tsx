import React, { ReactNode } from "react";
import { Card } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import "./DashboardPage.scss";

export interface EmptyStateProps {
	icon: string;
	title: string;
	description: string;
}

export interface DashboardCardProps {
	icon: string;
	title: string;
	subtitle?: string;
	badgeValue?: number;
	path?: string;
	onHeaderClick?: () => void;
	isEmpty?: boolean;
	emptyState?: EmptyStateProps;
	children: ReactNode;
	className?: string;
	bodyPadding?: boolean;
}

export const DashboardCard: React.FC<DashboardCardProps> = ({
	icon,
	title,
	subtitle,
	badgeValue,
	path,
	onHeaderClick,
	isEmpty = false,
	emptyState,
	children,
	className = "",
	bodyPadding = true,
}: DashboardCardProps): JSX.Element => {
	const navigate = useNavigate();

	const handleHeaderClick = (): void => {
		if (onHeaderClick) {
			onHeaderClick();
		}
		if (path) {
			navigate(path);
		}
	};

	const renderEmptyState = (): ReactNode => {
		if (!emptyState) return null;

		return (
			<div className="text-center py-5 px-4 flex-grow-1 d-flex flex-column justify-content-center">
				<div className="mb-3">
					<i className={`bi bi-${emptyState.icon} text-muted`} style={{ fontSize: "3.5rem" }}></i>
				</div>
				<h6 className="text-muted fw-semibold">{emptyState.title}</h6>
				<p className="text-muted small mb-0">{emptyState.description}</p>
			</div>
		);
	};

	return (
		<Card className={`shadow-sm border-0 h-100 d-flex flex-column ${className}`}>
			<Card.Header className="table-card-header border-0 p-0">
				<div className="d-flex align-items-center justify-content-between p-4">
					<div
						className="d-flex align-items-center"
						onClick={handleHeaderClick}
						style={{ cursor: path || onHeaderClick ? "pointer" : "default" }}
					>
						<div className="header-icon-wrapper me-3">
							<i className={`bi bi-${icon}`}></i>
						</div>
						<div>
							<h5 className="mb-0 fw-bold">{title}</h5>
							{subtitle && <small className="text-muted">{subtitle}</small>}
						</div>
					</div>
					{badgeValue != null && <div className="table-count-badge">{badgeValue}</div>}
				</div>
			</Card.Header>
			<Card.Body className="p-0 flex-grow-1 d-flex flex-column overflow-auto" style={{ minHeight: 0 }}>
				{isEmpty && emptyState ? (
					renderEmptyState()
				) : (
					<div className={bodyPadding ? "px-3" : ""} style={{ flexGrow: 1 }}>
						{children}
					</div>
				)}
			</Card.Body>
		</Card>
	);
};

export default DashboardCard;
