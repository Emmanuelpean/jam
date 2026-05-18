import React, { createContext, JSX, ReactNode, useContext, useEffect, useState } from "react";
import { currenciesApi } from "../services/api/DataTables";
import { Currency } from "../services/schemas/Others";

interface StaticData {
	currencies: Currency[];
}

const StaticDataContext = createContext<StaticData>({ currencies: [] });

export const StaticDataProvider = ({ children }: { children: ReactNode }): JSX.Element => {
	const [currencies, setCurrencies] = useState<Currency[]>([]);

	useEffect((): void => {
		currenciesApi.getAll("").then((res) => setCurrencies(res.data || [])).catch(() => {});
	}, []);

	return <StaticDataContext.Provider value={{ currencies }}>{children}</StaticDataContext.Provider>;
};

export const useStaticData = (): StaticData => useContext(StaticDataContext);
