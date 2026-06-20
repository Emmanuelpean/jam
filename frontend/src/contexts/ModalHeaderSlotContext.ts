import { createContext } from "react";

// Set by the admin page modal to the DOM node of its header's status area. When
// present, a page is being shown inside the modal: it renders its body only and
// portals its status control into this node (the modal builds the icon + title).
// Null on standalone routes, where pages render their own PageHeader inline.
export const ModalHeaderSlotContext = createContext<HTMLElement | null>(null);
