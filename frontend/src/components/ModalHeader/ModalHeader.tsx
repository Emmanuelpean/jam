import React from "react";
import { CloseButton, Modal } from "react-bootstrap";
import type { ModalHeaderProps } from "react-bootstrap";

interface JamModalHeaderProps extends Omit<ModalHeaderProps, "closeButton"> {
	onClose: () => void;
}

export const ModalHeader: React.FC<JamModalHeaderProps> = ({ onClose, children, ...props }) => (
	<Modal.Header {...props}>
		{children}
		<CloseButton id="modal-close-btn" onClick={onClose} />
	</Modal.Header>
);
