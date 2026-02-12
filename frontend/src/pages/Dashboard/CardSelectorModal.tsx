import React from "react";
import { Modal, Form } from "react-bootstrap";
import { CARD_REGISTRY } from "./cardRegistry";

interface CardSelectorModalProps {
	show: boolean;
	onHide: () => void;
	visibleCards: string[];
	onCardsChange: (cards: string[]) => void;
	isPremium: boolean;
}

const CardSelectorModal: React.FC<CardSelectorModalProps> = ({
	show,
	onHide,
	visibleCards,
	onCardsChange,
	isPremium,
}) => {
	const availableCards = CARD_REGISTRY.filter((c) => !c.premiumOnly || isPremium);

	const handleToggle = (cardId: string) => {
		if (visibleCards.includes(cardId)) {
			onCardsChange(visibleCards.filter((id) => id !== cardId));
		} else {
			onCardsChange([...visibleCards, cardId]);
		}
	};

	return (
		<Modal show={show} onHide={onHide} centered>
			<Modal.Header closeButton>
				<Modal.Title>Dashboard Cards</Modal.Title>
			</Modal.Header>
			<Modal.Body>
				<p className="text-muted small mb-3">Choose which cards to display on your dashboard.</p>
				{availableCards.map((card) => (
					<Form.Check
						key={card.id}
						type="switch"
						id={`card-toggle-${card.id}`}
						className="mb-2 py-1"
						label={
							<span className="d-flex align-items-center gap-2">
								<i className={`bi bi-${card.icon}`}></i>
								{card.label}
							</span>
						}
						checked={visibleCards.includes(card.id)}
						onChange={() => handleToggle(card.id)}
					/>
				))}
			</Modal.Body>
		</Modal>
	);
};

export default CardSelectorModal;
