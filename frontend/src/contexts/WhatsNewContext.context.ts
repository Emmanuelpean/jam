import { createContext, useContext } from "react";

export interface WhatsNewContextType {
	showWhatsNew: () => void;
	showWelcome: () => void;
}

export const WhatsNewContext = createContext<WhatsNewContextType | undefined>(undefined);

export function useWhatsNew(): WhatsNewContextType {
	const context: WhatsNewContextType | undefined = useContext(WhatsNewContext);
	if (context === undefined) {
		throw new Error("useWhatsNew must be used within a WhatsNewProvider");
	}
	return context;
}
