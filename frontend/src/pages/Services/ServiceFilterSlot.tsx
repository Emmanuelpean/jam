import React, { createContext, JSX, ReactNode, useContext } from "react";
import { createPortal } from "react-dom";

export const ServiceFilterSlotContext = createContext<HTMLElement | null>(null);

export const ServiceFilterSlot = ({ children }: { children: ReactNode }): JSX.Element => {
	const slot: HTMLElement | null = useContext(ServiceFilterSlotContext);
	if (slot) return createPortal(children, slot);
	return <div className="ms-auto">{children}</div>;
};
