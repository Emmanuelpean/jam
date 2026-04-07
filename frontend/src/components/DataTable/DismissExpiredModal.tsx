import React, { JSX } from "react";
import { Modal } from "react-bootstrap";
import JamModal from "../JamModal/JamModal";
import { ModalHeader } from "../ModalHeader/ModalHeader";
import { DataTable } from "./DataTable";
import { tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobModal } from "../DataModal/ScrapedJobModal";
import { ScrapedJobData } from "../../services/schemas/Services";
import { ActionButton } from "../rendering/form/ActionButton";

interface DismissExpiredModalProps {
	show: boolean;
	jobs: ScrapedJobData[];
	onConfirm: (ids: number[]) => Promise<void>;
	onHide: () => void;
}

const DismissExpiredModal: React.FC<DismissExpiredModalProps> = ({
	show,
	jobs,
	onConfirm,
	onHide,
}: DismissExpiredModalProps): JSX.Element => {
	const columns = [
		tableColumns.titleColumn(),
		tableColumns.scrapedCompanyColumn(),
		tableColumns.platformColumn(),
		tableColumns.applicationDeadline(),
		tableColumns.expiredReasonColumn(),
		tableColumns.scrapingStatusColumn(),
	];

	return (
		<JamModal
			show={show}
			onHide={onHide}
			size="xl"
			centered={true}
			className="data-modal"
			id="dismiss-expired-modal"
		>
			<ModalHeader onClose={onHide}>
				<Modal.Title>
					Delete {jobs.length} Expired Job Alert{jobs.length !== 1 ? "s" : ""}
				</Modal.Title>
			</ModalHeader>
			<Modal.Body>
				<DataTable
					entityType="scrapedJob"
					data={jobs}
					columns={columns}
					Modal={ScrapedJobModal}
					modalSize="xl"
					showAdd={false}
					showSearch={true}
					showAllEntries={true}
					compact={true}
					menuItems={["view"]}
					defaultModalMode="view"
				modalProps={{ canEdit: false }}
				/>
			</Modal.Body>
			<Modal.Footer>
				<div className="modal-buttons-container">
					<ActionButton
						id="dismiss-expired-cancel-btn"
						variant="secondary"
						onClick={onHide}
						defaultText="Cancel"
						fullWidth={false}
					/>
					<ActionButton
						id="dismiss-expired-confirm-btn"
						variant="danger"
						onClick={() => onConfirm(jobs.map((j) => j.id))}
						defaultText={`Delete ${jobs.length}`}
						loadingText="Deleting..."
						fullWidth={false}
					/>
				</div>
			</Modal.Footer>
		</JamModal>
	);
};

export default DismissExpiredModal;
