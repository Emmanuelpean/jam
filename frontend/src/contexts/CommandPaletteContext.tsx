import React, { JSX, ReactNode, useState } from "react";
import { CommandPaletteContext } from "./CommandPaletteContext.context";

export { useCommandPaletteContext } from "./CommandPaletteContext.context";
export type { CommandPaletteContextType } from "./CommandPaletteContext.context";

export const CommandPaletteProvider = ({ children }: { children: ReactNode }): JSX.Element => {
	const [isOpen, setIsOpen] = useState(false);
	return <CommandPaletteContext.Provider value={{ isOpen, setIsOpen }}>{children}</CommandPaletteContext.Provider>;
};
