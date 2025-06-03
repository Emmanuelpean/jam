import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

// Import the modal components
import JobFormModal from '../components/modals/JobFormModal';
import CompanyFormModal from '../components/modals/CompanyFormModal';
import LocationFormModal from '../components/modals/LocationFormModal';

const JobsPage = () => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [companies, setCompanies] = useState({});
  const [locations, setLocations] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortConfig, setSortConfig] = useState({ key: 'created_at', direction: 'desc' });
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');

  // Job Modal state
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    company_id: '',
    location_id: '',
    description: '',
    url: '',
    salary_min: '',
    salary_max: '',
    status: 'applied',
    personal_rating: 5,
    notes: ''
  });

  // New state for company and location modals
  const [showCompanyModal, setShowCompanyModal] = useState(false);
  const [showLocationModal, setShowLocationModal] = useState(false);
  const [companyFormData, setCompanyFormData] = useState({
    name: '',
    website: '',
    notes: ''
  });
  const [locationFormData, setLocationFormData] = useState({
    city: '',
    postcode: '',
    country: '',
    remote: false
  });

  const [availableCompanies, setAvailableCompanies] = useState([]);
  const [availableLocations, setAvailableLocations] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [formErrors, setFormErrors] = useState({});

  // Fetch jobs data
  useEffect(() => {
    const fetchData = async () => {
      if (!token) {
        navigate('/login');
        return;
      }

      setLoading(true);
      try {
        // Fetch jobs
        const jobsResponse = await fetch('http://localhost:8000/jobs/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        // Fetch companies
        const companiesResponse = await fetch('http://localhost:8000/companies/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        // Fetch locations
        const locationsResponse = await fetch('http://localhost:8000/locations/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!jobsResponse.ok || !companiesResponse.ok || !locationsResponse.ok) {
          throw new Error('Failed to fetch data');
        }

        const jobsData = await jobsResponse.json();
        const companiesData = await companiesResponse.json();
        const locationsData = await locationsResponse.json();

        // Create lookup objects for companies and locations
        const companiesMap = {};
        const locationsMap = {};

        companiesData.forEach(company => {
          companiesMap[company.id] = company;
        });

        locationsData.forEach(location => {
          locationsMap[location.id] = location;
        });

        setJobs(jobsData);
        setCompanies(companiesMap);
        setLocations(locationsMap);
        setAvailableCompanies(companiesData);
        setAvailableLocations(locationsData);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load jobs. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [token, navigate]);

  // Handle sorting
  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  // Get sorted and filtered data
  const getSortedJobs = () => {
    let filteredJobs = [...jobs];

    // Filter by search term
    if (searchTerm) {
      const searchTermLower = searchTerm.toLowerCase();
      filteredJobs = filteredJobs.filter(job =>
        job.title.toLowerCase().includes(searchTermLower) ||
        companies[job.company_id]?.name.toLowerCase().includes(searchTermLower)
      );
    }

    // Filter by status
    if (selectedStatus !== 'all') {
      filteredJobs = filteredJobs.filter(job => job.status === selectedStatus);
    }

    // Sort data
    if (sortConfig.key) {
      filteredJobs.sort((a, b) => {
        let aValue = a[sortConfig.key];
        let bValue = b[sortConfig.key];

        // Handle special cases for company and location
        if (sortConfig.key === 'company_id') {
          aValue = companies[a.company_id]?.name || '';
          bValue = companies[b.company_id]?.name || '';
        } else if (sortConfig.key === 'location_id') {
          aValue = locations[a.location_id]?.city || '';
          bValue = locations[b.location_id]?.city || '';
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

    return filteredJobs;
  };

  // Handle form input changes for job
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  // Handle job form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const response = await fetch('http://localhost:8000/jobs/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error('Failed to create job');
      }

      const newJob = await response.json();

      // Add the new job to the list and close the modal
      setJobs(prev => [newJob, ...prev]);
      setShowModal(false);

      // Reset the form
      setFormData({
        title: '',
        company_id: '',
        location_id: '',
        description: '',
        url: '',
        salary_min: '',
        salary_max: '',
        status: 'applied',
        personal_rating: 5,
        notes: ''
      });

    } catch (err) {
      console.error('Error creating job:', err);
      setFormErrors({
        ...formErrors,
        submit: 'Failed to create job. Please try again.'
      });
    } finally {
      setSubmitting(false);
    }
  };

  // Handle company form input changes
  const handleCompanyChange = (e) => {
    const { name, value } = e.target;
    setCompanyFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle location form input changes
  const handleLocationChange = (e) => {
    const { name, value, type, checked } = e.target;
    setLocationFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  // Submit new company
  const handleCompanySubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const response = await fetch('http://localhost:8000/companies/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(companyFormData)
      });

      if (!response.ok) {
        throw new Error('Failed to create company');
      }

      const newCompany = await response.json();

      // Update the available companies list
      setAvailableCompanies(prev => [...prev, newCompany]);

      // Update the companies lookup object
      setCompanies(prev => ({
        ...prev,
        [newCompany.id]: newCompany
      }));

      // Close the modal and reset form
      setShowCompanyModal(false);
      setCompanyFormData({
        name: '',
        website: '',
        notes: ''
      });

    } catch (err) {
      console.error('Error creating company:', err);
      setFormErrors({
        ...formErrors,
        company: 'Failed to create company. Please try again.'
      });
    } finally {
      setSubmitting(false);
    }
  };

  // Submit new location
  const handleLocationSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const response = await fetch('http://localhost:8000/locations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(locationFormData)
      });

      if (!response.ok) {
        throw new Error('Failed to create location');
      }

      const newLocation = await response.json();

      // Update the available locations list
      setAvailableLocations(prev => [...prev, newLocation]);

      // Update the locations lookup object
      setLocations(prev => ({
        ...prev,
        [newLocation.id]: newLocation
      }));

      // Close the modal and reset form
      setShowLocationModal(false);
      setLocationFormData({
        city: '',
        state: '',
        country: '',
        remote: false
      });

    } catch (err) {
      console.error('Error creating location:', err);
      setFormErrors({
        ...formErrors,
        location: 'Failed to create location. Please try again.'
      });
    } finally {
      setSubmitting(false);
    }
  };

  // Convert company and location arrays to options for react-select
  const companyOptions = availableCompanies.map(company => ({
    value: company.id,
    label: company.name
  }));

  const locationOptions = availableLocations.map(location => ({
    value: location.id,
    label: `${location.city}, ${location.state}, ${location.country}${location.remote ? ' (Remote)' : ''}`
  }));

  // Update form data handlers to work with react-select
  const handleCompanySelect = (selectedOption) => {
    setFormData(prev => ({
      ...prev,
      company_id: selectedOption ? selectedOption.value : ''
    }));
  };

  const handleLocationSelect = (selectedOption) => {
    setFormData(prev => ({
      ...prev,
      location_id: selectedOption ? selectedOption.value : ''
    }));
  };

  // Get the status badge
  const getStatusBadge = (status) => {
    const statusMap = {
      applied: 'primary',
      interview: 'warning',
      offer: 'success',
      rejected: 'danger',
      withdrawn: 'secondary'
    };

    return (
      <span className={`badge bg-${statusMap[status] || 'primary'}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  if (loading) {
    return <div className="d-flex justify-content-center mt-5"><div className="spinner-border" role="status"></div></div>;
  }

  if (error) {
    return <div className="alert alert-danger mt-3">{error}</div>;
  }

  return (
    <div className="container">
      <h2 className="my-4">Job Applications</h2>

      <div className="d-flex justify-content-between mb-3">
        <div className="d-flex">
          <input
            type="text"
            className="form-control me-2"
            placeholder="Search jobs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: '200px' }}
          />

          <select
            className="form-select me-2"
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            style={{ width: '150px' }}
          >
            <option value="all">All Statuses</option>
            <option value="applied">Applied</option>
            <option value="interview">Interview</option>
            <option value="offer">Offer</option>
            <option value="rejected">Rejected</option>
            <option value="withdrawn">Withdrawn</option>
          </select>
        </div>

        <button
          className="btn btn-primary"
          onClick={() => setShowModal(true)}
        >
          Add Job
        </button>
      </div>

      <table className="table table-striped">
        <thead>
          <tr>
            <th onClick={() => handleSort('title')} style={{cursor: 'pointer'}}>
              Job Title {sortConfig.key === 'title' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
            </th>
            <th onClick={() => handleSort('company_id')} style={{cursor: 'pointer'}}>
              Company {sortConfig.key === 'company_id' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
            </th>
            <th onClick={() => handleSort('location_id')} style={{cursor: 'pointer'}}>
              Location {sortConfig.key === 'location_id' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
            </th>
            <th onClick={() => handleSort('status')} style={{cursor: 'pointer'}}>
              Status {sortConfig.key === 'status' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
            </th>
            <th onClick={() => handleSort('created_at')} style={{cursor: 'pointer'}}>
              Date {sortConfig.key === 'created_at' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
            </th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {getSortedJobs().map((job) => (
            <tr key={job.id}>
              <td>{job.title}</td>
              <td>{companies[job.company_id]?.name || 'Unknown'}</td>
              <td>
                {locations[job.location_id] ?
                  `${locations[job.location_id].city}, ${locations[job.location_id].state}${locations[job.location_id].remote ? ' (Remote)' : ''}`
                  : 'Unknown'
                }
              </td>
              <td>{getStatusBadge(job.status)}</td>
              <td>{new Date(job.created_at).toLocaleDateString()}</td>
              <td>
                <button className="btn btn-sm btn-outline-primary me-1">View</button>
                <button className="btn btn-sm btn-outline-secondary">Edit</button>
              </td>
            </tr>
          ))}
          {getSortedJobs().length === 0 && (
            <tr>
              <td colSpan="6" className="text-center">No jobs found</td>
            </tr>
          )}
        </tbody>
      </table>

      {/* Add a note about required fields */}
      <div className="mt-3 text-muted small">
        <span className="text-danger">*</span> indicates required fields
      </div>

      {/* Import and use the modal components */}
      <JobFormModal
        showModal={showModal}
        setShowModal={setShowModal}
        formData={formData}
        handleChange={handleChange}
        handleSubmit={handleSubmit}
        handleCompanySelect={handleCompanySelect}
        handleLocationSelect={handleLocationSelect}
        companyOptions={companyOptions}
        locationOptions={locationOptions}
        setShowCompanyModal={setShowCompanyModal}
        setShowLocationModal={setShowLocationModal}
        formErrors={formErrors}
        submitting={submitting}
      />

      <CompanyFormModal
        showCompanyModal={showCompanyModal}
        setShowCompanyModal={setShowCompanyModal}
        companyFormData={companyFormData}
        handleCompanyChange={handleCompanyChange}
        handleCompanySubmit={handleCompanySubmit}
        formErrors={formErrors}
        submitting={submitting}
      />

      <LocationFormModal
        showLocationModal={showLocationModal}
        setShowLocationModal={setShowLocationModal}
        locationFormData={locationFormData}
        handleLocationChange={handleLocationChange}
        handleLocationSubmit={handleLocationSubmit}
        formErrors={formErrors}
        submitting={submitting}
      />
    </div>
  );
};

export default JobsPage;
