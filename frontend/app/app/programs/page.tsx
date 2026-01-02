"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@clerk/nextjs";
import { motion } from "framer-motion";
import { 
  ArrowRight, 
  Calendar, 
  Target, 
  Users, 
  CheckCircle, 
  Clock,
  BookOpen,
  TrendingUp,
  Play,
  Plus
} from "lucide-react";

interface Program {
  id: string;
  slug: string;
  title: string;
  description: string;
  target_role: string;
  difficulty: string;
}

interface Enrollment {
  id: string;
  program_id: string;
  program_title: string;
  program_slug: string;
  target_role: string;
  status: string;
  progress_percentage: number;
  enrolled_at: string;
  current_day: number;
}

export default function AuthProgramsPage() {
  const { getToken, isSignedIn } = useAuth();
  const [programs, setPrograms] = useState<Program[]>([]);
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [enrolling, setEnrolling] = useState<string | null>(null);

  useEffect(() => {
    if (isSignedIn) {
      loadData();
    }
  }, [isSignedIn]);

  const loadData = async () => {
    try {
      const token = await getToken();
      const headers = {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` })
      };

      // Load available programs
      const programsResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/programs`, {
        headers
      });

      // Load user enrollments
      const enrollmentsResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/me/programs`, {
        headers
      });

      if (programsResponse.ok) {
        const programsData = await programsResponse.json();
        setPrograms(programsData);
      }

      if (enrollmentsResponse.ok) {
        const enrollmentsData = await enrollmentsResponse.json();
        setEnrollments(enrollmentsData);
      }
    } catch (err) {
      setError("Error loading programs");
      console.error("Error loading data:", err);
    } finally {
      setLoading(false);
    }
  };

  const enrollInProgram = async (programId: string) => {
    if (!isSignedIn || enrolling) return;

    setEnrolling(programId);
    try {
      const token = await getToken();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/programs/${programId}/enroll`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token && { Authorization: `Bearer ${token}` })
        },
        body: JSON.stringify({})
      });

      if (response.ok) {
        // Refresh enrollments
        await loadData();
      } else {
        setError("Failed to enroll in program");
      }
    } catch (err) {
      setError("Error enrolling in program");
      console.error("Error enrolling:", err);
    } finally {
      setEnrolling(null);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'beginner':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'advanced':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'abandoned':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const isEnrolled = (programId: string) => {
    return enrollments.some(e => e.program_id === programId);
  };

  if (!isSignedIn) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center pt-20">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            Please sign in to access programs
          </h1>
          <Link href="/sign-in">
            <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
              Sign In
            </button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-6 py-8 pt-24">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            30-Day Programs
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Structured preparation programs to boost your interview skills
          </p>
        </motion.div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Loading programs...</p>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <div className="text-red-500 mb-4">⚠️ {error}</div>
            <button
              onClick={loadData}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        ) : (
          <div className="space-y-8">
            {/* My Enrollments */}
            {enrollments.length > 0 && (
              <motion.section
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.1 }}
              >
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">
                  My Programs
                </h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {enrollments.map((enrollment) => (
                    <motion.div
                      key={enrollment.id}
                      whileHover={{ scale: 1.02 }}
                      className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
                    >
                      <div className="flex justify-between items-start mb-4">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(enrollment.status)}`}>
                          {enrollment.status}
                        </span>
                        <div className="text-right text-sm text-gray-500 dark:text-gray-400">
                          Day {enrollment.current_day}/30
                        </div>
                      </div>

                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                        {enrollment.program_title}
                      </h3>
                      
                      <div className="flex items-center text-sm text-gray-600 dark:text-gray-400 mb-4">
                        <Target className="h-4 w-4 mr-2" />
                        <span>{enrollment.target_role}</span>
                      </div>

                      {/* Progress Bar */}
                      <div className="mb-4">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm text-gray-600 dark:text-gray-400">Progress</span>
                          <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                            {Math.round(enrollment.progress_percentage)}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${enrollment.progress_percentage}%` }}
                          ></div>
                        </div>
                      </div>

                      <Link href={`/app/programs/${enrollment.program_id}`}>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                        >
                          <Play className="h-4 w-4" />
                          Continue Program
                        </motion.button>
                      </Link>
                    </motion.div>
                  ))}
                </div>
              </motion.section>
            )}

            {/* Available Programs */}
            <motion.section
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">
                Available Programs
              </h2>
              
              {programs.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-600 dark:text-gray-400">No programs available at the moment.</p>
                </div>
              ) : (
                <div className="grid md:grid-cols-2 gap-8">
                  {programs.map((program) => (
                    <motion.div
                      key={program.id}
                      whileHover={{ scale: 1.02 }}
                      className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 border border-gray-200 dark:border-gray-700"
                    >
                      <div className="flex items-start justify-between mb-6">
                        <div>
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(program.difficulty)}`}>
                            {program.difficulty}
                          </span>
                          <h3 className="text-xl font-bold mt-4 mb-2 text-gray-900 dark:text-gray-100">
                            {program.title}
                          </h3>
                          <div className="flex items-center text-gray-600 dark:text-gray-400 mb-4">
                            <Users className="h-4 w-4 mr-2" />
                            <span>{program.target_role}</span>
                          </div>
                        </div>
                      </div>

                      <p className="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
                        {program.description}
                      </p>

                      {/* Program Features */}
                      <div className="space-y-3 mb-8">
                        <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                          <CheckCircle className="h-4 w-4 mr-3 text-green-500" />
                          <span>30 days of structured learning</span>
                        </div>
                        <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                          <Clock className="h-4 w-4 mr-3 text-blue-500" />
                          <span>Daily mock interview sessions</span>
                        </div>
                        <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                          <TrendingUp className="h-4 w-4 mr-3 text-purple-500" />
                          <span>Progress tracking & analytics</span>
                        </div>
                      </div>

                      {isEnrolled(program.id) ? (
                        <Link href={`/app/programs/${program.id}`}>
                          <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className="w-full bg-green-600 hover:bg-green-700 text-white px-6 py-4 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-2"
                          >
                            <Play className="h-5 w-5" />
                            Continue Program
                          </motion.button>
                        </Link>
                      ) : (
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => enrollInProgram(program.id)}
                          disabled={enrolling === program.id}
                          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-4 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-2 disabled:cursor-not-allowed"
                        >
                          {enrolling === program.id ? (
                            <>
                              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                              Enrolling...
                            </>
                          ) : (
                            <>
                              <Plus className="h-5 w-5" />
                              Enroll Now
                            </>
                          )}
                        </motion.button>
                      )}
                    </motion.div>
                  ))}
                </div>
              )}
            </motion.section>
          </div>
        )}
      </div>
    </div>
  );
}
