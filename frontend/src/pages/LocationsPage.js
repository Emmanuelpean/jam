
import React, {useState} from 'react';
import GenericTable, { createTableActions } from '../components/GenericTable';
import LocationFormModal from '../components/modals/LocationFormModal';
import LocationViewModal from '../components/modals/LocationViewModal';
import ConfirmationModal from '../components/ConfirmationModal';
import LocationMap from '../components/LocationMap';
import AlertModal from '../components/modals/AlertModal';
import {useTableData} from '../components/Table';
import {useAuth} from '../contexts/AuthContext';
import {useConfirmation} from '../hooks/useConfirmation';
import {useAlert} from '../hooks/UseAlert'; // Import directly from the hook file

const LocationsPage = () => {
    const {token} = useAuth();
    const {
        data: locations,
        setData: setLocations,
        loading,
        error,
        sortConfig,
        setSortConfig,
        searchTerm,
        setSearchTerm,
        addItem,
        updateItem,
        removeItem
    } = useTableData('locations');

    const [showModal, setShowModal] = useState(false);
    const [showViewModal, setShowViewModal] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [selectedLocation, setSelectedLocation] = useState(null);

    const {confirmationState, showConfirmation, hideConfirmation} = useConfirmation();
    const { alertState, showAlert, hideAlert } = useAlert();

    // Handle view location
    const handleView = (location) => {
        setSelectedLocation(location);
        setShowViewModal(true);
    };

    // Handle edit location
    const handleEdit = (location) => {
        setSelectedLocation(location);
        setShowEditModal(true);
    };

    // Handle edit success
    const handleEditSuccess = (updatedLocation) => {
        updateItem(updatedLocation);
        setShowEditModal(false);
        setSelectedLocation(null);
    };

    // Handle edit modal close
    const handleEditModalClose = () => {
        setShowEditModal(false);
        setSelectedLocation(null);
    };

    // Handle delete location
    const handleDelete = async (location) => {
        const locationName = location.city ? `${location.city}${location.country ? `, ${location.country}` : ''}` : 'this location';

        await showConfirmation({
            title: 'Delete Location',
            message: `Are you sure you want to delete "${locationName}"? This action cannot be undone.`,
            confirmText: 'Delete',
            cancelText: 'Cancel',
            confirmVariant: 'danger',
            icon: '🗑️',
            onConfirm: async () => {
                try {
                    const response = await fetch(`http://localhost:8000/locations/${location.id}/`, {
                        method: 'DELETE', headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });

                    if (response.ok) {
                        if (typeof removeItem === 'function') {
                            removeItem(location.id);
                        } else if (typeof setLocations === 'function') {
                            setLocations(prevLocations => prevLocations.filter(l => l.id !== location.id));
                        } else {
                            window.location.reload();
                        }

                        // Show success alert instead of browser alert
                        await showAlert({
                            title: 'Success',
                            message: `Location "${locationName}" has been deleted successfully.`,
                            type: 'success',
                            confirmText: 'OK'
                        });
                    } else {
                        // Show error alert instead of browser alert
                        await showAlert({
                            title: 'Error',
                            message: 'Failed to delete location. Please try again.',
                            type: 'error',
                            confirmText: 'OK'
                        });
                    }
                } catch (error) {
                    console.error('Error deleting location:', error);
                    // Show error alert instead of browser alert
                    await showAlert({
                        title: 'Error',
                        message: 'Failed to delete location. Please check your connection and try again.',
                        type: 'error',
                        confirmText: 'OK'
                    });
                }
            }
        });
    };

    // Define table columns (without actions)
    const columns = [{
        key: 'city',
        label: 'City',
        sortable: true,
        searchable: true,
        render: (location) => location.city || 'Not specified'
    }, {
        key: 'postcode',
        label: 'Postcode',
        sortable: true,
        searchable: true,
        render: (location) => location.postcode || 'Not specified'
    }, {
        key: 'country',
        label: 'Country',
        type: 'category',
        sortable: true,
        searchable: true,
        render: (location) => location.country || 'Not specified'
    }, {
        key: 'remote',
        label: 'Remote',
        sortable: true,
        render: (location) => (<span className={`badge ${location.remote ? 'bg-success' : 'bg-secondary'}`}>
                    {location.remote ? 'Yes' : 'No'}
                </span>)
    }, {
        key: 'created_at',
        label: 'Date Added',
        type: 'date',
        sortable: true,
        render: (item) => new Date(item.created_at).toLocaleDateString()
    }];

    // Create standardized actions using the utility function
    const tableActions = createTableActions([
        { type: 'view', onClick: handleView, title: 'View location details' },
        { type: 'edit', onClick: handleEdit, title: 'Edit location' },
        { type: 'delete', onClick: handleDelete, title: 'Delete location' }
    ]);

    const handleAddSuccess = (newLocation) => {
        addItem(newLocation);
    };

    return (<div className="container">
        <h2 className="my-4">Locations</h2>

        {/* Table first */}
        <GenericTable
            data={locations}
            columns={columns}
            actions={tableActions}
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

        {/* Map below table */}
        <div className="mt-4">
            <h5 className="mb-3">Location Map</h5>
            <LocationMap locations={locations || []} height="500px"/>
        </div>

        {/* Modals */}
        <LocationFormModal
            show={showModal}
            onHide={() => setShowModal(false)}
            onSuccess={handleAddSuccess}
        />

        <LocationFormModal
            show={showEditModal}
            onHide={handleEditModalClose}
            onSuccess={handleEditSuccess}
            initialData={selectedLocation || {}}
            isEdit={true}
        />

        <LocationViewModal
            show={showViewModal}
            onHide={() => setShowViewModal(false)}
            location={selectedLocation}
            onEdit={handleEdit}
        />

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

        {/* Alert Modal */}
        <AlertModal
            show={alertState.show}
            onHide={hideAlert}
            title={alertState.title}
            message={alertState.message}
            type={alertState.type}
            confirmText={alertState.confirmText}
            icon={alertState.icon}
            size={alertState.size}
        />
    </div>);
};

export default LocationsPage;