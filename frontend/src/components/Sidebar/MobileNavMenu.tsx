import React, { JSX } from "react";
import { Link, useLocation } from "react-router-dom";
import { getTableIcon } from "../rendering/view/Icons";
import { NavigationItem, NavigationSubItem, useNavigation } from "./useNavigation";
import "./MobileNavMenu.scss";

interface MobileNavMenuProps {
	open: boolean;
	onClose: () => void;
}

/**
 * Mobile-only dropdown that mirrors the desktop Sidebar's navigation. Rendered
 * underneath a PageHeader and opened by tapping the header. Submenu groups are
 * flattened into an indented section since a dropdown can show everything at once.
 */
export const MobileNavMenu = ({ open, onClose }: MobileNavMenuProps): JSX.Element | null => {
	const location = useLocation();
	const { topItems, bottomItems } = useNavigation();

	if (!open) return null;

	const isMenuActive = (path: string): boolean => {
		if (location.pathname.startsWith(path)) return true;
		const parts = path.split("/").filter(Boolean);
		if (parts.length > 1) {
			const parent = "/" + parts.slice(0, -1).join("/") + "/";
			return location.pathname.startsWith(parent);
		}
		return false;
	};

	const isSubItemActive = (item: NavigationSubItem): boolean => {
		if (!item.path) return false;
		if (location.pathname.startsWith(item.path)) return true;
		return item.alsoActiveFor?.some((p: string): boolean => location.pathname.startsWith(p)) ?? false;
	};

	const renderLeaf = (
		key: string,
		text: string,
		icon: string,
		active: boolean,
		extraClass: string,
		path?: string,
		onClick?: () => void,
		id?: string
	): JSX.Element => {
		const inner = (
			<>
				<span className="nav-icon">
					<i className={`bi bi-${icon || getTableIcon(text)}`}></i>
				</span>
				<span className="nav-text-container">
					<span className="nav-text">{text}</span>
				</span>
			</>
		);
		const className = `nav-item ${active ? "active" : ""} ${extraClass}`.trim();
		if (path) {
			return (
				<Link key={key} to={path} id={id} className={className} onClick={onClose}>
					{inner}
				</Link>
			);
		}
		return (
			<div
				key={key}
				id={id}
				className={className}
				role="button"
				tabIndex={0}
				onClick={(): void => {
					onClick?.();
					onClose();
				}}
				onKeyDown={(e: React.KeyboardEvent): void => {
					if (e.key === "Enter" || e.key === " ") {
						onClick?.();
						onClose();
					}
				}}
			>
				{inner}
			</div>
		);
	};

	const renderItem = (item: NavigationItem): JSX.Element => {
		if (item.submenu) {
			return (
				<div key={`group-${item.text}`} className="mobile-nav-group">
					<div className="mobile-nav-group-label">{item.text}</div>
					{item.submenu.map((sub: NavigationSubItem): JSX.Element =>
						renderLeaf(
							sub.text,
							sub.text,
							sub.icon ?? "",
							isSubItemActive(sub),
							"submenu-item",
							sub.path,
							sub.onClick,
							sub.id
						)
					)}
				</div>
			);
		}
		return renderLeaf(
			item.text,
			item.text,
			item.icon ?? "",
			item.path ? isMenuActive(item.path) : false,
			item.className ?? "",
			item.path,
			item.onClick,
			item.id
		);
	};

	return (
		<div className="mobile-nav-menu" role="menu">
			<nav className="mobile-nav-section">{topItems.map(renderItem)}</nav>
			<div className="mobile-nav-divider" />
			<nav className="mobile-nav-section">{bottomItems.map(renderItem)}</nav>
		</div>
	);
};

export default MobileNavMenu;
