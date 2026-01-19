import React, { MouseEvent, useEffect, useRef, useState, JSX } from "react";
import "./ContextMenu.css";
import { EntityType, JamData } from "../../contexts/DataContext";

export interface MenuItem {
	action: string;
	icon?: string;
	text: string;
	color?: string;
	function?: (item: JamData) => Promise<boolean | void> | void;
	submenus?: MenuItem[];
	displayCondition?: (item: JamData) => boolean;
	loading?: boolean;
	showLoading?: boolean;
}

export interface ContextMenuPosition {
	x: number;
	y: number;
}

interface MenuLevelProps {
	menuItems: MenuItem[];
	entityType: EntityType;
	selectedItem: JamData;
	onItemClick: (menuItem: MenuItem, entityType: EntityType, item: JamData) => void;
	compact: boolean;
	position: ContextMenuPosition;
	isSubmenu?: boolean;
	onMouseEnter?: () => void;
	onMouseLeave?: () => void;
	onClose: () => void; // TODO remove?
	disabled?: boolean;
}

const MenuLevel: React.FC<MenuLevelProps> = ({
	menuItems,
	entityType,
	selectedItem,
	onItemClick,
	compact,
	position,
	onClose,
	isSubmenu = false,
	onMouseEnter,
	onMouseLeave,
	disabled = false,
}: MenuLevelProps): JSX.Element => {
	const [activeSubmenu, setActiveSubmenu] = useState<string | null>(null);
	const [submenuPosition, setSubmenuPosition] = useState<ContextMenuPosition>({ x: 0, y: 0 });
	const submenuTimeoutRef = useRef<NodeJS.Timeout | null>(null);
	const preventCloseRef = useRef<boolean>(false); // ADD THIS

	const handleMouseEnter = (menuItem: MenuItem, e: MouseEvent): void => {
		if (disabled) return;

		if (submenuTimeoutRef.current) {
			clearTimeout(submenuTimeoutRef.current);
			submenuTimeoutRef.current = null;
		}

		if (menuItem.submenus?.length) {
			const itemElement = e.currentTarget as HTMLElement;
			const rect: DOMRect = itemElement.getBoundingClientRect();
			setSubmenuPosition({ x: rect.right + 5, y: rect.top });
			setActiveSubmenu(menuItem.action);
		} else {
			if (!isAnyItemLoading && !preventCloseRef.current) {
				setActiveSubmenu(null);
			}
		}
	};

	const handleMouseLeave = (): void => {
		if (preventCloseRef.current) return;
		submenuTimeoutRef.current = setTimeout(() => {
			setActiveSubmenu(null);
		}, 200);
	};

	const handleSubmenuMouseEnter = (): void => {
		if (submenuTimeoutRef.current) {
			clearTimeout(submenuTimeoutRef.current);
			submenuTimeoutRef.current = null;
		}
	};

	const handleItemClick = (e: MouseEvent, menuItem: MenuItem): void => {
		e.stopPropagation();
		console.log(menuItem);
		if (!menuItem.loading && !menuItem.submenus?.length && !disabled) {
			onItemClick(menuItem, entityType, selectedItem);
			if (menuItem.showLoading !== true) {
				onClose();
			}
		}
	};

	const filteredItems: MenuItem[] = menuItems.filter(
		(menuItem: MenuItem): boolean => !menuItem.displayCondition || menuItem.displayCondition(selectedItem),
	);

	const activeSubMenuItem: MenuItem | undefined = menuItems.find(
		(item: MenuItem): boolean => item.action === activeSubmenu,
	);

	const isAnyItemLoading: boolean = filteredItems.some((item: MenuItem): boolean | undefined => item.loading);

	return (
		<>
			<div
				className={`${isSubmenu ? "context-submenu" : "context-menu"}`}
				style={{
					top: position.y,
					left: position.x,
					minWidth: compact ? (isSubmenu ? "100px" : "120px") : isSubmenu ? "120px" : "150px",
				}}
				onClick={(e: MouseEvent): void => e.stopPropagation()}
				onMouseEnter={onMouseEnter}
				onMouseLeave={onMouseLeave}
			>
				{filteredItems.map(
					(menuItem: MenuItem, index: number): JSX.Element => (
						<div
							key={menuItem.action}
							className={`context-menu-item ${menuItem.loading ? "loading" : ""} ${isAnyItemLoading && !menuItem.loading ? "disabled" : ""}`}
							style={{
								padding: compact ? "6px 12px" : "8px 16px",
								fontSize: compact ? "13px" : "14px",
								borderBottom:
									index !== filteredItems.length - 1
										? "1px solid var(--bs-form-control-border-color)"
										: "none",
								color: menuItem.color || "inherit",
								opacity: isAnyItemLoading ? 0.5 : 1,
								pointerEvents: isAnyItemLoading ? "none" : "auto",
								cursor: isAnyItemLoading ? "not-allowed" : "pointer",
							}}
							onClick={(e: MouseEvent): void => handleItemClick(e, menuItem)}
							onMouseEnter={(e: MouseEvent): void => handleMouseEnter(menuItem, e)}
							onMouseLeave={handleMouseLeave}
							id={`context-menu-${menuItem.action}`}
						>
							<span>
								{menuItem.loading ? (
									<i className="bi bi-arrow-repeat me-2 spinning"></i>
								) : (
									menuItem.icon && <i className={`bi bi-${menuItem.icon} me-2`}></i>
								)}
								{menuItem.text}
							</span>
							{menuItem.submenus?.length && <i className="bi bi-chevron-right"></i>}
						</div>
					),
				)}
			</div>

			{activeSubmenu && activeSubMenuItem?.submenus && (
				<MenuLevel
					menuItems={activeSubMenuItem.submenus}
					entityType={entityType}
					selectedItem={selectedItem}
					onItemClick={onItemClick}
					compact={compact}
					position={submenuPosition}
					isSubmenu={true}
					onMouseEnter={handleSubmenuMouseEnter}
					onMouseLeave={handleMouseLeave}
					onClose={onClose}
					disabled={isAnyItemLoading}
				/>
			)}
		</>
	);
};

export interface ContextMenuProps {
	position: ContextMenuPosition;
	menuItems: MenuItem[];
	entityType: EntityType;
	selectedItem: JamData;
	onClose: () => void;
	onItemClick: (menuItem: MenuItem, entityType: EntityType, item: JamData) => void;
	compact?: boolean;
}

export const ContextMenu: React.FC<ContextMenuProps> = ({
	position,
	menuItems,
	entityType,
	selectedItem,
	onClose,
	onItemClick,
	compact = false,
}: ContextMenuProps): JSX.Element => {
	const menuRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		// Close the menu on outside click or Escape key press
		const handleGlobalClick = (e: Event): void => {
			if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
				onClose();
			}
		};

		const handleKeyPress = (e: KeyboardEvent): void => {
			if (e.key === "Escape") {
				onClose();
			}
		};

		document.addEventListener("click", handleGlobalClick);
		document.addEventListener("keydown", handleKeyPress);

		return (): void => {
			document.removeEventListener("click", handleGlobalClick);
			document.removeEventListener("keydown", handleKeyPress);
		};
	}, [onClose]);

	return (
		<div ref={menuRef}>
			<MenuLevel
				menuItems={menuItems}
				entityType={entityType}
				selectedItem={selectedItem}
				onItemClick={onItemClick}
				compact={compact}
				position={position}
				onClose={onClose}
			/>
		</div>
	);
};
