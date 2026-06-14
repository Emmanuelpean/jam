import React from "react";
import { TourStep } from "./tourSteps";

export const SPOTLIGHT_PAD = 8;
export const POP_W = 450;
export const POP_W_LAST = 550;

const GAP = 14;
const POP_MIN_H = 120;
const MARGIN = 16;

type Side = "top" | "bottom" | "left" | "right";
const OPPOSITE: Record<Side, Side> = { bottom: "top", top: "bottom", left: "right", right: "left" };
const ALL_SIDES: Side[] = ["bottom", "top", "right", "left"];

function bestSide(rect: DOMRect, preferred: Side): Side {
	const vw = window.innerWidth;
	const vh = window.innerHeight;
	const space: Record<Side, number> = {
		bottom: vh - rect.bottom - SPOTLIGHT_PAD - GAP,
		top: rect.top - SPOTLIGHT_PAD - GAP,
		right: vw - rect.right - SPOTLIGHT_PAD - GAP,
		left: rect.left - SPOTLIGHT_PAD - GAP,
	};
	const fits: Record<Side, boolean> = {
		bottom: space.bottom >= POP_MIN_H + MARGIN,
		top: space.top >= POP_MIN_H + MARGIN,
		right: space.right >= POP_W + MARGIN,
		left: space.left >= POP_W + MARGIN,
	};

	if (fits[preferred]) return preferred;
	if (fits[OPPOSITE[preferred]]) return OPPOSITE[preferred];

	const others = ALL_SIDES.filter((s) => s !== preferred && s !== OPPOSITE[preferred]);
	others.sort((a, b) => space[b] - space[a]);
	for (const s of others) if (fits[s]) return s;

	return ALL_SIDES.reduce((a, b) => (space[a] >= space[b] ? a : b));
}

export function computePopoverStyle(rect: DOMRect, placement: TourStep["placement"]): React.CSSProperties {
	if (placement === "center") return {};

	const vw = window.innerWidth;
	const vh = window.innerHeight;
	const side = bestSide(rect, placement as Side);
	const leftCentered = Math.max(MARGIN, Math.min(rect.left + rect.width / 2 - POP_W / 2, vw - POP_W - MARGIN));
	const topCentered = Math.max(MARGIN, Math.min(rect.top + rect.height / 2 - POP_MIN_H / 2, vh - POP_MIN_H - MARGIN));

	switch (side) {
		case "bottom": {
			const top = rect.bottom + SPOTLIGHT_PAD + GAP;
			return { top, left: leftCentered, maxHeight: Math.max(vh - top - MARGIN, POP_MIN_H) };
		}
		case "top": {
			const cssBottom = vh - (rect.top - SPOTLIGHT_PAD - GAP);
			return { bottom: cssBottom, left: leftCentered, maxHeight: Math.max(rect.top - SPOTLIGHT_PAD - GAP - MARGIN, POP_MIN_H) };
		}
		case "right": {
			const left = Math.min(rect.right + SPOTLIGHT_PAD + GAP, vw - POP_W - MARGIN);
			return { left, top: topCentered, maxHeight: Math.max(vh - topCentered - MARGIN, POP_MIN_H) };
		}
		case "left": {
			const left = Math.max(MARGIN, rect.left - SPOTLIGHT_PAD - GAP - POP_W);
			return { left, top: topCentered, maxHeight: Math.max(vh - topCentered - MARGIN, POP_MIN_H) };
		}
	}
}
