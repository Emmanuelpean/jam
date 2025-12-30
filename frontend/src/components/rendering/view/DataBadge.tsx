import React, { JSX, MouseEvent, useRef } from "react";
import { MenuItem, MenuItemKey } from "../../tables/ContextMenu";
import { DataModalHandle } from "../../modals/DataModal/DataModal";
import { useContextMenu } from "../../../contexts/ContextMenuContext";
import FollowUpModal, { FollowUpModalHandle } from "../../modals/FollowUpModal";
import { AggregatorData, CompanyData, JobData, KeywordData, LocationData, PersonData } from "../../../services/Schemas";
import { LocationModal } from "../../modals/LocationModal";
import { CompanyModal } from "../../modals/CompanyModal";
import { PersonModal } from "../../modals/PersonModal";
import { KeywordModal } from "../../modals/KeywordModal";
import { JobModal } from "../../modals/JobModal";
import { AggregatorModal } from "../../modals/AggregatorModal";
import { JobApplicationUpdateModal } from "../../modals/JobApplicationUpdateModal";
import { InterviewModal } from "../../modals/InterviewModal";
import { useDeleteEntity } from "../../../utils/DeleteHandler";
import { EntityType } from "../../../contexts/DataContext";

type FlexibleModalComponent = React.ForwardRefExoticComponent<any>;

export interface DataBadgeProps<T> {
	item: T;
	badgeId?: string;
	icon?: string;
	displayText?: string | ((item: T) => string);
	badgeClass?: string;
	menuItemKeys?: MenuItemKey[];
	compact?: boolean;
}

// Create badge manager with modal integration
const createBadgeModalManager = <T,>(
	ModalComponent: FlexibleModalComponent,
	entityType: EntityType,
	defaultIcon: string,
	defaultBadgeClass: string = "bg-info",
	defaultDisplayText: (item: T) => string,
	defaultMenuItemKeys: MenuItemKey[] = ["view", "edit", "delete"],
) => {
	return ({
		item,
		badgeId,
		icon = defaultIcon,
		displayText = defaultDisplayText,
		badgeClass = defaultBadgeClass,
		menuItemKeys = defaultMenuItemKeys,
		compact = true,
	}: DataBadgeProps<T>): JSX.Element => {
		const modalRef = useRef<DataModalHandle>(null);
		const { openContextMenu } = useContextMenu();
		const followUpModalRef = useRef<FollowUpModalHandle>(null);
		const deleteHandler = useDeleteEntity(entityType);

		const availableMenuItems: MenuItem[] = [
			{ action: "view", icon: "eye", text: "View", function: modalRef.current?.showView },
			{ action: "edit", icon: "pencil", text: "Edit", function: modalRef.current?.showEdit },
			{ action: "delete", icon: "trash", text: "Delete", color: "#dc3545", function: deleteHandler },
			{
				action: "followup",
				icon: "bell",
				text: "Follow-up Email",
				color: "#0d6efd",
				function: followUpModalRef.current?.show,
			},
		];

		const menuItems: MenuItem[] = availableMenuItems.filter((menuItem: MenuItem): boolean =>
			menuItemKeys.includes(menuItem.action),
		);

		const handleContextMenu = (e: MouseEvent<HTMLSpanElement>) => {
			if (menuItems.length === 0) return;

			openContextMenu(e, menuItems, item, compact);
		};

		const getText = (): string => {
			return typeof displayText === "function" ? displayText(item) : displayText;
		};

		return (
			<>
				<span
					className={`badge ${badgeClass} clickable-badge`}
					onClick={() => modalRef.current?.showView(item)}
					onContextMenu={handleContextMenu}
					id={badgeId}
				>
					<i className={`bi bi-${icon} me-1`}></i>
					{getText()}
				</span>
				<ModalComponent ref={modalRef} />
				<FollowUpModal ref={followUpModalRef} />
			</>
		);
	};
};

export const PersonBadge = createBadgeModalManager(
	PersonModal,
	"person",
	"file-person",
	"bg-info",
	(item: PersonData): string => item.name,
	["view", "edit", "delete", "followup"],
);
export const CompanyBadge = createBadgeModalManager(
	CompanyModal,
	"company",
	"building",
	"bg-success",
	(item: CompanyData): string => item.name,
);
export const LocationBadge = createBadgeModalManager(
	LocationModal,
	"location",
	"geo-alt",
	"bg-warning",
	(item: LocationData): string => item.name,
);
export const KeywordBadge = createBadgeModalManager(
	KeywordModal,
	"keyword",
	"tag",
	"bg-secondary",
	(item: KeywordData): string => item.name,
);
export const JobBadge = createBadgeModalManager(
	JobModal,
	"job",
	"briefcase",
	"bg-primary",
	(item: JobData): string => item.title,
);
export const AggregatorBadge = createBadgeModalManager(
	AggregatorModal,
	"aggregator",
	"collection",
	"bg-dark",
	(item: AggregatorData): string => item.name,
);
export const JobApplicationUpdateBadge = createBadgeModalManager(
	JobApplicationUpdateModal,
	"jobApplicationUpdate",
	"arrow-repeat",
	"bg-info",
	(item: JobData): string => item.title,
);
export const InterviewBadge = createBadgeModalManager(
	InterviewModal,
	"interview",
	"calendar-check",
	"bg-primary",
	(item: JobData): string => item.title,
);
