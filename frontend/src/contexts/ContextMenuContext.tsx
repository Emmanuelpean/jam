import React, { createContext, JSX, MouseEvent, ReactNode, useContext, useState } from "react";
import { ContextMenu, MenuItem } from "../components/ContextMenu/ContextMenu";
import { JamData } from "./DataContext";
import { useProgressOverlay } from "./useProgressOverlayContext";

interface ContextMenuState {
	position: { x: number; y: number };
	menuItems: MenuItem[];
	selectedItem: JamData | null;
	show: boolean;
	compact?: boolean;
}

interface ContextMenuContextType {
	openContextMenu: (
		e: MouseEvent,
		menuItems: MenuItem[],
		selectedItem: JamData,
		compact?: boolean
	) => void;
	closeContextMenu: () => void;
}

const ContextMenuContext = createContext<ContextMenuContextType | undefined>(undefined);

export const ContextMenuProvider: React.FC<{ children: ReactNode }> = ({
	children,
}): JSX.Element => {
	const { showProgress, hideProgress } = useProgressOverlay();
	const [menuState, setMenuState] = useState<ContextMenuState>({
		position: { x: 0, y: 0 },
		menuItems: [],
		selectedItem: null,
		show: false,
		compact: false,
	});

	const openContextMenu = (
		e: MouseEvent,
		menuItems: MenuItem[],
		selectedItem: JamData,
		compact: boolean = false
	): void => {
		e.preventDefault();
		setMenuState({
			position: { x: e.clientX, y: e.clientY },
			menuItems,
			selectedItem,
			show: true,
			compact,
		});
	};

	const closeContextMenu = (): void => {
		setMenuState((prev: ContextMenuState): ContextMenuState => ({ ...prev, show: false }));
	};

	const handleMenuItemClick = async (
		menuItem: MenuItem,
		selectedItem: JamData
	): Promise<void> => {
		if (!menuItem.function) {
			closeContextMenu();
			return;
		}

		if (menuItem.showLoading) {
			showProgress(menuItem.loadingMessage);
		}

		try {
			await menuItem.function(selectedItem);
		} finally {
			if (menuItem.showLoading) {
				hideProgress();
			}
			closeContextMenu();
		}
	};

	return (
		<ContextMenuContext.Provider value={{ openContextMenu, closeContextMenu }}>
			{children}
			{menuState.show && menuState.selectedItem && (
				<ContextMenu
					position={menuState.position}
					menuItems={menuState.menuItems}
					selectedItem={menuState.selectedItem}
					onClose={closeContextMenu}
					onItemClick={handleMenuItemClick}
					compact={menuState.compact}
					entityType={"job"}
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
