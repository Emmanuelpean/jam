import React, { forwardRef, JSX, ReactNode } from "react";
import DataModal, { DataModalHandle, JamDataModalProps } from "./DataModal";
import { ModalViewField } from "../rendering/view/ModalFields";
import { GeoLocationData } from "../../services/schemas/Base";
import { RenderParams } from "../rendering/view/ViewRenders";
import LocationMap, { GeolocatedEntry } from "../Maps/LocationMap";
import { ScrapedJobData } from "../../services/schemas/Services";
import { attendanceTypeOptions, SelectOption } from "../rendering/form/FormOptions";
import { getLocationIcon } from "../rendering/view/Icons";

export const LocationModal = forwardRef<DataModalHandle<GeoLocationData>, JamDataModalProps>(
	({ size = "lg" }: JamDataModalProps, ref): JSX.Element => {
		const ATTENDANCE_MESSAGES: Record<string, string> = {
			remote: "This job is fully remote",
			hybrid: "This is a hybrid position (part remote, part on-site)",
			"on-site": "This job requires on-site attendance",
		};

		const fields: { view: ModalViewField[]; form: [] } = {
			view: [
				{
					key: "location",
					isTitle: true,
					render: (param: RenderParams): ReactNode => {
						const item = param.item as GeolocatedEntry;
						const locationString = (item as ScrapedJobData).parsed_location ?? item.location;
						const attendanceLabel =
							attendanceTypeOptions.find((o: SelectOption): boolean => o.value === item.attendance_type)
								?.label ?? null;
						if (locationString && attendanceLabel) return `${locationString} (${attendanceLabel})`;
						return locationString || attendanceLabel || null;
					},
				},
				{
					key: "location_map",
					label: "Location on Map",
					render: (param: RenderParams): ReactNode => (
						<LocationMap geolocatedEntry={[param.item as GeolocatedEntry]} scrollWheelZoom={false} />
					),
					displayCondition: (item: GeolocatedEntry): boolean => !!item.geolocation,
				},
				{
					key: "attendance_message",
					render: (param: RenderParams): ReactNode => {
						const item = param.item as GeolocatedEntry;
						const icon = getLocationIcon(item.attendance_type);
						const msg = item.attendance_type ? ATTENDANCE_MESSAGES[item.attendance_type] : null;
						if (!msg) return null;
						return (
							<div className="text-center py-4">
								{icon && <i className={`bi bi-${icon} display-1 d-block mb-3`}></i>}
								<p className="lead fst-italic text-muted">{msg}</p>
							</div>
						);
					},
					displayCondition: (item: GeolocatedEntry): boolean => !item.geolocation && !!item.attendance_type,
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
