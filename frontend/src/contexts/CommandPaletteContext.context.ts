import { createContext, useContext } from "react";

export interface CommandPaletteContextType {
	isOpen: boolean;
	setIsOpen: (open: boolean) => void;
}

export const CommandPaletteContext = createContext<CommandPaletteContextType | undefined>(undefined);

export const useCommandPaletteContext = (): CommandPaletteContextType => {
	const context = useContext(CommandPaletteContext);
	if (!context) throw new Error("useCommandPaletteContext must be used within CommandPaletteProvider");
	return context;
};
