"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, User } from "lucide-react";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { useAuth } from "@clerk/nextjs";
import { ApplicationsTable } from "@/components/applications-table";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Application {
  id: string;
  job_id: string;
  candidate_id: string;
  candidate_name: string;
  candidate_email: string;
  status: string;
  fit_score: number | null;
  applied_at: string;
}

export default function JobApplicationsPage() {
  const router = useRouter();
  const params = useParams();
  const jobId = params.jobId as string;
  const { role, loading } = useCurrentUser();
  const { getToken } = useAuth();
  const [applications, setApplications] = useState<Application[]>([]);
  const [loadingApps, setLoadingApps] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && role !== "RECRUITER") {
      router.push("/onboarding/role");
      return;
    }

    if (!loading && role === "RECRUITER") {
      loadApplications();
    }
  }, [loading, role, router, jobId]);

  async function loadApplications() {
    try {
      const token = await getToken();
      if (!token) {
        console.error("No authentication token");
        setLoadingApps(false);
        return;
      }

      const response = await fetch(`${API_URL}/api/ats/v1/jobs/${jobId}/applications`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
        console.error("Failed to load applications:", errorData);
        setError(errorData.detail || `Failed to load applications (${response.status})`);
        if (response.status === 404) {
          // Job not found, redirect back
          router.push(`/recruiter/jobs/${jobId}`);
        }
        return;
      }

      const data = await response.json();
      setApplications(data);
      setError(null);
    } catch (error) {
      console.error("Failed to load applications:", error);
      // Check if it's a network error
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        setError("Cannot connect to backend. Please ensure the backend server is running on " + API_URL);
      } else {
        setError(error instanceof Error ? error.message : "Failed to load applications");
      }
    } finally {
      setLoadingApps(false);
    }
  }

  if (loading || loadingApps) {
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
        <Link href={`/recruiter/jobs/${jobId}`} className="inline-flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 mb-6">
          <ArrowLeft className="h-5 w-5" />
          Back to Job
        </Link>

        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent mb-2">
              Applications
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              {applications.length} {applications.length === 1 ? 'application' : 'applications'}
            </p>
          </div>
        </div>

        {error ? (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-2xl shadow-lg p-6">
            <p className="text-red-600 dark:text-red-400 font-semibold mb-2">Error loading applications</p>
            <p className="text-sm text-red-500 dark:text-red-500 mb-2">{error}</p>
            <p className="text-xs text-red-400 dark:text-red-600 mb-4">
              Backend URL: {API_URL}
            </p>
            <button
              onClick={loadApplications}
              className="mt-4 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
            >
              Retry
            </button>
          </div>
        ) : applications.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-12 text-center">
            <User className="h-16 w-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400 mb-4">No applications yet</p>
            <p className="text-sm text-gray-500 dark:text-gray-500">
              Applications will appear here when candidates apply to this job.
            </p>
          </div>
        ) : (
          <ApplicationsTable data={applications} jobId={jobId} />
        )}
      </div>
    </main>
  );
}

