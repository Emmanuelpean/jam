import React, { JSX, ReactNode, useState } from "react";
import { ProgressOverlay } from "../components/ProgressOverlay/ProgressOverlay";
import { useDelayedLoading } from "../hooks/useDelayedLoading";
import { ProgressOverlayContext } from "./ProgressOverlayContext.context";

export { useProgressOverlay } from "./ProgressOverlayContext.context";
export type { ProgressOverlayContextType } from "./ProgressOverlayContext.context";

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
