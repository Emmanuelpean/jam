import React, { JSX } from "react";

export interface Feature {
	icon: string;
	title: string;
	description: string;
}

interface AppFeaturesListProps {
	features: Feature[];
	className?: string;
}

const AppFeaturesList = ({ features, className }: AppFeaturesListProps): JSX.Element => (
	<div className={`features-grid${className ? ` ${className}` : ""}`}>
		{features.map(
			(feature: Feature, index: number): JSX.Element => (
				<div className="feature-card p-4" key={index}>
					<div className="d-flex align-items-start align-items-center">
						<div className="feature-icon me-3">
							<i className={`bi ${feature.icon}`} style={{ fontSize: "2rem" }} />
						</div>
						<div>
							<h5 className="fw-bold mb-1">{feature.title}</h5>
							<p className="about-text-muted mb-0">{feature.description}</p>
						</div>
					</div>
				</div>
			)
		)}
	</div>
);

export default AppFeaturesList;
