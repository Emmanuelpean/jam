import React, { JSX } from "react";
import PageHeader from "./PageHeader";
import { useViewport } from "../../contexts/ViewportContext";

export interface PageHeaderTab {
	id: string;
	title: string;
	icon: string;
	count?: number;
	/** DOM id for the rendered header, e.g. for tour/test selectors. Defaults to `${id}-header`. */
	headerId?: string;
}

interface PageHeaderGroupProps {
	tabs: PageHeaderTab[];
	activeId: string;
	onSelect: (tab: PageHeaderTab) => void;
	className?: string;
}

/**
 * Renders one PageHeader per tab side by side on desktop/tablet. On mobile, only the
 * active tab's header is shown (acting as that tab's own page) and tapping any visible
 * header's menu toggle still opens the shared nav — switching tabs happens via onSelect.
 */
export const PageHeaderGroup: React.FC<PageHeaderGroupProps> = ({
	tabs,
	activeId,
	onSelect,
	className = "",
}): JSX.Element => {
	const { isMobile } = useViewport();

	return (
		<div className={`d-flex gap-3 page-headers-row ${className}`}>
			{tabs
				.filter((tab: PageHeaderTab): boolean => !isMobile || tab.id === activeId)
				.map((tab: PageHeaderTab): JSX.Element => (
					<PageHeader
						key={tab.id}
						id={tab.headerId ?? `${tab.id}-header`}
						className="flex-fill"
						title={tab.title}
						icon={tab.icon}
						count={tab.count}
						onClick={isMobile ? undefined : (): void => onSelect(tab)}
						active={tab.id === activeId}
					/>
				))}
		</div>
	);
};

export default PageHeaderGroup;
