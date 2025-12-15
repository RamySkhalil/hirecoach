"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { motion } from "framer-motion";
import { Sparkles, Briefcase, Trophy, Globe, Hash, ArrowRight, Loader2 } from "lucide-react";
import { startInterview, type InterviewStartRequest } from "@/lib/api";
import { useCurrentUser } from "@/hooks/useCurrentUser";

export default function InterviewSetup() {
  const router = useRouter();
  const { getToken, isSignedIn } = useAuth();
  const { user, role, loading: userLoading } = useCurrentUser();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Redirect to onboarding if not signed in or if user needs to set/change role
  useEffect(() => {
    if (!userLoading) {
      if (!isSignedIn) {
        router.push("/sign-in");
        return;
      }
      // If user has recruiter role, redirect to onboarding to allow role change
      if (role === "RECRUITER") {
        router.push("/onboarding/role?switchTo=candidate");
        return;
      }
      // If user has no role, redirect to onboarding to select one
      if (role === null && user) {
        router.push("/onboarding/role");
        return;
      }
    }
  }, [userLoading, isSignedIn, role, user, router]);

  const [formData, setFormData] = useState<InterviewStartRequest>({
    job_title: "",
    seniority: "mid",
    language: "en",
    num_questions: 5,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = await getToken();
      if (!token) {
        router.push("/sign-in");
        return;
      }
      const response = await startInterview(formData, token);
      router.push(`/interview/session/${response.session_id}`);
    } catch (err: any) {
      setError(err.message || "Failed to start interview. Please try again.");
      setLoading(false);
    }
  };

  // Show loading while checking auth/role
  if (userLoading || !isSignedIn || role === "RECRUITER" || (role === null && user)) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-950 dark:to-indigo-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-950 dark:to-indigo-950 pt-20 transition-colors duration-300">
      <div className="max-w-4xl mx-auto px-6 py-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-full shadow-lg border border-blue-100 dark:border-blue-900 mb-6">
              <Sparkles className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">AI Interview Coach</span>
            </div>
            <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent">
              Set Up Your Interview
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400">
              Customize your mock interview to match your target role
            </p>
          </div>

          {/* Form Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 md:p-12"
          >
            <form onSubmit={handleSubmit} className="space-y-8">
              {/* Job Title */}
              <div>
                <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  <Briefcase className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  Job Title
                </label>
                <input
                  type="text"
                  value={formData.job_title}
                  onChange={(e) =>
                    setFormData({ ...formData, job_title: e.target.value })
                  }
                  placeholder="e.g., Software Engineer, Product Manager, Data Scientist"
                  className="w-full px-4 py-3 border border-gray-200 dark:border-gray-700 rounded-lg focus:border-blue-500 dark:focus:border-blue-400 focus:ring-2 focus:ring-blue-500/20 dark:focus:ring-blue-400/20 transition-all outline-none text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-900 placeholder:text-gray-500 dark:placeholder:text-gray-500"
                  required
                />
              </div>

              {/* Seniority */}
              <div>
                <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  <Trophy className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  Seniority Level
                </label>
                <div className="grid grid-cols-3 gap-4">
                  {["junior", "mid", "senior"].map((level) => (
                    <button
                      key={level}
                      type="button"
                      onClick={() =>
                        setFormData({
                          ...formData,
                          seniority: level as "junior" | "mid" | "senior",
                        })
                      }
                      className={`px-6 py-3 rounded-lg font-medium transition-all duration-300 ${
                        formData.seniority === level
                          ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg scale-105"
                          : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                      }`}
                    >
                      {level.charAt(0).toUpperCase() + level.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Language */}
              <div>
                <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  <Globe className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  Interview Language
                </label>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, language: "en" })}
                    className={`px-6 py-3 rounded-lg font-medium transition-all duration-300 ${
                      formData.language === "en"
                        ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg scale-105"
                        : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                    }`}
                  >
                    English
                  </button>
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, language: "ar" })}
                    className={`px-6 py-3 rounded-lg font-medium transition-all duration-300 ${
                      formData.language === "ar"
                        ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg scale-105"
                        : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                    }`}
                  >
                    Arabic
                  </button>
                </div>
              </div>

              {/* Number of Questions */}
              <div>
                <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  <Hash className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  Number of Questions
                </label>
                <select
                  value={formData.num_questions}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      num_questions: parseInt(e.target.value),
                    })
                  }
                  className="w-full px-4 py-3 border border-gray-200 dark:border-gray-700 rounded-lg focus:border-blue-500 dark:focus:border-blue-400 focus:ring-2 focus:ring-blue-500/20 dark:focus:ring-blue-400/20 transition-all outline-none text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-900"
                >
                  <option value={3}>3 Questions (Quick Practice)</option>
                  <option value={5}>5 Questions (Recommended)</option>
                  <option value={7}>7 Questions (Thorough)</option>
                  <option value={10}>10 Questions (Comprehensive)</option>
                </select>
              </div>

              {/* Error Message */}
              {error && (
                <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <p className="text-red-800 dark:text-red-200 text-sm">{error}</p>
                </div>
              )}

              {/* Submit Button */}
              <motion.button
                type="submit"
                disabled={loading || !formData.job_title}
                whileHover={{ scale: loading ? 1 : 1.02 }}
                whileTap={{ scale: loading ? 1 : 0.98 }}
                className={`w-full py-4 rounded-lg font-semibold text-lg shadow-xl transition-all duration-300 flex items-center justify-center gap-2 ${
                  loading || !formData.job_title
                    ? "bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-500 cursor-not-allowed"
                    : "bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white hover:shadow-2xl"
                }`}
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Starting Interview...
                  </>
                ) : (
                  <>
                    Start Interview
                    <ArrowRight className="h-5 w-5" />
                  </>
                )}
              </motion.button>
            </form>
          </motion.div>

          {/* Info Cards */}
          <div className="grid md:grid-cols-3 gap-6 mt-12">
            <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl p-6 border border-blue-100 dark:border-blue-900">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                ✨ <strong>AI-Generated Questions</strong>
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Questions tailored to your role and seniority
              </p>
            </div>
            <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl p-6 border border-blue-100 dark:border-blue-900">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                📊 <strong>Instant Feedback</strong>
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Detailed scoring and coaching after each answer
              </p>
            </div>
            <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl p-6 border border-blue-100 dark:border-blue-900">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                📈 <strong>Comprehensive Report</strong>
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Full analysis with action plan at the end
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </main>
  );
}
