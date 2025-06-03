import React from 'react';

const GenericTable = ({
                          data,
                          columns,
                          sortConfig,
                          onSort,
                          searchTerm,
                          onSearchChange,
                          onAddClick,
                          addButtonText = "Add Item",
                          filterComponent = null,
                          loading = false,
                          error = null,
                          emptyMessage = "No items found"
                      }) => {
    // Handle sorting
    const handleSort = (key) => {
        let direction = 'asc';
        if (sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc';
        }
        onSort({key, direction});
    };

    // Get sorted and filtered data
    const getSortedData = () => {
        let filteredData = [...data];

        // Filter by search term if provided
        if (searchTerm && columns.some(col => col.searchable)) {
            const searchTermLower = searchTerm.toLowerCase();
            filteredData = filteredData.filter(item => {
                return columns.some(column => {
                    if (!column.searchable) return false;
                    const value = column.accessor ? column.accessor(item) : item[column.key];
                    return value?.toString().toLowerCase().includes(searchTermLower);
                });
            });
        }

        // Sort data
        if (sortConfig.key) {
            filteredData.sort((a, b) => {
                const column = columns.find(col => col.key === sortConfig.key);
                let aValue, bValue;

                if (column?.accessor) {
                    aValue = column.accessor(a);
                    bValue = column.accessor(b);
                } else {
                    aValue = a[sortConfig.key];
                    bValue = b[sortConfig.key];
                }

                if (aValue < bValue) {
                    return sortConfig.direction === 'asc' ? -1 : 1;
                }
                if (aValue > bValue) {
                    return sortConfig.direction === 'asc' ? 1 : -1;
                }
                return 0;
            });
        }

        return filteredData;
    };

    if (loading) {
        return (
            <div className="d-flex justify-content-center mt-5">
                <div className="spinner-border" role="status"></div>
            </div>
        );
    }

    if (error) {
        return <div className="alert alert-danger mt-3">{error}</div>;
    }

    return (
        <div>
            {/* Header with search and filters */}
            <div className="d-flex justify-content-between mb-3">
                <div className="d-flex">
                    <input
                        type="text"
                        className="form-control me-2"
                        placeholder="Search..."
                        value={searchTerm}
                        onChange={(e) => onSearchChange(e.target.value)}
                        style={{width: '200px'}}
                    />
                    {filterComponent}
                </div>

                <button
                    className="btn btn-primary"
                    onClick={onAddClick}
                >
                    {addButtonText}
                </button>
            </div>

            {/* Table */}
            <table className="table table-striped">
                <thead>
                <tr>
                    {columns.map((column) => (
                        <th
                            key={column.key}
                            onClick={column.sortable ? () => handleSort(column.key) : undefined}
                            style={column.sortable ? {cursor: 'pointer'} : {}}
                        >
                            {column.label}
                            {column.sortable && sortConfig.key === column.key && (
                                sortConfig.direction === 'asc' ? ' ↑' : ' ↓'
                            )}
                        </th>
                    ))}
                </tr>
                </thead>
                <tbody>
                {getSortedData().map((item) => (
                    <tr key={item.id}>
                        {columns.map((column) => (
                            <td key={column.key}>
                                {column.render
                                    ? column.render(item)
                                    : column.accessor
                                        ? column.accessor(item)
                                        : item[column.key]
                                }
                            </td>
                        ))}
                    </tr>
                ))}
                {getSortedData().length === 0 && (
                    <tr>
                        <td colSpan={columns.length} className="text-center">
                            {emptyMessage}
                        </td>
                    </tr>
                )}
                </tbody>
            </table>
        </div>
    );
};

export default GenericTable;