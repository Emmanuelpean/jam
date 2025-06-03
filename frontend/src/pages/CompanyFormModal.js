import React from 'react';
import GenericFormModal from '../components/GenericFormModal';

const CompanyFormModal = ({
                              show,
                              onHide,
                              onSuccess
                          }) => {
    // Define form fields for company
    const formFields = [
        {
            name: 'name',
            label: 'Company Name',
            type: 'text',
            required: true,
            placeholder: 'Enter company name'
        },
        {
            name: 'url',
            label: 'Website',
            type: 'text',
            required: false,
            placeholder: 'https://example.com'
        },
        {
            name: 'description',
            label: 'Description',
            type: 'textarea',
            required: false,
            placeholder: 'Enter company description'
        }
    ];

    // Validation rules for company form
    const validationRules = {
        url: (value) => {
            if (value && !value.match(/^https?:\/\/.+/)) {
                return { isValid: false, message: 'Please enter a valid URL starting with http:// or https://' };
            }
            return { isValid: true };
        }
    };

    return (
        <GenericFormModal
            show={show}
            onHide={onHide}
            title="Company"
            fields={formFields}
            endpoint="companies"
            onSuccess={onSuccess}
            validationRules={validationRules}
        />
    );
};

export default CompanyFormModal;