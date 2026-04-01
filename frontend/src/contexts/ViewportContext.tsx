import React, { createContext, JSX, ReactNode, useContext, useEffect, useState } from "react";

export const MOBILE_BREAKPOINT = 768;
export const TABLET_BREAKPOINT = 993;
export const SMALL_DESKTOP_BREAKPOINT = 1300;

interface ViewportContextType {
	isMobile: boolean;
	isTablet: boolean;
	isSmallDesktop: boolean;
}

const ViewportContext = createContext<ViewportContextType | undefined>(undefined);

export const ViewportProvider: React.FC<{ children: ReactNode }> = ({ children }): JSX.Element => {
	const [isMobile, setIsMobile] = useState<boolean>(window.innerWidth <= MOBILE_BREAKPOINT);
	const [isTablet, setIsTablet] = useState<boolean>(window.innerWidth <= TABLET_BREAKPOINT);
	const [isSmallDesktop, setIsSmallDesktop] = useState<boolean>(window.innerWidth < SMALL_DESKTOP_BREAKPOINT);

	useEffect(() => {
		const handleResize = (): void => {
			setIsMobile(window.innerWidth <= MOBILE_BREAKPOINT);
			setIsTablet(window.innerWidth <= TABLET_BREAKPOINT);
			setIsSmallDesktop(window.innerWidth < SMALL_DESKTOP_BREAKPOINT);
		};
		window.addEventListener("resize", handleResize);
		return () => window.removeEventListener("resize", handleResize);
	}, []);

	return (
		<ViewportContext.Provider value={{ isMobile, isTablet, isSmallDesktop }}>{children}</ViewportContext.Provider>
	);
};

export const useViewport = (): ViewportContextType => {
	const context = useContext(ViewportContext);
	if (!context) {
		throw new Error("useViewport must be used within ViewportProvider");
	}
	return context;
};
