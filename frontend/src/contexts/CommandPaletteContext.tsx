import React, { createContext, JSX, ReactNode, useContext, useState } from "react";

interface CommandPaletteContextType {
	isOpen: boolean;
	setIsOpen: (open: boolean) => void;
}

const CommandPaletteContext = createContext<CommandPaletteContextType | undefined>(undefined);

export const useCommandPaletteContext = (): CommandPaletteContextType => {
	const context = useContext(CommandPaletteContext);
	if (!context) throw new Error("useCommandPaletteContext must be used within CommandPaletteProvider");
	return context;
};

export const CommandPaletteProvider = ({ children }: { children: ReactNode }): JSX.Element => {
	const [isOpen, setIsOpen] = useState(false);
	return <CommandPaletteContext.Provider value={{ isOpen, setIsOpen }}>{children}</CommandPaletteContext.Provider>;
};
