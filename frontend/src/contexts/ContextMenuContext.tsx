import React, { createContext, useContext, useState, ReactNode, MouseEvent } from "react";
import { ContextMenu, MenuItem, SubMenuItem } from "../components/tables/ContextMenu";

interface ContextMenuState {
	position: { x: number; y: number };
	items: MenuItem[];
	selectedItem: any;
	show: boolean;
	compact?: boolean;
	onItemClick?: (menuItem: MenuItem | SubMenuItem, selectedItem: any) => void;
}

interface ContextMenuContextType {
	openContextMenu: (e: MouseEvent<HTMLElement>, items: MenuItem[], selectedItem: any, compact?: boolean) => void;
	closeContextMenu: () => void;
}

const ContextMenuContext = createContext<ContextMenuContextType | undefined>(undefined);

export const ContextMenuProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
	const [menuState, setMenuState] = useState<ContextMenuState>({
		position: { x: 0, y: 0 },
		items: [],
		selectedItem: null,
		show: false,
		compact: false,
	});

	const openContextMenu = (
		e: MouseEvent<HTMLElement>,
		items: MenuItem[],
		selectedItem: any,
		compact: boolean = false,
	) => {
		const onItemClick = (menuItem: MenuItem | SubMenuItem, selectedItem: any): void => {
			if (menuItem.function) {
				menuItem.function(selectedItem);
			}
		};

		e.preventDefault();
		setMenuState({
			position: { x: e.clientX, y: e.clientY },
			items,
			selectedItem,
			show: true,
			compact,
			onItemClick,
		});
	};

	const closeContextMenu = () => {
		setMenuState((prev) => ({ ...prev, show: false }));
	};

	const handleMenuItemClick = (menuItem: MenuItem | SubMenuItem, selectedItem: any) => {
		menuState.onItemClick?.(menuItem, selectedItem);
		closeContextMenu();
	};

	return (
		<ContextMenuContext.Provider value={{ openContextMenu, closeContextMenu }}>
			{children}
			{menuState.show && (
				<ContextMenu
					position={menuState.position}
					items={menuState.items}
					selectedItem={menuState.selectedItem}
					onClose={closeContextMenu}
					onItemClick={handleMenuItemClick}
					compact={menuState.compact}
				/>
			)}
		</ContextMenuContext.Provider>
	);
};

export const useContextMenu = (): ContextMenuContextType => {
	const context = useContext(ContextMenuContext);
	if (!context) {
		throw new Error("useContextMenu must be used within a ContextMenuProvider");
	}
	return context;
};
