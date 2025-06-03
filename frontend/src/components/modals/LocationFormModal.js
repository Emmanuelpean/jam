import React from 'react';
import GenericFormModal from '../GenericFormModal';

const LocationFormModal = ({
                               show,
                               onHide,
                               onSuccess
                           }) => {

    const formFields = [
        {
            name: 'postcode',
            label: 'Post Code',
            type: 'text',
            required: false,
            placeholder: 'Enter a post code'
        },
        {
            name: 'city',
            label: 'City',
            type: 'text',
            required: false,
            placeholder: 'Enter a city name'
        },
        {
            name: 'country',
            label: 'Country',
            type: 'text',
            required: false,
            placeholder: 'Enter country'
        },
        {
            name: 'remote',
            label: 'Remote',
            type: 'checkbox',
            required: false
        }
    ];

    // Custom validation rules to ensure at least one field is filled
    const validationRules = {
        city: (value, formData) => {
            const hasAnyValue = formData.city || formData.postcode || formData.country || formData.remote;
            if (!hasAnyValue) {
                return {
                    isValid: false,
                    message: 'Please fill in at least one field (city, state, country, or check remote)'
                };
            }
            return {isValid: true};
        }
    };

    return (
        <GenericFormModal
            show={show}
            onHide={onHide}
            title="Location"
            fields={formFields}
            endpoint="locations"
            onSuccess={onSuccess}
            validationRules={validationRules}
        />
    );
};

export default LocationFormModal;