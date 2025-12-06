"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { motion } from "framer-motion";
import {
  FileText,
  CheckCircle2,
  TrendingUp,
  Download,
  ArrowLeft,
  Loader2,
  Wand2,
  Sparkles,
  Copy,
  X,
} from "lucide-react";

interface ImprovementResult {
  rewrite_id: string;
  analysis_id: string;
  original_text: string;
  improved_text: string;
  improvements_made: string[];
  keywords_added: string[];
  ats_score_before: number;
  ats_score_after: number;
  style: string;
  analysis_weaknesses: string[];
  analysis_suggestions: string[];
}

export default function CVImprovePage() {
  const params = useParams();
  const router = useRouter();
  const { getToken } = useAuth();
  const analysisId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ImprovementResult | null>(null);
  const [selectedStyle, setSelectedStyle] = useState("ats_optimized");
  const [improving, setImproving] = useState(false);
  const [copied, setCopied] = useState(false);

  const styles = [
    { id: "ats_optimized", name: "ATS Optimized", icon: "🎯" },
    { id: "modern", name: "Modern", icon: "✨" },
    { id: "executive", name: "Executive", icon: "👔" },
    { id: "minimal", name: "Minimal", icon: "📄" },
  ];

  useEffect(() => {
    improveCV(selectedStyle);
  }, [analysisId]);

  const improveCV = async (style: string) => {
    setImproving(true);
    setError(null);

    try {
      const token = await getToken();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/cv/improve/${analysisId}?style=${style}`,
        {
          method: "POST",
          headers: {
            ...(token && { Authorization: `Bearer ${token}` }),
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to improve CV");
      }

      const data: ImprovementResult = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to improve CV");
    } finally {
      setLoading(false);
      setImproving(false);
    }
  };

  const handleStyleChange = (style: string) => {
    setSelectedStyle(style);
    improveCV(style);
  };

  const handleDownload = async (format: string) => {
    if (!result) return;

    try {
      const token = await getToken();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/cv/export/${result.rewrite_id}/${format}`,
        {
          headers: {
            ...(token && { Authorization: `Bearer ${token}` }),
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Download failed");
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `improved-cv-${selectedStyle}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error("Download failed:", err);
      setError(err.message || "Download failed. Please try TXT format or restart backend.");
    }
  };

  const handleCopy = () => {
    if (result?.improved_text) {
      navigator.clipboard.writeText(result.improved_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 pt-20">
        <div className="max-w-7xl mx-auto px-6 py-24 flex flex-col items-center justify-center">
          <Loader2 className="h-12 w-12 animate-spin text-purple-600 mb-4" />
          <p className="text-gray-600">Improving your CV with AI...</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 pt-20">
        <div className="max-w-7xl mx-auto px-6 py-24">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <p className="text-red-800">{error}</p>
            <button
              onClick={() => router.push("/cv")}
              className="mt-4 px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Go Back
            </button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 pt-20">
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push("/cv")}
            className="flex items-center gap-2 text-gray-600 hover:text-purple-600 transition-colors mb-4"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Analysis
          </button>

          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            CV Improvement Studio
          </h1>
          <p className="text-gray-600">
            Side-by-side comparison of your original and improved CV
          </p>
        </div>

        {result && (
          <>
            {/* ATS Score Comparison */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-2xl shadow-2xl p-8 mb-8"
            >
              <h2 className="text-2xl font-bold mb-6 text-gray-900">
                Score Improvement
              </h2>
              <div className="grid md:grid-cols-2 gap-8">
                <div className="text-center">
                  <div className="text-sm text-gray-600 mb-2">Before</div>
                  <div className="text-5xl font-bold text-gray-400">
                    {result.ats_score_before}
                  </div>
                  <div className="text-sm text-gray-500 mt-2">ATS Score</div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-green-700 mb-2">After</div>
                  <div className="text-5xl font-bold text-green-600">
                    {result.ats_score_after}
                  </div>
                  <div className="text-sm text-green-600 mt-2">
                    +{result.ats_score_after - result.ats_score_before} points
                  </div>
                </div>
              </div>
              <div className="mt-6 flex items-center justify-center gap-2 text-purple-600">
                <TrendingUp className="h-5 w-5" />
                <span className="font-semibold">
                  {Math.round(
                    ((result.ats_score_after - result.ats_score_before) /
                      result.ats_score_before) *
                      100
                  )}
                  % improvement
                </span>
              </div>
            </motion.div>

            {/* Style Selector */}
            <div className="bg-white rounded-2xl shadow-2xl p-6 mb-8">
              <h3 className="text-lg font-bold mb-4 text-gray-900">
                Try Different Styles
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {styles.map((style) => (
                  <button
                    key={style.id}
                    onClick={() => handleStyleChange(style.id)}
                    disabled={improving}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      selectedStyle === style.id
                        ? "border-purple-500 bg-purple-50 shadow-lg"
                        : "border-gray-200 hover:border-purple-300"
                    } ${improving ? "opacity-50 cursor-not-allowed" : ""}`}
                  >
                    <div className="text-2xl mb-1">{style.icon}</div>
                    <div className="font-semibold text-sm">{style.name}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Improvements Made */}
            {result.improvements_made && result.improvements_made.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-white rounded-2xl shadow-2xl p-8 mb-8"
              >
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-purple-600">
                  <Sparkles className="h-6 w-6" />
                  Improvements Applied
                </h3>
                <ul className="space-y-2">
                  {result.improvements_made.map((improvement, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <CheckCircle2 className="h-5 w-5 text-purple-600 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{improvement}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            )}

            {/* Keywords Added */}
            {result.keywords_added && result.keywords_added.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="bg-white rounded-2xl shadow-2xl p-8 mb-8"
              >
                <h3 className="text-xl font-bold mb-4 text-pink-600">
                  Keywords Added
                </h3>
                <div className="flex flex-wrap gap-2">
                  {result.keywords_added.map((keyword, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-pink-100 text-pink-700 rounded-full text-sm font-medium"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Side-by-Side Comparison */}
            <div className="grid lg:grid-cols-2 gap-8 mb-8">
              {/* Original CV */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 }}
                className="bg-white rounded-2xl shadow-2xl p-8"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-gray-900">
                    Original CV
                  </h3>
                  <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm">
                    Before
                  </span>
                </div>
                <div className="bg-gray-50 rounded-lg p-6 max-h-[600px] overflow-y-auto">
                  <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
                    {result.original_text}
                  </pre>
                </div>
              </motion.div>

              {/* Improved CV */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                className="bg-white rounded-2xl shadow-2xl p-8"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-green-600">
                    Improved CV
                  </h3>
                  <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-semibold">
                    After ✨
                  </span>
                </div>
                <div className="bg-green-50 rounded-lg p-6 max-h-[600px] overflow-y-auto">
                  <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
                    {result.improved_text}
                  </pre>
                </div>
              </motion.div>
            </div>

            {/* Actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl shadow-2xl p-8 text-white"
            >
              <h3 className="text-2xl font-bold mb-4">
                Download Your Improved CV
              </h3>
              <p className="mb-6 text-purple-100">
                Export in your preferred format
              </p>
              <div className="flex flex-wrap gap-4">
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-2 px-6 py-3 bg-white text-purple-600 rounded-lg font-semibold hover:bg-purple-50 transition-all shadow-lg"
                >
                  {copied ? (
                    <>
                      <CheckCircle2 className="h-5 w-5" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="h-5 w-5" />
                      Copy Text
                    </>
                  )}
                </button>
                <button
                  onClick={() => handleDownload("pdf")}
                  className="flex items-center gap-2 px-6 py-3 bg-white text-purple-600 rounded-lg font-semibold hover:bg-purple-50 transition-all shadow-lg"
                >
                  <Download className="h-5 w-5" />
                  Download PDF
                </button>
                <button
                  onClick={() => handleDownload("docx")}
                  className="flex items-center gap-2 px-6 py-3 bg-white text-purple-600 rounded-lg font-semibold hover:bg-purple-50 transition-all shadow-lg"
                >
                  <Download className="h-5 w-5" />
                  Download DOCX
                </button>
                <button
                  onClick={() => handleDownload("txt")}
                  className="flex items-center gap-2 px-6 py-3 bg-white text-purple-600 rounded-lg font-semibold hover:bg-purple-50 transition-all shadow-lg"
                >
                  <Download className="h-5 w-5" />
                  Download TXT
                </button>
              </div>
            </motion.div>
          </>
        )}
      </div>
    </main>
  );
}
