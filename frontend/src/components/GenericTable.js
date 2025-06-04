import React, {useState, useEffect, useRef} from 'react';
import Select from 'react-select';

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
    const [columnFilters, setColumnFilters] = useState({});
    const [showFilters, setShowFilters] = useState({});
    const [showTooltips, setShowTooltips] = useState({});
    const filterRefs = useRef({});
    const tooltipRefs = useRef({});

    // Handle clicking outside filter dropdowns and tooltips
    useEffect(() => {
        const handleClickOutside = (event) => {
            // Check if the click is outside any open filter dropdown
            const openFilters = Object.keys(showFilters).filter(key => showFilters[key]);

            for (const columnKey of openFilters) {
                const filterRef = filterRefs.current[columnKey];
                if (filterRef && !filterRef.contains(event.target)) {
                    setShowFilters(prev => ({
                        ...prev, [columnKey]: false
                    }));
                }
            }

            // Check if the click is outside any open tooltip
            const openTooltips = Object.keys(showTooltips).filter(key => showTooltips[key]);

            for (const columnKey of openTooltips) {
                const tooltipRef = tooltipRefs.current[columnKey];
                if (tooltipRef && !tooltipRef.contains(event.target)) {
                    setShowTooltips(prev => ({
                        ...prev, [columnKey]: false
                    }));
                }
            }
        };

        // Add event listener when any filter or tooltip is open
        const hasOpenFilters = Object.values(showFilters).some(isOpen => isOpen);
        const hasOpenTooltips = Object.values(showTooltips).some(isOpen => isOpen);
        if (hasOpenFilters || hasOpenTooltips) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        // Cleanup
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [showFilters, showTooltips]);

    // Handle sorting
    const handleSort = (key) => {
        let direction = 'asc';
        if (sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc';
        }
        onSort({key, direction});
    };

    // Toggle filter visibility for a column
    const toggleFilter = (columnKey) => {
        setShowFilters(prev => ({
            ...prev, [columnKey]: !prev[columnKey]
        }));
    };

    // Handle column filter change
    const handleColumnFilterChange = (columnKey, value) => {
        setColumnFilters(prev => ({
            ...prev, [columnKey]: value
        }));
    };

    // Handle category filter change (for react-select)
    const handleCategoryFilterChange = (columnKey, selectedOptions) => {
        const selectedValues = selectedOptions ? selectedOptions.map(option => option.value) : [];
        setColumnFilters(prev => ({
            ...prev, [columnKey]: selectedValues
        }));
    };

    // Handle date filter change
    const handleDateFilterChange = (columnKey, field, value) => {
        setColumnFilters(prev => ({
            ...prev, [columnKey]: {
                ...prev[columnKey], [field]: value
            }
        }));
    };

    // Handle number filter change
    const handleNumberFilterChange = (columnKey, field, value) => {
        setColumnFilters(prev => ({
            ...prev, [columnKey]: {
                ...prev[columnKey], [field]: value
            }
        }));
    };

    // Clear filter for a column
    const clearColumnFilter = (columnKey) => {
        setColumnFilters(prev => {
            const newFilters = {...prev};
            delete newFilters[columnKey];
            return newFilters;
        });
        setShowFilters(prev => ({
            ...prev, [columnKey]: false
        }));
    };

    // Get unique categories for a column
    const getUniqueCategories = (column) => {
        // Check if data is available and not empty
        if (!data || !Array.isArray(data) || data.length === 0) {
            return [];
        }

        const values = data.map(item => {
            let value;
            if (column.accessor) {
                value = column.accessor(item);
            } else {
                value = item[column.key];
            }

            // Convert to string and filter out empty values
            const stringValue = value?.toString() || '';
            return stringValue.trim();
        }).filter(value => value !== '');

        // Get unique values and sort them
        const uniqueValues = [...new Set(values)].sort();

        // Convert to react-select format
        return uniqueValues.map(value => ({
            value: value, label: value
        }));
    };

    // Convert wildcard pattern to regex
    const createRegexFromPattern = (pattern) => {
        try {
            // If pattern contains %, treat it as a wildcard pattern
            if (pattern.includes('%')) {
                // Escape special regex characters except %
                const escapedPattern = pattern
                    .replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
                    .replace(/\\%/g, '%'); // Unescape % that we want to keep as wildcard

                // Replace % with .* for regex wildcard
                const regexPattern = escapedPattern.replace(/%/g, '.*');

                return new RegExp(regexPattern, 'i');
            }

            // If no %, treat as regular expression if it looks like one
            // Check for common regex patterns
            if (pattern.match(/[.*+?^${}()|[\]\\]/)) {
                return new RegExp(pattern, 'i');
            }

            // Otherwise, treat as plain text with word boundary matching
            return null;
        } catch (error) {
            // If regex is invalid, fall back to plain text search
            return null;
        }
    };

    // Check if a value matches the text filter (multiple keywords or regex)
    const matchesTextFilter = (value, filterValue) => {
        if (!filterValue || filterValue.trim() === '') return true;

        const valueStr = value?.toString().toLowerCase() || '';

        // Try to create regex from pattern
        const regex = createRegexFromPattern(filterValue);

        if (regex) {
            // Use regex matching
            return regex.test(value?.toString() || '');
        } else {
            // Fall back to keyword matching
            const keywords = filterValue.toLowerCase().split(/\s+/).filter(keyword => keyword.length > 0);

            // All keywords must be present (AND logic)
            return keywords.every(keyword => valueStr.includes(keyword));
        }
    };

    // Check if a value matches the category filter
    const matchesCategoryFilter = (value, selectedCategories) => {
        if (!selectedCategories || selectedCategories.length === 0) return true;

        const valueStr = value?.toString() || '';
        return selectedCategories.includes(valueStr);
    };

    // Check if a value matches the number filter
    const matchesNumberFilter = (value, filter) => {
        if (!filter || (filter.min === undefined && filter.max === undefined)) return true;

        const numValue = parseFloat(value);
        if (isNaN(numValue)) return false;

        if (filter.min !== undefined && filter.min !== '' && numValue < parseFloat(filter.min)) return false;
        if (filter.max !== undefined && filter.max !== '' && numValue > parseFloat(filter.max)) return false;

        return true;
    };

    // Check if a value matches the date filter
    const matchesDateFilter = (value, filter) => {
        if (!filter || (!filter.date1 && !filter.date2)) return true;

        const itemDate = new Date(value);
        if (isNaN(itemDate.getTime())) return false;

        // Reset time to start of day for comparison
        itemDate.setHours(0, 0, 0, 0);

        // If only one date is provided, use exact match
        if (filter.date1 && !filter.date2) {
            const exactDate = new Date(filter.date1);
            exactDate.setHours(0, 0, 0, 0);
            return itemDate.getTime() === exactDate.getTime();
        }

        // If only second date is provided, use exact match
        if (!filter.date1 && filter.date2) {
            const exactDate = new Date(filter.date2);
            exactDate.setHours(0, 0, 0, 0);
            return itemDate.getTime() === exactDate.getTime();
        }

        // If both dates are provided, use range
        if (filter.date1 && filter.date2) {
            const fromDate = new Date(filter.date1);
            const toDate = new Date(filter.date2);

            // Ensure correct order (swap if necessary)
            const earlierDate = fromDate <= toDate ? fromDate : toDate;
            const laterDate = fromDate <= toDate ? toDate : fromDate;

            earlierDate.setHours(0, 0, 0, 0);
            laterDate.setHours(23, 59, 59, 999);

            return itemDate.getTime() >= earlierDate.getTime() && itemDate.getTime() <= laterDate.getTime();
        }

        return true;
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

        // Apply column filters
        Object.entries(columnFilters).forEach(([columnKey, filterValue]) => {
            const column = columns.find(col => col.key === columnKey);

            if (column?.type === 'date' || column?.type === 'datetime') {
                // Handle date filtering
                if (filterValue && (filterValue.date1 || filterValue.date2)) {
                    filteredData = filteredData.filter(item => {
                        const value = column?.accessor ? column.accessor(item) : item[columnKey];
                        return matchesDateFilter(value, filterValue);
                    });
                }
            } else if (column?.type === 'number') {
                // Handle number filtering
                if (filterValue && (filterValue.min !== undefined || filterValue.max !== undefined)) {
                    filteredData = filteredData.filter(item => {
                        const value = column?.accessor ? column.accessor(item) : item[columnKey];
                        return matchesNumberFilter(value, filterValue);
                    });
                }
            } else if (column?.type === 'category') {
                // Handle category filtering
                if (filterValue && Array.isArray(filterValue) && filterValue.length > 0) {
                    filteredData = filteredData.filter(item => {
                        const value = column?.accessor ? column.accessor(item) : item[columnKey];
                        return matchesCategoryFilter(value, filterValue);
                    });
                }
            } else {
                // Handle text filtering with regex/keywords
                if (filterValue && filterValue.trim() !== '') {
                    filteredData = filteredData.filter(item => {
                        const value = column?.accessor ? column.accessor(item) : item[columnKey];
                        return matchesTextFilter(value, filterValue);
                    });
                }
            }
        });

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

    // Custom styles for react-select to match Bootstrap
    const customSelectStyles = {
        control: (provided, state) => ({
            ...provided,
            minHeight: '31px',
            height: '31px',
            fontSize: '0.875rem',
            borderColor: state.isFocused ? '#86b7fe' : '#dee2e6',
            boxShadow: state.isFocused ? '0 0 0 0.2rem rgba(13, 110, 253, 0.25)' : 'none',
            '&:hover': {
                borderColor: state.isFocused ? '#86b7fe' : '#adb5bd'
            }
        }), valueContainer: (provided) => ({
            ...provided, height: '29px', padding: '0 8px'
        }), input: (provided) => ({
            ...provided, margin: '0px'
        }), indicatorSeparator: () => ({
            display: 'none'
        }), indicatorsContainer: (provided) => ({
            ...provided, height: '29px'
        }), multiValue: (provided) => ({
            ...provided, fontSize: '0.75rem'
        }), multiValueLabel: (provided) => ({
            ...provided, fontSize: '0.75rem'
        }), option: (provided, state) => ({
            ...provided, fontSize: '0.875rem'
        }), menu: (provided) => ({
            ...provided, fontSize: '0.875rem', zIndex: 9999
        }), menuPortal: (provided) => ({
            ...provided, zIndex: 9999
        })
    };

    // Get tooltip content based on column type
    const getFilterTooltip = (column) => {
        switch (column.type) {
            case 'date':
            case 'datetime':
                return (<div className="small text-dark">
                        <strong>Date Filtering:</strong>
                        <ul className="mb-0 ps-3 mt-1">
                            <li>One date = exact match</li>
                            <li>Two dates = date range</li>
                        </ul>
                    </div>);
            case 'number':
                return (<div className="small text-dark">
                        <strong>Number Filtering:</strong>
                        <ul className="mb-0 ps-3 mt-1">
                            <li>Set minimum and/or maximum values</li>
                            <li>Leave empty for no limit</li>
                        </ul>
                    </div>);
            case 'category':
                return (<div className="small text-dark">
                        <strong>Category Filtering:</strong>
                        <ul className="mb-0 ps-3 mt-1">
                            <li>Multi-select dropdown with search</li>
                            <li>Type to search within options</li>
                            <li>Shows only items matching selected categories</li>
                        </ul>
                    </div>);
            default:
                return (<div className="small text-dark">
                        <strong>Text Filtering:</strong>
                        <ul className="mb-0 ps-3 mt-1">
                            <li><code>%manager%</code> - wildcard matching</li>
                            <li><code>software engineer</code> - multiple keywords (AND)</li>
                            <li><code>^Java</code> - regex patterns</li>
                        </ul>
                    </div>);
        }
    };

    // Render filter input based on column type
    const renderFilterInput = (column) => {
        const tooltipKey = `${column.key}_tooltip`;

        if (column.type === 'date' || column.type === 'datetime') {
            const filter = columnFilters[column.key] || {};
            return (<div className="d-flex flex-column gap-2">
                    <div className="d-flex align-items-center gap-2">
                        <label className="form-label mb-0 small text-muted">
                            {filter.date1 && filter.date2 ? 'Date Range' : 'Single Date'}
                        </label>
                        <div style={{position: 'relative'}}>
                            <button
                                className="btn btn-sm p-0 border-0 bg-transparent text-info"
                                style={{fontSize: '0.75rem', width: '16px', height: '16px'}}
                                onMouseEnter={() => setShowTooltips(prev => ({...prev, [tooltipKey]: true}))}
                                onMouseLeave={() => setShowTooltips(prev => ({...prev, [tooltipKey]: false}))}
                                onClick={(e) => e.stopPropagation()}
                            >
                                ℹ️
                            </button>
                            {showTooltips[tooltipKey] && (<div
                                    ref={el => tooltipRefs.current[tooltipKey] = el}
                                    className="position-absolute bg-white border rounded shadow-lg p-2"
                                    style={{
                                        top: '20px', left: '-100px', zIndex: 1002, width: '200px', fontSize: '0.8rem'
                                    }}
                                >
                                    {getFilterTooltip(column)}
                                </div>)}
                        </div>
                    </div>
                    <input
                        type="date"
                        className="form-control form-control-sm"
                        placeholder="Date"
                        value={filter.date1 || ''}
                        onChange={(e) => handleDateFilterChange(column.key, 'date1', e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                    />
                    <input
                        type="date"
                        className="form-control form-control-sm"
                        placeholder="Second date (optional)"
                        value={filter.date2 || ''}
                        onChange={(e) => handleDateFilterChange(column.key, 'date2', e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                    />
                </div>);
        } else if (column.type === 'number') {
            const filter = columnFilters[column.key] || {};
            return (<div className="d-flex flex-column gap-2">
                    <div className="d-flex align-items-center gap-2">
                        <label className="form-label mb-0 small text-muted">Number Range</label>
                        <div style={{position: 'relative'}}>
                            <button
                                className="btn btn-sm p-0 border-0 bg-transparent text-info"
                                style={{fontSize: '0.75rem', width: '16px', height: '16px'}}
                                onMouseEnter={() => setShowTooltips(prev => ({...prev, [tooltipKey]: true}))}
                                onMouseLeave={() => setShowTooltips(prev => ({...prev, [tooltipKey]: false}))}
                                onClick={(e) => e.stopPropagation()}
                            >
                                ℹ️
                            </button>
                            {showTooltips[tooltipKey] && (<div
                                    ref={el => tooltipRefs.current[tooltipKey] = el}
                                    className="position-absolute bg-white border rounded shadow-lg p-2"
                                    style={{
                                        top: '20px', left: '-100px', zIndex: 1002, width: '200px', fontSize: '0.8rem'
                                    }}
                                >
                                    {getFilterTooltip(column)}
                                </div>)}
                        </div>
                    </div>
                    <input
                        type="number"
                        className="form-control form-control-sm"
                        placeholder="Minimum"
                        value={filter.min || ''}
                        onChange={(e) => handleNumberFilterChange(column.key, 'min', e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                    />
                    <input
                        type="number"
                        className="form-control form-control-sm"
                        placeholder="Maximum"
                        value={filter.max || ''}
                        onChange={(e) => handleNumberFilterChange(column.key, 'max', e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                    />
                </div>);
        } else if (column.type === 'category') {
            const categoryOptions = getUniqueCategories(column);
            const selectedCategories = columnFilters[column.key] || [];
            const selectedOptions = categoryOptions.filter(option => selectedCategories.includes(option.value));

            return (<div className="d-flex flex-column gap-2">
                    <div className="d-flex align-items-center gap-2">
                        <label className="form-label mb-0 small text-muted">Select Categories</label>
                        <div style={{position: 'relative'}}>
                            <button
                                className="btn btn-sm p-0 border-0 bg-transparent text-info"
                                style={{fontSize: '0.75rem', width: '16px', height: '16px'}}
                                onMouseEnter={() => setShowTooltips(prev => ({...prev, [tooltipKey]: true}))}
                                onMouseLeave={() => setShowTooltips(prev => ({...prev, [tooltipKey]: false}))}
                                onClick={(e) => e.stopPropagation()}
                            >
                                ℹ️
                            </button>
                            {showTooltips[tooltipKey] && (<div
                                    ref={el => tooltipRefs.current[tooltipKey] = el}
                                    className="position-absolute bg-white border rounded shadow-lg p-2"
                                    style={{
                                        top: '20px', left: '-100px', zIndex: 1002, width: '250px', fontSize: '0.8rem'
                                    }}
                                >
                                    {getFilterTooltip(column)}
                                </div>)}
                        </div>
                    </div>
                    <div onClick={(e) => e.stopPropagation()}>
                        <Select
                            isMulti
                            value={selectedOptions}
                            onChange={(selectedOptions) => handleCategoryFilterChange(column.key, selectedOptions)}
                            options={categoryOptions}
                            placeholder={categoryOptions.length === 0 ? 'No options available' : `Filter by ${column.label.toLowerCase()}...`}
                            noOptionsMessage={() => 'No options found'}
                            isSearchable={true}
                            isClearable={true}
                            closeMenuOnSelect={false}
                            hideSelectedOptions={false}
                            styles={customSelectStyles}
                            menuPortalTarget={document.body}
                            menuPosition="fixed"
                            className="react-select-container"
                            classNamePrefix="react-select"
                            maxMenuHeight={200}
                        />
                    </div>
                    {selectedCategories.length > 0 && (<small className="text-muted">
                            {selectedCategories.length} selected
                        </small>)}
                    {categoryOptions.length === 0 && (<small className="text-muted">
                            No data available for filtering
                        </small>)}
                </div>);
        } else {
            return (<div className="d-flex flex-column gap-2">
                    <div className="d-flex align-items-center gap-2">
                        <label className="form-label mb-0 small text-muted">Filter Text</label>
                        <div style={{position: 'relative'}}>
                            <button
                                className="btn btn-sm p-0 border-0 bg-transparent text-info"
                                style={{fontSize: '0.75rem', width: '16px', height: '16px'}}
                                onMouseEnter={() => setShowTooltips(prev => ({...prev, [tooltipKey]: true}))}
                                onMouseLeave={() => setShowTooltips(prev => ({...prev, [tooltipKey]: false}))}
                                onClick={(e) => e.stopPropagation()}
                            >
                                ℹ️
                            </button>
                            {showTooltips[tooltipKey] && (<div
                                    ref={el => tooltipRefs.current[tooltipKey] = el}
                                    className="position-absolute bg-white border rounded shadow-lg p-2"
                                    style={{
                                        top: '20px', left: '-150px', zIndex: 1002, width: '280px', fontSize: '0.8rem'
                                    }}
                                >
                                    {getFilterTooltip(column)}
                                </div>)}
                        </div>
                    </div>
                    <input
                        type="text"
                        className="form-control form-control-sm"
                        placeholder={`Filter ${column.label}...`}
                        value={columnFilters[column.key] || ''}
                        onChange={(e) => handleColumnFilterChange(column.key, e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                        autoFocus
                    />
                </div>);
        }
    };

    if (loading) {
        return (<div className="d-flex justify-content-center mt-5">
                <div className="spinner-border" role="status"></div>
            </div>);
    }

    if (error) {
        return <div className="alert alert-danger mt-3">{error}</div>;
    }

    return (<div>
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

                <div className="d-flex gap-2">
                    <button
                        className="btn btn-primary"
                        onClick={onAddClick}
                    >
                        {addButtonText}
                    </button>
                </div>
            </div>

            {/* Table */}
            <table className="table table-striped">
                <thead>
                <tr>
                    {columns.map((column) => (<th key={column.key} style={{position: 'relative'}}>
                            <div className="d-flex align-items-center justify-content-between">
                                <span
                                    onClick={() => toggleFilter(column.key)}
                                    style={{cursor: 'pointer', flex: 1}}
                                    title="Click to filter"
                                >
                                    {column.label}
                                    {columnFilters[column.key] && (<span
                                            className="badge bg-primary ms-1"
                                            style={{fontSize: '0.6em'}}
                                        >
                                            F
                                        </span>)}
                                </span>
                                {column.sortable && (<button
                                        className="btn btn-sm p-1 ms-2"
                                        onClick={() => handleSort(column.key)}
                                        style={{
                                            border: 'none', background: 'none', fontSize: '0.8em', minWidth: '20px'
                                        }}
                                        title="Sort column"
                                    >
                                        {sortConfig.key === column.key ? (sortConfig.direction === 'asc' ? '↑' : '↓') : ('↕')}
                                    </button>)}
                            </div>
                            {showFilters[column.key] && (<div
                                    ref={el => filterRefs.current[column.key] = el}
                                    className="position-absolute bg-white border rounded shadow-sm p-3 mt-1"
                                    style={{
                                        top: '100%',
                                        left: 0,
                                        zIndex: 1001,
                                        minWidth: column.type === 'category' ? '350px' : '300px'
                                    }}
                                >
                                    <div className="d-flex flex-column">
                                        {renderFilterInput(column)}
                                        <button
                                            className="btn btn-sm btn-outline-secondary mt-3"
                                            onClick={() => clearColumnFilter(column.key)}
                                        >
                                            Clear Filter
                                        </button>
                                    </div>
                                </div>)}
                        </th>))}
                </tr>
                </thead>
                <tbody>
                {getSortedData().map((item) => (<tr key={item.id}>
                        {columns.map((column) => (<td key={column.key}>
                                {column.render ? column.render(item) : column.accessor ? column.accessor(item) : item[column.key]}
                            </td>))}
                    </tr>))}
                {getSortedData().length === 0 && (<tr>
                        <td colSpan={columns.length} className="text-center">
                            {emptyMessage}
                        </td>
                    </tr>)}
                </tbody>
            </table>
        </div>);
};

export default GenericTable;