import React, { JSX, MouseEvent, useEffect, useRef, useState } from "react";
import "./ContextMenu.scss";
import { EntityType, JamData } from "../../contexts/DataContext";

export interface MenuItem {
	action: string;
	icon?: string;
	text: string;
	color?: string;
	function?: (item: JamData) => Promise<boolean | void> | void;
	submenus?: MenuItem[];
	displayCondition?: (item: JamData) => boolean;
	showLoading?: boolean;
	loadingMessage?: string;
}

export interface ContextMenuPosition {
	x: number;
	y: number;
}

interface MenuLevelProps {
	menuItems: MenuItem[];
	selectedItem: JamData;
	onItemClick: (menuItem: MenuItem, item: JamData) => void;
	compact: boolean;
	position: ContextMenuPosition;
	isSubmenu?: boolean;
	onMouseEnter?: () => void;
	onMouseLeave?: () => void;
	onClose: () => void;
	disabled?: boolean;
}

const MenuLevel: React.FC<MenuLevelProps> = ({
	menuItems,
	selectedItem,
	onItemClick,
	compact,
	position,
	onClose,
	isSubmenu = false,
	onMouseEnter,
	onMouseLeave,
}: MenuLevelProps): JSX.Element => {
	const [activeSubmenu, setActiveSubmenu] = useState<string | null>(null);
	const [submenuPosition, setSubmenuPosition] = useState<ContextMenuPosition>({ x: 0, y: 0 });
	const submenuTimeoutRef = useRef<NodeJS.Timeout | null>(null);
	const preventCloseRef = useRef<boolean>(false);

	const handleMouseEnter = (menuItem: MenuItem, e: MouseEvent): void => {
		if (submenuTimeoutRef.current) {
			clearTimeout(submenuTimeoutRef.current);
			submenuTimeoutRef.current = null;
		}

		if (menuItem.submenus?.length) {
			const itemElement = e.currentTarget as HTMLElement;
			const rect: DOMRect = itemElement.getBoundingClientRect();
			setSubmenuPosition({ x: rect.right + 5, y: rect.top });
			setActiveSubmenu(menuItem.action);
		} else if (!preventCloseRef.current) {
			setActiveSubmenu(null);
		}
	};

	const filteredItems: MenuItem[] = menuItems.filter(
		(menuItem: MenuItem): boolean =>
			!menuItem.displayCondition || menuItem.displayCondition(selectedItem)
	);

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
		if (!menuItem.submenus?.length) {
			onItemClick(menuItem, selectedItem);
			onClose();
		}
	};

	const activeSubMenuItem: MenuItem | undefined = menuItems.find(
		(item: MenuItem): boolean => item.action === activeSubmenu
	);

	return (
		<>
			<div
				className={isSubmenu ? "context-submenu" : "context-menu"}
				style={{
					top: position.y,
					left: position.x,
					minWidth: compact
						? isSubmenu
							? "100px"
							: "120px"
						: isSubmenu
							? "120px"
							: "150px",
				}}
				onClick={(e: MouseEvent): void => e.stopPropagation()}
				onMouseEnter={onMouseEnter}
				onMouseLeave={onMouseLeave}
			>
				{filteredItems.map(
					(menuItem: MenuItem, index: number): JSX.Element => (
						<div
							key={menuItem.action}
							className={`context-menu-item`}
							style={{
								padding: compact ? "6px 12px" : "8px 16px",
								fontSize: compact ? "13px" : "14px",
								borderBottom:
									index !== filteredItems.length - 1
										? "1px solid var(--bs-form-control-border-color)"
										: "none",
								color: menuItem.color || "inherit",
							}}
							onClick={(e: MouseEvent): void => handleItemClick(e, menuItem)}
							onMouseEnter={(e: MouseEvent): void => handleMouseEnter(menuItem, e)}
							onMouseLeave={handleMouseLeave}
							id={`context-menu-${menuItem.action}`}
						>
							<span>
								{menuItem.icon && <i className={`bi bi-${menuItem.icon} me-2`} />}
								{menuItem.text}
							</span>
							{menuItem.submenus?.length && <i className="bi bi-chevron-right" />}
						</div>
					)
				)}
			</div>

			{activeSubmenu && activeSubMenuItem?.submenus && (
				<MenuLevel
					menuItems={activeSubMenuItem.submenus}
					selectedItem={selectedItem}
					onItemClick={onItemClick}
					compact={compact}
					position={submenuPosition}
					isSubmenu
					onMouseEnter={handleSubmenuMouseEnter}
					onMouseLeave={handleMouseLeave}
					onClose={onClose}
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
	onItemClick: (menuItem: MenuItem, item: JamData) => void;
	compact?: boolean;
}

export const ContextMenu: React.FC<ContextMenuProps> = ({
	position,
	menuItems,
	selectedItem,
	onClose,
	onItemClick,
	compact = false,
}: ContextMenuProps): JSX.Element => {
	const menuRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
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
				selectedItem={selectedItem}
				onItemClick={onItemClick}
				compact={compact}
				position={position}
				onClose={onClose}
			/>
		</div>
	);
};
