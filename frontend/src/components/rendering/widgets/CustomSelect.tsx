import React, { JSX, useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { GroupedSelectOption, SelectOption } from "../form/FormOptions";

export interface CustomSelectProps {
	id: string;
	name?: string;
	inputId?: string;
	options: SelectOption[] | GroupedSelectOption[];
	value: SelectOption | SelectOption[] | null;
	onChange: (value: SelectOption | SelectOption[] | null) => void;
	isMulti?: boolean;
	isSearchable?: boolean;
	isClearable?: boolean;
	isDisabled?: boolean;
	closeMenuOnSelect?: boolean;
	placeholder?: string;
	size?: "sm";
	className?: string;
	menuPortalClassName?: string;
	onMenuClose?: () => void;
	addButton?: {
		modalRef: React.RefObject<any>;
		transformParentData?: ((parentData: any) => any) | null;
		onSuccess?: (newData: any) => void;
		id?: string;
	};
	parentData?: any;
	previewHandlers?: {
		onHover: (option: SelectOption, position: { top: number; left: number }) => void;
		onHoverEnd: () => void;
	};
}

interface AddButtonIndicatorProps {
	addButton: NonNullable<CustomSelectProps["addButton"]>;
	parentData?: any;
	onClose: () => void;
}

const AddButtonIndicator = ({ addButton, parentData, onClose }: AddButtonIndicatorProps): JSX.Element => {
	const buttonId: string = addButton.id ?? "add-button";
	const [hover, setHover] = useState(false);

	const handleMouseDown = (e: React.MouseEvent) => {
		e.preventDefault();
		e.stopPropagation();
		onClose();
		const { modalRef, transformParentData, onSuccess } = addButton;
		const cb = onSuccess ?? (() => {});
		if (transformParentData && parentData) {
			const defaultData = transformParentData(parentData);
			modalRef.current?.showAdd(defaultData, cb);
		} else {
			modalRef.current?.showAdd({}, cb);
		}
	};

	return (
		<div
			className={`custom-dropdown-indicator${hover ? " active" : ""}`}
			onMouseDown={handleMouseDown}
			onClick={(e) => {
				e.preventDefault();
				e.stopPropagation();
			}}
			onMouseEnter={() => setHover(true)}
			onMouseLeave={() => setHover(false)}
			tabIndex={-1}
			aria-label="Add new item"
			role="button"
			title="Add new item"
			id={buttonId}
		>
			<i className="bi bi-plus-circle"></i>
		</div>
	);
};

export const CustomSelect = ({
	id,
	name,
	inputId,
	options,
	value,
	onChange,
	isMulti = false,
	isSearchable = true,
	isClearable = true,
	isDisabled = false,
	closeMenuOnSelect,
	placeholder,
	className = "",
	menuPortalClassName = "",
	size,
	onMenuClose,
	addButton,
	parentData,
	previewHandlers,
}: CustomSelectProps): JSX.Element => {
	const [isOpen, setIsOpen] = useState(false);
	const [isClosing, setIsClosing] = useState(false);
	const [inputValue, setInputValue] = useState("");
	const [focusedIndex, setFocusedIndex] = useState(-1);
	const [isFocused, setIsFocused] = useState(false);
	const [menuStyles, setMenuStyles] = useState<React.CSSProperties>({});
	const [removingValues, setRemovingValues] = useState<Set<string>>(new Set());
	const [menuPlacedAbove, setMenuPlacedAbove] = useState(false);

	const containerRef = useRef<HTMLDivElement>(null);
	const controlRef = useRef<HTMLDivElement>(null);
	const inputRef = useRef<HTMLInputElement>(null);
	const menuRef = useRef<HTMLDivElement>(null);
	const isClickingOptionRef = useRef(false);
	const closeTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

	const effectiveCloseMenuOnSelect = closeMenuOnSelect ?? !isMulti;

	const isGrouped = useMemo(() => options.length > 0 && "options" in options[0]!, [options]);

	const flatOptions = useMemo(() => {
		const all = isGrouped
			? (options as GroupedSelectOption[]).flatMap((g) => g.options)
			: (options as SelectOption[]);
		if (!inputValue || !isSearchable) return all;
		const lower = inputValue.toLowerCase();
		return all.filter((o) => o.label.toLowerCase().includes(lower));
	}, [options, inputValue, isSearchable, isGrouped]);

	const hasValue = isMulti
		? Array.isArray(value) && (value as SelectOption[]).length > 0
		: value !== null && value !== undefined;

	const positionMenu = useCallback(() => {
		if (!controlRef.current) return;
		const rect = controlRef.current.getBoundingClientRect();
		const MARGIN = 6;
		const spaceBelow = window.innerHeight - rect.bottom - MARGIN;
		const spaceAbove = rect.top - MARGIN;
		const placeAbove = spaceBelow < 200 && spaceAbove > spaceBelow;
		setMenuPlacedAbove(placeAbove);
		const maxHeight = Math.max(placeAbove ? spaceAbove : spaceBelow, 80);
		setMenuStyles({
			position: "fixed",
			...(placeAbove ? { bottom: window.innerHeight - rect.top + MARGIN } : { top: rect.bottom + MARGIN }),
			left: rect.left,
			width: rect.width,
			zIndex: 9999,
			maxHeight,
		});
	}, []);

	const closeMenu = useCallback(() => {
		if (closeTimerRef.current) clearTimeout(closeTimerRef.current);
		setIsOpen((wasOpen) => {
			if (wasOpen) setIsClosing(true);
			return false;
		});
		setInputValue("");
		setFocusedIndex(-1);
		closeTimerRef.current = setTimeout(() => {
			setIsClosing(false);
			onMenuClose?.();
		}, 150);
	}, [onMenuClose]);

	const openMenu = useCallback(() => {
		if (isDisabled) return;
		if (closeTimerRef.current) {
			clearTimeout(closeTimerRef.current);
			setIsClosing(false);
		}
		if (controlRef.current) {
			const rect = controlRef.current.getBoundingClientRect();
			const MARGIN = 6;
			const spaceBelow = window.innerHeight - rect.bottom - MARGIN;
			const spaceAbove = rect.top - MARGIN;
			setMenuPlacedAbove(spaceBelow < 200 && spaceAbove > spaceBelow);
		}
		setIsOpen(true);
		setFocusedIndex(-1);
	}, [isDisabled]);

	// Cleanup close timer on unmount
	useEffect(
		() => () => {
			if (closeTimerRef.current) clearTimeout(closeTimerRef.current);
		},
		[]
	);

	// Reposition menu on open and on scroll/resize
	useLayoutEffect(() => {
		if (!isOpen) return;
		positionMenu();
		const handleReposition = () => positionMenu();
		window.addEventListener("scroll", handleReposition, true);
		window.addEventListener("resize", handleReposition);
		const ro = new ResizeObserver(() => positionMenu());
		if (controlRef.current) ro.observe(controlRef.current);
		return () => {
			window.removeEventListener("scroll", handleReposition, true);
			window.removeEventListener("resize", handleReposition);
			ro.disconnect();
		};
	}, [isOpen, positionMenu]);

	// Click-outside to close
	useEffect(() => {
		if (!isOpen) return;
		const handler = (e: PointerEvent) => {
			if (!containerRef.current?.contains(e.target as Node) && !menuRef.current?.contains(e.target as Node)) {
				closeMenu();
			}
		};
		document.addEventListener("pointerdown", handler);
		return () => document.removeEventListener("pointerdown", handler);
	}, [isOpen, closeMenu]);

	// Scroll focused option into view
	useEffect(() => {
		if (focusedIndex >= 0 && isOpen && menuRef.current) {
			const el = menuRef.current.querySelector(`#${id}-option-${focusedIndex}`);
			el?.scrollIntoView({ block: "nearest" });
		}
	}, [focusedIndex, isOpen, id]);

	// Reset focusedIndex when search changes
	useEffect(() => {
		setFocusedIndex(-1);
	}, [inputValue]);

	const removeOptionValue = useCallback(
		(opt: SelectOption) => {
			setRemovingValues((prev) => new Set([...prev, opt.value]));
			setTimeout(() => {
				const current = Array.isArray(value) ? (value as SelectOption[]) : [];
				const newValue = current.filter((v) => v.value !== opt.value);
				onChange(newValue.length > 0 ? newValue : null);
				setRemovingValues((prev) => {
					const next = new Set(prev);
					next.delete(opt.value);
					return next;
				});
			}, 250);
		},
		[value, onChange]
	);

	const selectOption = useCallback(
		(opt: SelectOption) => {
			if (isMulti) {
				const current = Array.isArray(value) ? (value as SelectOption[]) : [];
				const isSelected = current.some((v) => v.value === opt.value);
				const newValue = isSelected ? current.filter((v) => v.value !== opt.value) : [...current, opt];
				onChange(newValue.length > 0 ? newValue : null);
				if (effectiveCloseMenuOnSelect) {
					closeMenu();
					inputRef.current?.blur();
				}
			} else {
				onChange(opt);
				if (effectiveCloseMenuOnSelect) {
					closeMenu();
					inputRef.current?.blur();
				}
			}
		},
		[isMulti, value, onChange, effectiveCloseMenuOnSelect, closeMenu]
	);

	const handleClear = useCallback(
		(e: React.MouseEvent) => {
			e.preventDefault();
			e.stopPropagation();
			onChange(null);
		},
		[onChange]
	);

	const handleControlMouseDown = useCallback(
		(e: React.MouseEvent) => {
			if (isDisabled) return;
			const target = e.target as HTMLElement;
			if (
				target.closest(".jam-select__tag-remove") ||
				target.closest(".jam-select__clear") ||
				target.closest(".custom-dropdown-indicator")
			)
				return;
			e.preventDefault();
			if (isOpen) {
				closeMenu();
			} else {
				openMenu();
			}
			inputRef.current?.focus();
		},
		[isDisabled, isOpen, openMenu, closeMenu]
	);

	const handleKeyDown = useCallback(
		(e: React.KeyboardEvent<HTMLInputElement>) => {
			if (!isOpen) {
				if (e.key === "ArrowDown" || e.key === "ArrowUp" || e.key === "Enter" || e.key === " ") {
					e.preventDefault();
					openMenu();
				}
				return;
			}
			switch (e.key) {
				case "ArrowDown":
					e.preventDefault();
					setFocusedIndex((prev) => Math.min(prev + 1, flatOptions.length - 1));
					break;
				case "ArrowUp":
					e.preventDefault();
					setFocusedIndex((prev) => Math.max(prev - 1, 0));
					break;
				case "Enter":
					e.preventDefault();
					if (focusedIndex >= 0 && flatOptions[focusedIndex]) {
						selectOption(flatOptions[focusedIndex]!);
					}
					break;
				case "Escape":
					e.preventDefault();
					closeMenu();
					break;
				case "Tab":
					closeMenu();
					break;
				case "Backspace":
					if (isMulti && !inputValue && Array.isArray(value) && (value as SelectOption[]).length > 0) {
						const vals = value as SelectOption[];
						removeOptionValue(vals[vals.length - 1]!);
					}
					break;
				default:
					break;
			}
		},
		[
			isOpen,
			flatOptions,
			focusedIndex,
			selectOption,
			closeMenu,
			openMenu,
			isMulti,
			inputValue,
			value,
			removeOptionValue,
		]
	);

	const renderOption = (opt: SelectOption, flatIdx: number): JSX.Element => {
		const isFocusedOpt = flatIdx === focusedIndex;
		const isSelected = isMulti
			? Array.isArray(value) && (value as SelectOption[]).some((v) => v.value === opt.value)
			: !Array.isArray(value) && (value as SelectOption | null)?.value === opt.value;

		let optClassName = "jam-select__option";
		if (isFocusedOpt) optClassName += " jam-select__option--focused";
		if (isSelected) optClassName += " jam-select__option--selected";

		return (
			<div
				key={opt.value}
				id={`${id}-option-${flatIdx}`}
				className={optClassName}
				role="option"
				aria-selected={isSelected}
				onMouseDown={(e) => {
					e.preventDefault();
					isClickingOptionRef.current = true;
					previewHandlers?.onHoverEnd();
				}}
				onMouseUp={() => {
					setTimeout(() => {
						isClickingOptionRef.current = false;
					}, 100);
				}}
				onClick={() => selectOption(opt)}
				onMouseEnter={(e) => {
					setFocusedIndex(flatIdx);
					if (!isClickingOptionRef.current && previewHandlers) {
						if (window.innerWidth <= 768) return;
						const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
						const GAP = 20;
						const PREVIEW_WIDTH = 450;
						const spaceRight = window.innerWidth - rect.right;
						const left = spaceRight >= rect.left ? rect.right + GAP : rect.left - GAP - PREVIEW_WIDTH;
						previewHandlers.onHover(opt, { top: rect.top, left });
					}
				}}
				onMouseLeave={() => {
					previewHandlers?.onHoverEnd();
				}}
			>
				{opt.label}
			</div>
		);
	};

	const renderMenu = (): JSX.Element => {
		if (flatOptions.length === 0) {
			return (
				<div className="jam-select__option" style={{ opacity: 0.5, cursor: "default", pointerEvents: "none" }}>
					No options
				</div>
			);
		}

		if (!isGrouped) {
			return <>{flatOptions.map((opt, i) => renderOption(opt, i))}</>;
		}

		const groups = options as GroupedSelectOption[];
		const lower = inputValue ? inputValue.toLowerCase() : "";
		let flatIdx = 0;

		const groupElements = groups.map((group) => {
			const filteredOpts =
				inputValue && isSearchable
					? group.options.filter((o) => o.label.toLowerCase().includes(lower))
					: group.options;

			if (filteredOpts.length === 0) return null;

			const groupItems = filteredOpts.map((opt) => {
				const idx = flatIdx++;
				return renderOption(opt, idx);
			});

			return (
				<div key={group.label} className="jam-select__group">
					<div className="jam-select__group-heading">{group.label}</div>
					{groupItems}
				</div>
			);
		});

		return <>{groupElements}</>;
	};

	const effectiveInputId: string = inputId ?? `${id}-input`;
	const listboxId = `${id}-listbox`;

	const controlClasses: string[] = ["jam-select__control"];
	if (isOpen) controlClasses.push("jam-select--open");
	if (isFocused) controlClasses.push("jam-select--focused");

	const containerClasses: string[] = ["jam-select"];
	if (size === "sm") containerClasses.push("jam-select--sm");
	if (isDisabled) containerClasses.push("jam-select--disabled");
	if (className) containerClasses.push(className);

	const valuesClasses: string[] = ["jam-select__values"];
	if (isMulti) valuesClasses.push("jam-select--multi");

	const portalClasses: string[] = ["jam-select__portal"];
	if (isClosing) portalClasses.push("jam-select__portal--closing");
	if (size === "sm") portalClasses.push("jam-select--sm-menu");
	if (menuPortalClassName) portalClasses.push(menuPortalClassName);

	const selectedValues: SelectOption[] = Array.isArray(value) ? (value as SelectOption[]) : [];
	const singleValue: SelectOption | null = !isMulti ? (value as SelectOption | null) : null;
	const showPlaceholder: boolean = !hasValue && !inputValue;
	const showSingleValue: boolean = !isMulti && singleValue !== null && !inputValue;

	// Collapse input to cursor-width when a value is shown so it stays inline with the value/tags
	const inputShrunk = (showSingleValue || (isMulti && hasValue)) && !inputValue;
	const inputStyle: React.CSSProperties = {
		...(isSearchable ? {} : { width: "2px", color: "transparent", caretColor: "transparent" }),
		...(!isMulti && showSingleValue ? { order: -1, caretColor: "transparent" } : {}),
		...(inputShrunk ? { flex: "0 0 auto", minWidth: "2px", width: "2px" } : {}),
	};

	const backdrop = (
		<div
			className={`jam-select__backdrop${isClosing ? " jam-select__backdrop--closing" : ""}`}
			onPointerDown={(e) => {
				e.preventDefault();
				closeMenu();
			}}
		/>
	);

	const menu = (
		<div
			id={listboxId}
			className={portalClasses.join(" ")}
			style={menuStyles}
			ref={menuRef}
			role="listbox"
			aria-multiselectable={isMulti}
		>
			<div
				className="jam-select__menu"
				style={{ transformOrigin: menuPlacedAbove ? "bottom center" : "top center" }}
			>
				<div
					className="jam-select__menu-list"
					style={
						menuStyles.maxHeight
							? { maxHeight: Math.min(300, (menuStyles.maxHeight as number) - 12) }
							: undefined
					}
				>
					{renderMenu()}
				</div>
			</div>
		</div>
	);

	return (
		<div id={id} className={containerClasses.join(" ")} ref={containerRef}>
			<div className={controlClasses.join(" ")} ref={controlRef} onMouseDown={handleControlMouseDown}>
				<div className={valuesClasses.join(" ")}>
					{isMulti &&
						selectedValues.map((v) => (
							<div
								key={v.value}
								className={`jam-select__tag${removingValues.has(v.value) ? " jam-select__tag--removing" : ""}`}
							>
								<span className="jam-select__tag-label">{v.label}</span>
								<button
									type="button"
									className="jam-select__tag-remove"
									onMouseDown={(e) => {
										e.preventDefault();
										e.stopPropagation();
										removeOptionValue(v);
									}}
									tabIndex={-1}
									aria-label={`Remove ${v.label}`}
								>
									×
								</button>
							</div>
						))}
					{showSingleValue && <span className="jam-select__single-value">{singleValue!.label}</span>}
					{showPlaceholder && <span className="jam-select__placeholder">{placeholder ?? "Select..."}</span>}
					<input
						id={effectiveInputId}
						name={name}
						className="jam-select__input"
						ref={inputRef}
						value={inputValue}
						onChange={(e) => {
							if (!isSearchable) return;
							setInputValue(e.target.value);
							if (e.target.value && !isOpen) openMenu();
						}}
						onKeyDown={handleKeyDown}
						onFocus={() => setIsFocused(true)}
						onBlur={() => setIsFocused(false)}
						size={1}
						readOnly={!isSearchable}
						role="combobox"
						aria-controls={listboxId}
						aria-expanded={isOpen}
						aria-autocomplete="list"
						autoComplete="off"
						disabled={isDisabled}
						style={inputStyle}
					/>
				</div>
				<div className="jam-select__indicators">
					{isClearable && hasValue && (
						<button
							type="button"
							className="jam-select__clear"
							onMouseDown={handleClear}
							tabIndex={-1}
							aria-label="Clear"
						>
							<i className="bi bi-x" />
						</button>
					)}
					<span className="jam-select__separator" aria-hidden="true" />
					{addButton ? (
						<AddButtonIndicator addButton={addButton} parentData={parentData} onClose={closeMenu} />
					) : (
						<i
							className={`bi bi-chevron-down jam-select__arrow${isOpen ? " jam-select__arrow--open" : ""}${isOpen && menuPlacedAbove ? " jam-select__arrow--above" : ""}`}
							aria-hidden="true"
						></i>
					)}
				</div>
			</div>
			{(isOpen || isClosing) && createPortal(<>{backdrop}{menu}</>, document.getElementById("jam-select-portal") ?? document.body)}
		</div>
	);
};
