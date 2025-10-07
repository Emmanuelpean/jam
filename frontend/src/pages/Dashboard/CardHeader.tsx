import { Card } from "react-bootstrap";

interface TableCardHeaderProps {
	icon: string;
	title: string;
	subtitle: string;
	badgeValue?: number;
}

export const CardHeader: React.FC<TableCardHeaderProps> = ({ icon, title, subtitle, badgeValue }) => (
	<Card.Header className="table-card-header border-0 p-0 bg-white">
		<div className="d-flex align-items-center justify-content-between p-4">
			<div className="d-flex align-items-center">
				<div className="header-icon-wrapper me-3">
					<i className={`bi bi-${icon}`}></i>
				</div>
				<div>
					<h5 className="mb-0 fw-bold text-dark">{title}</h5>
					<small className="text-muted">{subtitle}</small>
				</div>
			</div>
			{badgeValue != null && <div className="table-count-badge">{badgeValue}</div>}
		</div>
	</Card.Header>
);
