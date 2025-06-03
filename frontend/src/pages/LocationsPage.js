import React, { useState } from 'react';
import GenericTable from '../components/GenericTable';
import GenericFormModal from '../components/GenericFormModal';
import { useTableData } from '../components/Table';

const LocationsPage = () => {
    const {
        data: locations,
        loading,
        error,
        sortConfig,
        setSortConfig,
        searchTerm,
        setSearchTerm,
        addItem
    } = useTableData('locations');

    const [showModal, setShowModal] = useState(false);

    // Define table columns
    const columns = [
        {
            key: 'city',
            label: 'City',
            sortable: true,
            searchable: true
        },
        {
            key: 'postcode',
            label: 'Postcode',
            sortable: true,
            searchable: true
        },
        {
            key: 'country',
            label: 'Country',
            sortable: true,
            searchable: true
        },
        {
            key: 'remote',
            label: 'Remote',
            sortable: true,
            render: (location) => (
                <span className={`badge ${location.remote ? 'bg-success' : 'bg-secondary'}`}>
          {location.remote ? 'Yes' : 'No'}
        </span>
            )
        },
        {
            key: 'created_at',
            label: 'Date Added',
            sortable: true,
            render: (location) => new Date(location.created_at).toLocaleDateString()
        },
        {
            key: 'actions',
            label: 'Actions',
            sortable: false,
            render: (location) => (
                <div>
                    <button className="btn btn-sm btn-outline-primary me-1">View</button>
                    <button className="btn btn-sm btn-outline-secondary">Edit</button>
                </div>
            )
        }
    ];

    // Define form fields
    const formFields = [
        {
            name: 'city',
            label: 'City',
            type: 'text',
            required: false,
            placeholder: 'Enter city name'
        },
        {
            name: 'postcode',
            label: 'Postcode',
            type: 'text',
            required: false,
            placeholder: 'Enter postcode'
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
            label: 'Remote Work',
            type: 'checkbox',
            required: false,
            checkboxLabel: 'This is a remote position'
        }
    ];

    const handleAddSuccess = (newLocation) => {
        addItem(newLocation);
    };

    return (
        <div className="container">
            <h2 className="my-4">Locations</h2>

            <GenericTable
                data={locations}
                columns={columns}
                sortConfig={sortConfig}
                onSort={setSortConfig}
                searchTerm={searchTerm}
                onSearchChange={setSearchTerm}
                onAddClick={() => setShowModal(true)}
                addButtonText="Add Location"
                loading={loading}
                error={error}
                emptyMessage="No locations found"
            />

            <GenericFormModal
                show={showModal}
                onHide={() => setShowModal(false)}
                title="Location"
                fields={formFields}
                endpoint="locations"
                onSuccess={handleAddSuccess}
            />
        </div>
    );
};

export default LocationsPage;