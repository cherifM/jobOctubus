import React, { useState, useEffect } from 'react';
import { 
  ClipboardDocumentListIcon, 
  EyeIcon,
  PencilIcon,
  TrashIcon,
  CalendarIcon,
  BuildingOfficeIcon,
  MapPinIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import { applicationService, Application } from '../services/applicationService';
import toast from 'react-hot-toast';

const Applications: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedApplication, setSelectedApplication] = useState<Application | null>(null);
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    loadApplications();
  }, []);

  const loadApplications = async () => {
    try {
      const applicationsData = await applicationService.getApplications();
      setApplications(applicationsData);
    } catch (error) {
      toast.error('Failed to load applications');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (applicationId: number, newStatus: string) => {
    try {
      const updatedApplication = await applicationService.updateApplication(applicationId, {
        status: newStatus
      });
      
      setApplications(applications.map(app => 
        app.id === applicationId ? updatedApplication : app
      ));
      
      if (selectedApplication?.id === applicationId) {
        setSelectedApplication(updatedApplication);
      }
      
      toast.success('Status updated successfully');
    } catch (error) {
      toast.error('Failed to update status');
    }
  };

  const handleDeleteApplication = async (applicationId: number) => {
    if (!window.confirm('Are you sure you want to delete this application?')) return;

    try {
      await applicationService.deleteApplication(applicationId);
      setApplications(applications.filter(app => app.id !== applicationId));
      if (selectedApplication?.id === applicationId) {
        setSelectedApplication(null);
      }
      toast.success('Application deleted successfully');
    } catch (error) {
      toast.error('Failed to delete application');
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'applied': return 'bg-blue-100 text-blue-800';
      case 'responded': return 'bg-green-100 text-green-800';
      case 'interview_scheduled': return 'bg-purple-100 text-purple-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'offer': return 'bg-emerald-100 text-emerald-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const statusOptions = [
    { value: 'draft', label: 'Draft' },
    { value: 'pending', label: 'Pending' },
    { value: 'applied', label: 'Applied' },
    { value: 'responded', label: 'Responded' },
    { value: 'interview_scheduled', label: 'Interview Scheduled' },
    { value: 'rejected', label: 'Rejected' },
    { value: 'offer', label: 'Offer Received' }
  ];

  const filteredApplications = statusFilter === 'all' 
    ? applications 
    : applications.filter(app => app.status === statusFilter);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Job Applications</h1>
        <div className="flex items-center space-x-4">
          <select
            className="input"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">All Status</option>
            {statusOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Applications List */}
        <div className="space-y-4">
          <h2 className="text-lg font-medium text-gray-900">
            {filteredApplications.length} Application{filteredApplications.length !== 1 ? 's' : ''}
            {statusFilter !== 'all' && ` (${statusFilter})`}
          </h2>
          
          {filteredApplications.length > 0 ? (
            filteredApplications.map((application) => (
              <div 
                key={application.id} 
                className={`card p-4 cursor-pointer transition-all hover:shadow-md ${
                  selectedApplication?.id === application.id ? 'ring-2 ring-primary-500' : ''
                }`}
                onClick={() => setSelectedApplication(application)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900">{application.job.title}</h3>
                    <div className="flex items-center space-x-2 mt-1">
                      <BuildingOfficeIcon className="h-4 w-4 text-gray-400" />
                      <span className="text-sm text-gray-600">{application.job.company}</span>
                    </div>
                    
                    <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                      <div className="flex items-center">
                        <MapPinIcon className="h-4 w-4 mr-1" />
                        {application.job.location}
                      </div>
                      <div className="flex items-center">
                        <DocumentTextIcon className="h-4 w-4 mr-1" />
                        {application.cv.title}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-400">
                      <div className="flex items-center">
                        <CalendarIcon className="h-4 w-4 mr-1" />
                        Applied: {formatDate(application.applied_date || application.created_at)}
                      </div>
                    </div>
                    
                    {application.notes && (
                      <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                        <strong>Notes:</strong> {application.notes}
                      </p>
                    )}
                  </div>
                  
                  <div className="flex flex-col items-end space-y-2 ml-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(application.status)}`}>
                      {statusOptions.find(opt => opt.value === application.status)?.label || application.status}
                    </span>
                    
                    <div className="flex items-center space-x-1">
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedApplication(application);
                        }}
                        className="p-1 text-gray-400 hover:text-primary-600 transition-colors"
                        title="View Details"
                      >
                        <EyeIcon className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          // TODO: Implement edit functionality
                          toast('Edit functionality coming soon', { icon: 'ℹ️' });
                        }}
                        className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                        title="Edit Application"
                      >
                        <PencilIcon className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteApplication(application.id);
                        }}
                        className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                        title="Delete Application"
                      >
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-12">
              <ClipboardDocumentListIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No applications found</h3>
              <p className="mt-1 text-sm text-gray-500">
                {statusFilter === 'all' 
                  ? "You haven't applied to any jobs yet. Start by searching for jobs!"
                  : `No applications with status "${statusFilter}". Try a different filter.`
                }
              </p>
            </div>
          )}
        </div>

        {/* Application Details */}
        <div className="lg:sticky lg:top-6">
          {selectedApplication ? (
            <div className="card p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{selectedApplication.job.title}</h2>
                  <p className="text-lg text-gray-600">{selectedApplication.job.company}</p>
                  <div className="flex items-center mt-2 text-sm text-gray-500">
                    <MapPinIcon className="h-4 w-4 mr-1" />
                    {selectedApplication.job.location}
                  </div>
                </div>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(selectedApplication.status)}`}>
                  {statusOptions.find(opt => opt.value === selectedApplication.status)?.label || selectedApplication.status}
                </span>
              </div>
              
              <div className="space-y-4">
                {/* Status Update */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Update Status
                  </label>
                  <select
                    className="input"
                    value={selectedApplication.status}
                    onChange={(e) => handleStatusUpdate(selectedApplication.id, e.target.value)}
                  >
                    {statusOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                
                {/* Dates */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Applied:</span>
                    <p className="text-gray-600">{formatDate(selectedApplication.applied_date || selectedApplication.created_at)}</p>
                  </div>
                  {selectedApplication.response_date && (
                    <div>
                      <span className="font-medium text-gray-700">Response:</span>
                      <p className="text-gray-600">{formatDate(selectedApplication.response_date)}</p>
                    </div>
                  )}
                  {selectedApplication.interview_date && (
                    <div>
                      <span className="font-medium text-gray-700">Interview:</span>
                      <p className="text-gray-600">{formatDate(selectedApplication.interview_date)}</p>
                    </div>
                  )}
                </div>
                
                {/* CV Used */}
                <div>
                  <span className="block text-sm font-medium text-gray-700 mb-1">CV Used:</span>
                  <div className="bg-gray-50 p-3 rounded-md">
                    <p className="text-sm font-medium">{selectedApplication.cv.title}</p>
                    <p className="text-xs text-gray-500">
                      Language: {selectedApplication.cv.language.toUpperCase()}
                      {selectedApplication.cv.is_base_cv && ' • Base CV'}
                    </p>
                  </div>
                </div>
                
                {/* Cover Letter */}
                {selectedApplication.cover_letter && (
                  <div>
                    <span className="block text-sm font-medium text-gray-700 mb-2">Cover Letter:</span>
                    <div className="bg-gray-50 p-3 rounded-md max-h-48 overflow-y-auto">
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">
                        {selectedApplication.cover_letter}
                      </p>
                    </div>
                  </div>
                )}
                
                {/* Notes */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Notes
                  </label>
                  <textarea
                    className="textarea h-24"
                    placeholder="Add notes about this application..."
                    value={selectedApplication.notes || ''}
                    onChange={(e) => {
                      // Update local state immediately
                      setSelectedApplication({
                        ...selectedApplication,
                        notes: e.target.value
                      });
                    }}
                    onBlur={(e) => {
                      // Save to backend when user stops typing
                      if (e.target.value !== (applications.find(app => app.id === selectedApplication.id)?.notes || '')) {
                        handleStatusUpdate(selectedApplication.id, selectedApplication.status);
                      }
                    }}
                  />
                </div>
                
                {/* Job Details Link */}
                <div className="pt-4 border-t">
                  <a 
                    href={selectedApplication.job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full btn btn-primary mb-2"
                  >
                    View Original Job Posting
                  </a>
                  <button className="w-full btn btn-outline">
                    Generate New Cover Letter
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="card p-6 text-center">
              <ClipboardDocumentListIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Select an application</h3>
              <p className="mt-1 text-sm text-gray-500">
                Click on an application from the list to view its details.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Applications;