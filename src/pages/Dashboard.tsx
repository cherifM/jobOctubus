import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  BriefcaseIcon, 
  DocumentTextIcon, 
  ClipboardDocumentListIcon,
  ChartBarIcon,
  PlusIcon 
} from '@heroicons/react/24/outline';
import { jobService, Job } from '../services/jobService';
import { cvService } from '../services/cvService';
import { applicationService, Application } from '../services/applicationService';
import toast from 'react-hot-toast';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState({
    totalJobs: 0,
    totalCVs: 0,
    totalApplications: 0,
    pendingApplications: 0
  });
  const [recentJobs, setRecentJobs] = useState<Job[]>([]);
  const [recentApplications, setRecentApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [jobs, cvs, applications] = await Promise.all([
        jobService.getJobs({ limit: 5 }),
        cvService.getCVs({ limit: 5 }),
        applicationService.getApplications({ limit: 5 })
      ]);

      setStats({
        totalJobs: jobs.length,
        totalCVs: cvs.length,
        totalApplications: applications.length,
        pendingApplications: applications.filter(app => app.status === 'pending').length
      });

      setRecentJobs(jobs);
      setRecentApplications(applications);
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
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
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <Link to="/" className="btn btn-primary flex items-center space-x-2">
          <PlusIcon className="w-5 h-5" />
          <span>Start Agentic Search</span>
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BriefcaseIcon className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Available Jobs
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  {stats.totalJobs}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <DocumentTextIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  My CVs
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  {stats.totalCVs}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ClipboardDocumentListIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Applications
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  {stats.totalApplications}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-yellow-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Pending
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  {stats.pendingApplications}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Jobs and Applications */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Jobs */}
        <div className="card p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Job Matches</h2>
          <div className="space-y-4">
            {recentJobs.length > 0 ? (
              recentJobs.map((job) => (
                <div key={job.id} className="border-l-4 border-primary-400 pl-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-medium text-gray-900">{job.title}</h3>
                    {job.match_score && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        {Math.round(job.match_score)}% match
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500">{job.company} • {job.location}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(job.posted_date).toLocaleDateString()}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">No jobs found. Start searching for opportunities!</p>
            )}
          </div>
        </div>

        {/* Recent Applications */}
        <div className="card p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Applications</h2>
          <div className="space-y-4">
            {recentApplications.length > 0 ? (
              recentApplications.map((application) => (
                <div key={application.id} className="border-l-4 border-blue-400 pl-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-medium text-gray-900">
                      {application.job.title}
                    </h3>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      application.status === 'applied' 
                        ? 'bg-blue-100 text-blue-800'
                        : application.status === 'pending'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {application.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500">{application.job.company}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    Applied {new Date(application.created_at).toLocaleDateString()}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">No applications yet. Find jobs and start applying!</p>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link to="/" className="btn btn-outline flex items-center justify-center space-x-2 py-4">
            <BriefcaseIcon className="w-5 h-5" />
            <span>Agentic Job Search</span>
          </Link>
          <Link to="/cvs" className="btn btn-outline flex items-center justify-center space-x-2 py-4">
            <DocumentTextIcon className="w-5 h-5" />
            <span>Manage CVs</span>
          </Link>
          <Link to="/applications" className="btn btn-outline flex items-center justify-center space-x-2 py-4">
            <ClipboardDocumentListIcon className="w-5 h-5" />
            <span>View Applications</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;