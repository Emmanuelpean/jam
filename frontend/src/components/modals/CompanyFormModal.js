import React from 'react';
import GenericFormModal from '../GenericFormModal';

const CompanyFormModal = ({
                              show,
                              onHide,
                              onSuccess,
                              initialData = {},
                              isEdit = false
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

    return (
        <GenericFormModal
            show={show}
            onHide={onHide}
            title="Company"
            fields={formFields}
            endpoint="companies"
            onSuccess={onSuccess}
            initialData={initialData}
            isEdit={isEdit}
        />
    );
};

export default CompanyFormModal;