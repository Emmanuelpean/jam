import React, { ReactElement, ReactNode, useRef } from "react";
import { LocationModal } from "./LocationModal";
import { CompanyModal } from "./CompanyModal";
import { PersonModal } from "./PersonModal";
import { KeywordModal } from "./KeywordModal";
import { AggregatorModal } from "./AggregatorModal";
import { JobModal } from "./JobModal";
import { InterviewModal } from "./InterviewModal";
import { JobApplicationUpdateModal } from "./JobApplicationUpdateModal";
import { DataModalHandle } from "./DataModal/DataModal";

interface ModalManagerProps {
	children: (handleClick: (item: any) => void) => ReactNode;
}

type FlexibleModalComponent = React.ForwardRefExoticComponent<React.RefAttributes<DataModalHandle>>;

const createModalManager = (ModalComponent: FlexibleModalComponent) => {
	return ({ children }: ModalManagerProps): ReactElement => {
		const modalRef = useRef<DataModalHandle>(null);

		const handleClick = (item: any): void => {
			modalRef.current?.showView(item);
		};

		return (
			<>
				{children(handleClick)}
				<ModalComponent ref={modalRef} />
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
export const InterviewModalManager = createModalManager(InterviewModal);
export const JobApplicationUpdateModalManager = createModalManager(JobApplicationUpdateModal);
