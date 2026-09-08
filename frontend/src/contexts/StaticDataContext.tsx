import React, { JSX, ReactNode, useEffect, useState } from "react";
import { currenciesApi } from "../services/api/DataTables";
import { Currency } from "../services/schemas/Others";
import { StaticDataContext } from "./StaticDataContext.context";

export { useStaticData } from "./StaticDataContext.context";
export type { StaticData } from "./StaticDataContext.context";

export const StaticDataProvider = ({ children }: { children: ReactNode }): JSX.Element => {
	const [currencies, setCurrencies] = useState<Currency[]>([]);

	useEffect((): void => {
		currenciesApi.getAll("").then((res) => setCurrencies(res.data || [])).catch(() => {});
	}, []);

	return <StaticDataContext.Provider value={{ currencies }}>{children}</StaticDataContext.Provider>;
};
