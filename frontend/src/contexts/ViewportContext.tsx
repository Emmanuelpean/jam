import React, { createContext, JSX, ReactNode, useContext, useEffect, useState } from "react";

const MOBILE_BREAKPOINT = 768;

interface ViewportContextType {
	isMobile: boolean;
}

const ViewportContext = createContext<ViewportContextType | undefined>(undefined);

export const ViewportProvider: React.FC<{ children: ReactNode }> = ({ children }): JSX.Element => {
	const [isMobile, setIsMobile] = useState<boolean>(window.innerWidth <= MOBILE_BREAKPOINT);

	useEffect(() => {
		const handleResize = (): void => setIsMobile(window.innerWidth <= MOBILE_BREAKPOINT);
		window.addEventListener("resize", handleResize);
		return () => window.removeEventListener("resize", handleResize);
	}, []);

	return <ViewportContext.Provider value={{ isMobile }}>{children}</ViewportContext.Provider>;
};

export const useViewport = (): ViewportContextType => {
	const context = useContext(ViewportContext);
	if (!context) {
		throw new Error("useViewport must be used within ViewportProvider");
	}
	return context;
};