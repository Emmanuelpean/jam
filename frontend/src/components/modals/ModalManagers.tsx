import React, { ReactElement, ReactNode, useState } from "react";
import { LocationModal } from "./LocationModal";
import { CompanyModal } from "./CompanyModal";
import { PersonModal } from "./PersonModal";
import { KeywordModal } from "./KeywordModal";
import { AggregatorModal } from "./AggregatorModal";
import { JobModal } from "./JobModal";

interface ModalManagerProps {
	children: (handleClick: (item: any) => void) => ReactNode;
}

type FlexibleModalComponent = React.ComponentType<any>;

const createModalManager = (ModalComponent: FlexibleModalComponent) => {
	return ({ children }: ModalManagerProps): ReactElement => {
		const [showModal, setShowModal] = useState<boolean>(false);
		const [selectedItem, setSelectedItem] = useState<any>(null);

		const handleClick = (item: any): void => {
			setSelectedItem(item);
			setShowModal(true);
		};

		const handleHide = () => {
			setShowModal(false);
			setTimeout(() => {
				setSelectedItem(null);
			}, 300);
		};

		return (
			<>
				{children(handleClick)}
				<ModalComponent show={showModal} onHide={handleHide} data={selectedItem} submode="view" />
			</>
		);
	};
};

export const LocationModalManager = createModalManager(LocationModal);
export const CompanyModalManager = createModalManager(CompanyModal);
export const PersonModalManager = createModalManager(PersonModal);
export const KeywordModalManager = createModalManager(KeywordModal);
export const JobModalManager = createModalManager(JobModal);
export const AggregatorModalManager = createModalManager(AggregatorModal);
