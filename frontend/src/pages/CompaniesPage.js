import React, {useState} from 'react';
import GenericTable from '../components/GenericTable';
import CompanyFormModal from '../components/modals/CompanyFormModal';
import CompanyViewModal from '../components/modals/CompanyViewModal';
import ConfirmationModal from '../components/ConfirmationModal';
import {useTableData} from '../components/Table';
import {useAuth} from '../contexts/AuthContext';
import {useConfirmation} from '../hooks/useConfirmation';

const CompaniesPage = () => {
    const {token} = useAuth();
    const {
        data: companies, setData: setCompanies, // Add setData to directly update companies
        loading, error, sortConfig, setSortConfig, searchTerm, setSearchTerm, addItem, updateItem, removeItem // Keep this but add fallback
    } = useTableData('companies');

    const [showModal, setShowModal] = useState(false);
    const [showViewModal, setShowViewModal] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [selectedCompany, setSelectedCompany] = useState(null);

    const {confirmationState, showConfirmation, hideConfirmation} = useConfirmation();

    // Handle view company
    const handleView = (company) => {
        setSelectedCompany(company);
        setShowViewModal(true);
    };

    // Handle edit company
    const handleEdit = (company) => {
        setSelectedCompany(company);
        setShowEditModal(true);
    };

    // Handle edit success
    const handleEditSuccess = (updatedCompany) => {
        updateItem(updatedCompany);
        setShowEditModal(false);
        setSelectedCompany(null);
    };

    // Handle edit modal close
    const handleEditModalClose = () => {
        setShowEditModal(false);
        setSelectedCompany(null);
    };

    // Handle delete company
    const handleDelete = async (company) => {
        await showConfirmation({
            title: 'Delete Company',
            message: `Are you sure you want to delete "${company.name}"? This action cannot be undone.`,
            confirmText: 'Delete',
            cancelText: 'Cancel',
            confirmVariant: 'danger',
            icon: '🗑️',
            onConfirm: async () => {
                try {
                    const response = await fetch(`http://localhost:8000/companies/${company.id}/`, {
                        method: 'DELETE', headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });

                    if (response.ok) {
                        // Try removeItem first, fallback to manual update if it doesn't exist
                        if (typeof removeItem === 'function') {
                            removeItem(company.id);
                        } else if (typeof setCompanies === 'function') {
                            // Fallback: manually update the companies array
                            setCompanies(prevCompanies => prevCompanies.filter(c => c.id !== company.id));
                        } else {
                            // Last fallback: reload the page or refetch data
                            window.location.reload();
                        }
                    } else {
                        alert('Failed to delete company');
                    }
                } catch (error) {
                    console.error('Error deleting company:', error);
                    alert('Failed to delete company');
                }
            }
        });
    };

    // Define table columns
    const columns = [{
        key: 'name', label: 'Company Name', sortable: true, searchable: true
    }, {
        key: 'description',
        label: 'Description',
        sortable: false,
        searchable: true,
        render: (company) => (<div style={{maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis'}}>
                {company.description || 'No description'}
            </div>)
    }, {
        key: 'url',
        label: 'Website',
        sortable: false,
        render: (company) => company.url ? (<a href={company.url} target="_blank" rel="noopener noreferrer">
                Visit Website
            </a>) : 'No website'
    }, {
        key: 'created_at',
        label: 'Date Added',
        sortable: true,
        render: (company) => new Date(company.created_at).toLocaleDateString()
    }, {
        key: 'actions', label: 'Actions', sortable: false, render: (company) => (<div>
                <button
                    className="btn btn-sm btn-outline-primary me-1"
                    onClick={() => handleView(company)}
                >
                    View
                </button>
                <button
                    className="btn btn-sm btn-outline-secondary me-1"
                    onClick={() => handleEdit(company)}
                >
                    Edit
                </button>
                <button
                    className="btn btn-sm btn-outline-danger"
                    onClick={() => handleDelete(company)}
                >
                    Delete
                </button>
            </div>)
    }];

    const handleAddSuccess = (newCompany) => {
        addItem(newCompany);
    };

    return (<div className="container">
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

            {/* Add Company Modal */}
            <CompanyFormModal
                show={showModal}
                onHide={() => setShowModal(false)}
                onSuccess={handleAddSuccess}
            />

            {/* Edit Company Modal */}
            <CompanyFormModal
                show={showEditModal}
                onHide={handleEditModalClose}
                onSuccess={handleEditSuccess}
                initialData={selectedCompany || {}}
                isEdit={true}
            />

            {/* View Company Modal */}
            <CompanyViewModal
                show={showViewModal}
                onHide={() => setShowViewModal(false)}
                company={selectedCompany}
                onEdit={handleEdit}
            />

            {/* Confirmation Modal */}
            <ConfirmationModal
                show={confirmationState.show}
                onHide={hideConfirmation}
                onConfirm={confirmationState.onConfirm}
                title={confirmationState.title}
                message={confirmationState.message}
                confirmText={confirmationState.confirmText}
                cancelText={confirmationState.cancelText}
                confirmVariant={confirmationState.confirmVariant}
                icon={confirmationState.icon}
            />
        </div>);
};

export default CompaniesPage;