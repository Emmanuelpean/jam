import { createContext, useContext } from "react";

export interface ViewportContextType {
	isMobile: boolean;
	isTablet: boolean;
	isSmallDesktop: boolean;
}

export const ViewportContext = createContext<ViewportContextType | undefined>(undefined);

export const useViewport = (): ViewportContextType => {
	const context = useContext(ViewportContext);
	if (!context) {
		throw new Error("useViewport must be used within ViewportProvider");
	}
	return context;
};
