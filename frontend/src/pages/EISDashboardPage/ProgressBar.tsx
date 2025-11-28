import { JSX } from "react";
import "./ProgressBar.css";

interface ProgressBarProps {
	title: string;
	current: number;
	total: number;
	width?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
	title,
	current,
	total,
	width = "350px",
}: ProgressBarProps): JSX.Element => {
	return (
		<div style={{ flex: 1, minWidth: 0 }}>
			<span style={{ fontWeight: "bold" }}>{title}</span>
			<div className="progressbar-div">
				<div className="progress" style={{ width }}>
					<div
						className="progress-bar"
						role="progressbar"
						style={{ width: `${(current / total) * 100}%` }}
						aria-valuenow={(current / total) * 100}
						aria-valuemin={0}
						aria-valuemax={100}
					/>
				</div>
				<span>
					{current}/{total}
				</span>
			</div>
		</div>
	);
};

export default ProgressBar;
