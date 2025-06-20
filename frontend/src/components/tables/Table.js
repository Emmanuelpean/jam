import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { api } from "../../services/api";


export const useTableData = (endpoint, dependencies = [], queryParams = {}) => {
	const { token } = useAuth();
	const navigate = useNavigate();
	const [data, setData] = useState([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);
	const [sortConfig, setSortConfig] = useState({ key: "created_at", direction: "desc" });
	const [searchTerm, setSearchTerm] = useState("");

	useEffect(() => {
		const fetchData = async () => {
			if (!token) {
				navigate("/login");
				return;
			}

			setLoading(true);
			try {
				// Build query string from queryParams
				const queryString = Object.keys(queryParams).length > 0
					? '?' + new URLSearchParams(queryParams).toString()
					: '';

				const result = await api.get(`${endpoint}/${queryString}`, token);
				setData(result);
			} catch (err) {
				console.error(`Error fetching ${endpoint}:`, err);
				setError(`Failed to load ${endpoint}. Please try again later.`);
			} finally {
				setLoading(false);
			}
		};

		fetchData();
	}, [token, navigate, endpoint, ...dependencies]);

	const addItem = (newItem) => {
		setData((prev) => [newItem, ...prev]);
	};

	const updateItem = (updatedItem) => {
		setData((prev) => prev.map((item) => (item.id === updatedItem.id ? updatedItem : item)));
	};

	const deleteItem = (itemId) => {
		setData((prev) => prev.filter((item) => item.id !== itemId));
	};

	return {
		data,
		setData,
		loading,
		error,
		sortConfig,
		setSortConfig,
		searchTerm,
		setSearchTerm,
		addItem,
		updateItem,
		deleteItem,
	};
};