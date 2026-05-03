import React, { createContext, JSX, ReactNode, useContext, useState } from "react";
import { ProgressOverlay } from "../components/ProgressOverlay/ProgressOverlay";
import { useDelayedLoading } from "../hooks/useDelayedLoading";

interface ProgressOverlayContextType {
	showProgress: (message?: string, title?: string) => void;
	hideProgress: () => void;
	isShowing: boolean;
}

const ProgressOverlayContext = createContext<ProgressOverlayContextType | undefined>(undefined);

interface ProgressOverlayProviderProps {
	children: ReactNode;
}
export const ProgressOverlayProvider: React.FC<ProgressOverlayProviderProps> = ({
	children,
}: ProgressOverlayProviderProps): JSX.Element => {
	const [loading, setLoading] = useState<boolean>(false);
	const [title, setTitle] = useState<string | undefined>(undefined);
	const [message, setMessage] = useState<string | React.ReactNode | undefined>(undefined);
	const show = useDelayedLoading(loading);

	const showProgress = (message?: string, title?: string): void => {
		setTitle(title);
		setMessage(message);
		setLoading(true);
	};

	const hideProgress = (): void => {
		setLoading(false);
	};

	return (
		<ProgressOverlayContext.Provider value={{ showProgress, hideProgress, isShowing: show }}>
			{children}
			<ProgressOverlay show={show} title={title} message={message} />
		</ProgressOverlayContext.Provider>
	);
};

export const useProgressOverlay = (): ProgressOverlayContextType => {
	const context = useContext(ProgressOverlayContext);
	if (!context) {
		throw new Error("useProgressOverlay must be used within a ProgressOverlayProvider");
	}
	return context;
};
