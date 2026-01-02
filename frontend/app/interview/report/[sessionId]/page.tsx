"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { motion } from "framer-motion";
import {
  Award,
  TrendingUp,
  TrendingDown,
  CheckCircle2,
  Target,
  Briefcase,
  Home,
  Loader2,
  AlertCircle,
  Clock,
} from "lucide-react";
import Link from "next/link";
import { finishInterview, type InterviewSummary } from "@/lib/api";

export default function InterviewReport() {
  const router = useRouter();
  const params = useParams();
  const { getToken } = useAuth();
  const sessionId = params.sessionId as string;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<InterviewSummary | null>(null);
  const [reportStatus, setReportStatus] = useState<string>("unknown");
  const [questionsCompleted, setQuestionsCompleted] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);

  useEffect(() => {
    const loadReport = async () => {
      try {
        const token = await getToken();
        
        // Try new report endpoint first
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/interview/session/${sessionId}/report`,
          {
            headers: token ? { Authorization: `Bearer ${token}` } : {}
          }
        );
        
        if (!response.ok) {
          // Fallback to old finish endpoint
          const fallbackResponse = await finishInterview(sessionId, token);
          setSummary(fallbackResponse.summary);
          setReportStatus("completed");
          setTotalQuestions(fallbackResponse.summary?.total_questions || 0);
          setQuestionsCompleted(fallbackResponse.summary?.questions_completed || 0);
        } else {
          const data = await response.json();
          
          if (data.summary) {
            setSummary(data.summary);
            setReportStatus(data.status || "completed");
            setQuestionsCompleted(data.questions_completed || 0);
            setTotalQuestions(data.total_questions || 0);
          } else {
            setError(data.message || "Not enough data for report yet");
          }
        }
        
        setLoading(false);
      } catch (err: any) {
        setError(err.message || "Failed to load report");
        setLoading(false);
      }
    };

    loadReport();
  }, [sessionId, getToken]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center pt-20">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Generating your report...</p>
        </div>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center pt-20">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md">
          <p className="text-red-600 mb-4">{error || "No report data found"}</p>
          <Link href="/interview/setup">
            <button className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-lg font-medium w-full">
              Start New Interview
            </button>
          </Link>
        </div>
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return "from-green-500 to-emerald-600";
    if (score >= 70) return "from-blue-500 to-indigo-600";
    if (score >= 60) return "from-yellow-500 to-orange-600";
    return "from-orange-500 to-red-600";
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return "Excellent";
    if (score >= 70) return "Good";
    if (score >= 60) return "Fair";
    return "Needs Improvement";
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 pt-20 pb-12">
      <div className="max-w-5xl mx-auto px-6 py-12">
        {/* Completion Status Banner */}
        {(reportStatus === "in_progress" || questionsCompleted < totalQuestions) && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-xl p-6"
          >
            <div className="flex items-start gap-4">
              <AlertCircle className="h-6 w-6 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-lg font-semibold text-yellow-900 dark:text-yellow-100 mb-2">
                  Partial Interview Report
                </h3>
                <p className="text-yellow-800 dark:text-yellow-200 text-sm mb-2">
                  You completed <strong>{questionsCompleted} out of {totalQuestions}</strong> questions before leaving.
                  This report reflects your performance up to that point.
                </p>
                <div className="flex items-center gap-2 text-yellow-700 dark:text-yellow-300 text-sm">
                  <Clock className="h-4 w-4" />
                  <span>Complete the full interview for a comprehensive evaluation</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
        
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 mb-6">
            <Award className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent">
            Interview Report
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            {reportStatus === "completed" && questionsCompleted === totalQuestions 
              ? "Here's your comprehensive performance analysis"
              : "Here's your performance analysis so far"}
          </p>
        </motion.div>

        {/* Overall Score Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-12 mb-8 text-center"
        >
          <p className="text-gray-600 dark:text-gray-400 mb-2">Overall Score</p>
          <div className="relative inline-block">
            <svg className="w-40 h-40 transform -rotate-90">
              <circle
                cx="80"
                cy="80"
                r="70"
                stroke="#e5e7eb"
                strokeWidth="12"
                fill="none"
                className="dark:stroke-gray-700"
              />
              <circle
                cx="80"
                cy="80"
                r="70"
                stroke="url(#gradient)"
                strokeWidth="12"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 70}`}
                strokeDashoffset={`${
                  2 * Math.PI * 70 * (1 - summary.overall_score / 100)
                }`}
                strokeLinecap="round"
              />
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#4f46e5" />
                </linearGradient>
              </defs>
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <div>
                <p className="text-5xl font-bold text-gray-900 dark:text-gray-100">
                  {summary.overall_score}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">/ 100</p>
              </div>
            </div>
          </div>
          <p
            className={`mt-4 text-2xl font-bold bg-gradient-to-r ${getScoreColor(
              summary.overall_score
            )} bg-clip-text text-transparent`}
          >
            {getScoreLabel(summary.overall_score)}
          </p>
          {questionsCompleted < totalQuestions && (
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              Based on {questionsCompleted} of {totalQuestions} questions
            </p>
          )}
        </motion.div>

        {/* Strengths */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
            <div className="inline-flex p-2 rounded-xl bg-gradient-to-r from-green-500 to-emerald-600">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
            Your Strengths
          </h2>
          <ul className="space-y-3">
            {summary.strengths.map((strength, index) => (
              <motion.li
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                className="flex items-start gap-3"
              >
                <CheckCircle2 className="h-6 w-6 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                <span className="text-gray-700 dark:text-gray-300 leading-relaxed">{strength}</span>
              </motion.li>
            ))}
          </ul>
        </motion.div>

        {/* Weaknesses */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
            <div className="inline-flex p-2 rounded-xl bg-gradient-to-r from-orange-500 to-red-600">
              <TrendingDown className="h-6 w-6 text-white" />
            </div>
            Areas for Improvement
          </h2>
          <ul className="space-y-3">
            {summary.weaknesses.map((weakness, index) => (
              <motion.li
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + index * 0.1 }}
                className="flex items-start gap-3"
              >
                <Target className="h-6 w-6 text-orange-600 dark:text-orange-400 flex-shrink-0 mt-0.5" />
                <span className="text-gray-700 dark:text-gray-300 leading-relaxed">{weakness}</span>
              </motion.li>
            ))}
          </ul>
        </motion.div>

        {/* Action Plan */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-2xl shadow-xl p-8 mb-8 border border-blue-100 dark:border-blue-800"
        >
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
            <div className="inline-flex p-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600">
              <CheckCircle2 className="h-6 w-6 text-white" />
            </div>
            Your Action Plan
          </h2>
          <ul className="space-y-3">
            {summary.action_plan.map((action, index) => (
              <motion.li
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                className="flex items-start gap-3"
              >
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-600 dark:bg-blue-500 text-white flex items-center justify-center text-sm font-bold mt-0.5">
                  {index + 1}
                </div>
                <span className="text-gray-700 dark:text-gray-300 leading-relaxed">{action}</span>
              </motion.li>
            ))}
          </ul>
        </motion.div>

        {/* Suggested Roles */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
            <div className="inline-flex p-2 rounded-xl bg-gradient-to-r from-purple-500 to-pink-600">
              <Briefcase className="h-6 w-6 text-white" />
            </div>
            Recommended Roles
          </h2>
          <div className="flex flex-wrap gap-3">
            {summary.suggested_roles.map((role, index) => (
              <motion.span
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.6 + index * 0.1 }}
                className="px-4 py-2 bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 text-purple-800 dark:text-purple-300 rounded-full font-medium"
              >
                {role}
              </motion.span>
            ))}
          </div>
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="flex flex-col sm:flex-row gap-4"
        >
          <Link href="/interview/setup" className="flex-1">
            <button className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-8 py-4 rounded-lg font-semibold text-lg shadow-xl hover:shadow-2xl transition-all duration-300">
              Start New Interview
            </button>
          </Link>
          <Link href="/" className="flex-1">
            <button className="w-full bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-600 px-8 py-4 rounded-lg font-semibold text-lg shadow-md hover:shadow-lg transition-all duration-300 flex items-center justify-center gap-2">
              <Home className="h-5 w-5" />
              Back to Home
            </button>
          </Link>
        </motion.div>
      </div>
    </main>
  );
}

