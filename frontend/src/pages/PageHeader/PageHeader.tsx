import React, { JSX } from "react";
import "./PageHeader.scss";
import { Card } from "react-bootstrap";

interface TableHeaderProps {
	title: string;
	count?: number;
	icon: string;
	className?: string;
	id?: string;
	onClick?: () => void;
	active?: boolean;
}

const PageHeader: React.FC<TableHeaderProps> = ({
	title,
	count,
	icon,
	className = "",
	id,
	onClick,
	active = false,
}: TableHeaderProps): JSX.Element => {
	return (
		<div
			id={id}
			className={`mb-4 page-header ${onClick ? "page-header-clickable" : ""} ${onClick && active ? "page-header-active" : ""} ${className}`}
			onClick={onClick}
		>
			<Card className="h-100 shadow-sm border-0 rounded-3">
				<div className="d-flex align-items-center justify-content-between" style={{ padding: "1rem 1.5rem" }}>
					<div className="d-flex align-items-center">
						<div className="header-icon-wrapper me-2">
							<i className={`bi bi-${icon}`}></i>
						</div>
						<div>
							<h4 className="mb-0 fw-bold mx-2 me-3">{title}</h4>
						</div>
					</div>
					{count !== undefined && <div className="table-count-badge">{count}</div>}
				</div>
			</Card>
		</div>
	);
};

export default PageHeader;
