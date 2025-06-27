'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { 
  PlusIcon, 
  DocumentArrowUpIcon, 
  CpuChipIcon,
  FolderPlusIcon,
  ChartBarIcon,
  SparklesIcon 
} from '@heroicons/react/24/outline';
import { useAuthStore } from '@/stores/authStore';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { api } from '@/services/api';
import { Project } from '@/types';

interface UserAnalytics {
  total_projects: number;
  total_documents: number;
  total_elements: number;
  total_generations: number;
  total_cost: number;
  recent_activity: Array<{
    type: string;
    description: string;
    timestamp: string;
  }>;
}

export default function Dashboard() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  
  // State for dashboard data
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null);
  const [recentProjects, setRecentProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, router]);

  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      if (!isAuthenticated || !user) return;
      
      try {
        setIsLoading(true);
        setError(null);

        // Fetch user analytics and recent projects in parallel
        const [analyticsResponse, projectsResponse] = await Promise.allSettled([
          api.getUserAnalytics(),
          api.getProjects({ page: 1, page_size: 5 }) // Get 5 most recent projects
        ]);

        // Handle analytics response
        if (analyticsResponse.status === 'fulfilled') {
          setAnalytics(analyticsResponse.value);
        } else {
          console.error('Failed to fetch analytics:', analyticsResponse.reason);
        }

        // Handle projects response
        if (projectsResponse.status === 'fulfilled') {
          setRecentProjects(projectsResponse.value.items || []);
        } else {
          console.error('Failed to fetch projects:', projectsResponse.reason);
        }

      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [isAuthenticated, user]);

  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show loading state
  if (isLoading) {
    return (
      <DashboardLayout title="Dashboard">
        <div className="flex items-center justify-center min-h-96">
          <LoadingSpinner size="lg" />
        </div>
      </DashboardLayout>
    );
  }

  const quickActions = [
    {
      title: 'Create Project',
      description: 'Start a new RAG project with your documents',
      icon: FolderPlusIcon,
      color: 'bg-blue-500 hover:bg-blue-600',
      href: '/projects/create'
    },
    {
      title: 'Upload Documents',
      description: 'Add documents to process and analyze',
      icon: DocumentArrowUpIcon,
      color: 'bg-green-500 hover:bg-green-600',
      href: '/documents'
    },
    {
      title: 'Create Element',
      description: 'Build prompt templates and AI tools',
      icon: CpuChipIcon,
      color: 'bg-purple-500 hover:bg-purple-600',
      href: '/elements/create'
    }
  ];

  // Use real analytics data or fallback to zeros
  const stats = [
    { 
      name: 'Total Projects', 
      value: analytics?.total_projects?.toString() || '0', 
      icon: FolderPlusIcon, 
      color: 'text-blue-600' 
    },
    { 
      name: 'Documents', 
      value: analytics?.total_documents?.toString() || '0', 
      icon: DocumentArrowUpIcon, 
      color: 'text-green-600' 
    },
    { 
      name: 'Elements', 
      value: analytics?.total_elements?.toString() || '0', 
      icon: CpuChipIcon, 
      color: 'text-purple-600' 
    },
    { 
      name: 'Generations', 
      value: analytics?.total_generations?.toString() || '0', 
      icon: SparklesIcon, 
      color: 'text-orange-600' 
    },
  ];

  // Helper function to format dates
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Helper function to get tenant type display
  const getTenantTypeDisplay = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'hr': return 'Human Resources';
      case 'coding': return 'Software Development';
      case 'financial_report': return 'Financial Analysis';
      case 'deep_research': return 'Research & Analysis';
      case 'qa_generation': return 'Q&A Generation';
      case 'raw_rag': return 'General RAG Tasks';
      default: return type || 'Unknown';
    }
  };

  return (
    <DashboardLayout title="Dashboard">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Welcome Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Welcome back, {user.username}! 👋
          </h2>
          <p className="text-gray-600">
            Ready to build some intelligent RAG workflows? Here's what's happening with your projects.
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat) => (
            <div key={stat.name} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <stat.icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        {stat.name}
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {stat.value}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Quick Actions */}
          <div className="lg:col-span-2">
            <div className="bg-white shadow rounded-lg">
              <div className="p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-6">Quick Actions</h3>
                <div className="grid grid-cols-1 gap-4">
                  {quickActions.map((action) => (
                    <button
                      key={action.title}
                      onClick={() => router.push(action.href)}
                      className="flex items-center p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-left"
                    >
                      <div className={`flex-shrink-0 w-10 h-10 ${action.color} rounded-lg flex items-center justify-center mr-4`}>
                        <action.icon className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">{action.title}</h4>
                        <p className="text-sm text-gray-500">{action.description}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Recent Projects */}
            <div className="bg-white shadow rounded-lg mt-6">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-medium text-gray-900">Recent Projects</h3>
                  <button
                    onClick={() => router.push('/projects')}
                    className="text-sm text-blue-600 hover:text-blue-500"
                  >
                    View all
                  </button>
                </div>
                {recentProjects.length > 0 ? (
                  <div className="space-y-4">
                    {recentProjects.map((project) => (
                      <div
                        key={project.id}
                        className="flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors"
                        onClick={() => router.push(`/projects/${project.id}`)}
                      >
                        <div className="flex items-center space-x-3">
                          <FolderPlusIcon className="h-6 w-6 text-blue-600" />
                          <div>
                            <h4 className="text-sm font-medium text-gray-900">{project.name}</h4>
                            <p className="text-xs text-gray-500">
                              {getTenantTypeDisplay(project.tenant_type)} • {formatDate(project.created_at)}
                            </p>
                          </div>
                        </div>
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          project.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {project.status}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <FolderPlusIcon className="mx-auto h-12 w-12 text-gray-400" />
                    <h4 className="mt-2 text-sm font-medium text-gray-900">No projects yet</h4>
                    <p className="mt-1 text-sm text-gray-500">
                      Get started by creating your first RAG project.
                    </p>
                    <div className="mt-6">
                      <button
                        onClick={() => router.push('/projects/create')}
                        className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                      >
                        <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
                        Create Project
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Recent Activity */}
            <div className="bg-white shadow rounded-lg">
              <div className="p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-6">Recent Activity</h3>
                {analytics?.recent_activity && analytics.recent_activity.length > 0 ? (
                  <div className="space-y-4">
                    {analytics.recent_activity.map((activity, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="flex-shrink-0">
                          {activity.type === 'project_created' && (
                            <FolderPlusIcon className="h-5 w-5 text-blue-600" />
                          )}
                          {activity.type === 'document_uploaded' && (
                            <DocumentArrowUpIcon className="h-5 w-5 text-green-600" />
                          )}
                          {activity.type === 'element_created' && (
                            <CpuChipIcon className="h-5 w-5 text-purple-600" />
                          )}
                          {activity.type === 'generation_completed' && (
                            <SparklesIcon className="h-5 w-5 text-orange-600" />
                          )}
                          {!['project_created', 'document_uploaded', 'element_created', 'generation_completed'].includes(activity.type) && (
                            <ChartBarIcon className="h-5 w-5 text-gray-500" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-gray-900">{activity.description}</p>
                          <p className="text-xs text-gray-500">{formatDate(activity.timestamp)}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <ChartBarIcon className="mx-auto h-8 w-8 text-gray-400" />
                    <p className="mt-2 text-sm text-gray-500">
                      No recent activity. Start using TinyRAG to see your activity here!
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Getting Started */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg">
              <div className="p-6">
                <h3 className="text-lg font-medium text-blue-900 mb-4">Getting Started</h3>
                <div className="space-y-3">
                  <div className="flex items-start">
                    <div className="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center mr-3 mt-0.5">
                      <span className="text-xs font-bold text-white">1</span>
                    </div>
                    <p className="text-sm text-blue-800">Create your first project</p>
                  </div>
                  <div className="flex items-start">
                    <div className="flex-shrink-0 w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center mr-3 mt-0.5">
                      <span className="text-xs font-bold text-gray-600">2</span>
                    </div>
                    <p className="text-sm text-gray-600">Upload documents to process</p>
                  </div>
                  <div className="flex items-start">
                    <div className="flex-shrink-0 w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center mr-3 mt-0.5">
                      <span className="text-xs font-bold text-gray-600">3</span>
                    </div>
                    <p className="text-sm text-gray-600">Create elements and generate content</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
