import React from 'react';
import GenericModal from '../GenericModal';

const LocationFormModal = ({
                               show,
                               onHide,
                               initialData = {},
                               onSuccess,
                               isEdit = false
                           }) => {
    const locationFields = [
        {
            name: 'city',
            label: 'City',
            type: 'text',
            placeholder: 'Enter city name...',
            required: true
        },
        {
            name: 'state',
            label: 'State/Province',
            type: 'text',
            placeholder: 'Enter state or province...'
        },
        {
            name: 'country',
            label: 'Country',
            type: 'text',
            placeholder: 'Enter country...',
            required: true
        },
        {
            name: 'postcode',
            label: 'Postal Code',
            type: 'text',
            placeholder: 'Enter postal code...'
        },
        {
            name: 'remote',
            label: 'Remote Position',
            type: 'checkbox',
            checkboxLabel: 'This is a remote position'
        }
    ];

    return (
        <GenericModal
            show={show}
            onHide={onHide}
            mode="form"
            title="Location"
            fields={locationFields}
            initialData={{
                city: '',
                state: '',
                country: '',
                postcode: '',
                remote: false,
                ...initialData
            }}
            endpoint="locations"
            onSuccess={onSuccess}
            isEdit={isEdit}
        />
    );
};

export default LocationFormModal;