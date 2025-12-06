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

  useEffect(() => {
    const loadReport = async () => {
      try {
        const token = await getToken();
        const response = await finishInterview(sessionId, token);
        setSummary(response.summary);
        setLoading(false);
      } catch (err: any) {
        setError(err.message || "Failed to load report");
        setLoading(false);
      }
    };

    loadReport();
  }, [sessionId]);

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
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 pt-20 pb-12">
      <div className="max-w-5xl mx-auto px-6 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 mb-6">
            <Award className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
            Interview Report
          </h1>
          <p className="text-xl text-gray-600">
            Here's your comprehensive performance analysis
          </p>
        </motion.div>

        {/* Overall Score Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl shadow-2xl p-12 mb-8 text-center"
        >
          <p className="text-gray-600 mb-2">Overall Score</p>
          <div className="relative inline-block">
            <svg className="w-40 h-40 transform -rotate-90">
              <circle
                cx="80"
                cy="80"
                r="70"
                stroke="#e5e7eb"
                strokeWidth="12"
                fill="none"
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
                <p className="text-5xl font-bold text-gray-900">
                  {summary.overall_score}
                </p>
                <p className="text-sm text-gray-500">/ 100</p>
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
        </motion.div>

        {/* Strengths */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-2xl shadow-xl p-8 mb-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
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
                <CheckCircle2 className="h-6 w-6 text-green-600 flex-shrink-0 mt-0.5" />
                <span className="text-gray-700 leading-relaxed">{strength}</span>
              </motion.li>
            ))}
          </ul>
        </motion.div>

        {/* Weaknesses */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-2xl shadow-xl p-8 mb-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
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
                <Target className="h-6 w-6 text-orange-600 flex-shrink-0 mt-0.5" />
                <span className="text-gray-700 leading-relaxed">{weakness}</span>
              </motion.li>
            ))}
          </ul>
        </motion.div>

        {/* Action Plan */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl shadow-xl p-8 mb-8 border border-blue-100"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
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
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold mt-0.5">
                  {index + 1}
                </div>
                <span className="text-gray-700 leading-relaxed">{action}</span>
              </motion.li>
            ))}
          </ul>
        </motion.div>

        {/* Suggested Roles */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white rounded-2xl shadow-xl p-8 mb-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
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
                className="px-4 py-2 bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800 rounded-full font-medium"
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
            <button className="w-full bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 px-8 py-4 rounded-lg font-semibold text-lg shadow-md hover:shadow-lg transition-all duration-300 flex items-center justify-center gap-2">
              <Home className="h-5 w-5" />
              Back to Home
            </button>
          </Link>
        </motion.div>
      </div>
    </main>
  );
}

