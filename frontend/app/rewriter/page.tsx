"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FileText,
  Wand2,
  Loader2,
  Copy,
  Download,
  CheckCircle2,
  TrendingUp,
  Sparkles,
  X,
  ArrowRight,
  Zap,
  Target,
  Star,
  Award,
} from "lucide-react";
import { useAuth } from "@clerk/nextjs";
import Link from "next/link";

interface CVRewriteResult {
  id: string;
  rewritten_cv_text: string;
  rewritten_cv_markdown: string;
  style: string;
  improvements_made: string[];
  keywords_added: string[];
  ats_score_before: number;
  ats_score_after: number;
}

export default function CVRewriter() {
  const { getToken } = useAuth();
  const [cvText, setCvText] = useState("");
  const [targetJob, setTargetJob] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [selectedStyle, setSelectedStyle] = useState("modern");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CVRewriteResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const styles = [
    { 
      id: "modern", 
      name: "Modern", 
      description: "Contemporary & impact-focused",
      icon: "✨",
      gradient: "from-blue-500 to-cyan-500",
      bgGradient: "from-blue-50 to-cyan-50"
    },
    { 
      id: "minimal", 
      name: "Minimal", 
      description: "Clean & concise format",
      icon: "📄",
      gradient: "from-slate-500 to-gray-500",
      bgGradient: "from-slate-50 to-gray-50"
    },
    { 
      id: "executive", 
      name: "Executive", 
      description: "Leadership-focused premium",
      icon: "👔",
      gradient: "from-purple-500 to-indigo-600",
      bgGradient: "from-purple-50 to-indigo-50"
    },
    { 
      id: "ats_optimized", 
      name: "ATS Optimized", 
      description: "Maximum keyword optimization",
      icon: "🎯",
      gradient: "from-emerald-500 to-green-600",
      bgGradient: "from-emerald-50 to-green-50"
    },
  ];

  const handleRewrite = async () => {
    if (!cvText.trim()) {
      setError("Please enter your CV text");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const token = await getToken();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/rewriter/cv`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token && { Authorization: `Bearer ${token}` }),
          },
          body: JSON.stringify({
            cv_text: cvText,
            target_job_title: targetJob || null,
            target_job_description: jobDescription || null,
            style: selectedStyle,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to rewrite CV");
      }

      const data: CVRewriteResult = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to rewrite CV");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (result?.rewritten_cv_text) {
      navigator.clipboard.writeText(result.rewritten_cv_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // Convert markdown to HTML (simplified and robust)
  const markdownToHtml = (markdown: string): string => {
    const escapeHtml = (text: string): string => {
      return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    };
    
    const processInline = (text: string): string => {
      // Process bold
      return text.replace(/\*\*(.*?)\*\*/g, '<strong style="font-weight: 600;">$1</strong>');
    };
    
    const lines = markdown.split('\n');
    let processedLines: string[] = [];
    let inList = false;
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();
      
      // Headers
      if (trimmed.startsWith('### ')) {
        if (inList) { processedLines.push('</ul>'); inList = false; }
        const content = escapeHtml(trimmed.substring(4));
        processedLines.push(`<h3 style="font-size: 1.5em; font-weight: bold; margin-top: 1.5em; margin-bottom: 0.5em; color: #1f2937;">${content}</h3>`);
      } else if (trimmed.startsWith('## ')) {
        if (inList) { processedLines.push('</ul>'); inList = false; }
        const content = escapeHtml(trimmed.substring(3));
        processedLines.push(`<h2 style="font-size: 2em; font-weight: bold; margin-top: 2em; margin-bottom: 1em; color: #111827; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5em;">${content}</h2>`);
      } else if (trimmed.startsWith('# ')) {
        if (inList) { processedLines.push('</ul>'); inList = false; }
        const content = escapeHtml(trimmed.substring(2));
        processedLines.push(`<h1 style="font-size: 2.5em; font-weight: bold; margin-top: 1em; margin-bottom: 1em; color: #111827;">${content}</h1>`);
      } else if (trimmed === '---' || trimmed === '***') {
        if (inList) { processedLines.push('</ul>'); inList = false; }
        processedLines.push('<hr style="border: none; border-top: 1px solid #e5e7eb; margin: 2em 0;">');
      } else {
        const listMatch = trimmed.match(/^[\-\*\+]\s+(.+)$/);
        if (listMatch) {
          if (!inList) {
            processedLines.push('<ul style="margin: 1em 0; padding-left: 2em;">');
            inList = true;
          }
          let content = listMatch[1];
          content = processInline(escapeHtml(content));
          processedLines.push(`<li style="margin-bottom: 0.5em; line-height: 1.6;">${content}</li>`);
        } else {
          if (inList) { processedLines.push('</ul>'); inList = false; }
          if (trimmed) {
            let content = processInline(escapeHtml(trimmed));
            processedLines.push(`<p style="margin: 1em 0; line-height: 1.6;">${content}</p>`);
          } else {
            processedLines.push('<br>');
          }
        }
      }
    }
    
    if (inList) processedLines.push('</ul>');
    
    return processedLines.join('\n');
  };

  const handleDownload = () => {
    if (!result) return;
    
    const cvContent = result.rewritten_cv_markdown || result.rewritten_cv_text;
    const styleName = styles.find(s => s.id === selectedStyle)?.name || selectedStyle;
    
    // Get style-specific CSS
    const getStyleCSS = () => {
      switch (selectedStyle) {
        case 'modern':
          return `
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1f2937; }
            .container { max-width: 900px; margin: 0 auto; padding: 40px; }
            h1 { color: #2563eb; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }
            h2 { color: #1e40af; margin-top: 30px; }
            strong { color: #1e40af; }
          `;
        case 'minimal':
          return `
            body { font-family: 'Georgia', serif; color: #374151; }
            .container { max-width: 800px; margin: 0 auto; padding: 50px; }
            h1 { color: #111827; font-weight: 300; letter-spacing: 2px; }
            h2 { color: #4b5563; font-weight: 400; margin-top: 40px; border-bottom: 1px solid #d1d5db; padding-bottom: 5px; }
            strong { color: #111827; font-weight: 500; }
          `;
        case 'executive':
          return `
            body { font-family: 'Times New Roman', serif; color: #1f2937; }
            .container { max-width: 850px; margin: 0 auto; padding: 60px; }
            h1 { color: #7c3aed; font-size: 2.8em; letter-spacing: 1px; }
            h2 { color: #5b21b6; margin-top: 35px; font-size: 1.8em; border-left: 4px solid #8b5cf6; padding-left: 15px; }
            strong { color: #6d28d9; }
          `;
        case 'ats_optimized':
          return `
            body { font-family: 'Arial', sans-serif; color: #1f2937; }
            .container { max-width: 900px; margin: 0 auto; padding: 40px; }
            h1 { color: #059669; font-size: 2.2em; }
            h2 { color: #047857; margin-top: 30px; font-size: 1.5em; background: #ecfdf5; padding: 10px; border-left: 4px solid #10b981; }
            strong { color: #065f46; }
          `;
        default:
          return '';
      }
    };
    
    // Convert markdown to HTML
    const htmlContent = markdownToHtml(cvContent);
    
    // Create full HTML document
    const fullHTML = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CV - ${styleName} Style</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      ${getStyleCSS()}
      background: #ffffff;
      line-height: 1.6;
    }
    .container {
      background: #ffffff;
      box-shadow: 0 0 20px rgba(0,0,0,0.1);
      margin: 20px auto;
    }
    p { margin: 1em 0; line-height: 1.8; }
    ul { margin: 1em 0; padding-left: 2em; }
    li { margin-bottom: 0.5em; }
    hr { margin: 2em 0; border: none; border-top: 1px solid #e5e7eb; }
    @media print {
      body { background: white; }
      .container { box-shadow: none; }
    }
  </style>
</head>
<body>
  <div class="container">
    ${htmlContent}
  </div>
</body>
</html>`;
    
    // Create and download the file
    const blob = new Blob([fullHTML], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `CV-${styleName}-${new Date().toISOString().split('T')[0]}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const currentStyle = styles.find(s => s.id === selectedStyle) || styles[0];

  return (
    <main className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-pink-50 dark:from-gray-900 dark:via-orange-950 dark:to-pink-950 pt-20 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Header */}
          <div className="text-center mb-12">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800/80 backdrop-blur-sm rounded-full shadow-lg border border-amber-200 mb-6"
            >
              <Wand2 className="h-5 w-5 text-amber-600" />
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">GPT-4o Powered</span>
              <Sparkles className="h-4 w-4 text-amber-500" />
            </motion.div>
            <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-amber-600 via-orange-600 to-pink-600 bg-clip-text text-transparent">
              Elite CV Rewriter
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Transform your CV with AI in multiple professional styles. ATS-optimized and job-tailored.
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
              {/* CV Input */}
              <div className="bg-white dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-amber-100">
                <div className="flex items-center gap-2 mb-6">
                  <FileText className="h-6 w-6 text-amber-600" />
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Your Current CV</h2>
                </div>
                
                <textarea
                  value={cvText}
                  onChange={(e) => setCvText(e.target.value)}
                  placeholder="Paste your CV text here... (minimum 50 characters)&#10;&#10;Include your experience, skills, education, and achievements."
                  className="w-full h-64 px-4 py-3 border-2 border-amber-200 rounded-xl focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 transition-all outline-none text-gray-900 dark:text-gray-100 resize-none bg-white dark:bg-gray-800/50"
                />
                
                <div className="flex items-center justify-between mt-2">
                  <div className="text-sm text-gray-500">
                    {cvText.length} characters {cvText.length < 50 && "- Need at least 50"}
                  </div>
                  {cvText.length >= 50 && (
                    <div className="text-sm font-medium text-green-600 flex items-center gap-1">
                      <CheckCircle2 className="h-4 w-4" />
                      Ready to rewrite
                    </div>
                  )}
                </div>
              </div>

              {/* Target Job (Optional) */}
              <div className="bg-white dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-amber-100">
                <div className="flex items-center gap-2 mb-4">
                  <Target className="h-5 w-5 text-amber-600" />
                  <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                    Target Job (Optional but Recommended)
                  </h3>
                </div>
                
                <input
                  type="text"
                  value={targetJob}
                  onChange={(e) => setTargetJob(e.target.value)}
                  placeholder="e.g., Senior Software Engineer"
                  className="w-full px-4 py-3 border-2 border-amber-200 rounded-xl focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 transition-all outline-none text-gray-900 dark:text-gray-100 mb-4 bg-white dark:bg-gray-800/50"
                />
                
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste job description here to tailor your CV for maximum impact..."
                  className="w-full h-32 px-4 py-3 border-2 border-amber-200 rounded-xl focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 transition-all outline-none text-gray-900 dark:text-gray-100 resize-none bg-white dark:bg-gray-800/50"
                />
                
                <div className="mt-3 p-3 bg-amber-50 rounded-lg border border-amber-200">
                  <p className="text-xs text-gray-600 dark:text-gray-400 flex items-start gap-2">
                    <Zap className="h-4 w-4 text-amber-600 flex-shrink-0 mt-0.5" />
                    <span>
                      <strong>Pro Tip:</strong> Adding a job description helps AI tailor your CV with relevant keywords and experience highlights.
                    </span>
                  </p>
                </div>
              </div>

              {/* Style Selection */}
              <div className="bg-white dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-amber-100">
                <div className="flex items-center gap-2 mb-6">
                  <Star className="h-6 w-6 text-amber-600" />
                  <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                    Choose Your Style
                  </h3>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  {styles.map((style) => (
                    <motion.button
                      key={style.id}
                      onClick={() => setSelectedStyle(style.id)}
                      whileHover={{ scale: 1.03 }}
                      whileTap={{ scale: 0.97 }}
                      className={`p-5 rounded-xl border-2 transition-all duration-300 text-left relative overflow-hidden ${
                        selectedStyle === style.id
                          ? `border-amber-500 bg-gradient-to-br ${style.bgGradient} shadow-lg`
                          : "border-gray-200 dark:border-gray-700 hover:border-amber-300 bg-white dark:bg-gray-800/50"
                      }`}
                    >
                      {selectedStyle === style.id && (
                        <div className="absolute top-2 right-2">
                          <CheckCircle2 className="h-5 w-5 text-amber-600" />
                        </div>
                      )}
                      <div className="text-3xl mb-3">{style.icon}</div>
                      <div className={`font-bold text-gray-900 dark:text-gray-100 mb-1 ${
                        selectedStyle === style.id ? 'text-lg' : 'text-base'
                      }`}>
                        {style.name}
                      </div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">{style.description}</div>
                    </motion.button>
                  ))}
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-red-50 border-2 border-red-200 rounded-xl p-4 flex items-start gap-3"
                >
                  <X className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <p className="text-red-800 text-sm">{error}</p>
                </motion.div>
              )}

              {/* Rewrite Button */}
              <motion.button
                type="button"
                onClick={handleRewrite}
                disabled={loading || cvText.length < 50}
                whileHover={{ scale: loading || cvText.length < 50 ? 1 : 1.02 }}
                whileTap={{ scale: loading || cvText.length < 50 ? 1 : 0.98 }}
                className={`w-full py-5 rounded-xl font-bold text-lg shadow-2xl transition-all duration-300 flex items-center justify-center gap-3 ${
                  loading || cvText.length < 50
                    ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                    : "bg-gradient-to-r from-amber-600 via-orange-600 to-pink-600 hover:from-amber-700 hover:via-orange-700 hover:to-pink-700 text-white hover:shadow-amber-500/50"
                }`}
              >
                {loading ? (
                  <>
                    <Loader2 className="h-6 w-6 animate-spin" />
                    <span>Rewriting with AI...</span>
                  </>
                ) : (
                  <>
                    <Wand2 className="h-6 w-6" />
                    <span>Transform My CV</span>
                    <ArrowRight className="h-5 w-5" />
                  </>
                )}
              </motion.button>

              <p className="text-center text-sm text-gray-500">
                Powered by GPT-4o • Results in 5-10 seconds
              </p>
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
                  {/* ATS Score Improvement */}
                  <div className="bg-white dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-amber-100">
                    <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center gap-2">
                        <Award className="h-6 w-6 text-amber-600" />
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Performance Boost</h2>
                      </div>
                      <button
                        onClick={() => setResult(null)}
                        className="text-gray-400 hover:text-gray-600 dark:text-gray-400 transition-colors p-2 hover:bg-gray-100 dark:bg-gray-700 rounded-lg"
                      >
                        <X className="h-5 w-5" />
                      </button>
                    </div>

                    <div className="grid grid-cols-2 gap-6 mb-6">
                      <div className="p-5 bg-gradient-to-br from-gray-100 to-gray-200 rounded-xl border-2 border-gray-300">
                        <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Before</div>
                        <div className="text-4xl font-bold text-gray-700 dark:text-gray-300">
                          {result.ats_score_before}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">ATS Score</div>
                      </div>
                      <div className="p-5 bg-gradient-to-br from-green-100 to-emerald-200 rounded-xl border-2 border-green-300">
                        <div className="text-sm font-medium text-green-700 mb-2">After</div>
                        <div className="text-4xl font-bold text-green-700">
                          {result.ats_score_after}
                        </div>
                        <div className="text-xs text-green-600 mt-1">ATS Score</div>
                      </div>
                    </div>

                    <div className="flex items-center justify-center gap-3 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200">
                      <TrendingUp className="h-6 w-6 text-green-600" />
                      <span className="font-bold text-green-700 text-lg">
                        +{result.ats_score_after - result.ats_score_before} points improvement!
                      </span>
                    </div>
                  </div>

                  {/* Improvements */}
                  {result.improvements_made && result.improvements_made.length > 0 && (
                    <div className="bg-white dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-amber-100">
                      <h3 className="text-xl font-bold mb-5 flex items-center gap-2 text-purple-600">
                        <Sparkles className="h-6 w-6" />
                        AI Improvements Made
                      </h3>
                      <ul className="space-y-3">
                        {result.improvements_made.map((improvement, idx) => (
                          <motion.li
                            key={idx}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: idx * 0.1 }}
                            className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg border border-purple-100"
                          >
                            <CheckCircle2 className="h-5 w-5 text-purple-600 flex-shrink-0 mt-0.5" />
                            <span className="text-gray-700 dark:text-gray-300">{improvement}</span>
                          </motion.li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Keywords Added */}
                  {result.keywords_added && result.keywords_added.length > 0 && (
                    <div className="bg-white dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-amber-100">
                      <h3 className="text-xl font-bold mb-4 text-pink-600 flex items-center gap-2">
                        <Target className="h-6 w-6" />
                        Keywords Added
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {result.keywords_added.map((keyword, idx) => (
                          <motion.span
                            key={idx}
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: idx * 0.05 }}
                            className="px-4 py-2 bg-gradient-to-r from-pink-100 to-rose-100 text-pink-700 rounded-full text-sm font-semibold border border-pink-200"
                          >
                            {keyword}
                          </motion.span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Rewritten CV */}
                  <div className="bg-white dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-amber-100">
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <FileText className="h-6 w-6 text-amber-600" />
                        Your Transformed CV
                      </h3>
                      <div className="flex gap-2">
                        <button
                          onClick={handleCopy}
                          className="px-4 py-2 bg-gradient-to-r from-purple-100 to-purple-200 hover:from-purple-200 hover:to-purple-300 text-purple-700 rounded-lg font-semibold transition-all flex items-center gap-2 border border-purple-300"
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
                          className="px-4 py-2 bg-gradient-to-r from-pink-100 to-pink-200 hover:from-pink-200 hover:to-pink-300 text-pink-700 rounded-lg font-semibold transition-all flex items-center gap-2 border border-pink-300"
                        >
                          <Download className="h-4 w-4" />
                          Download
                        </button>
                      </div>
                    </div>
                    
                    <div className="bg-gradient-to-br from-gray-50 to-white rounded-xl p-6 max-h-[500px] overflow-y-auto border-2 border-gray-200 dark:border-gray-700">
                      <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono leading-relaxed">
                        {result.rewritten_cv_text}
                      </pre>
                    </div>

                    <div className="mt-4 p-4 bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg border border-amber-200">
                      <p className="text-sm text-gray-700 dark:text-gray-300 flex items-start gap-2">
                        <Sparkles className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
                        <span>
                          <strong>Next Steps:</strong> Use this CV for your applications! You can also try different styles or add more job details for even better results.
                        </span>
                      </p>
                    </div>
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  key="placeholder"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="bg-white dark:bg-gray-800/60 backdrop-blur-sm rounded-2xl border-2 border-dashed border-amber-300 p-12 flex flex-col items-center justify-center text-center min-h-[600px]"
                >
                  <motion.div
                    animate={{ 
                      rotate: [0, 5, -5, 0],
                      scale: [1, 1.05, 1]
                    }}
                    transition={{ 
                      duration: 3, 
                      repeat: Infinity,
                      ease: "easeInOut"
                    }}
                  >
                    <Wand2 className="h-32 w-32 text-amber-300 mb-6" />
                  </motion.div>
                  <h3 className="text-2xl font-bold text-gray-700 dark:text-gray-300 mb-3">
                    Ready to Transform?
                  </h3>
                  <p className="text-gray-500 max-w-md mb-6">
                    Paste your CV on the left, choose your style, and let our GPT-4o AI 
                    create a professional, ATS-optimized version in seconds.
                  </p>
                  <div className="flex flex-wrap gap-3 justify-center">
                    <span className="px-4 py-2 bg-white dark:bg-gray-800 rounded-full text-sm font-medium text-gray-600 dark:text-gray-400 shadow-md">
                      ✨ 4 Professional Styles
                    </span>
                    <span className="px-4 py-2 bg-white dark:bg-gray-800 rounded-full text-sm font-medium text-gray-600 dark:text-gray-400 shadow-md">
                      🎯 ATS Optimized
                    </span>
                    <span className="px-4 py-2 bg-white dark:bg-gray-800 rounded-full text-sm font-medium text-gray-600 dark:text-gray-400 shadow-md">
                      ⚡ Instant Results
                    </span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </div>
    </main>
  );
}
