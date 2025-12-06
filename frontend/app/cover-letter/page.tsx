"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Mail,
  Wand2,
  Loader2,
  Copy,
  Download,
  CheckCircle2,
  Building2,
  Briefcase,
  X,
} from "lucide-react";
import { useAuth } from "@clerk/nextjs";

interface CoverLetterResult {
  id: string;
  cover_letter_text: string;
  matching_skills: string[];
  key_highlights: string[];
  tone: string;
}

export default function CoverLetterGenerator() {
  const { getToken } = useAuth();
  const [cvText, setCvText] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [selectedTone, setSelectedTone] = useState("professional");
  const [additionalInfo, setAdditionalInfo] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CoverLetterResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const tones = [
    { 
      id: "formal", 
      name: "Formal", 
      description: "Traditional business language",
      icon: "🎩"
    },
    { 
      id: "smart", 
      name: "Smart", 
      description: "Intelligent and insightful",
      icon: "🧠"
    },
    { 
      id: "professional", 
      name: "Professional", 
      description: "Standard business tone",
      icon: "💼"
    },
    { 
      id: "friendly", 
      name: "Friendly", 
      description: "Warm and personable",
      icon: "😊"
    },
  ];

  const handleGenerate = async () => {
    if (!cvText.trim() || !jobTitle.trim() || !companyName.trim()) {
      setError("Please fill in CV, job title, and company name");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const token = await getToken();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/rewriter/cover-letter`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token && { Authorization: `Bearer ${token}` }),
          },
          body: JSON.stringify({
            cv_text: cvText,
            job_title: jobTitle,
            company_name: companyName,
            job_description: jobDescription || null,
            tone: selectedTone,
            additional_info: additionalInfo || null,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to generate cover letter");
      }

      const data: CoverLetterResult = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to generate cover letter");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (result?.cover_letter_text) {
      navigator.clipboard.writeText(result.cover_letter_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    if (result?.cover_letter_text) {
      const blob = new Blob([result.cover_letter_text], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `cover-letter-${companyName.replace(/\s+/g, "-")}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50 pt-20">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-full shadow-lg border border-cyan-100 mb-6">
              <Mail className="h-4 w-4 text-cyan-600" />
              <span className="text-sm font-medium text-gray-700">AI-Generated</span>
            </div>
            <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-cyan-600 to-teal-600 bg-clip-text text-transparent">
              Cover Letter Generator
            </h1>
            <p className="text-xl text-gray-600">
              Create personalized cover letters that highlight your matching skills
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            {/* Input Section */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="space-y-6"
            >
              {/* Job Details */}
              <div className="bg-white rounded-2xl shadow-2xl p-8">
                <h2 className="text-2xl font-bold mb-6 text-gray-900">Job Details</h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      <Briefcase className="inline h-4 w-4 mr-2 text-cyan-600" />
                      Job Title *
                    </label>
                    <input
                      type="text"
                      value={jobTitle}
                      onChange={(e) => setJobTitle(e.target.value)}
                      placeholder="e.g., Senior Software Engineer"
                      className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 transition-all outline-none text-gray-900"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      <Building2 className="inline h-4 w-4 mr-2 text-cyan-600" />
                      Company Name *
                    </label>
                    <input
                      type="text"
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      placeholder="e.g., Tech Corp"
                      className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 transition-all outline-none text-gray-900"
                      required
                    />
                  </div>
                </div>
              </div>

              {/* CV Input */}
              <div className="bg-white rounded-2xl shadow-2xl p-8">
                <h3 className="text-lg font-bold mb-4 text-gray-900">Your CV *</h3>
                
                <textarea
                  value={cvText}
                  onChange={(e) => setCvText(e.target.value)}
                  placeholder="Paste your CV here..."
                  className="w-full h-48 px-4 py-3 border border-gray-200 rounded-lg focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 transition-all outline-none text-gray-900 resize-none"
                />
              </div>

              {/* Job Description (Optional) */}
              <div className="bg-white rounded-2xl shadow-2xl p-8">
                <h3 className="text-lg font-bold mb-4 text-gray-900">
                  Job Description (Optional)
                </h3>
                
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the job description to highlight matching skills..."
                  className="w-full h-32 px-4 py-3 border border-gray-200 rounded-lg focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 transition-all outline-none text-gray-900 resize-none"
                />
              </div>

              {/* Tone Selection */}
              <div className="bg-white rounded-2xl shadow-2xl p-8">
                <h3 className="text-lg font-bold mb-4 text-gray-900">
                  Select Tone
                </h3>
                
                <div className="grid grid-cols-2 gap-4">
                  {tones.map((tone) => (
                    <button
                      key={tone.id}
                      onClick={() => setSelectedTone(tone.id)}
                      className={`p-4 rounded-xl border-2 transition-all duration-300 text-left ${
                        selectedTone === tone.id
                          ? "border-cyan-600 bg-cyan-50 shadow-lg scale-105"
                          : "border-gray-200 hover:border-cyan-300 hover:bg-cyan-50/50"
                      }`}
                    >
                      <div className="text-2xl mb-2">{tone.icon}</div>
                      <div className="font-semibold text-gray-900">{tone.name}</div>
                      <div className="text-xs text-gray-600 mt-1">{tone.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Additional Info */}
              <div className="bg-white rounded-2xl shadow-2xl p-8">
                <h3 className="text-lg font-bold mb-4 text-gray-900">
                  Additional Info (Optional)
                </h3>
                
                <textarea
                  value={additionalInfo}
                  onChange={(e) => setAdditionalInfo(e.target.value)}
                  placeholder="Any specific points you want to mention..."
                  className="w-full h-24 px-4 py-3 border border-gray-200 rounded-lg focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 transition-all outline-none text-gray-900 resize-none"
                />
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}

              {/* Generate Button */}
              <motion.button
                type="button"
                onClick={handleGenerate}
                disabled={loading || !cvText || !jobTitle || !companyName}
                whileHover={{ scale: loading || !cvText || !jobTitle || !companyName ? 1 : 1.02 }}
                whileTap={{ scale: loading || !cvText || !jobTitle || !companyName ? 1 : 0.98 }}
                className={`w-full py-4 rounded-lg font-semibold text-lg shadow-xl transition-all duration-300 flex items-center justify-center gap-2 ${
                  loading || !cvText || !jobTitle || !companyName
                    ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                    : "bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-700 hover:to-teal-700 text-white hover:shadow-2xl"
                }`}
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Wand2 className="h-5 w-5" />
                    Generate Cover Letter
                  </>
                )}
              </motion.button>
            </motion.div>

            {/* Results Section */}
            <AnimatePresence mode="wait">
              {result ? (
                <motion.div
                  key="results"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="space-y-6"
                >
                  {/* Matching Skills */}
                  {result.matching_skills && result.matching_skills.length > 0 && (
                    <div className="bg-white rounded-2xl shadow-2xl p-8">
                      <div className="flex items-center justify-between mb-6">
                        <h2 className="text-2xl font-bold text-gray-900">Matching Skills</h2>
                        <button
                          onClick={() => setResult(null)}
                          className="text-gray-400 hover:text-gray-600 transition-colors"
                        >
                          <X className="h-6 w-6" />
                        </button>
                      </div>

                      <div className="flex flex-wrap gap-2">
                        {result.matching_skills.map((skill, idx) => (
                          <span
                            key={idx}
                            className="px-3 py-1 bg-cyan-100 text-cyan-700 rounded-full text-sm font-medium"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Key Highlights */}
                  {result.key_highlights && result.key_highlights.length > 0 && (
                    <div className="bg-white rounded-2xl shadow-2xl p-8">
                      <h3 className="text-xl font-bold mb-4 text-teal-600">
                        Key Highlights
                      </h3>
                      <ul className="space-y-2">
                        {result.key_highlights.map((highlight, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <CheckCircle2 className="h-5 w-5 text-teal-600 flex-shrink-0 mt-0.5" />
                            <span className="text-gray-700">{highlight}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Cover Letter */}
                  <div className="bg-white rounded-2xl shadow-2xl p-8">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-xl font-bold text-gray-900">
                        Your Cover Letter
                      </h3>
                      <div className="flex gap-2">
                        <button
                          onClick={handleCopy}
                          className="px-4 py-2 bg-cyan-100 hover:bg-cyan-200 text-cyan-700 rounded-lg font-medium transition-colors flex items-center gap-2"
                        >
                          {copied ? (
                            <>
                              <CheckCircle2 className="h-4 w-4" />
                              Copied!
                            </>
                          ) : (
                            <>
                              <Copy className="h-4 w-4" />
                              Copy
                            </>
                          )}
                        </button>
                        <button
                          onClick={handleDownload}
                          className="px-4 py-2 bg-teal-100 hover:bg-teal-200 text-teal-700 rounded-lg font-medium transition-colors flex items-center gap-2"
                        >
                          <Download className="h-4 w-4" />
                          Download
                        </button>
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg p-6 max-h-96 overflow-y-auto">
                      <pre className="whitespace-pre-wrap text-sm text-gray-800 leading-relaxed">
                        {result.cover_letter_text}
                      </pre>
                    </div>
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  key="placeholder"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="bg-white/60 backdrop-blur-sm rounded-2xl border-2 border-dashed border-gray-300 p-12 flex flex-col items-center justify-center text-center h-full"
                >
                  <Mail className="h-24 w-24 text-gray-300 mb-4" />
                  <h3 className="text-xl font-semibold text-gray-600 mb-2">
                    Fill in the details to generate
                  </h3>
                  <p className="text-gray-500">
                    AI will create a personalized cover letter
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

