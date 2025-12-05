import { createContext, useContext, ReactNode } from "react";
import useGenericAlert from "../hooks/useGenericAlert";
import AlertModal from "../components/modals/AlertModal";

const AlertContext = createContext<ReturnType<typeof useGenericAlert> | null>(null);

export const AlertProvider = ({ children }: { children: ReactNode }) => {
	const alertHook = useGenericAlert();

	return (
		<AlertContext.Provider value={alertHook}>
			{children}
			<AlertModal alertState={alertHook.alertState} hideAlert={alertHook.hideAlert} />
		</AlertContext.Provider>
	);
};

export const useAlert = () => {
	const context = useContext(AlertContext);
	if (!context) {
		throw new Error("useAlert must be used within AlertProvider");
	}
	return context;
};
