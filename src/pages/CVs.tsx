import React, { useState, useEffect } from 'react';
import { 
  DocumentTextIcon, 
  PlusIcon, 
  EyeIcon,
  PencilIcon,
  TrashIcon,
  CloudArrowUpIcon
} from '@heroicons/react/24/outline';
import { cvService, CV } from '../services/cvService';
import toast from 'react-hot-toast';

const CVs: React.FC = () => {
  const [cvs, setCvs] = useState<CV[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCV, setSelectedCV] = useState<CV | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadLanguage, setUploadLanguage] = useState('en');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadCVs();
  }, []);

  const loadCVs = async () => {
    try {
      const cvsData = await cvService.getCVs();
      setCvs(cvsData);
    } catch (error) {
      toast.error('Failed to load CVs');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async () => {
    if (!uploadFile || !uploadTitle.trim()) {
      toast.error('Please select a file and enter a title');
      return;
    }

    setUploading(true);
    try {
      const newCV = await cvService.uploadCV(uploadFile, uploadTitle, uploadLanguage);
      setCvs([newCV, ...cvs]);
      setShowUploadModal(false);
      setUploadFile(null);
      setUploadTitle('');
      setUploadLanguage('en');
      toast.success('CV uploaded and parsed successfully');
    } catch (error) {
      toast.error('Failed to upload CV');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteCV = async (cvId: number) => {
    if (!window.confirm('Are you sure you want to delete this CV?')) return;

    try {
      await cvService.deleteCV(cvId);
      setCvs(cvs.filter(cv => cv.id !== cvId));
      if (selectedCV?.id === cvId) {
        setSelectedCV(null);
      }
      toast.success('CV deleted successfully');
    } catch (error) {
      toast.error('Failed to delete CV');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

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
        <h1 className="text-3xl font-bold text-gray-900">My CVs</h1>
        <button 
          onClick={() => setShowUploadModal(true)}
          className="btn btn-primary flex items-center space-x-2"
        >
          <PlusIcon className="w-5 h-5" />
          <span>Upload CV</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CV List */}
        <div className="space-y-4">
          <h2 className="text-lg font-medium text-gray-900">
            {cvs.length} CV{cvs.length !== 1 ? 's' : ''} Available
          </h2>
          
          {cvs.length > 0 ? (
            cvs.map((cv) => (
              <div 
                key={cv.id} 
                className={`card p-4 cursor-pointer transition-all hover:shadow-md ${
                  selectedCV?.id === cv.id ? 'ring-2 ring-primary-500' : ''
                }`}
                onClick={() => setSelectedCV(cv)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-medium text-gray-900">{cv.title}</h3>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {cv.language.toUpperCase()}
                      </span>
                      {cv.is_base_cv && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Base CV
                        </span>
                      )}
                    </div>
                    
                    <div className="mt-2 text-sm text-gray-600">
                      <p><strong>Skills:</strong> {cv.skills.slice(0, 3).join(', ')}{cv.skills.length > 3 ? ` +${cv.skills.length - 3} more` : ''}</p>
                      <p><strong>Experience:</strong> {cv.experience.length} position{cv.experience.length !== 1 ? 's' : ''}</p>
                      <p><strong>Education:</strong> {cv.education.length} qualification{cv.education.length !== 1 ? 's' : ''}</p>
                    </div>
                    
                    <div className="mt-2 text-xs text-gray-400">
                      Created: {formatDate(cv.created_at)}
                      {cv.updated_at && ` • Updated: ${formatDate(cv.updated_at)}`}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 ml-4">
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedCV(cv);
                      }}
                      className="p-2 text-gray-400 hover:text-primary-600 transition-colors"
                      title="View CV"
                    >
                      <EyeIcon className="w-4 h-4" />
                    </button>
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        // TODO: Implement edit functionality
                        toast('Edit functionality coming soon', { icon: 'ℹ️' });
                      }}
                      className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                      title="Edit CV"
                    >
                      <PencilIcon className="w-4 h-4" />
                    </button>
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteCV(cv.id);
                      }}
                      className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                      title="Delete CV"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-12">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No CVs found</h3>
              <p className="mt-1 text-sm text-gray-500">
                Upload your first CV to get started with job applications.
              </p>
              <button 
                onClick={() => setShowUploadModal(true)}
                className="mt-4 btn btn-primary"
              >
                Upload CV
              </button>
            </div>
          )}
        </div>

        {/* CV Details */}
        <div className="lg:sticky lg:top-6">
          {selectedCV ? (
            <div className="card p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{selectedCV.title}</h2>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {selectedCV.language.toUpperCase()}
                    </span>
                    {selectedCV.is_base_cv && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Base CV
                      </span>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="space-y-6">
                {/* Personal Info */}
                {selectedCV.personal_info && Object.keys(selectedCV.personal_info).length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-900 mb-2">Personal Information</h3>
                    <div className="bg-gray-50 p-3 rounded-md text-sm">
                      {selectedCV.personal_info.name && (
                        <p><strong>Name:</strong> {selectedCV.personal_info.name}</p>
                      )}
                      {selectedCV.personal_info.email && (
                        <p><strong>Email:</strong> {selectedCV.personal_info.email}</p>
                      )}
                      {selectedCV.personal_info.phone && (
                        <p><strong>Phone:</strong> {selectedCV.personal_info.phone}</p>
                      )}
                      {selectedCV.personal_info.address && (
                        <p><strong>Address:</strong> {selectedCV.personal_info.address}</p>
                      )}
                    </div>
                  </div>
                )}
                
                {/* Skills */}
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Skills ({selectedCV.skills.length})</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedCV.skills.map((skill, index) => (
                      <span 
                        key={index}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
                
                {/* Experience */}
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Experience ({selectedCV.experience.length})</h3>
                  <div className="space-y-3">
                    {selectedCV.experience.slice(0, 3).map((exp, index) => (
                      <div key={index} className="bg-gray-50 p-3 rounded-md text-sm">
                        <h4 className="font-medium">{exp.position || 'Position'}</h4>
                        <p className="text-gray-600">{exp.company || 'Company'}</p>
                        {exp.start_date && (
                          <p className="text-gray-500 text-xs">
                            {exp.start_date} - {exp.end_date || 'Present'}
                          </p>
                        )}
                      </div>
                    ))}
                    {selectedCV.experience.length > 3 && (
                      <p className="text-xs text-gray-500">
                        +{selectedCV.experience.length - 3} more positions
                      </p>
                    )}
                  </div>
                </div>
                
                {/* Education */}
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Education ({selectedCV.education.length})</h3>
                  <div className="space-y-3">
                    {selectedCV.education.slice(0, 2).map((edu, index) => (
                      <div key={index} className="bg-gray-50 p-3 rounded-md text-sm">
                        <h4 className="font-medium">{edu.degree || 'Degree'}</h4>
                        <p className="text-gray-600">{edu.institution || 'Institution'}</p>
                        {edu.field && (
                          <p className="text-gray-500">{edu.field}</p>
                        )}
                        {edu.start_date && (
                          <p className="text-gray-500 text-xs">
                            {edu.start_date} - {edu.end_date || 'Present'}
                          </p>
                        )}
                      </div>
                    ))}
                    {selectedCV.education.length > 2 && (
                      <p className="text-xs text-gray-500">
                        +{selectedCV.education.length - 2} more qualifications
                      </p>
                    )}
                  </div>
                </div>
                
                <div className="pt-4 border-t">
                  <button className="w-full btn btn-primary mb-2">
                    Adapt for Job
                  </button>
                  <button className="w-full btn btn-outline">
                    Download PDF
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="card p-6 text-center">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Select a CV</h3>
              <p className="mt-1 text-sm text-gray-500">
                Click on a CV from the list to view its details.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Upload CV</h3>
                <button 
                  onClick={() => setShowUploadModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    CV Title
                  </label>
                  <input
                    type="text"
                    className="input"
                    placeholder="e.g., My Resume 2024"
                    value={uploadTitle}
                    onChange={(e) => setUploadTitle(e.target.value)}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Language
                  </label>
                  <select
                    className="input"
                    value={uploadLanguage}
                    onChange={(e) => setUploadLanguage(e.target.value)}
                  >
                    <option value="en">English</option>
                    <option value="de">German</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    PDF File
                  </label>
                  <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                    <div className="space-y-1 text-center">
                      <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
                      <div className="flex text-sm text-gray-600">
                        <label htmlFor="file-upload" className="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500">
                          <span>Upload a file</span>
                          <input 
                            id="file-upload" 
                            name="file-upload" 
                            type="file" 
                            className="sr-only"
                            accept=".pdf"
                            onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                          />
                        </label>
                        <p className="pl-1">or drag and drop</p>
                      </div>
                      <p className="text-xs text-gray-500">PDF files only</p>
                      {uploadFile && (
                        <p className="text-sm text-gray-900">{uploadFile.name}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex space-x-3 mt-6">
                <button 
                  onClick={() => setShowUploadModal(false)}
                  className="flex-1 btn btn-outline"
                >
                  Cancel
                </button>
                <button 
                  onClick={handleFileUpload}
                  disabled={uploading || !uploadFile || !uploadTitle.trim()}
                  className="flex-1 btn btn-primary"
                >
                  {uploading ? 'Uploading...' : 'Upload'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CVs;