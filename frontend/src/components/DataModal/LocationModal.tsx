import React, { forwardRef, JSX, ReactNode } from "react";
import DataModal, { DataModalHandle, JamDataModalProps } from "./DataModal";
import { modalViewFields } from "../rendering/view/ModalFields";
import { GeoLocationData } from "../../services/schemas/Base";
import { RenderParams } from "../rendering/view/ViewRenders";
import { GeolocatedEntry } from "../Maps/LocationMap";
import { getLocationIcon } from "../rendering/view/Icons";

export const LocationModal = forwardRef<DataModalHandle<GeoLocationData>, JamDataModalProps>(
	({ size = "lg" }: JamDataModalProps, ref): JSX.Element => {
		const ATTENDANCE_MESSAGES: Record<string, string> = {
			remote: "This job is fully remote",
			hybrid: "This is a hybrid position",
			"on-site": "This job requires on-site attendance",
		};

		const fields = {
			view: [
				modalViewFields.location({ isTitle: true }),
				[modalViewFields.city(), modalViewFields.postcode(), modalViewFields.country()],
				modalViewFields.geolocationMap(),
				{
					key: "attendance_message",
					render: (param: RenderParams): ReactNode => {
						const item = param.item as GeolocatedEntry;
						const icon = getLocationIcon(item.attendance_type ?? null);
						const msg = item.attendance_type ? ATTENDANCE_MESSAGES[item.attendance_type] : null;
						if (!msg) return null;
						return (
							<div className="text-center py-4">
								{icon && <i className={`bi bi-${icon} display-1 d-block mb-3`}></i>}
								<div className="lead fst-italic text-muted">{msg}</div>
							</div>
						);
					},
					displayCondition: (item: GeolocatedEntry): boolean => !item.location && !!item.attendance_type,
				},
			],
			form: [],
		};

		return (
			<DataModal<GeoLocationData>
				ref={ref}
				entityType="geolocation"
				size={size}
				fields={fields}
				canEdit={false}
				canDelete={false}
			/>
		);
	}
);
