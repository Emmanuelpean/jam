import React, { JSX } from "react";
import "./PageHeader.scss";
import { Card } from "react-bootstrap";

export interface FilterPill {
	key: string;
	label: string;
	summary: string;
	onRemove: () => void;
}

interface TableHeaderProps {
	title: string;
	subtitle?: string;
	count?: number;
	icon: string;
	className?: string;
	filterPills?: FilterPill[];
}

const PageHeader: React.FC<TableHeaderProps> = ({
	title,
	count,
	icon,
	subtitle,
	className = "",
	filterPills,
}: TableHeaderProps): JSX.Element => {
	return (
		<div className={`mb-4 ${className}`}>
			<Card className="h-100 shadow-sm border-0 rounded-3">
				<div className="d-flex align-items-center justify-content-between p-4">
					<div className="d-flex align-items-center">
						<div className="header-icon-wrapper me-3">
							<i className={`bi bi-${icon}`}></i>
						</div>
						<div>
							<h4 className="mb-0 fw-bold">{title}</h4>
							{subtitle && <small className="text-muted">{subtitle}</small>}
						</div>
						{filterPills && filterPills.length > 0 && (
							<div className="header-filter-pills">
								{filterPills.map((pill) => (
									<span key={pill.key} className="header-filter-pill">
										<span className="header-filter-pill-label">{pill.label}:</span>
										<span className="header-filter-pill-value">{pill.summary}</span>
										<button
											type="button"
											className="header-filter-pill-remove"
											onClick={pill.onRemove}
											aria-label={`Remove ${pill.label} filter`}
										>
											<i className="bi bi-x" />
										</button>
									</span>
								))}
							</div>
						)}
					</div>
					{count !== undefined && <div className="table-count-badge">{count}</div>}
				</div>
			</Card>
		</div>
	);
};

export default PageHeader;
