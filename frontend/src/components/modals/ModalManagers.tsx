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
		const [selectedId, setSelectedId] = useState<string | number | null>(null);

		const handleClick = (itemId: number): void => {
			setSelectedItem(null);
			setSelectedId(itemId);
			setShowModal(true);
		};

		const handleHide = () => {
			setShowModal(false);
			setTimeout(() => {
				setSelectedItem(null);
				setSelectedId(null);
			}, 300);
		};

		// Empty handlers for modal callbacks since we're just viewing
		const handleSuccess = () => {};
		const handleDelete = () => {};

		return (
			<>
				{children(handleClick)}
				<ModalComponent
					show={showModal}
					onHide={handleHide}
					data={selectedItem}
					id={selectedId}
					submode="view"
					onSuccess={handleSuccess}
					onDelete={handleDelete}
					onJobSuccess={handleSuccess}
					onApplicationSuccess={handleSuccess}
					onJobDelete={handleDelete}
					onApplicationDelete={handleDelete}
				/>
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
