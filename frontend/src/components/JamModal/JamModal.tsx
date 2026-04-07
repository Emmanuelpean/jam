import React, { JSX } from "react";
import { Modal, ModalProps } from "react-bootstrap";
import { useCommandPaletteContext } from "../../contexts/CommandPaletteContext";

const JamModalBase = ({ enforceFocus, ...props }: ModalProps): JSX.Element => {
	const { isOpen: isPaletteOpen } = useCommandPaletteContext();
	return <Modal {...props} enforceFocus={enforceFocus ?? !isPaletteOpen} />;
};

const JamModal = Object.assign(JamModalBase, {
	Body: Modal.Body,
	Footer: Modal.Footer,
	Title: Modal.Title,
	Header: Modal.Header,
	Dialog: Modal.Dialog,
	TRANSITION_DURATION: Modal.TRANSITION_DURATION,
	BACKDROP_TRANSITION_DURATION: Modal.BACKDROP_TRANSITION_DURATION,
});

export default JamModal;
