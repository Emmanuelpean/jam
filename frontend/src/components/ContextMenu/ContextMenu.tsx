import React, { JSX, MouseEvent, useEffect, useMemo, useRef, useState } from "react";
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

type AnchoredStyle = {
	top?: number;
	left?: number;
	right?: number;
	bottom?: number;
	transform: string;
	minWidth: string;
};

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
	submenuOpensLeft?: boolean;
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
	submenuOpensLeft: submenuOpensLeftProp = false,
}: MenuLevelProps): JSX.Element => {
	const [activeSubmenu, setActiveSubmenu] = useState<string | null>(null);
	const [submenuPosition, setSubmenuPosition] = useState<ContextMenuPosition>({ x: 0, y: 0 });
	const [submenuOpenLeftByAction, setSubmenuOpenLeftByAction] = useState<Record<string, boolean>>({});
	const submenuTimeoutRef = useRef<NodeJS.Timeout | null>(null);
	const preventCloseRef = useRef<boolean>(false);

	const filteredItems: MenuItem[] = menuItems.filter(
		(menuItem: MenuItem): boolean => !menuItem.displayCondition || menuItem.displayCondition(selectedItem)
	);

	const handleMouseEnterItem = (menuItem: MenuItem, e: MouseEvent): void => {
		if (submenuTimeoutRef.current) {
			clearTimeout(submenuTimeoutRef.current);
			submenuTimeoutRef.current = null;
		}

		if (menuItem.submenus?.length) {
			const itemElement = e.currentTarget as HTMLElement;
			const rect: DOMRect = itemElement.getBoundingClientRect();

			const gap: number = 4;
			const margin: number = 0;

			// Estimate submenu width (matches your minWidth logic for submenus)
			const submenuWidth: 100 | 120 = compact ? 100 : 120;

			// Prefer right, but if it would overflow, open left
			const openLeft: boolean = rect.right + gap + submenuWidth > window.innerWidth;

			setSubmenuOpenLeftByAction((prev) => ({ ...prev, [menuItem.action]: openLeft }));

			let x: number = openLeft ? rect.left - gap - submenuWidth : rect.right + gap;
			let y: number = rect.top;

			// Clamp
			x = Math.min(Math.max(margin, x), window.innerWidth - submenuWidth - margin);

			// Optional vertical clamp (keeps submenu on-screen if near bottom)
			y = Math.min(Math.max(margin, y), window.innerHeight - margin);

			setSubmenuPosition({ x, y });
			setActiveSubmenu(menuItem.action);
		} else if (!preventCloseRef.current) {
			setActiveSubmenu(null);
		}
	};

	useEffect(() => {
		const handleScroll = (): void => onClose();

		// capture=true catches scroll on nested containers too
		window.addEventListener("scroll", handleScroll, true);

		return () => window.removeEventListener("scroll", handleScroll, true);
	}, [onClose]);

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

	const anchoredStyle: AnchoredStyle = useMemo(() => {
		const vw = window.innerWidth;
		const vh = window.innerHeight;
		const margin = 0;

		const isLeftHalf = position.x < vw / 2;
		const isTopHalf = position.y < vh / 2;

		// Root menu: place in the opposite quadrant relative to click
		if (!isSubmenu) {
			const minWidth = compact ? "108px" : "135px";

			if (isLeftHalf && isTopHalf) {
				return { top: position.y + margin, left: position.x + margin, transform: "none", minWidth };
			}
			if (!isLeftHalf && isTopHalf) {
				return { top: position.y + margin, right: vw - position.x + margin, transform: "none", minWidth };
			}
			if (isLeftHalf && !isTopHalf) {
				return { bottom: vh - position.y + margin, left: position.x + margin, transform: "none", minWidth };
			}
			return { bottom: vh - position.y + margin, right: vw - position.x + margin, transform: "none", minWidth };
		}

		// Submenu: keep old behavior (x/y)
		return {
			top: position.y,
			left: position.x,
			transform: "none",
			minWidth: compact ? "90px" : "108px",
		};
	}, [compact, isSubmenu, position.x, position.y]);

	const submenuOpensLeftComputed: boolean = !!(activeSubmenu && submenuOpenLeftByAction[activeSubmenu]);
	const submenuOpensLeft: boolean = isSubmenu ? submenuOpensLeftProp : submenuOpensLeftComputed;

	const menuClassName: string = isSubmenu
		? `context-submenu${submenuOpensLeft ? " context-submenu--left" : ""}`
		: "context-menu";

	return (
		<>
			<div
				className={menuClassName}
				style={anchoredStyle}
				onClick={(e: MouseEvent): void => e.stopPropagation()}
				onMouseEnter={onMouseEnter}
				onMouseLeave={onMouseLeave}
			>
				{filteredItems.map(
					(menuItem: MenuItem, index: number): JSX.Element => (
						<div
							key={menuItem.action}
							className="context-menu-item"
							style={{
								padding: compact ? "5.4px 10.8px" : "7.2px 14.4px",
								fontSize: compact ? "11.7px" : "12.6px",
								borderBottom:
									index !== filteredItems.length - 1
										? "1px solid var(--bs-form-control-border-color)"
										: "none",
								color: menuItem.color || "inherit",
							}}
							onClick={(e: MouseEvent): void => handleItemClick(e, menuItem)}
							onMouseEnter={(e: MouseEvent): void => handleMouseEnterItem(menuItem, e)}
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
					submenuOpensLeft={submenuOpensLeftComputed}
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
	const wrapperRef = useRef<HTMLDivElement | null>(null);

	useEffect(() => {
		const handleGlobalClick = (e: Event): void => {
			if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) onClose();
		};
		const handleKeyPress = (e: KeyboardEvent): void => {
			if (e.key === "Escape") onClose();
		};

		document.addEventListener("click", handleGlobalClick);
		document.addEventListener("keydown", handleKeyPress);
		return (): void => {
			document.removeEventListener("click", handleGlobalClick);
			document.removeEventListener("keydown", handleKeyPress);
		};
	}, [onClose]);

	return (
		<div ref={wrapperRef}>
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
