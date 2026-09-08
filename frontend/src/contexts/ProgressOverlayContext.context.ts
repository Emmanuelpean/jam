import { createContext, useContext } from "react";

export interface ProgressOverlayContextType {
	showProgress: (message?: string, title?: string) => void;
	hideProgress: () => void;
	isShowing: boolean;
}

export const ProgressOverlayContext = createContext<ProgressOverlayContextType | undefined>(undefined);

export const useProgressOverlay = (): ProgressOverlayContextType => {
	const context = useContext(ProgressOverlayContext);
	if (!context) {
		throw new Error("useProgressOverlay must be used within a ProgressOverlayProvider");
	}
	return context;
};
