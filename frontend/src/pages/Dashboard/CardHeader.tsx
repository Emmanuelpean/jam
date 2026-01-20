import { Card } from "react-bootstrap";
import { useNavigate } from "react-router-dom"; // <- client-side navigation
import "./DashboardPage.scss";

interface TableCardHeaderProps {
	icon: string;
	title: string;
	subtitle: string;
	badgeValue?: number;
	path?: string;
	onClick?: () => void;
}

export const CardHeader: React.FC<TableCardHeaderProps> = ({
	icon,
	title,
	subtitle,
	badgeValue,
	path,
	onClick,
}) => {
	const navigate = useNavigate();

	const handleClick = (): void => {
		if (onClick) {
			onClick();
		}
		if (path) {
			navigate(path); // navigate client-side without reload
		}
	};

	const content = (
		<div
			className="d-flex align-items-center"
			style={{ cursor: path || onClick ? "pointer" : "default" }}
		>
			<div className="header-icon-wrapper me-3">
				<i className={`bi bi-${icon}`}></i>
			</div>
			<div>
				<h5 className="mb-0 fw-bold">{title}</h5>
				<small className="text-muted">{subtitle}</small>
			</div>
		</div>
	);

	return (
		<Card.Header className="table-card-header border-0 p-0" onClick={handleClick}>
			<div className="d-flex align-items-center justify-content-between p-4">
				{content}
				{badgeValue != null && <div className="table-count-badge">{badgeValue}</div>}
			</div>
		</Card.Header>
	);
};
