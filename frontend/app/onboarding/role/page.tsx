"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { motion } from "framer-motion";
import { Briefcase, User, ArrowRight } from "lucide-react";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { setUserRole } from "@/lib/auth";

export default function RoleOnboardingPage() {
  const router = useRouter();
  const { isSignedIn, getToken, isLoaded: authLoaded } = useAuth();
  const { user, role, loading } = useCurrentUser();
  const [selecting, setSelecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Wait for Clerk to load
    if (!isSignedIn && isSignedIn !== undefined) {
      router.push("/sign-in");
      return;
    }

    // If user has a role, redirect (but only if we're sure)
    if (!loading && role) {
      if (role === "RECRUITER") {
        router.push("/recruiter/dashboard");
      } else if (role === "CANDIDATE") {
        router.push("/interview/setup");
      }
    }
  }, [loading, isSignedIn, role, router]);

  const handleRoleSelect = async (selectedRole: "RECRUITER" | "CANDIDATE") => {
    if (selecting) return;

    try {
      setSelecting(true);
      setError(null);
      const token = await getToken();
      if (!token) {
        throw new Error("No authentication token. Please sign in again.");
      }

      await setUserRole(selectedRole, token);

      // Small delay to ensure state updates
      await new Promise(resolve => setTimeout(resolve, 300));

      // Redirect based on role
      if (selectedRole === "RECRUITER") {
        router.push("/recruiter/dashboard");
      } else {
        router.push("/interview/setup");
      }
    } catch (error) {
      console.error("Failed to set role:", error);
      const errorMessage = error instanceof Error ? error.message : "Failed to set role. Please check your connection and try again.";
      setError(errorMessage);
      setSelecting(false);
    }
  };

  // Show loading only if Clerk is still loading
  if (!authLoaded || (loading && !error)) {
    return (
      <main className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </main>
    );
  }

  // If not signed in, show sign in prompt
  if (!isSignedIn) {
    return (
      <main className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 dark:text-gray-400 mb-4">Please sign in to continue</p>
          <button
            onClick={() => router.push("/sign-in")}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg"
          >
            Sign In
          </button>
        </div>
      </main>
    );
  }

  if (role) {
    // Will redirect in useEffect, but show loading while redirecting
    return (
      <main className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Redirecting...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-950 dark:to-indigo-950 flex items-center justify-center p-6">
      <div className="max-w-4xl w-full">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent">
            Welcome to Interviewly
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            Choose your role to get started
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Recruiter Card */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-all duration-300 cursor-pointer group"
            onClick={() => handleRoleSelect("RECRUITER")}
          >
            <div className="flex flex-col items-center text-center">
              <div className="inline-flex p-6 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600 mb-6 group-hover:scale-110 transition-transform duration-300">
                <Briefcase className="h-12 w-12 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
                I'm a Recruiter
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
                Post jobs, screen candidates, and conduct AI-powered interviews with our ATS platform.
              </p>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                disabled={selecting}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-8 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-2 disabled:opacity-50"
              >
                {selecting ? "Setting up..." : "Continue as Recruiter"}
                <ArrowRight className="h-5 w-5" />
              </motion.button>
            </div>
          </motion.div>

          {/* Candidate Card */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-all duration-300 cursor-pointer group"
            onClick={() => handleRoleSelect("CANDIDATE")}
          >
            <div className="flex flex-col items-center text-center">
              <div className="inline-flex p-6 rounded-2xl bg-gradient-to-r from-purple-500 to-pink-600 mb-6 group-hover:scale-110 transition-transform duration-300">
                <User className="h-12 w-12 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
                I'm a Candidate
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
                Practice interviews, optimize your CV, and get AI-powered career coaching.
              </p>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                disabled={selecting}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-8 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-2 disabled:opacity-50"
              >
                {selecting ? "Setting up..." : "Continue as Candidate"}
                <ArrowRight className="h-5 w-5" />
              </motion.button>
            </div>
          </motion.div>
        </div>

        <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-8">
          You can change your role later in settings
        </p>

        {error && (
          <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-sm text-red-600 dark:text-red-400">
              {error}
            </p>
          </div>
        )}
      </div>
    </main>
  );
}

