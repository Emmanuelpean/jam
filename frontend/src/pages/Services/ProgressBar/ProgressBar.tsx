import { JSX } from "react";
import "./ProgressBar.scss";

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
	width = "100%",
}: ProgressBarProps): JSX.Element => {
	const percentage: number = total > 0 ? (current / total) * 100 : 0;
	return (
		<div style={{ flex: 1, minWidth: 0 }}>
			<span style={{ fontWeight: "bold" }}>{title}</span>
			<div className="progressbar-div">
				<div className="progress" style={{ width }}>
					<div
						className="progress-bar"
						role="progressbar"
						style={{ width: `${percentage}%` }}
						aria-valuenow={percentage}
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
