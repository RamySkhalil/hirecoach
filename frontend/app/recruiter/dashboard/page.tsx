"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Briefcase, Users, Calendar, Plus, ArrowRight } from "lucide-react";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { useAuth } from "@clerk/nextjs";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Job {
  id: string;
  title: string;
  status: string;
  applications_count: number;
  created_at: string;
}

export default function RecruiterDashboard() {
  const router = useRouter();
  const { user, role, loading } = useCurrentUser();
  const { getToken } = useAuth();
  const [jobs, setJobs] = useState<Job[]>([]);
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
  }, [loading, role, router]);

  async function loadJobs() {
    try {
      const token = await getToken();
      if (!token) return;
      
      const response = await fetch(`${API_URL}/api/ats/v1/jobs`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setJobs(data);
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
    <main className="min-h-screen bg-white dark:bg-gray-950 py-12">
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

        {/* Recent Jobs */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Recent Jobs</h2>
            <Link href="/recruiter/jobs">
              <span className="text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1">
                View All
                <ArrowRight className="h-4 w-4" />
              </span>
            </Link>
          </div>

          {jobs.length === 0 ? (
            <div className="text-center py-12">
              <Briefcase className="h-16 w-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400 mb-4">No jobs yet</p>
              <Link href="/recruiter/jobs/new">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-lg font-semibold"
                >
                  Create Your First Job
                </motion.button>
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {jobs.slice(0, 5).map((job) => (
                <Link key={job.id} href={`/recruiter/jobs/${job.id}`}>
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-all cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{job.title}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {job.applications_count} applications • {job.status}
                        </p>
                      </div>
                      <ArrowRight className="h-5 w-5 text-gray-400" />
                    </div>
                  </motion.div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

