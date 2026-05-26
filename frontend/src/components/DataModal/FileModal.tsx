import React, { forwardRef, JSX } from "react";
import DataModal, { DataModalHandle, JamDataModalProps } from "./DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { ModalViewField, modalViewFields } from "../rendering/view/ModalFields";
import { FileData } from "../../services/schemas/DataTables";

export const FileModal = forwardRef<DataModalHandle<FileData>, JamDataModalProps>(
	({ size = "lg" }: JamDataModalProps, ref): JSX.Element => {
		const fields = {
			form: [formFields.name({ key: "filename", label: "Filename", required: true })],
			view: [
				modalViewFields.name({ key: "filename", label: "Filename", isTitle: true }),
				modalViewFields.fileSize(),
				modalViewFields.fileActions(),
			],
		};

		const additionalFields: ModalViewField[] = [
			modalViewFields.accordionJobTableFile({ helpText: "Jobs that used this file." }),
		];

		const transformFormData = (data: FileData) => ({
			filename: data.filename?.trim(),
		});

		return (
			<DataModal<FileData>
				ref={ref}
				size={size}
				fields={fields}
				additionalFields={additionalFields}
				entityType="file"
				transformFormData={transformFormData}
			/>
		);
	}
);
