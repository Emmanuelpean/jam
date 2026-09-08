import { createContext, useContext } from "react";
import { Status } from "../services/schemas/Base";

export interface StatusContextValue extends Status {
	isLoading: boolean;
}

export const StatusContext = createContext<StatusContextValue | undefined>(undefined);

export const useStatus = (): StatusContextValue => {
	const context: StatusContextValue | undefined = useContext(StatusContext);
	if (!context) throw new Error("useStatus must be used within a StatusProvider");
	return context;
};
