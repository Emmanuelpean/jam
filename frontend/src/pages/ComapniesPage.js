import React, { useState } from 'react';
import GenericTable from '../components/GenericTable';
import CompanyFormModal from '../pages/CompanyFormModal';
import { useTableData } from '../components/Table';

const CompaniesPage = () => {
    const {
        data: companies,
        loading,
        error,
        sortConfig,
        setSortConfig,
        searchTerm,
        setSearchTerm,
        addItem
    } = useTableData('companies');

    const [showModal, setShowModal] = useState(false);

    // Define table columns
    const columns = [
        {
            key: 'name',
            label: 'Company Name',
            sortable: true,
            searchable: true
        },
        {
            key: 'description',
            label: 'Description',
            sortable: false,
            searchable: true,
            render: (company) => (
                <div style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {company.description || 'No description'}
                </div>
            )
        },
        {
            key: 'url',
            label: 'Website',
            sortable: false,
            render: (company) =>
                company.url ? (
                    <a href={company.url} target="_blank" rel="noopener noreferrer">
                        Visit Website
                    </a>
                ) : 'No website'
        },
        {
            key: 'created_at',
            label: 'Date Added',
            sortable: true,
            render: (company) => new Date(company.created_at).toLocaleDateString()
        },
        {
            key: 'actions',
            label: 'Actions',
            sortable: false,
            render: (company) => (
                <div>
                    <button className="btn btn-sm btn-outline-primary me-1">View</button>
                    <button className="btn btn-sm btn-outline-secondary">Edit</button>
                </div>
            )
        }
    ];

    const handleAddSuccess = (newCompany) => {
        addItem(newCompany);
    };

    return (
        <div className="container">
            <h2 className="my-4">Companies</h2>

            <GenericTable
                data={companies}
                columns={columns}
                sortConfig={sortConfig}
                onSort={setSortConfig}
                searchTerm={searchTerm}
                onSearchChange={setSearchTerm}
                onAddClick={() => setShowModal(true)}
                addButtonText="Add Company"
                loading={loading}
                error={error}
                emptyMessage="No companies found"
            />

            <CompanyFormModal
                show={showModal}
                onHide={() => setShowModal(false)}
                onSuccess={handleAddSuccess}
            />
        </div>
    );
};

export default CompaniesPage;