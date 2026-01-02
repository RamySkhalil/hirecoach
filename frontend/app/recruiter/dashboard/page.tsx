"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Briefcase, Users, Calendar, Plus, ArrowRight, Search, Filter, Power } from "lucide-react";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { useAuth } from "@clerk/nextjs";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

interface Job {
  id: string;
  title: string;
  status: string;
  applications_count: number;
  created_at: string;
  is_active: boolean;
}

export default function RecruiterDashboard() {
  const router = useRouter();
  const { user, role, loading } = useCurrentUser();
  const { getToken } = useAuth();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [filteredJobs, setFilteredJobs] = useState<Job[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState<"all" | "active" | "inactive">("all");
  const [stats, setStats] = useState({
    totalJobs: 0,
    totalApplications: 0,
    totalInterviews: 0
  });

  useEffect(() => {
    if (!loading && role !== "RECRUITER") {
      router.push("/onboarding/role");
      return;
    }

    if (!loading && role === "RECRUITER") {
      loadJobs();
    }
  }, [loading, role, router, searchQuery, filterStatus]);

  async function loadJobs() {
    try {
      const token = await getToken();
      if (!token) return;
      
      const params = new URLSearchParams();
      if (searchQuery) params.append('search', searchQuery);
      if (filterStatus !== 'all') params.append('filter_status', filterStatus);
      
      const response = await fetch(`${API_URL}/api/ats/v1/jobs?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setJobs(data);
        setFilteredJobs(data);
        setStats({
          totalJobs: data.length,
          totalApplications: data.reduce((sum: number, job: Job) => sum + job.applications_count, 0),
          totalInterviews: 0 // TODO: Calculate from interviews
        });
      }
    } catch (error) {
      console.error("Failed to load jobs:", error);
    }
  }

  async function toggleJobActive(jobId: string, currentStatus: boolean) {
    try {
      const token = await getToken();
      if (!token) return;
      
      const response = await fetch(`${API_URL}/api/ats/v1/jobs/${jobId}/toggle-active`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        // Reload jobs to get updated status
        await loadJobs();
      } else {
        console.error("Failed to toggle job status");
      }
    } catch (error) {
      console.error("Failed to toggle job status:", error);
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-white dark:bg-gray-950 pt-24 pb-12">
      <div className="max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent mb-2">
              Recruiter Dashboard
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Manage jobs, applications, and interviews
            </p>
          </div>
          <Link href="/recruiter/jobs/new">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-6 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-2"
            >
              <Plus className="h-5 w-5" />
              Create Job
            </motion.button>
          </Link>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-900 rounded-2xl shadow-lg p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">Total Jobs</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-gray-100">{stats.totalJobs}</p>
              </div>
              <Briefcase className="h-12 w-12 text-blue-600 dark:text-blue-400" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-gray-800 dark:to-gray-900 rounded-2xl shadow-lg p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">Applications</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-gray-100">{stats.totalApplications}</p>
              </div>
              <Users className="h-12 w-12 text-purple-600 dark:text-purple-400" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-gray-800 dark:to-gray-900 rounded-2xl shadow-lg p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">Interviews</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-gray-100">{stats.totalInterviews}</p>
              </div>
              <Calendar className="h-12 w-12 text-green-600 dark:text-green-400" />
            </div>
          </motion.div>
        </div>

        {/* Search and Filter Bar */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 mb-8"
        >
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search Bar */}
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by job title..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
            </div>
            
            {/* Filter Dropdown */}
            <div className="relative">
              <Filter className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 z-10" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as "all" | "active" | "inactive")}
                className="pl-12 pr-10 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none cursor-pointer transition-all"
              >
                <option value="all">All Ads</option>
                <option value="active">Active Ads</option>
                <option value="inactive">Inactive Ads</option>
              </select>
            </div>
          </div>
        </motion.div>

        {/* Recent Jobs */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Your Job Ads</h2>
            <Link href="/recruiter/jobs">
              <span className="text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1">
                View All
                <ArrowRight className="h-4 w-4" />
              </span>
            </Link>
          </div>

          {filteredJobs.length === 0 ? (
            <div className="text-center py-12">
              <Briefcase className="h-16 w-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                {jobs.length === 0 ? "No jobs yet" : "No jobs match your search criteria"}
              </p>
              {jobs.length === 0 && (
                <Link href="/recruiter/jobs/new">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-lg font-semibold"
                  >
                    Create Your First Job
                  </motion.button>
                </Link>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {filteredJobs.map((job) => (
                <motion.div
                  key={job.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  whileHover={{ scale: 1.01 }}
                  className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-all"
                >
                  <div className="flex items-center justify-between gap-4">
                    <Link href={`/recruiter/jobs/${job.id}`} className="flex-1">
                      <div>
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{job.title}</h3>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            job.is_active 
                              ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400' 
                              : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                          }`}>
                            {job.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {job.applications_count} applications • {job.status}
                        </p>
                      </div>
                    </Link>
                    
                    {/* Toggle Switch */}
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-gray-600 dark:text-gray-400 hidden sm:block">
                        {job.is_active ? 'Active' : 'Inactive'}
                      </span>
                      <button
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          toggleJobActive(job.id, job.is_active);
                        }}
                        className={`relative inline-flex h-7 w-14 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                          job.is_active ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                        }`}
                        role="switch"
                        aria-checked={job.is_active}
                      >
                        <motion.span
                          className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform ${
                            job.is_active ? 'translate-x-8' : 'translate-x-1'
                          }`}
                          layout
                          transition={{ type: "spring", stiffness: 500, damping: 30 }}
                        />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

