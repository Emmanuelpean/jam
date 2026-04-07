import { useEffect } from "react";
import { useAuth } from "../../contexts/AuthContext";
import { useCommandPaletteContext } from "../../contexts/CommandPaletteContext";

export function useCommandPalette(): { isOpen: boolean; close: () => void } {
	const { isAuthenticated } = useAuth();
	const { isOpen, setIsOpen } = useCommandPaletteContext();

	useEffect(() => {
		if (!isOpen) return;
		const handleEsc = (e: KeyboardEvent): void => {
			if (e.key === "Escape") {
				e.stopPropagation();
				setIsOpen(false);
			}
		};
		window.addEventListener("keydown", handleEsc, true);
		return () => window.removeEventListener("keydown", handleEsc, true);
	}, [isOpen]);

	useEffect(() => {
		const handleKeyDown = (e: KeyboardEvent): void => {
			if (!isAuthenticated) return;
			if (e.key === "k" && (e.ctrlKey || e.metaKey)) {
				e.preventDefault();
				setIsOpen(!isOpen);
			}
		};
		window.addEventListener("keydown", handleKeyDown);
		return () => window.removeEventListener("keydown", handleKeyDown);
	}, [isAuthenticated, isOpen]);

	return { isOpen, close: () => setIsOpen(false) };
}
