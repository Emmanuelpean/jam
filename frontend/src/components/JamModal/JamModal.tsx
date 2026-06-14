import React, { JSX } from "react";
import { CloseButton, Modal, ModalProps } from "react-bootstrap";
import type { ModalHeaderProps } from "react-bootstrap";
import { useCommandPaletteContext } from "../../contexts/CommandPaletteContext";
import "./JamModal.scss";

const JamModalBase = ({ enforceFocus, ...props }: ModalProps): JSX.Element => {
	const { isOpen: isPaletteOpen } = useCommandPaletteContext();
	return <Modal {...props} enforceFocus={enforceFocus ?? !isPaletteOpen} />;
};

interface JamModalHeaderProps extends Omit<ModalHeaderProps, "closeButton"> {
	onClose: () => void;
}

const JamModalHeader: React.FC<JamModalHeaderProps> = ({ onClose, children, ...props }) => (
	<Modal.Header {...props}>
		{children}
		<CloseButton id="modal-close-btn" onClick={onClose} />
	</Modal.Header>
);

const JamModal = Object.assign(JamModalBase, {
	Body: Modal.Body,
	Footer: Modal.Footer,
	Title: Modal.Title,
	Header: JamModalHeader,
	Dialog: Modal.Dialog,
	TRANSITION_DURATION: Modal.TRANSITION_DURATION,
	BACKDROP_TRANSITION_DURATION: Modal.BACKDROP_TRANSITION_DURATION,
});

export default JamModal;
