import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

if (import.meta.env.VITE_ENABLE_ANALYTICS === "true") {
	const s = document.createElement("script");
	s.src = import.meta.env.BASE_URL + "swetrix.js";
	s.onload = () => {
		window.swetrix.init("uQe6o51TmAzM", { apiURL: "/api/v1/data" });
		window.swetrix.trackViews();
	};
	document.head.appendChild(s);
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
	// <React.StrictMode>
	<App />
	// </React.StrictMode>
);

