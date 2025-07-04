import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  MagnifyingGlassIcon, 
  MapPinIcon, 
  BriefcaseIcon,
  CalendarIcon,
  CheckIcon,
  DocumentTextIcon,
  PaperAirplaneIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';
import { jobService, Job, JobSearchRequest } from '../services/jobService';
import { cvService, CV } from '../services/cvService';
import { applicationService } from '../services/applicationService';
import { settingsService, JobSearchServicesResponse } from '../services/settingsService';
import toast from 'react-hot-toast';

const AgenticJobSearch: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJobs, setSelectedJobs] = useState<Set<number>>(new Set());
  const [cvs, setCvs] = useState<CV[]>([]);
  const [selectedCV, setSelectedCV] = useState<CV | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [location, setLocation] = useState('');
  const [currentStep, setCurrentStep] = useState<'search' | 'select' | 'process' | 'complete'>('search');
  const [searchServices, setSearchServices] = useState<JobSearchServicesResponse | null>(null);

  useEffect(() => {
    loadCVs();
    loadSearchServices();
  }, []);

  const loadCVs = async () => {
    try {
      const cvsData = await cvService.getCVs();
      setCvs(cvsData);
      if (cvsData.length > 0) {
        setSelectedCV(cvsData.find(cv => cv.is_base_cv) || cvsData[0]);
      }
    } catch (error) {
      toast.error('Failed to load CVs');
    }
  };


  const loadSearchServices = async () => {
    try {
      const services = await settingsService.getJobSearchServices();
      setSearchServices(services);
    } catch (error) {
      console.error('Failed to load search services');
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a search query or keywords');
      return;
    }

    setLoading(true);
    try {
      const searchRequest: JobSearchRequest = {
        query: searchQuery,
        location: location || undefined,
        max_results: 50
      };
      
      const searchResults = await jobService.searchJobs(searchRequest);
      setJobs(searchResults);
      setCurrentStep('select');
      toast.success(`Found ${searchResults.length} jobs`);
    } catch (error) {
      toast.error('Search failed');
    } finally {
      setLoading(false);
    }
  };

  const toggleJobSelection = (jobId: number) => {
    const newSelection = new Set(selectedJobs);
    if (newSelection.has(jobId)) {
      newSelection.delete(jobId);
    } else {
      newSelection.add(jobId);
    }
    setSelectedJobs(newSelection);
  };

  const selectAllJobs = () => {
    setSelectedJobs(new Set(jobs.map(job => job.id)));
  };

  const clearSelection = () => {
    setSelectedJobs(new Set());
  };

  const processSelectedJobs = async () => {
    if (selectedJobs.size === 0) {
      toast.error('Please select at least one job');
      return;
    }

    if (!selectedCV) {
      toast.error('Please select a CV to use');
      return;
    }

    setCurrentStep('process');

    try {
      const selectedJobList = jobs.filter(job => selectedJobs.has(job.id));
      let successCount = 0;
      let errors: string[] = [];

      for (const job of selectedJobList) {
        try {
          // Step 1: Adapt CV for this specific job
          toast(`Adapting CV for ${job.title} at ${job.company}...`, { 
            icon: '🔄',
            duration: 2000 
          });
          
          const adaptedCV = await cvService.adaptCV({
            cv_id: selectedCV.id,
            job_id: job.id,
            focus_areas: job.skills_required.slice(0, 3)
          });

          // Step 2: Create application
          const application = await applicationService.createApplication({
            job_id: job.id,
            cv_id: adaptedCV.id,
            status: 'draft'
          });

          // Step 3: Generate cover letter
          toast(`Generating cover letter for ${job.title}...`, { 
            icon: '✍️',
            duration: 2000 
          });
          
          await applicationService.generateCoverLetter(application.id, {
            job_id: job.id,
            cv_id: adaptedCV.id,
            tone: 'professional',
            length: 'medium'
          });

          // Step 4: Update application status
          await applicationService.updateApplication(application.id, {
            status: 'ready'
          });

          successCount++;
          toast.success(`✅ ${job.title} at ${job.company} - Ready to apply!`);

        } catch (error) {
          const errorMsg = `Failed to process ${job.title} at ${job.company}`;
          errors.push(errorMsg);
          toast.error(errorMsg);
        }
      }

      setCurrentStep('complete');
      
      if (successCount > 0) {
        toast.success(
          `🎉 Successfully processed ${successCount} job application${successCount !== 1 ? 's' : ''}! Check your Applications page.`,
          { duration: 5000 }
        );
      }

      if (errors.length > 0) {
        toast.error(`${errors.length} applications failed to process`, { duration: 3000 });
      }

    } catch (error) {
      toast.error('Failed to process applications');
      setCurrentStep('select');
    } finally {
      // Processing state managed by currentStep
    }
  };

  const resetWorkflow = () => {
    setSelectedJobs(new Set());
    setCurrentStep('search');
    setSearchQuery('');
    setLocation('');
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getMatchScoreColor = (score?: number) => {
    if (!score) return 'bg-gray-100 text-gray-800';
    if (score >= 80) return 'bg-green-100 text-green-800';
    if (score >= 60) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Agentic Job Search</h1>
          <p className="text-gray-600 mt-1">
            Search → Select → Auto-apply with adapted CVs and cover letters
          </p>
        </div>
        {currentStep !== 'search' && (
          <button 
            onClick={resetWorkflow}
            className="btn btn-outline"
          >
            New Search
          </button>
        )}
      </div>

      {/* Progress Steps */}
      <div className="flex items-center space-x-4 bg-gray-50 p-4 rounded-lg">
        <div className={`flex items-center space-x-2 ${currentStep === 'search' ? 'text-primary-600 font-medium' : ['select', 'process', 'complete'].includes(currentStep) ? 'text-green-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep === 'search' ? 'bg-primary-100' : ['select', 'process', 'complete'].includes(currentStep) ? 'bg-green-100' : 'bg-gray-100'}`}>
            {['select', 'process', 'complete'].includes(currentStep) ? <CheckIcon className="w-4 h-4" /> : '1'}
          </div>
          <span>Search Jobs</span>
        </div>
        <div className="w-8 h-px bg-gray-300"></div>
        <div className={`flex items-center space-x-2 ${currentStep === 'select' ? 'text-primary-600 font-medium' : currentStep === 'process' || currentStep === 'complete' ? 'text-green-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep === 'select' ? 'bg-primary-100' : currentStep === 'process' || currentStep === 'complete' ? 'bg-green-100' : 'bg-gray-100'}`}>
            {currentStep === 'process' || currentStep === 'complete' ? <CheckIcon className="w-4 h-4" /> : '2'}
          </div>
          <span>Select Jobs</span>
        </div>
        <div className="w-8 h-px bg-gray-300"></div>
        <div className={`flex items-center space-x-2 ${currentStep === 'process' ? 'text-primary-600 font-medium' : currentStep === 'complete' ? 'text-green-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep === 'process' ? 'bg-primary-100' : currentStep === 'complete' ? 'bg-green-100' : 'bg-gray-100'}`}>
            {currentStep === 'complete' ? <CheckIcon className="w-4 h-4" /> : '3'}
          </div>
          <span>Auto-Process</span>
        </div>
      </div>

      {/* Search Form */}
      {currentStep === 'search' && (
        <div className="card p-6">
          <h2 className="text-lg font-medium mb-4">Step 1: Search for Jobs</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
                Job Keywords or Description
              </label>
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  id="search"
                  className="input pl-10"
                  placeholder="e.g., CFD Engineer, Python Developer, Wind Energy"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
              </div>
            </div>
            
            <div>
              <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
                Location (Optional)
              </label>
              <div className="relative">
                <MapPinIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  id="location"
                  className="input pl-10"
                  placeholder="e.g., Hamburg, Germany"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
              </div>
            </div>
          </div>
          
          <div className="mt-6">
            <button 
              onClick={handleSearch}
              disabled={loading}
              className="btn btn-primary flex items-center space-x-2"
            >
              <MagnifyingGlassIcon className="w-5 h-5" />
              <span>{loading ? 'Searching...' : 'Search Jobs'}</span>
            </button>
          </div>

          {/* Job Search Services Status */}
          {searchServices && (
            <div className="mt-4 pt-4 border-t">
              <p className="text-xs text-gray-500 mb-2">Enabled Search Services:</p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(searchServices.services)
                  .filter(([_, service]) => service.enabled)
                  .map(([key, service]) => (
                    <span 
                      key={key}
                      className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
                    >
                      <span className="w-2 h-2 bg-green-500 rounded-full mr-1"></span>
                      {service.name}
                    </span>
                  ))}
                {Object.values(searchServices.services).filter(service => service.enabled).length === 0 && (
                  <span className="text-xs text-red-600">No services enabled</span>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Job Selection */}
      {(currentStep === 'select' || currentStep === 'process') && jobs.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium">
              Step 2: Select Jobs to Apply ({selectedJobs.size} selected)
            </h2>
            <div className="flex space-x-2">
              <button onClick={selectAllJobs} className="btn btn-outline btn-sm">
                Select All
              </button>
              <button onClick={clearSelection} className="btn btn-outline btn-sm">
                Clear All
              </button>
            </div>
          </div>

          {/* CV Selection */}
          <div className="card p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <DocumentTextIcon className="w-5 h-5 text-gray-400" />
                <label className="text-sm font-medium text-gray-700">Base CV to Use:</label>
                {cvs.length > 0 ? (
                  <select
                    className="input flex-1 max-w-xs"
                    value={selectedCV?.id || ''}
                    onChange={(e) => {
                      const cv = cvs.find(c => c.id === parseInt(e.target.value));
                      setSelectedCV(cv || null);
                    }}
                  >
                    {cvs.map(cv => (
                      <option key={cv.id} value={cv.id}>
                        {cv.title} ({cv.language.toUpperCase()})
                        {cv.is_base_cv && ' - Base CV'}
                      </option>
                    ))}
                  </select>
                ) : (
                  <span className="text-sm text-gray-500">No CVs found</span>
                )}
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={async () => {
                    try {
                      const initializedCVs = await cvService.initializeFromWebsite();
                      if (initializedCVs.length > 0) {
                        setCvs([...cvs, ...initializedCVs]);
                        setSelectedCV(initializedCVs[0]);
                        toast.success(`Initialized ${initializedCVs.length} CV(s) from personal website`);
                      } else {
                        toast.error('No CVs found in personal website folder');
                      }
                    } catch (error) {
                      toast.error('Failed to initialize CVs from website');
                    }
                  }}
                  className="btn btn-outline btn-sm"
                >
                  Load from Website
                </button>
                <Link to="/cvs" className="btn btn-outline btn-sm">
                  Manage CVs
                </Link>
              </div>
            </div>
          </div>

          {/* Job List */}
          <div className="grid grid-cols-1 gap-4">
            {jobs.map((job) => (
              <div 
                key={job.id} 
                className={`card p-4 cursor-pointer transition-all hover:shadow-md ${
                  selectedJobs.has(job.id) ? 'ring-2 ring-primary-500 bg-primary-50' : ''
                }`}
                onClick={() => toggleJobSelection(job.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div className={`w-5 h-5 rounded border-2 flex items-center justify-center mt-1 ${
                      selectedJobs.has(job.id) 
                        ? 'bg-primary-600 border-primary-600' 
                        : 'border-gray-300'
                    }`}>
                      {selectedJobs.has(job.id) && (
                        <CheckIcon className="w-3 h-3 text-white" />
                      )}
                    </div>
                    
                    <div className="flex-1">
                      <h3 className="text-lg font-medium text-gray-900">{job.title}</h3>
                      <p className="text-sm text-gray-600">{job.company}</p>
                      
                      <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                        <div className="flex items-center">
                          <MapPinIcon className="h-4 w-4 mr-1" />
                          {job.location}
                        </div>
                        <div className="flex items-center">
                          <BriefcaseIcon className="h-4 w-4 mr-1" />
                          {job.job_type}
                        </div>
                        {job.remote_option && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            Remote
                          </span>
                        )}
                      </div>
                      
                      <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                        {job.description}
                      </p>
                      
                      <div className="mt-3 flex flex-wrap gap-1">
                        {job.skills_required.slice(0, 4).map((skill, index) => (
                          <span 
                            key={index}
                            className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800"
                          >
                            {skill}
                          </span>
                        ))}
                        {job.skills_required.length > 4 && (
                          <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-500">
                            +{job.skills_required.length - 4} more
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col items-end space-y-2">
                    {job.match_score && (
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getMatchScoreColor(job.match_score)}`}>
                        {Math.round(job.match_score)}% match
                      </span>
                    )}
                    <div className="flex items-center text-xs text-gray-400">
                      <CalendarIcon className="h-4 w-4 mr-1" />
                      {formatDate(job.posted_date)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Process Button */}
          {currentStep === 'select' && (
            <div className="flex justify-center pt-6">
              <button 
                onClick={processSelectedJobs}
                disabled={selectedJobs.size === 0 || !selectedCV}
                className="btn btn-primary btn-lg flex items-center space-x-2"
              >
                <SparklesIcon className="w-5 h-5" />
                <span>
                  Process {selectedJobs.size} Job{selectedJobs.size !== 1 ? 's' : ''} 
                  (Adapt CV + Generate Cover Letters)
                </span>
              </button>
            </div>
          )}
        </div>
      )}

      {/* Processing Status */}
      {currentStep === 'process' && (
        <div className="card p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Processing Applications...</h3>
          <p className="text-gray-600">
            Adapting CVs and generating personalized cover letters for each selected job.
            This may take a few moments.
          </p>
        </div>
      )}

      {/* Complete */}
      {currentStep === 'complete' && (
        <div className="card p-8 text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckIcon className="w-8 h-8 text-green-600" />
          </div>
          <h3 className="text-xl font-medium text-gray-900 mb-2">Applications Ready!</h3>
          <p className="text-gray-600 mb-6">
            Your job applications have been processed with adapted CVs and personalized cover letters.
          </p>
          <div className="flex justify-center space-x-4">
            <button 
              onClick={() => window.location.href = '/applications'}
              className="btn btn-primary flex items-center space-x-2"
            >
              <PaperAirplaneIcon className="w-5 h-5" />
              <span>View Applications</span>
            </button>
            <button 
              onClick={resetWorkflow}
              className="btn btn-outline"
            >
              Search More Jobs
            </button>
          </div>
        </div>
      )}

      {/* Empty State */}
      {currentStep === 'select' && jobs.length === 0 && (
        <div className="text-center py-12">
          <MagnifyingGlassIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No jobs found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Try adjusting your search criteria or use different keywords.
          </p>
          <button 
            onClick={() => setCurrentStep('search')}
            className="mt-4 btn btn-primary"
          >
            Try New Search
          </button>
        </div>
      )}
    </div>
  );
};

export default AgenticJobSearch;