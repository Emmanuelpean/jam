import React, { MouseEvent, useEffect, useRef, useState } from "react";

export interface MenuItem {
	action: string;
	icon?: string;
	text: string;
	id?: string;
	color?: string;
	function?: (item: any) => void;
	hasSubmenu?: boolean;
	submenu?: MenuItem[];
}

export interface ContextMenuState {
	item: any;
	x: number;
	y: number;
	show: boolean;
}

export interface ContextMenuPosition {
	x: number;
	y: number;
}

export interface ContextMenuProps {
	position: ContextMenuPosition;
	items: MenuItem[];
	selectedItem: any;
	onClose: () => void;
	onItemClick: (menuItem: MenuItem, item: any) => void;
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
		const handleGlobalClick = (e: Event) => {
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
	useEffect(() => {
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

	const handleItemClick = (menuItem: MenuItem, e: MouseEvent) => {
		e.stopPropagation();

		if (menuItem.hasSubmenu) {
			return;
		}

		onItemClick(menuItem, selectedItem);
		onClose();
	};

	const handleMouseEnter = (menuItem: MenuItem, e: MouseEvent) => {
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

	const handleMouseLeave = () => {
		// Delay closing the submenu to allow moving to it
		submenuTimeoutRef.current = setTimeout(() => {
			setSubmenuVisible(null);
		}, 200);
	};

	const handleSubmenuMouseEnter = () => {
		// Clear timeout when entering submenu
		if (submenuTimeoutRef.current) {
			clearTimeout(submenuTimeoutRef.current);
			submenuTimeoutRef.current = null;
		}
	};

	const handleSubmenuMouseLeave = () => {
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
					position: "fixed",
					top: position.y,
					left: position.x,
					zIndex: 10000,
					backgroundColor: "white",
					border: "1px solid #ccc",
					borderRadius: "8px",
					boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
					padding: "4px 0",
					minWidth: compact ? "120px" : "150px",
					overflow: "hidden",
				}}
				onClick={(e) => e.stopPropagation()}
			>
				{items.map((menuItem, index) => (
					<div
						key={menuItem.action}
						className="context-menu-item"
						style={{
							padding: compact ? "6px 12px" : "8px 16px",
							cursor: "pointer",
							fontSize: compact ? "13px" : "14px",
							borderBottom: index !== items.length - 1 ? "1px solid #eee" : "none",
							color: menuItem.color || "inherit",
							display: "flex",
							justifyContent: "space-between",
							alignItems: "center",
							transition: "background-color 0.15s ease",
						}}
						onClick={(e) => handleItemClick(menuItem, e)}
						onMouseEnter={(e) => {
							(e.currentTarget as HTMLElement).style.backgroundColor = "#f8f9fa";
							handleMouseEnter(menuItem, e);
						}}
						onMouseLeave={(e) => {
							(e.currentTarget as HTMLElement).style.backgroundColor = "white";
							handleMouseLeave();
						}}
						id={menuItem.id}
					>
						<span>
							{menuItem.icon && <i className={`bi bi-${menuItem.icon} me-2`}></i>}
							{menuItem.text}
						</span>
						{menuItem.hasSubmenu && <i className="bi bi-chevron-right"></i>}
					</div>
				))}
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
								position: "fixed",
								left: submenuPosition.x,
								top: submenuPosition.y,
								zIndex: 10001,
								backgroundColor: "white",
								border: "1px solid #ccc",
								borderRadius: "8px",
								boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
								padding: "4px 0",
								minWidth: compact ? "100px" : "120px",
							}}
							onMouseEnter={handleSubmenuMouseEnter}
							onMouseLeave={handleSubmenuMouseLeave}
							onClick={(e) => e.stopPropagation()}
						>
							{menuItem.submenu?.map((subItem, subIndex) => (
								<div
									key={subItem.action}
									className="context-menu-item"
									style={{
										padding: compact ? "6px 12px" : "8px 16px",
										cursor: "pointer",
										fontSize: compact ? "13px" : "14px",
										borderBottom:
											subIndex !== (menuItem.submenu?.length || 0) - 1
												? "1px solid #eee"
												: "none",
										transition: "background-color 0.15s ease",
									}}
									onClick={(e) => handleItemClick(subItem, e)}
									onMouseEnter={(e) =>
										((e.currentTarget as HTMLElement).style.backgroundColor = "#f8f9fa")
									}
									onMouseLeave={(e) =>
										((e.currentTarget as HTMLElement).style.backgroundColor = "white")
									}
								>
									{subItem.text}
								</div>
							))}
						</div>
					))}
		</>
	);
};
