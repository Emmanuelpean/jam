import React, { JSX, MouseEvent, useRef } from "react";
import { MenuItem, MenuItemKey } from "../../tables/ContextMenu";
import { DataModalHandle } from "../../modals/DataModal/DataModal";
import { useContextMenu } from "../../../contexts/ContextMenuContext";
import FollowUpModal, { FollowUpModalHandle } from "../../modals/FollowUpModal";
import { LocationModal } from "../../modals/LocationModal";
import { CompanyModal } from "../../modals/CompanyModal";
import { PersonModal } from "../../modals/PersonModal";
import { KeywordModal } from "../../modals/KeywordModal";
import { JobModal } from "../../modals/JobModal";
import { AggregatorModal } from "../../modals/AggregatorModal";
import { JobApplicationUpdateModal } from "../../modals/JobApplicationUpdateModal";
import { InterviewModal } from "../../modals/InterviewModal";
import { useDeleteEntity } from "../../../utils/DeleteHandler";
import { DataContextValue, EntityType, JamData, useDataContext } from "../../../contexts/DataContext";
import { getEntityIcon } from "./Icons";
import { useGlobalToast } from "../../../hooks/useNotificationToast";
import {
	AggregatorData,
	CompanyData,
	JobData,
	KeywordData,
	LocationData,
	PersonData,
} from "../../../services/schemas/DataTables";

type FlexibleModalComponent = React.ForwardRefExoticComponent<any>;

export interface DataBadgeProps<T extends JamData> {
	item: T | undefined;
	badgeId: string;
	parentItem?: JamData;
	parentKey?: string;
	parentEntityType?: EntityType;
	icon?: string;
	displayText?: string | ((item: T) => string);
	badgeClass?: string;
	menuItemKeys?: MenuItemKey[];
	compact?: boolean;
}

// Create badge manager with modal integration
const createBadgeModalManager = <T extends JamData>(
	ModalComponent: FlexibleModalComponent,
	entityType: EntityType,
	defaultBadgeClass: string = "bg-info",
	defaultDisplayText: (item: T) => string,
	defaultMenuItemKeys: MenuItemKey[] = ["view", "edit", "delete"],
) => {
	return ({
		item,
		badgeId,
		parentItem,
		parentKey,
		parentEntityType,
		icon,
		displayText = defaultDisplayText,
		badgeClass = defaultBadgeClass,
		menuItemKeys = defaultMenuItemKeys,
		compact = true,
	}: DataBadgeProps<T>): JSX.Element => {
		const modalRef = useRef<DataModalHandle>(null);
		const { openContextMenu } = useContextMenu();
		const followUpModalRef = useRef<FollowUpModalHandle>(null);
		const deleteHandler = useDeleteEntity(entityType);
		const dataContext: DataContextValue = useDataContext();
		const { showToastSuccess } = useGlobalToast();

		const handleRemove = (id: number): void => {
			if (parentItem && parentKey) {
				let updatedParent;
				if (Array.isArray((parentItem as any)[parentKey])) {
					updatedParent = {
						...parentItem,
						[parentKey]: (parentItem as any)[parentKey].filter((itemId: number): boolean => itemId !== id),
					};
				} else {
					updatedParent = {
						...parentItem,
						[parentKey]: null,
					};
				}
				if (parentEntityType) {
					dataContext.updateEntity(parentEntityType, parentItem.id, updatedParent).then((_) => {
						showToastSuccess("Association removed successfully.");
					});
				}
			}
		};
		const availableMenuItems: MenuItem[] = [
			{ action: "view", icon: "eye", text: "View", function: modalRef.current?.showView },
			{ action: "edit", icon: "pencil", text: "Edit", function: modalRef.current?.showEdit },
			{ action: "delete", icon: "trash", text: "Delete", color: "#dc3545", function: deleteHandler },
			{
				action: "remove",
				icon: "x-circle",
				text: "Remove",
				color: "#dc3545",
				function: handleRemove,
			},
			{
				action: "followup",
				icon: "bell",
				text: "Follow-up Email",
				function: (item: PersonData): void => {
					followUpModalRef.current?.show(parentItem as JobData, item);
				},
				displayCondition: (item: PersonData): boolean => !!(item.email && parentItem),
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
			if (typeof displayText === "function") {
				return item ? displayText(item) : "";
			} else if (displayText) {
				return displayText;
			} else {
				return "";
			}
		};

		return (
			<>
				<span
					className={`badge ${badgeClass} clickable-badge`}
					onClick={() => item && modalRef.current?.showView(item)}
					onContextMenu={handleContextMenu}
					id={badgeId}
				>
					<i className={`bi bi-${icon || getEntityIcon(entityType)} me-2`}></i>
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
	"bg-info",
	(item: PersonData): string => item.name,
	["view", "edit", "delete", "followup"],
);
export const CompanyBadge = createBadgeModalManager(
	CompanyModal,
	"company",
	"bg-success",
	(item: CompanyData): string => item.name,
);
export const LocationBadge = createBadgeModalManager(
	LocationModal,
	"location",
	"bg-warning",
	(item: LocationData): string => item.name,
);
export const KeywordBadge = createBadgeModalManager(
	KeywordModal,
	"keyword",
	"bg-secondary",
	(item: KeywordData): string => item.name,
);
export const JobBadge = createBadgeModalManager(JobModal, "job", "bg-primary", (item: JobData): string => item.name);
export const AggregatorBadge = createBadgeModalManager(
	AggregatorModal,
	"aggregator",
	"bg-dark",
	(item: AggregatorData): string => item.name,
);
export const JobApplicationUpdateBadge = createBadgeModalManager(
	JobApplicationUpdateModal,
	"jobApplicationUpdate",
	"bg-info",
	(item: JobData): string => item.title,
);
export const InterviewBadge = createBadgeModalManager(
	InterviewModal,
	"interview",
	"bg-primary",
	(item: JobData): string => item.title,
);
