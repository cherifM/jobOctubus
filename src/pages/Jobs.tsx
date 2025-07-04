import React, { useState, useEffect } from 'react';
import { 
  MagnifyingGlassIcon, 
  MapPinIcon, 
  BriefcaseIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { jobService, Job, JobSearchRequest } from '../services/jobService';
import toast from 'react-hot-toast';

const Jobs: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [location, setLocation] = useState('');
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  useEffect(() => {
    // No automatic job loading - only show jobs from searches
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a search query');
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
      toast.success(`Found ${searchResults.length} jobs`);
    } catch (error) {
      toast.error('Search failed');
    } finally {
      setLoading(false);
    }
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
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Job Search</h1>
      </div>

      {/* Search Form */}
      <div className="card p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
              Job Title or Keywords
            </label>
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                id="search"
                className="input pl-10"
                placeholder="e.g., CFD Engineer, OpenFOAM Developer"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
          </div>
          
          <div>
            <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
              Location
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
        
        <div className="mt-4 flex justify-end">
          <button 
            onClick={handleSearch}
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? 'Searching...' : 'Search Jobs'}
          </button>
        </div>
      </div>

      {/* Job Results */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Job List */}
        <div className="space-y-4">
          <h2 className="text-lg font-medium text-gray-900">
            {jobs.length} Job{jobs.length !== 1 ? 's' : ''} Found
          </h2>
          
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
          ) : jobs.length > 0 ? (
            jobs.map((job) => (
              <div 
                key={job.id} 
                className={`card p-4 cursor-pointer transition-all hover:shadow-md ${
                  selectedJob?.id === job.id ? 'ring-2 ring-primary-500' : ''
                }`}
                onClick={() => setSelectedJob(job)}
              >
                <div className="flex items-start justify-between">
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
                    
                    {job.salary_range && (
                      <div className="flex items-center mt-2 text-sm text-gray-600">
                        <CurrencyDollarIcon className="h-4 w-4 mr-1" />
                        {job.salary_range}
                      </div>
                    )}
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
                
                <div className="mt-3">
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {job.description}
                  </p>
                </div>
                
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
            ))
          ) : (
            <div className="text-center py-12">
              <BriefcaseIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No jobs found</h3>
              <p className="mt-1 text-sm text-gray-500">
                Try adjusting your search criteria or search for different keywords.
              </p>
            </div>
          )}
        </div>

        {/* Job Details */}
        <div className="lg:sticky lg:top-6">
          {selectedJob ? (
            <div className="card p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{selectedJob.title}</h2>
                  <p className="text-lg text-gray-600">{selectedJob.company}</p>
                </div>
                <a 
                  href={selectedJob.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary flex items-center space-x-2"
                >
                  <EyeIcon className="w-4 h-4" />
                  <span>View Job</span>
                </a>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <div className="flex items-center">
                    <MapPinIcon className="h-4 w-4 mr-1" />
                    {selectedJob.location}
                  </div>
                  <div className="flex items-center">
                    <BriefcaseIcon className="h-4 w-4 mr-1" />
                    {selectedJob.job_type}
                  </div>
                  <div className="flex items-center">
                    <CalendarIcon className="h-4 w-4 mr-1" />
                    {formatDate(selectedJob.posted_date)}
                  </div>
                </div>
                
                {selectedJob.salary_range && (
                  <div className="flex items-center text-sm text-gray-600">
                    <CurrencyDollarIcon className="h-4 w-4 mr-1" />
                    {selectedJob.salary_range}
                  </div>
                )}
                
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Description</h3>
                  <p className="text-sm text-gray-600 whitespace-pre-wrap">
                    {selectedJob.description}
                  </p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Requirements</h3>
                  <p className="text-sm text-gray-600 whitespace-pre-wrap">
                    {selectedJob.requirements}
                  </p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Required Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedJob.skills_required.map((skill, index) => (
                      <span 
                        key={index}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div className="pt-4 border-t">
                  <button className="w-full btn btn-primary">
                    Apply to This Job
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="card p-6 text-center">
              <BriefcaseIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Select a job</h3>
              <p className="mt-1 text-sm text-gray-500">
                Click on a job from the list to view its details.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Jobs;