import React from 'react';
import GenericViewModal from '../components/GenericViewModal';

const CompanyViewModal = ({show, onHide, company, onEdit}) => {
    // Define view fields for company (same structure as form fields)
    const viewFields = [
        {
            name: 'name',
            label: 'Company Name',
            type: 'text'
        },
        {
            name: 'url',
            label: 'Website',
            type: 'url'
        },
        {
            name: 'description',
            label: 'Description',
            type: 'textarea'
        }
    ];

    return (
        <GenericViewModal
            show={show}
            onHide={onHide}
            title="Company"
            data={company}
            fields={viewFields}
            onEdit={onEdit}
        />
    );
};

export default CompanyViewModal;