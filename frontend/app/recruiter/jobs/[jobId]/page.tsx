"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowLeft, Edit, Share2, Copy, Check, Users, Calendar, MapPin, DollarSign, Briefcase } from "lucide-react";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { useAuth } from "@clerk/nextjs";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Job {
  id: string;
  title: string;
  location: string | null;
  employment_type: string | null;
  description: string;
  status: string;
  company_name: string | null;
  created_at: string;
  applications_count: number;
  min_salary: number | null;
  max_salary: number | null;
  currency: string | null;
}

interface SocialMediaPost {
  text: string;
  link: string;
}

export default function JobDetailPage() {
  const router = useRouter();
  const params = useParams();
  const jobId = params.jobId as string;
  const { role, loading } = useCurrentUser();
  const { getToken } = useAuth();
  const [job, setJob] = useState<Job | null>(null);
  const [loadingJob, setLoadingJob] = useState(true);
  const [socialPost, setSocialPost] = useState<SocialMediaPost | null>(null);
  const [generatingPost, setGeneratingPost] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && role !== "RECRUITER") {
      router.push("/onboarding/role");
      return;
    }

    if (!loading && role === "RECRUITER") {
      loadJob();
    }
  }, [loading, role, router, jobId]);

  async function loadJob() {
    try {
      const token = await getToken();
      if (!token) {
        console.error("No authentication token");
        setLoadingJob(false);
        return;
      }

      const response = await fetch(`${API_URL}/api/ats/v1/jobs/${jobId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setJob(data);
      } else if (response.status === 404) {
        router.push("/recruiter/jobs");
      } else {
        const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
        console.error("Failed to load job:", errorData);
      }
    } catch (error) {
      console.error("Failed to load job:", error);
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        console.error("Network error - is the backend running at", API_URL);
      }
    } finally {
      setLoadingJob(false);
    }
  }

  async function generateSocialPost() {
    if (!job) return;

    try {
      setGeneratingPost(true);
      const token = await getToken();
      if (!token) return;

      const response = await fetch(`${API_URL}/api/ats/v1/jobs/${jobId}/social-post`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSocialPost(data);
      }
    } catch (error) {
      console.error("Failed to generate social post:", error);
      alert("Failed to generate social media post");
    } finally {
      setGeneratingPost(false);
    }
  }

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (loading || loadingJob) {
    return (
      <main className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </main>
    );
  }

  if (!job) {
    return (
      <main className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 dark:text-gray-400 mb-4">Job not found</p>
          <Link href="/recruiter/jobs">
            <button className="bg-blue-600 text-white px-6 py-3 rounded-lg">
              Back to Jobs
            </button>
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-white dark:bg-gray-950 py-12">
      <div className="max-w-4xl mx-auto px-6">
        <Link href="/recruiter/jobs" className="inline-flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 mb-6">
          <ArrowLeft className="h-5 w-5" />
          Back to Jobs
        </Link>

        {/* Header */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                {job.title}
              </h1>
              {job.company_name && (
                <p className="text-lg text-gray-600 dark:text-gray-400 mb-4">
                  {job.company_name}
                </p>
              )}
            </div>
            <span className={`px-3 py-1 text-sm rounded-full ${
              job.status === 'OPEN' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
              job.status === 'DRAFT' ? 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200' :
              'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
            }`}>
              {job.status}
            </span>
          </div>

          {/* Job Details Grid */}
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            {job.location && (
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <MapPin className="h-5 w-5" />
                <span>{job.location}</span>
              </div>
            )}
            {job.employment_type && (
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <Briefcase className="h-5 w-5" />
                <span>{job.employment_type.replace(/_/g, ' ')}</span>
              </div>
            )}
            {(job.min_salary || job.max_salary) && (
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <DollarSign className="h-5 w-5" />
                <span>
                  {job.min_salary && job.max_salary 
                    ? `${job.min_salary.toLocaleString()} - ${job.max_salary.toLocaleString()} ${job.currency || 'USD'}`
                    : job.min_salary 
                      ? `${job.min_salary.toLocaleString()}+ ${job.currency || 'USD'}`
                      : `Up to ${job.max_salary?.toLocaleString()} ${job.currency || 'USD'}`
                  }
                </span>
              </div>
            )}
            <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
              <Users className="h-5 w-5" />
              <span>{job.applications_count} applications</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-4">
            <Link href={`/recruiter/jobs/${jobId}/applications`}>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-2 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-2"
              >
                <Users className="h-4 w-4" />
                View Applications ({job.applications_count})
              </motion.button>
            </Link>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={generateSocialPost}
              disabled={generatingPost}
              className="bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-2 border-gray-300 dark:border-gray-600 px-6 py-2 rounded-lg font-semibold hover:bg-gray-50 dark:hover:bg-gray-600 transition-all duration-300 flex items-center gap-2 disabled:opacity-50"
            >
              <Share2 className="h-4 w-4" />
              {generatingPost ? "Generating..." : "Generate Social Post"}
            </motion.button>
          </div>
        </div>

        {/* Job Description */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            Job Description
          </h2>
          <div className="prose dark:prose-invert max-w-none">
            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
              {job.description}
            </p>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-2xl shadow-lg p-6 mb-6">
            <p className="text-red-600 dark:text-red-400 font-semibold mb-2">Error</p>
            <p className="text-sm text-red-500 dark:text-red-500">{error}</p>
          </div>
        )}

        {/* Social Media Post */}
        {socialPost && (
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-900 rounded-2xl shadow-lg p-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                Social Media Post
              </h2>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => copyToClipboard(socialPost.text + "\n\n" + socialPost.link)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold flex items-center gap-2"
              >
                {copied ? (
                  <>
                    <Check className="h-4 w-4" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4" />
                    Copy
                  </>
                )}
              </motion.button>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 mb-4">
              <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap mb-4">
                {socialPost.text}
              </p>
              <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                <a 
                  href={socialPost.link} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 dark:text-blue-400 hover:underline text-sm"
                >
                  {socialPost.link}
                </a>
              </div>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Copy and paste this post to share on LinkedIn, Twitter, or other social media platforms.
            </p>
          </div>
        )}
      </div>
    </main>
  );
}

