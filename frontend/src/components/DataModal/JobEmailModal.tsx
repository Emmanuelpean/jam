import React, { forwardRef, JSX } from "react";
import DataModal, { DataModalHandle, Fields, JamDataModalProps } from "./DataModal";
import { modalViewFields } from "../rendering/view/ModalFields";

export const JobEmailModal = forwardRef<DataModalHandle, JamDataModalProps>(
	({ size = "lg", onDelete }: JamDataModalProps, ref): JSX.Element => {
		const viewFields: Fields = [
			modalViewFields.title({ isTitle: true, key: "subject", label: undefined }),
			[modalViewFields.emailSender(), modalViewFields.platform({ label: "Platform" })],
			[modalViewFields.emailAlertName(), modalViewFields.emailJobFoundN()],
			modalViewFields.emailDateReceived(),
			modalViewFields.emailBody(),
		];

		return (
			<DataModal
				ref={ref}
				fields={{ form: [], view: viewFields }}
				entityType="jobEmail"
				size={size}
				onDelete={onDelete}
				canEdit={false}
				canDelete={false}
				additionalFields={[modalViewFields.emailScrapedJobs()]}
			/>
		);
	}
);
