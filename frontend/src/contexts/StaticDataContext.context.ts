import { createContext, useContext } from "react";
import { Currency } from "../services/schemas/Others";

export interface StaticData {
	currencies: Currency[];
}

export const StaticDataContext = createContext<StaticData>({ currencies: [] });

export const useStaticData = (): StaticData => useContext(StaticDataContext);
