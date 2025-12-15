"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  FileText,
  CheckCircle2,
  XCircle,
  Loader2,
  TrendingUp,
  TrendingDown,
  Award,
  Target,
  Lightbulb,
  Tag,
  X,
  Wand2,
  Sparkles,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { useAuth } from "@clerk/nextjs";
import Link from "next/link";

interface CVScores {
  content: number;
  formatting: number;
  keywords: number;
  experience: number;
  skills: number;
}

interface CVAnalysis {
  id: string;
  filename: string;
  status: string;
  overall_score?: number;
  ats_score?: number;
  scores_breakdown?: CVScores;
  strengths?: string[];
  weaknesses?: string[];
  suggestions?: string[];
  keywords_found?: string[];
  keywords_missing?: string[];
  created_at: string;
  completed_at?: string;
}

export default function CVAnalyzer() {
  const { getToken } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [targetJob, setTargetJob] = useState("");
  const [targetSeniority, setTargetSeniority] = useState("mid");
  const [uploading, setUploading] = useState(false);
  const [analysis, setAnalysis] = useState<CVAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploadCollapsed, setUploadCollapsed] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      const fileExt = selectedFile.name.split('.').pop()?.toLowerCase();
      
      if (!['pdf', 'docx', 'txt'].includes(fileExt || '')) {
        setError("Please upload a PDF, DOCX, or TXT file");
        return;
      }
      
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError("File size must be less than 10MB");
        return;
      }
      
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file");
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const token = await getToken();
      const formData = new FormData();
      formData.append("file", file);
      
      if (targetJob) {
        formData.append("target_job_title", targetJob);
      }
      
      formData.append("target_seniority", targetSeniority);

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/cv/upload`, {
        method: "POST",
        headers: {
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to upload CV");
      }

      const result: CVAnalysis = await response.json();
      setAnalysis(result);
      setFile(null);
    } catch (err: any) {
      setError(err.message || "Failed to analyze CV");
    } finally {
      setUploading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return "bg-green-100 border-green-200";
    if (score >= 60) return "bg-yellow-100 border-yellow-200";
    return "bg-red-100 border-red-200";
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-950 dark:to-indigo-950 pt-20 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
              CV Analyzer
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400">
              Get AI-powered insights and ATS compatibility scores for your resume
            </p>
          </div>

          {/* Upload Section - Compact */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 mb-8"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">Upload Your CV</h2>
              {analysis && (
                <button
                  onClick={() => setUploadCollapsed(!uploadCollapsed)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                >
                  {uploadCollapsed ? <ChevronDown className="h-5 w-5" /> : <ChevronUp className="h-5 w-5" />}
                </button>
              )}
            </div>

            <AnimatePresence>
              {!uploadCollapsed && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="overflow-hidden"
                >
                  <div className="grid md:grid-cols-3 gap-4">
                    {/* File Upload */}
                    <div className="md:col-span-1">
                      <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">
                        <FileText className="inline h-4 w-4 mr-1 text-blue-600" />
                        Resume File
                      </label>
                      <input
                        type="file"
                        accept=".pdf,.docx,.txt"
                        onChange={handleFileChange}
                        className="hidden"
                        id="cv-upload"
                      />
                      <label
                        htmlFor="cv-upload"
                        className="flex items-center justify-center w-full px-3 py-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:border-blue-500 transition-colors bg-gray-50 dark:bg-gray-700/50 hover:bg-blue-50 dark:hover:bg-blue-900/20"
                      >
                        <div className="text-center">
                          <Upload className="mx-auto h-8 w-8 text-gray-400 mb-1" />
                          <p className="text-xs text-gray-600 dark:text-gray-400">
                            {file ? (file.name.length > 20 ? file.name.substring(0, 20) + "..." : file.name) : "Click to upload"}
                          </p>
                          <p className="text-xs text-gray-500 mt-0.5">Max 10MB</p>
                        </div>
                      </label>
                    </div>

                    {/* Target Job */}
                    <div className="md:col-span-1">
                      <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">
                        <Target className="inline h-4 w-4 mr-1 text-blue-600" />
                        Target Job (Optional)
                      </label>
                      <input
                        type="text"
                        value={targetJob}
                        onChange={(e) => setTargetJob(e.target.value)}
                        placeholder="e.g., Software Engineer"
                        className="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-700 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all outline-none text-sm text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700"
                      />
                    </div>

                    {/* Seniority & Button */}
                    <div className="md:col-span-1 space-y-2">
                      <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">
                        Seniority Level
                      </label>
                      <div className="grid grid-cols-3 gap-2 mb-2">
                        {["junior", "mid", "senior"].map((level) => (
                          <button
                            key={level}
                            type="button"
                            onClick={() => setTargetSeniority(level)}
                            className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                              targetSeniority === level
                                ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md"
                                : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                            }`}
                          >
                            {level.charAt(0).toUpperCase() + level.slice(1)}
                          </button>
                        ))}
                      </div>
                      <motion.button
                        type="button"
                        onClick={handleUpload}
                        disabled={uploading || !file}
                        whileHover={{ scale: uploading || !file ? 1 : 1.02 }}
                        whileTap={{ scale: uploading || !file ? 1 : 0.98 }}
                        className={`w-full py-2.5 rounded-lg font-semibold text-sm shadow-lg transition-all flex items-center justify-center gap-2 ${
                          uploading || !file
                            ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                            : "bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white"
                        }`}
                      >
                        {uploading ? (
                          <>
                            <Loader2 className="h-4 w-4 animate-spin" />
                            Analyzing...
                          </>
                        ) : (
                          <>
                            <Upload className="h-4 w-4" />
                            Analyze
                          </>
                        )}
                      </motion.button>
                    </div>
                  </div>

                  {/* Error Message */}
                  {error && (
                    <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-2">
                      <XCircle className="h-4 w-4 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                      <p className="text-red-800 dark:text-red-300 text-xs">{error}</p>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          {/* Results Section */}
          <AnimatePresence mode="wait">
            {analysis ? (
              <div className="space-y-6">
                {/* Ready to Improve Section - Prominent at Top */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="bg-gradient-to-br from-purple-50 via-pink-50 to-indigo-50 dark:from-purple-900/20 dark:via-pink-900/20 dark:to-indigo-900/20 rounded-2xl shadow-xl p-6 border-2 border-purple-200 dark:border-purple-700"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl">
                        <Wand2 className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                          Ready to Improve Your CV?
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Apply all suggestions and rewrite professionally
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => setAnalysis(null)}
                      className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
                    >
                      <X className="h-5 w-5" />
                    </button>
                  </div>

                  <div className="grid md:grid-cols-2 gap-3">
                    <Link href={`/cv/improve/${analysis.id}`}>
                      <motion.div
                        whileHover={{ scale: 1.02 }}
                        className="p-4 bg-white dark:bg-gray-800 border-2 border-purple-300 dark:border-purple-600 rounded-xl hover:border-purple-500 dark:hover:border-purple-500 hover:shadow-lg transition-all cursor-pointer"
                      >
                        <div className="flex items-center gap-2 mb-1.5">
                          <Target className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                          <div className="font-bold text-sm text-gray-900 dark:text-gray-100">🎯 ATS Optimized</div>
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                          Best for online applications
                        </div>
                        <div className="text-xs text-purple-600 dark:text-purple-400">
                          Fix weaknesses • Add keywords • Boost ATS score
                        </div>
                      </motion.div>
                    </Link>

                    <Link href={`/rewriter?from_analysis=${analysis.id}`}>
                      <motion.div
                        whileHover={{ scale: 1.02 }}
                        className="p-4 bg-white dark:bg-gray-800 border-2 border-pink-300 dark:border-pink-600 rounded-xl hover:border-pink-500 dark:hover:border-pink-500 hover:shadow-lg transition-all cursor-pointer"
                      >
                        <div className="flex items-center gap-2 mb-1.5">
                          <Sparkles className="h-4 w-4 text-pink-600 dark:text-pink-400" />
                          <div className="font-bold text-sm text-gray-900 dark:text-gray-100">✨ Choose Style</div>
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                          Modern, Minimal, or Executive
                        </div>
                        <div className="text-xs text-pink-600 dark:text-pink-400">
                          4 professional styles • Job tailored • Download ready
                        </div>
                      </motion.div>
                    </Link>
                  </div>
                </motion.div>

                {/* Scores Card - Compact */}
                <motion.div
                  key="results"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 20 }}
                  className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6"
                >
                  <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">Analysis Results</h2>

                  {analysis.overall_score !== undefined && (
                    <div className="grid grid-cols-2 gap-4 mb-6">
                      <div className={`p-4 rounded-xl border-2 ${getScoreBgColor(analysis.overall_score)}`}>
                        <Award className={`h-6 w-6 mb-2 ${getScoreColor(analysis.overall_score)}`} />
                        <div className={`text-3xl font-bold mb-1 ${getScoreColor(analysis.overall_score)}`}>
                          {analysis.overall_score}
                        </div>
                        <div className="text-xs font-medium text-gray-600 dark:text-gray-400">Overall Score</div>
                      </div>

                      {analysis.ats_score !== undefined && (
                        <div className={`p-4 rounded-xl border-2 ${getScoreBgColor(analysis.ats_score)}`}>
                          <Target className={`h-6 w-6 mb-2 ${getScoreColor(analysis.ats_score)}`} />
                          <div className={`text-3xl font-bold mb-1 ${getScoreColor(analysis.ats_score)}`}>
                            {analysis.ats_score}
                          </div>
                          <div className="text-xs font-medium text-gray-600 dark:text-gray-400">ATS Score</div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Detailed Scores */}
                  {analysis.scores_breakdown && (
                    <div className="space-y-2.5">
                      {Object.entries(analysis.scores_breakdown).map(([key, value]) => (
                        <div key={key}>
                          <div className="flex justify-between items-center mb-1">
                            <span className="text-xs font-medium text-gray-700 dark:text-gray-300 capitalize">
                              {key}
                            </span>
                            <span className={`text-xs font-bold ${getScoreColor(value)}`}>
                              {value}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                            <div
                              className={`h-1.5 rounded-full transition-all duration-500 ${
                                value >= 80
                                  ? "bg-green-500"
                                  : value >= 60
                                  ? "bg-yellow-500"
                                  : "bg-red-500"
                              }`}
                              style={{ width: `${value}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </motion.div>

                {/* Insights Grid - Compact */}
                <div className="grid md:grid-cols-2 gap-4">
                  {/* Strengths */}
                  {analysis.strengths && analysis.strengths.length > 0 && (
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-5">
                      <h3 className="text-lg font-bold mb-3 flex items-center gap-2 text-green-600 dark:text-green-400">
                        <TrendingUp className="h-5 w-5" />
                        Strengths
                      </h3>
                      <ul className="space-y-1.5">
                        {analysis.strengths.slice(0, 4).map((strength, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                            <span className="text-sm text-gray-700 dark:text-gray-300">{strength}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Weaknesses */}
                  {analysis.weaknesses && analysis.weaknesses.length > 0 && (
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-5">
                      <h3 className="text-lg font-bold mb-3 flex items-center gap-2 text-orange-600 dark:text-orange-400">
                        <TrendingDown className="h-5 w-5" />
                        Areas for Improvement
                      </h3>
                      <ul className="space-y-1.5">
                        {analysis.weaknesses.slice(0, 4).map((weakness, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <XCircle className="h-4 w-4 text-orange-600 dark:text-orange-400 flex-shrink-0 mt-0.5" />
                            <span className="text-sm text-gray-700 dark:text-gray-300">{weakness}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Keywords - Compact */}
                {(analysis.keywords_found || analysis.keywords_missing) && (
                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-5">
                    <h3 className="text-lg font-bold mb-3 flex items-center gap-2 text-indigo-600 dark:text-indigo-400">
                      <Tag className="h-5 w-5" />
                      Keywords
                    </h3>
                    
                    {analysis.keywords_found && analysis.keywords_found.length > 0 && (
                      <div className="mb-3">
                        <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">Found:</p>
                        <div className="flex flex-wrap gap-1.5">
                          {analysis.keywords_found.slice(0, 10).map((keyword, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full text-xs"
                            >
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {analysis.keywords_missing && analysis.keywords_missing.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">Missing:</p>
                        <div className="flex flex-wrap gap-1.5">
                          {analysis.keywords_missing.slice(0, 10).map((keyword, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-full text-xs"
                            >
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <motion.div
                key="placeholder"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="bg-white dark:bg-gray-800/60 backdrop-blur-sm rounded-2xl border-2 border-dashed border-gray-300 dark:border-gray-600 p-12 flex flex-col items-center justify-center text-center"
              >
                <FileText className="h-20 w-20 text-gray-300 dark:text-gray-600 mb-4" />
                <h3 className="text-lg font-semibold text-gray-600 dark:text-gray-400 mb-2">
                  Upload a CV to see results
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-500">
                  Get instant AI-powered analysis and actionable insights
                </p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Suggestions Section - Full Width */}
          {analysis && analysis.suggestions && analysis.suggestions.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="mt-6 bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl">
                  <Lightbulb className="h-5 w-5 text-white" />
                </div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                  Career Recommendations
                </h2>
              </div>

              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
                {analysis.suggestions.map((suggestion: string, idx: number) => {
                  // Categorize suggestions
                  const isCert = /certif|certificate|credential|license/i.test(suggestion);
                  const isStudy = /course|training|education|learn|study|degree|program/i.test(suggestion);
                  const isExp = /experience|project|role|position|internship|work/i.test(suggestion);
                  
                  let icon = <Target className="h-4 w-4 text-blue-600 dark:text-blue-400 flex-shrink-0" />;
                  let bgColor = "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800";
                  
                  if (isCert) {
                    icon = <Award className="h-4 w-4 text-purple-600 dark:text-purple-400 flex-shrink-0" />;
                    bgColor = "bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800";
                  } else if (isStudy) {
                    icon = <FileText className="h-4 w-4 text-indigo-600 dark:text-indigo-400 flex-shrink-0" />;
                    bgColor = "bg-indigo-50 dark:bg-indigo-900/20 border-indigo-200 dark:border-indigo-800";
                  } else if (isExp) {
                    icon = <TrendingUp className="h-4 w-4 text-emerald-600 dark:text-emerald-400 flex-shrink-0" />;
                    bgColor = "bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800";
                  }
                  
                  return (
                    <div key={idx} className={`flex items-start gap-2 p-3 rounded-lg border ${bgColor}`}>
                      <div className="mt-0.5">{icon}</div>
                      <span className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{suggestion}</span>
                    </div>
                  );
                })}
              </div>
            </motion.div>
          )}
        </motion.div>
      </div>
    </main>
  );
}

