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
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 pt-20">
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
            <p className="text-xl text-gray-600">
              Get AI-powered insights and ATS compatibility scores for your resume
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            {/* Upload Section */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-2xl shadow-2xl p-8"
            >
              <h2 className="text-2xl font-bold mb-6 text-gray-900">Upload Your CV</h2>

              {/* File Upload */}
              <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  <FileText className="inline h-5 w-5 mr-2 text-blue-600" />
                  Resume File (PDF, DOCX, TXT)
                </label>
                <div className="relative">
                  <input
                    type="file"
                    accept=".pdf,.docx,.txt"
                    onChange={handleFileChange}
                    className="hidden"
                    id="cv-upload"
                  />
                  <label
                    htmlFor="cv-upload"
                    className="flex items-center justify-center w-full px-4 py-8 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 transition-colors bg-gray-50 hover:bg-blue-50"
                  >
                    <div className="text-center">
                      <Upload className="mx-auto h-12 w-12 text-gray-400 mb-2" />
                      <p className="text-sm text-gray-600">
                        {file ? file.name : "Click to upload or drag and drop"}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Max 10MB • PDF, DOCX, or TXT
                      </p>
                    </div>
                  </label>
                </div>
              </div>

              {/* Target Job */}
              <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  <Target className="inline h-5 w-5 mr-2 text-blue-600" />
                  Target Job Title (Optional)
                </label>
                <input
                  type="text"
                  value={targetJob}
                  onChange={(e) => setTargetJob(e.target.value)}
                  placeholder="e.g., Software Engineer, Product Manager"
                  className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all outline-none text-gray-900"
                />
              </div>

              {/* Target Seniority */}
              <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Seniority Level
                </label>
                <div className="grid grid-cols-3 gap-4">
                  {["junior", "mid", "senior"].map((level) => (
                    <button
                      key={level}
                      type="button"
                      onClick={() => setTargetSeniority(level)}
                      className={`px-6 py-3 rounded-lg font-medium transition-all duration-300 ${
                        targetSeniority === level
                          ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg scale-105"
                          : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      }`}
                    >
                      {level.charAt(0).toUpperCase() + level.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                  <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}

              {/* Upload Button */}
              <motion.button
                type="button"
                onClick={handleUpload}
                disabled={uploading || !file}
                whileHover={{ scale: uploading || !file ? 1 : 1.02 }}
                whileTap={{ scale: uploading || !file ? 1 : 0.98 }}
                className={`w-full py-4 rounded-lg font-semibold text-lg shadow-xl transition-all duration-300 flex items-center justify-center gap-2 ${
                  uploading || !file
                    ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                    : "bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white hover:shadow-2xl"
                }`}
              >
                {uploading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Upload className="h-5 w-5" />
                    Analyze CV
                  </>
                )}
              </motion.button>
            </motion.div>

            {/* Results Section */}
            <AnimatePresence mode="wait">
              {analysis ? (
                <motion.div
                  key="results"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="space-y-6"
                >
                  {/* Overall Scores */}
                  <div className="bg-white rounded-2xl shadow-2xl p-8">
                    <div className="flex items-center justify-between mb-6">
                      <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
                      <button
                        onClick={() => setAnalysis(null)}
                        className="text-gray-400 hover:text-gray-600 transition-colors"
                      >
                        <X className="h-6 w-6" />
                      </button>
                    </div>

                    {analysis.overall_score !== undefined && (
                      <div className="grid grid-cols-2 gap-6 mb-8">
                        <div className={`p-6 rounded-xl border-2 ${getScoreBgColor(analysis.overall_score)}`}>
                          <Award className={`h-8 w-8 mb-2 ${getScoreColor(analysis.overall_score)}`} />
                          <div className={`text-4xl font-bold mb-1 ${getScoreColor(analysis.overall_score)}`}>
                            {analysis.overall_score}
                          </div>
                          <div className="text-sm font-medium text-gray-600">Overall Score</div>
                        </div>

                        {analysis.ats_score !== undefined && (
                          <div className={`p-6 rounded-xl border-2 ${getScoreBgColor(analysis.ats_score)}`}>
                            <Target className={`h-8 w-8 mb-2 ${getScoreColor(analysis.ats_score)}`} />
                            <div className={`text-4xl font-bold mb-1 ${getScoreColor(analysis.ats_score)}`}>
                              {analysis.ats_score}
                            </div>
                            <div className="text-sm font-medium text-gray-600">ATS Score</div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Detailed Scores */}
                    {analysis.scores_breakdown && (
                      <div className="space-y-3">
                        {Object.entries(analysis.scores_breakdown).map(([key, value]) => (
                          <div key={key}>
                            <div className="flex justify-between items-center mb-1">
                              <span className="text-sm font-medium text-gray-700 capitalize">
                                {key}
                              </span>
                              <span className={`text-sm font-bold ${getScoreColor(value)}`}>
                                {value}%
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full transition-all duration-500 ${
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
                  </div>

                  {/* Strengths */}
                  {analysis.strengths && analysis.strengths.length > 0 && (
                    <div className="bg-white rounded-2xl shadow-2xl p-8">
                      <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-green-600">
                        <TrendingUp className="h-6 w-6" />
                        Strengths
                      </h3>
                      <ul className="space-y-2">
                        {analysis.strengths.map((strength, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                            <span className="text-gray-700">{strength}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Weaknesses */}
                  {analysis.weaknesses && analysis.weaknesses.length > 0 && (
                    <div className="bg-white rounded-2xl shadow-2xl p-8">
                      <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-orange-600">
                        <TrendingDown className="h-6 w-6" />
                        Areas for Improvement
                      </h3>
                      <ul className="space-y-2">
                        {analysis.weaknesses.map((weakness, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <XCircle className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
                            <span className="text-gray-700">{weakness}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Suggestions */}
                  {analysis.suggestions && analysis.suggestions.length > 0 && (
                    <div className="bg-white rounded-2xl shadow-2xl p-8">
                      <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-blue-600">
                        <Lightbulb className="h-6 w-6" />
                        Suggestions
                      </h3>
                      <ul className="space-y-2">
                        {analysis.suggestions.map((suggestion, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-blue-100 text-blue-600 text-sm font-bold flex-shrink-0">
                              {idx + 1}
                            </span>
                            <span className="text-gray-700">{suggestion}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Keywords */}
                  {(analysis.keywords_found || analysis.keywords_missing) && (
                    <div className="bg-white rounded-2xl shadow-2xl p-8">
                      <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-indigo-600">
                        <Tag className="h-6 w-6" />
                        Keywords
                      </h3>
                      
                      {analysis.keywords_found && analysis.keywords_found.length > 0 && (
                        <div className="mb-4">
                          <p className="text-sm font-medium text-gray-700 mb-2">Found:</p>
                          <div className="flex flex-wrap gap-2">
                            {analysis.keywords_found.map((keyword, idx) => (
                              <span
                                key={idx}
                                className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm"
                              >
                                {keyword}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {analysis.keywords_missing && analysis.keywords_missing.length > 0 && (
                        <div>
                          <p className="text-sm font-medium text-gray-700 mb-2">Missing:</p>
                          <div className="flex flex-wrap gap-2">
                            {analysis.keywords_missing.map((keyword, idx) => (
                              <span
                                key={idx}
                                className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm"
                              >
                                {keyword}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Improve CV Section - NEW */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl shadow-2xl p-8 border-2 border-purple-200"
                  >
                    <div className="flex items-center gap-3 mb-4">
                      <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl">
                        <Wand2 className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-2xl font-bold text-gray-900">
                          Ready to Improve Your CV?
                        </h3>
                        <p className="text-gray-600">
                          Let AI apply all suggestions and rewrite your CV professionally
                        </p>
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4 mb-6">
                      <Link href={`/cv/improve/${analysis.id}`}>
                        <motion.div
                          whileHover={{ scale: 1.02 }}
                          className="p-5 bg-white border-2 border-purple-300 rounded-xl hover:border-purple-500 hover:shadow-lg transition-all cursor-pointer group"
                        >
                          <div className="flex items-center gap-2 mb-2">
                            <Target className="h-5 w-5 text-purple-600" />
                            <div className="font-bold text-gray-900">🎯 ATS Optimized</div>
                          </div>
                          <div className="text-sm text-gray-600">
                            Best for online applications
                          </div>
                          <div className="mt-3 text-xs text-purple-600 group-hover:text-purple-700">
                            Fix weaknesses • Add keywords • Boost ATS score
                          </div>
                        </motion.div>
                      </Link>

                      <Link href={`/rewriter?from_analysis=${analysis.id}`}>
                        <motion.div
                          whileHover={{ scale: 1.02 }}
                          className="p-5 bg-white border-2 border-pink-300 rounded-xl hover:border-pink-500 hover:shadow-lg transition-all cursor-pointer group"
                        >
                          <div className="flex items-center gap-2 mb-2">
                            <Sparkles className="h-5 w-5 text-pink-600" />
                            <div className="font-bold text-gray-900">✨ Choose Style</div>
                          </div>
                          <div className="text-sm text-gray-600">
                            Modern, Minimal, or Executive
                          </div>
                          <div className="mt-3 text-xs text-pink-600 group-hover:text-pink-700">
                            4 professional styles • Job tailored • Download ready
                          </div>
                        </motion.div>
                      </Link>
                    </div>

                    <div className="bg-purple-100/50 rounded-lg p-4 border border-purple-200">
                      <div className="flex items-start gap-3">
                        <Lightbulb className="h-5 w-5 text-purple-600 flex-shrink-0 mt-0.5" />
                        <div className="text-sm text-gray-700">
                          <span className="font-semibold">Pro Tip:</span> The comparison view shows before/after changes,
                          while the rewriter gives you full control over style and formatting.
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </motion.div>
              ) : (
                <motion.div
                  key="placeholder"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="bg-white/60 backdrop-blur-sm rounded-2xl border-2 border-dashed border-gray-300 p-12 flex flex-col items-center justify-center text-center"
                >
                  <FileText className="h-24 w-24 text-gray-300 mb-4" />
                  <h3 className="text-xl font-semibold text-gray-600 mb-2">
                    Upload a CV to see results
                  </h3>
                  <p className="text-gray-500">
                    Get instant AI-powered analysis and actionable insights
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </div>
    </main>
  );
}

