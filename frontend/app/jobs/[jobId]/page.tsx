"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { MapPin, Briefcase, DollarSign, Calendar, ArrowLeft, Send, CheckCircle2, Upload, FileText, X } from "lucide-react";
import Link from "next/link";

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
  min_salary: number | null;
  max_salary: number | null;
  currency: string | null;
}

interface ApplicationFormData {
  candidate_name: string;
  candidate_email: string;
  candidate_phone: string;
  candidate_location: string;
  resume_url: string;
}

interface ResumeFile {
  file: File;
  preview?: string;
}

export default function PublicJobPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.jobId as string;
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [resumeFile, setResumeFile] = useState<ResumeFile | null>(null);
  const [formData, setFormData] = useState<ApplicationFormData>({
    candidate_name: "",
    candidate_email: "",
    candidate_phone: "",
    candidate_location: "",
    resume_url: ""
  });

  useEffect(() => {
    loadJob();
  }, [jobId]);

  async function loadJob() {
    try {
      // Public endpoint - no auth required
      const response = await fetch(`${API_URL}/api/ats/v1/jobs/${jobId}/public`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        if (response.status === 404) {
          setError("Job not found or no longer accepting applications");
        } else {
          const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
          setError(errorData.detail || `Failed to load job (${response.status})`);
        }
        setLoading(false);
        return;
      }

      const data = await response.json();
      setJob(data);
      setError(null);
    } catch (error) {
      console.error("Failed to load job:", error);
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        setError(`Cannot connect to backend server at ${API_URL}. Please ensure the backend is running.`);
      } else {
        setError(error instanceof Error ? error.message : "Cannot connect to server. Please try again later.");
      }
    } finally {
      setLoading(false);
    }
  }

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    const allowedExtensions = ['.pdf', '.doc', '.docx', '.txt'];
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!allowedExtensions.includes(fileExt) && !allowedTypes.includes(file.type)) {
      setError("Invalid file type. Please upload a PDF, DOC, DOCX, or TXT file.");
      return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError("File size exceeds 10MB limit. Please upload a smaller file.");
      return;
    }

    setResumeFile({ file });
    setError(null);
    // Clear resume_url if file is selected
    setFormData({ ...formData, resume_url: "" });
  }

  function handleRemoveFile() {
    setResumeFile(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setUploadProgress(0);

    try {
      // Create FormData for file upload
      const formDataToSend = new FormData();
      formDataToSend.append('candidate_name', formData.candidate_name);
      formDataToSend.append('candidate_email', formData.candidate_email);
      if (formData.candidate_phone) {
        formDataToSend.append('candidate_phone', formData.candidate_phone);
      }
      if (formData.candidate_location) {
        formDataToSend.append('candidate_location', formData.candidate_location);
      }
      
      // Add file if selected, otherwise add URL
      if (resumeFile) {
        formDataToSend.append('resume_file', resumeFile.file);
      } else if (formData.resume_url) {
        formDataToSend.append('resume_url', formData.resume_url);
      }

      // Simulate upload progress (since we can't track actual progress with fetch)
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 100);

      const response = await fetch(`${API_URL}/api/ats/v1/jobs/${jobId}/apply`, {
        method: 'POST',
        body: formDataToSend
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.ok) {
        setSubmitted(true);
        // Reset form
        setFormData({
          candidate_name: "",
          candidate_email: "",
          candidate_phone: "",
          candidate_location: "",
          resume_url: ""
        });
        setResumeFile(null);
        setUploadProgress(0);
      } else {
        const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
        setError(errorData.detail || "Failed to submit application. Please try again.");
        setUploadProgress(0);
      }
    } catch (error) {
      console.error("Failed to submit application:", error);
      setError("Failed to submit application. Please check your connection and try again.");
      setUploadProgress(0);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading job details...</p>
        </div>
      </main>
    );
  }

  if (error && !job) {
    return (
      <main className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center p-6">
        <div className="text-center max-w-md">
          <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
          <Link href="/" className="text-blue-600 dark:text-blue-400 hover:underline">
            Return to home
          </Link>
        </div>
      </main>
    );
  }

  if (!job || job.status !== 'OPEN') {
    return (
      <main className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center p-6">
        <div className="text-center max-w-md">
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            This job is no longer accepting applications.
          </p>
          <Link href="/" className="text-blue-600 dark:text-blue-400 hover:underline">
            Browse other opportunities
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-950 dark:to-indigo-950 py-12">
      <div className="max-w-5xl mx-auto px-6">
        <Link href="/" className="inline-flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 mb-6">
          <ArrowLeft className="h-5 w-5" />
          Back to Home
        </Link>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Job Details - Left Side */}
          <div className="lg:col-span-2 space-y-6">
            {/* Job Header */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
              <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-3">
                {job.title}
              </h1>
              {job.company_name && (
                <p className="text-2xl text-gray-600 dark:text-gray-400 mb-6">
                  {job.company_name}
                </p>
              )}

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
                  <Calendar className="h-5 w-5" />
                  <span>Posted {new Date(job.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>

            {/* Job Description */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
                Job Description
              </h2>
              <div className="prose dark:prose-invert max-w-none">
                <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                  {job.description}
                </p>
              </div>
            </div>
          </div>

          {/* Application Form - Right Side */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 sticky top-6">
              {submitted ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="text-center py-8"
                >
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/20 mb-4">
                    <CheckCircle2 className="h-8 w-8 text-green-600 dark:text-green-400" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                    Application Submitted!
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Thank you for your interest. We'll review your application and get back to you soon.
                  </p>
                  <button
                    onClick={() => setSubmitted(false)}
                    className="text-blue-600 dark:text-blue-400 hover:underline text-sm"
                  >
                    Apply to another position
                  </button>
                </motion.div>
              ) : (
                <>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">
                    Apply for this Position
                  </h2>

                  {error && (
                    <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                      <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
                    </div>
                  )}

                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Full Name *
                      </label>
                      <input
                        type="text"
                        required
                        value={formData.candidate_name}
                        onChange={(e) => setFormData({ ...formData, candidate_name: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="John Doe"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Email Address *
                      </label>
                      <input
                        type="email"
                        required
                        value={formData.candidate_email}
                        onChange={(e) => setFormData({ ...formData, candidate_email: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="john@example.com"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Phone Number
                      </label>
                      <input
                        type="tel"
                        value={formData.candidate_phone}
                        onChange={(e) => setFormData({ ...formData, candidate_phone: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="+1 (555) 123-4567"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Location
                      </label>
                      <input
                        type="text"
                        value={formData.candidate_location}
                        onChange={(e) => setFormData({ ...formData, candidate_location: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="City, State or Remote"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Resume/CV *
                      </label>
                      
                      {resumeFile ? (
                        <div className="border border-gray-300 dark:border-gray-600 rounded-lg p-4 bg-gray-50 dark:bg-gray-700/50">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                              <div>
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                  {resumeFile.file.name}
                                </p>
                                <p className="text-xs text-gray-500 dark:text-gray-400">
                                  {(resumeFile.file.size / 1024 / 1024).toFixed(2)} MB
                                </p>
                              </div>
                            </div>
                            <button
                              type="button"
                              onClick={handleRemoveFile}
                              className="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
                            >
                              <X className="h-5 w-5" />
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div>
                          <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 dark:border-gray-600 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                            <div className="flex flex-col items-center justify-center pt-5 pb-6">
                              <Upload className="w-8 h-8 mb-2 text-gray-500 dark:text-gray-400" />
                              <p className="mb-2 text-sm text-gray-500 dark:text-gray-400">
                                <span className="font-semibold">Click to upload</span> or drag and drop
                              </p>
                              <p className="text-xs text-gray-500 dark:text-gray-400">
                                PDF, DOC, DOCX, TXT (MAX. 10MB)
                              </p>
                            </div>
                            <input
                              type="file"
                              className="hidden"
                              accept=".pdf,.doc,.docx,.txt,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
                              onChange={handleFileSelect}
                            />
                          </label>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
                            Or provide a URL instead
                          </p>
                        </div>
                      )}
                      
                      {!resumeFile && (
                        <div className="mt-3">
                          <input
                            type="url"
                            value={formData.resume_url}
                            onChange={(e) => setFormData({ ...formData, resume_url: e.target.value })}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                            placeholder="https://linkedin.com/in/johndoe or Google Drive link"
                          />
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            Link to your resume, LinkedIn profile, or portfolio (optional if uploading file)
                          </p>
                        </div>
                      )}
                    </div>

                    {uploadProgress > 0 && uploadProgress < 100 && (
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${uploadProgress}%` }}
                        ></div>
                      </div>
                    )}

                    <motion.button
                      type="submit"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      disabled={submitting}
                      className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-6 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {submitting ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                          Submitting...
                        </>
                      ) : (
                        <>
                          <Send className="h-5 w-5" />
                          Submit Application
                        </>
                      )}
                    </motion.button>
                  </form>

                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-4 text-center">
                    By applying, you agree to our terms and privacy policy
                  </p>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

