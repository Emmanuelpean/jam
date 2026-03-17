import React, { forwardRef, JSX } from "react";
import DataModal, { DataModalHandle, Fields, JamDataModalProps, SectionConfig } from "./DataModal";
import { modalViewFields } from "../rendering/view/ModalFields";

export const JobEmailModal = forwardRef<DataModalHandle, JamDataModalProps & { scrapedJobsReadOnly?: boolean }>(
	(
		{ size = "xl", onDelete, scrapedJobsReadOnly = false }: JamDataModalProps & { scrapedJobsReadOnly?: boolean },
		ref
	): JSX.Element => {
		const viewFields: Fields = [
			modalViewFields.title({ isTitle: true, key: "subject", label: undefined }),
			[modalViewFields.emailSender(), modalViewFields.platform({ label: "Platform" })],
			[modalViewFields.emailAlertName(), modalViewFields.emailJobFoundN()],
			modalViewFields.emailDateReceived(),
			{
				type: "section",
				key: "scraped-jobs",
				title: "Scraped Jobs",
				icon: "bi-briefcase",
				defaultExpanded: false,
				fields: [
					scrapedJobsReadOnly
						? modalViewFields.emailScrapedJobsReadOnly()
						: modalViewFields.emailScrapedJobs(),
				],
			} as SectionConfig,
			{
				type: "section",
				key: "email-content",
				title: "Email content",
				icon: "bi-envelope-open",
				defaultExpanded: false,
				fields: [modalViewFields.emailBody({ label: "" })],
			} as SectionConfig,
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
			/>
		);
	}
);
