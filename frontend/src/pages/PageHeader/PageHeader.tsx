import React, { JSX } from "react";
import "./PageHeader.scss";
import { Card } from "react-bootstrap";

interface TableHeaderProps {
	title: string;
	subtitle?: string;
	count?: number;
	icon: string;
	onClick?: () => void;
	active?: boolean;
}

const PageHeader: React.FC<TableHeaderProps> = ({
	title,
	count,
	icon,
	subtitle,
	onClick,
	active = false,
}: TableHeaderProps): JSX.Element => {
	return (
		<div
			className={`mb-4 page-header ${onClick ? "page-header-clickable" : ""} ${onClick && active ? "page-header-active" : ""} flex-fill`}
			onClick={onClick}
		>
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
					</div>
					{count !== undefined && <div className="table-count-badge">{count}</div>}
				</div>
			</Card>
		</div>
	);
};

export default PageHeader;
