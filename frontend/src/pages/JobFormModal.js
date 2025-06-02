import React from 'react';
import { Modal, Button, Form, Row, Col } from 'react-bootstrap';
import Select from 'react-select';

// Required field indicator
const RequiredIndicator = () => (
  <span className="text-danger ms-1">*</span>
);

// Style for required field labels
const requiredLabelStyle = {
  color: "#212529"  // Default text color
};

const JobFormModal = ({
  showModal,
  setShowModal,
  formData,
  handleChange,
  handleSubmit,
  handleCompanySelect,
  handleLocationSelect,
  companyOptions,
  locationOptions,
  setShowCompanyModal,
  setShowLocationModal,
  formErrors,
  submitting
}) => {
  return (
    <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Add New Job Application</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label style={requiredLabelStyle}>
              Job Title
              <RequiredIndicator />
            </Form.Label>
            <Form.Control
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label style={requiredLabelStyle}>
              Company
              <RequiredIndicator />
            </Form.Label>
            <Select
              options={companyOptions}
              onChange={handleCompanySelect}
              placeholder="Select or search company..."
              isClearable
              className={!formData.company_id ? "is-invalid" : ""}
            />
            <div className="mt-1">
              <Button variant="link" size="sm" onClick={() => setShowCompanyModal(true)} className="p-0">
                + Add New Company
              </Button>
            </div>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label style={requiredLabelStyle}>
              Location
              <RequiredIndicator />
            </Form.Label>
            <Select
              options={locationOptions}
              onChange={handleLocationSelect}
              placeholder="Select or search location..."
              isClearable
              className={!formData.location_id ? "is-invalid" : ""}
            />
            <div className="mt-1">
              <Button variant="link" size="sm" onClick={() => setShowLocationModal(true)} className="p-0">
                + Add New Location
              </Button>
            </div>
          </Form.Group>

          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label style={requiredLabelStyle}>
                  Status
                  <RequiredIndicator />
                </Form.Label>
                <Form.Select
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  required
                >
                  <option value="applied">Applied</option>
                  <option value="interview">Interview</option>
                  <option value="offer">Offer</option>
                  <option value="rejected">Rejected</option>
                  <option value="withdrawn">Withdrawn</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>URL</Form.Label>
                <Form.Control
                  type="url"
                  name="url"
                  value={formData.url}
                  onChange={handleChange}
                />
              </Form.Group>
            </Col>
          </Row>

          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Minimum Salary</Form.Label>
                <Form.Control
                  type="number"
                  name="salary_min"
                  value={formData.salary_min}
                  onChange={handleChange}
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Maximum Salary</Form.Label>
                <Form.Control
                  type="number"
                  name="salary_max"
                  value={formData.salary_max}
                  onChange={handleChange}
                />
              </Form.Group>
            </Col>
          </Row>

          <Form.Group className="mb-3">
            <Form.Label>Personal Rating (1-5)</Form.Label>
            <Form.Range
              name="personal_rating"
              value={formData.personal_rating}
              onChange={handleChange}
              min="1"
              max="5"
            />
            <div className="d-flex justify-content-between">
              <span>1</span>
              <span>2</span>
              <span>3</span>
              <span>4</span>
              <span>5</span>
            </div>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Description</Form.Label>
            <Form.Control
              as="textarea"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Notes</Form.Label>
            <Form.Control
              as="textarea"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={3}
            />
          </Form.Group>

          {formErrors.submit && (
            <div className="alert alert-danger">{formErrors.submit}</div>
          )}

          <div className="d-flex justify-content-end">
            <Button variant="secondary" onClick={() => setShowModal(false)} className="me-2">
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={submitting}>
              {submitting ? 'Saving...' : 'Save Job'}
            </Button>
          </div>
        </Form>
      </Modal.Body>
    </Modal>
  );
};

export default JobFormModal;
