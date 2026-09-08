import { createContext, MouseEvent, useContext } from "react";
import { MenuItem } from "../components/ContextMenu/ContextMenu";
import { JamData } from "./DataContext";

export interface ContextMenuContextType {
	openContextMenu: (e: MouseEvent, menuItems: MenuItem[], selectedItem: JamData, compact?: boolean) => void;
	closeContextMenu: () => void;
}

export const ContextMenuContext = createContext<ContextMenuContextType | undefined>(undefined);

export const useContextMenu = (): ContextMenuContextType => {
	const context = useContext(ContextMenuContext);
	if (!context) {
		throw new Error("useContextMenu must be used within a ContextMenuProvider");
	}
	return context;
};
