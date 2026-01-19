import React, { createContext, useContext, useState, useRef, ReactNode, MouseEvent, JSX } from "react";
import { ContextMenu, MenuItem } from "../components/ContextMenu/ContextMenu";
import { EntityType, JamData } from "./DataContext";

interface ContextMenuState {
	position: { x: number; y: number };
	menuItems: MenuItem[];
	entityType: EntityType | null;
	selectedItem: JamData | null;
	show: boolean;
	compact?: boolean;
}

interface ContextMenuContextType {
	openContextMenu: (
		e: MouseEvent<HTMLElement>,
		menuItems: MenuItem[],
		entityType: EntityType,
		selectedItem: JamData,
		compact?: boolean,
	) => void;
	closeContextMenu: () => void;
}

const ContextMenuContext = createContext<ContextMenuContextType | undefined>(undefined);

export const ContextMenuProvider: React.FC<{ children: ReactNode }> = ({ children }): JSX.Element => {
	const [menuState, setMenuState] = useState<ContextMenuState>({
		position: { x: 0, y: 0 },
		menuItems: [],
		entityType: null,
		selectedItem: null,
		show: false,
		compact: false,
	});

	// Track loading actions by entity ID and action: Map<entityId, Set<action>>
	const loadingActionsRef = useRef<Map<string, Set<string>>>(new Map());
	const [, forceUpdate] = useState({});

	const getEntityId = (entityType: EntityType, item: JamData): string => {
		return entityType + item.id.toString();
	};

	const applyLoadingState = (menuItems: MenuItem[], entityId: string): MenuItem[] => {
		return menuItems.map((item: MenuItem): MenuItem => {
			const entityLoadingActions: Set<string> | undefined = loadingActionsRef.current.get(entityId);
			return {
				...item,
				loading: entityLoadingActions?.has(item.action) ?? false,
				submenus: item.submenus ? applyLoadingState(item.submenus, entityId) : undefined,
			};
		});
	};

	const openContextMenu = (
		e: MouseEvent<HTMLElement>,
		menuItems: MenuItem[],
		entityType: EntityType,
		selectedItem: any,
		compact: boolean = false,
	): void => {
		e.preventDefault();
		const entityId: string = getEntityId(entityType, selectedItem);
		setMenuState({
			position: { x: e.clientX, y: e.clientY },
			menuItems: applyLoadingState(menuItems, entityId),
			entityType,
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
		entityType: EntityType,
		selectedItem: JamData,
	): Promise<void> => {
		if (menuItem.function) {
			const entityId: string = getEntityId(entityType, selectedItem);

			if (!loadingActionsRef.current.has(entityId)) {
				loadingActionsRef.current.set(entityId, new Set());
			}
			loadingActionsRef.current.get(entityId)!.add(menuItem.action);
			console.log("Loading actions:", loadingActionsRef.current);

			setMenuState(
				(prev: ContextMenuState): ContextMenuState => ({
					...prev,
					menuItems: applyLoadingState(prev.menuItems, entityId),
				}),
			);

			try {
				await menuItem.function(selectedItem);
			} finally {
				loadingActionsRef.current.get(entityId)?.delete(menuItem.action);
				if (loadingActionsRef.current.get(entityId)?.size === 0) {
					loadingActionsRef.current.delete(entityId);
				}
				if (menuItem.showLoading) {
					closeContextMenu();
				}
				forceUpdate({});
			}
		} else {
			closeContextMenu();
		}
	};

	return (
		<ContextMenuContext.Provider value={{ openContextMenu, closeContextMenu }}>
			{children}
			{menuState.show && menuState.selectedItem && menuState.entityType && (
				<ContextMenu
					position={menuState.position}
					menuItems={menuState.menuItems}
					entityType={menuState.entityType}
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
	const context: ContextMenuContextType | undefined = useContext(ContextMenuContext);
	if (!context) {
		throw new Error("useContextMenu must be used within a ContextMenuProvider");
	}
	return context;
};
