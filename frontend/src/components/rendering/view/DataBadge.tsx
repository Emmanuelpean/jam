import React, { JSX, MouseEvent, useRef } from "react";
import { MenuItem } from "../../ContextMenu/ContextMenu";
import { DataModalHandle } from "../../DataModal/DataModal";
import { useContextMenu } from "../../../contexts/ContextMenuContext";
import FollowUpModal, { FollowUpModalHandle } from "../../FollowUpModal/FollowUpModal";
import { LocationModal } from "../../DataModal/LocationModal";
import { CompanyModal } from "../../DataModal/CompanyModal";
import { PersonModal } from "../../DataModal/PersonModal";
import { KeywordModal } from "../../DataModal/KeywordModal";
import { JobModal } from "../../DataModal/JobModal";
import { AggregatorModal } from "../../DataModal/AggregatorModal";
import { JobApplicationUpdateModal } from "../../DataModal/JobApplicationUpdateModal";
import { InterviewModal } from "../../DataModal/InterviewModal";
import { useDeleteEntityConfirm } from "../../../utils/DeleteHandler";
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
	menuItemKeys?: string[];
	compact?: boolean;
}

// Create badge manager with modal integration
const createDataBadge = <T extends JamData>(
	ModalComponent: FlexibleModalComponent,
	entityType: EntityType,
	defaultBadgeClass: string = "bg-info",
	defaultDisplayText: (item: T) => string,
	defaultMenuItemKeys: string[] = ["view", "edit", "delete"]
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
		const dataModalRef = useRef<DataModalHandle>(null);
		const { openContextMenu } = useContextMenu();
		const followUpModalRef = useRef<FollowUpModalHandle>(null);
		const deleteHandler = useDeleteEntityConfirm(entityType);
		const dataContext: DataContextValue = useDataContext();
		const { showToastSuccess } = useGlobalToast();

		const handleRemove = (item: JamData): void => {
			if (parentItem && parentKey) {
				let updatedParent;
				if (Array.isArray((parentItem as any)[parentKey])) {
					updatedParent = {
						...parentItem,
						[parentKey]: (parentItem as any)[parentKey].filter(
							(itemId: number): boolean => itemId !== item.id
						),
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
			{ action: "view", icon: "eye", text: "View", function: dataModalRef.current?.showView },
			{ action: "edit", icon: "pencil", text: "Edit", function: dataModalRef.current?.showEdit },
			{
				action: "delete",
				icon: "trash",
				text: "Delete",
				color: "#dc3545",
				function: deleteHandler,
			},
			{
				action: "remove",
				icon: "x-circle",
				text: "Remove",
				color: "#ff8e3f",
				function: handleRemove,
			},
			{
				action: "followup",
				icon: "bell",
				text: "Follow-up Email",
				function: (item: JamData): void => {
					followUpModalRef.current?.show(parentItem as JobData, item as PersonData);
				},
				displayCondition: (item: JamData): boolean => !!((item as PersonData).email && parentItem),
			},
		];

		const menuItems: MenuItem[] = availableMenuItems.filter((menuItem: MenuItem): boolean =>
			menuItemKeys.includes(menuItem.action)
		);

		const handleContextMenu = (e: MouseEvent<HTMLSpanElement>) => {
			if (menuItems.length === 0) return;
			if (!item) return;
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
					onClick={() => item && dataModalRef.current?.showView(item)}
					onContextMenu={handleContextMenu}
					id={badgeId}
				>
					<i className={`bi bi-${icon || getEntityIcon(entityType)} me-2`}></i>
					{getText()}
				</span>
				<ModalComponent ref={dataModalRef} />
				<FollowUpModal ref={followUpModalRef} />
			</>
		);
	};
};

export const PersonBadge = createDataBadge(
	PersonModal,
	"person",
	"bg-info",
	(item: PersonData): string => item.name,
	["view", "edit", "delete", "followup"]
);
export const CompanyBadge = createDataBadge(
	CompanyModal,
	"company",
	"bg-success",
	(item: CompanyData): string => item.name
);
export const LocationBadge = createDataBadge(
	LocationModal,
	"location",
	"bg-warning",
	(item: LocationData): string => item.name
);
export const KeywordBadge = createDataBadge(
	KeywordModal,
	"keyword",
	"bg-secondary",
	(item: KeywordData): string => item.name
);
export const JobBadge = createDataBadge(JobModal, "job", "bg-primary", (item: JobData): string => item.name);
export const AggregatorBadge = createDataBadge(
	AggregatorModal,
	"aggregator",
	"bg-dark",
	(item: AggregatorData): string => item.name
);
export const JobApplicationUpdateBadge = createDataBadge(
	JobApplicationUpdateModal,
	"jobApplicationUpdate",
	"bg-info",
	(item: JobData): string => item.title
);
export const InterviewBadge = createDataBadge(
	InterviewModal,
	"interview",
	"bg-success",
	(item: JobData): string => item.title
);
