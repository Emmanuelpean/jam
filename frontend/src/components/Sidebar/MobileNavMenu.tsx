import React, { JSX, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { NavigationItem, NavigationSubItem, useNavigation } from "./useNavigation";
import "./MobileNavMenu.scss";

interface MobileNavMenuProps {
	open: boolean;
	onClose: () => void;
	/** Screen position to anchor the menu under, in viewport pixels. The menu stretches from
	 * `anchor.top` down to the bottom of the viewport so it opens at full height. */
	anchor: { top: number; left: number; right: number };
}

/**
 * Mobile-only dropdown that mirrors the desktop Sidebar's navigation. Rendered
 * underneath a PageHeader and opened by tapping the header. Submenu groups are
 * flattened into an indented section since a dropdown can show everything at once.
 */
export const MobileNavMenu = ({ open, onClose, anchor }: MobileNavMenuProps): JSX.Element | null => {
	const { topItems, bottomItems, isMenuActive, isSubItemActive } = useNavigation();
	const [rendered, setRendered] = useState<boolean>(open);
	const [closing, setClosing] = useState<boolean>(false);

	useEffect(() => {
		if (open) {
			setRendered(true);
			setClosing(false);
		} else if (rendered) {
			setClosing(true);
		}
	}, [open, rendered]);

	if (!rendered) return null;

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
					<i className={`bi bi-${icon}`}></i>
				</span>
				<span className="nav-text-container">
					<span className="nav-text">{text}</span>
				</span>
			</>
		);
		const className = `nav-item ${active ? "active" : ""} ${extraClass}`.trim();
		if (path) {
			return (
				<Link
					key={key}
					to={path}
					id={id}
					className={className}
					onClick={(e: React.MouseEvent): void => {
						e.stopPropagation();
						onClose();
					}}
				>
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
				onClick={(e: React.MouseEvent): void => {
					e.stopPropagation();
					onClick?.();
					onClose();
				}}
				onKeyDown={(e: React.KeyboardEvent): void => {
					if (e.key === "Enter" || e.key === " ") {
						e.stopPropagation();
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
					{item.submenu.map(
						(sub: NavigationSubItem): JSX.Element =>
							renderLeaf(
								sub.text,
								sub.text,
								sub.icon,
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
			item.icon,
			isMenuActive(item),
			item.className ?? "",
			item.path,
			item.onClick,
			item.id
		);
	};

	return (
		<div
			id="mobile-nav-menu"
			className={`mobile-nav-menu ${closing ? "closing" : ""}`}
			role="menu"
			style={{ top: anchor.top, left: anchor.left, right: anchor.right }}
			onAnimationEnd={(e: React.AnimationEvent): void => {
				if (e.animationName === "mobile-nav-menu-close") {
					setRendered(false);
					setClosing(false);
				}
			}}
		>
			<nav className="mobile-nav-section">{topItems.map(renderItem)}</nav>
			<div className="mobile-nav-divider" />
			<nav className="mobile-nav-section">{bottomItems.map(renderItem)}</nav>
		</div>
	);
};

export default MobileNavMenu;
