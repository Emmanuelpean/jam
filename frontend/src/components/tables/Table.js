import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

export const useTableData = (endpoint, dependencies = []) => {
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
				const response = await fetch(`http://localhost:8000/${endpoint}/`, {
					headers: {
						Authorization: `Bearer ${token}`,
					},
				});

				if (!response.ok) {
					throw new Error(`Failed to fetch ${endpoint}`);
				}

				const result = await response.json();
				console.log(result);
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
