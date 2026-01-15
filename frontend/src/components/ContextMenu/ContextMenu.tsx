import React, { MouseEvent, useEffect, useRef, useState, JSX } from "react";
import "./ContextMenu.css";

export interface MenuItem {
	action: string;
	icon?: string;
	text: string;
	color?: string;
	function?: (item: any) => void;
	hasSubmenu?: boolean;
	submenu?: SubMenuItem[];
	displayCondition?: (item: any) => boolean;
}

export interface SubMenuItem extends Omit<MenuItem, "submenu | hasSubmenu"> {}

export interface ContextMenuPosition {
	x: number;
	y: number;
}

export interface ContextMenuProps {
	position: ContextMenuPosition;
	items: MenuItem[];
	selectedItem: any;
	onClose: () => void;
	onItemClick: (menuItem: MenuItem | SubMenuItem, item: any) => void;
	compact?: boolean;
}

export const ContextMenu: React.FC<ContextMenuProps> = ({
	position,
	items,
	selectedItem,
	onClose,
	onItemClick,
	compact = false,
}) => {
	const menuRef = useRef<HTMLDivElement>(null);
	const [submenuVisible, setSubmenuVisible] = useState<string | null>(null);
	const [submenuPosition, setSubmenuPosition] = useState<ContextMenuPosition>({ x: 0, y: 0 });
	const submenuTimeoutRef = useRef<NodeJS.Timeout | null>(null);

	useEffect(() => {
		const handleGlobalClick = (e: Event): void => {
			if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
				onClose();
			}
		};

		const handleKeyPress = (e: KeyboardEvent) => {
			if (e.key === "Escape") {
				onClose();
			}
		};

		document.addEventListener("click", handleGlobalClick);
		document.addEventListener("keydown", handleKeyPress);

		return () => {
			document.removeEventListener("click", handleGlobalClick);
			document.removeEventListener("keydown", handleKeyPress);
			if (submenuTimeoutRef.current) {
				clearTimeout(submenuTimeoutRef.current);
			}
		};
	}, [onClose]);

	// Adjust menu position if it goes off screen
	useEffect((): void => {
		if (menuRef.current) {
			const menuRect = menuRef.current.getBoundingClientRect();
			const viewportWidth = window.innerWidth;
			const viewportHeight = window.innerHeight;

			let adjustedX = position.x;
			let adjustedY = position.y;

			if (menuRect.right > viewportWidth) {
				adjustedX = viewportWidth - menuRect.width - 10;
			}

			if (menuRect.bottom > viewportHeight) {
				adjustedY = viewportHeight - menuRect.height - 10;
			}

			if (adjustedX !== position.x || adjustedY !== position.y) {
				menuRef.current.style.left = `${adjustedX}px`;
				menuRef.current.style.top = `${adjustedY}px`;
			}
		}
	}, [position]);

	const handleItemClick = (menuItem: MenuItem | SubMenuItem, e: MouseEvent): void => {
		e.stopPropagation();
		if (menuItem.hasSubmenu) {
			return;
		}
		onItemClick(menuItem, selectedItem);
		onClose();
	};

	const handleMouseEnter = (menuItem: MenuItem | SubMenuItem, e: MouseEvent): void => {
		// Clear any pending timeout
		if (submenuTimeoutRef.current) {
			clearTimeout(submenuTimeoutRef.current);
			submenuTimeoutRef.current = null;
		}

		if (menuItem.hasSubmenu) {
			const itemElement = e.currentTarget as HTMLElement;
			const rect = itemElement.getBoundingClientRect();

			setSubmenuPosition({
				x: rect.right + 5,
				y: rect.top,
			});
			setSubmenuVisible(menuItem.action);
		} else {
			// Close submenu when hovering over non-submenu items
			setSubmenuVisible(null);
		}
	};

	const handleMouseLeave = (): void => {
		// Delay closing the submenu to allow moving to it
		submenuTimeoutRef.current = setTimeout(() => {
			setSubmenuVisible(null);
		}, 200);
	};

	const handleSubmenuMouseEnter = (): void => {
		// Clear timeout when entering submenu
		if (submenuTimeoutRef.current) {
			clearTimeout(submenuTimeoutRef.current);
			submenuTimeoutRef.current = null;
		}
	};

	const handleSubmenuMouseLeave = (): void => {
		// Delay closing when leaving submenu
		submenuTimeoutRef.current = setTimeout(() => {
			setSubmenuVisible(null);
		}, 200);
	};

	return (
		<>
			<div
				ref={menuRef}
				className="context-menu"
				style={{
					top: position.y,
					left: position.x,
					minWidth: compact ? "120px" : "150px",
				}}
				onClick={(e: MouseEvent): void => e.stopPropagation()}
			>
				{items
					.filter(
						(menuItem: MenuItem): boolean =>
							!menuItem.displayCondition || menuItem.displayCondition(selectedItem),
					)
					.map(
						(menuItem: MenuItem, index: number, filteredItems: MenuItem[]): JSX.Element => (
							<div
								key={menuItem.action}
								className="context-menu-item"
								style={{
									padding: compact ? "6px 12px" : "8px 16px",
									fontSize: compact ? "13px" : "14px",
									borderBottom:
										index !== filteredItems.length - 1
											? "1px solid var(--bs-form-control-border-color)"
											: "none",
									color: menuItem.color || "inherit",
								}}
								onClick={(e: MouseEvent): void => handleItemClick(menuItem, e)}
								onMouseEnter={(e: MouseEvent): void => {
									handleMouseEnter(menuItem, e);
								}}
								onMouseLeave={(_: MouseEvent): void => {
									handleMouseLeave();
								}}
								id={`context-menu-${menuItem.action}`}
							>
								<span>
									{menuItem.icon && <i className={`bi bi-${menuItem.icon} me-2`}></i>}
									{menuItem.text}
								</span>
								{menuItem.hasSubmenu && <i className="bi bi-chevron-right"></i>}
							</div>
						),
					)}
			</div>

			{/* Submenu */}
			{submenuVisible &&
				items
					.filter((item) => item.action === submenuVisible && item.hasSubmenu)
					.map((menuItem) => (
						<div
							key={`submenu-${menuItem.action}`}
							className="context-submenu"
							style={{
								left: submenuPosition.x,
								top: submenuPosition.y,
								minWidth: compact ? "100px" : "120px",
							}}
							onMouseEnter={handleSubmenuMouseEnter}
							onMouseLeave={handleSubmenuMouseLeave}
							onClick={(e) => e.stopPropagation()}
						>
							{menuItem.submenu?.map(
								(subItem: SubMenuItem, subIndex: number): JSX.Element => (
									<div
										key={subItem.action}
										className="context-menu-item"
										style={{
											padding: compact ? "6px 12px" : "8px 16px",
											cursor: "pointer",
											fontSize: compact ? "13px" : "14px",
											borderBottom:
												subIndex !== (menuItem.submenu?.length || 0) - 1
													? "1px solid var(--bs-form-control-border-color)"
													: "none",
											transition: "background-color 0.15s ease",
										}}
										onClick={(e: MouseEvent<HTMLDivElement>): void => handleItemClick(subItem, e)}
									>
										{subItem.text}
									</div>
								),
							)}
						</div>
					))}
		</>
	);
};
