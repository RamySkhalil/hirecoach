"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import { useAuth } from "@clerk/nextjs";
import { motion } from "framer-motion";
import { 
  ArrowLeft,
  Calendar, 
  Target, 
  CheckCircle, 
  Clock,
  Play,
  Lock,
  Star,
  TrendingUp
} from "lucide-react";

interface Task {
  id: string;
  task_type: string;
  title: string;
  details?: string;
  meta?: any;
  sort_order: number;
}

interface Day {
  id: string;
  day_number: number;
  title: string;
  focus_competencies?: string[];
  tasks: Task[];
}

interface Program {
  id: string;
  slug: string;
  title: string;
  description: string;
  target_role: string;
  difficulty: string;
  days: Day[];
}

interface EnrollmentDetail {
  id: string;
  program: Program;
  status: string;
  progress_percentage: number;
  enrolled_at: string;
  current_day: number;
  task_progress: Record<string, boolean>;
  completed_days: number[];
}

export default function ProgramDetailPage({ params }: { params: Promise<{ programId: string }> }) {
  const { programId } = use(params);
  const { getToken, isSignedIn } = useAuth();
  const [enrollment, setEnrollment] = useState<EnrollmentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isSignedIn && programId) {
      loadEnrollment();
    }
  }, [isSignedIn, programId]);

  const loadEnrollment = async () => {
    try {
      const token = await getToken();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/me/programs/${programId}`, {
        headers: {
          "Content-Type": "application/json",
          ...(token && { Authorization: `Bearer ${token}` })
        }
      });

      if (response.ok) {
        const data = await response.json();
        setEnrollment(data);
      } else {
        setError("Program enrollment not found");
      }
    } catch (err) {
      setError("Error loading program");
      console.error("Error loading enrollment:", err);
    } finally {
      setLoading(false);
    }
  };

  const getDayStatus = (dayNumber: number) => {
    if (!enrollment) return 'locked';
    
    if (enrollment.completed_days.includes(dayNumber)) {
      return 'completed';
    }
    
    if (dayNumber === enrollment.current_day) {
      return 'current';
    }
    
    if (dayNumber <= enrollment.current_day) {
      return 'available';
    }
    
    return 'locked';
  };

  const getDayStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500 text-white border-green-500';
      case 'current':
        return 'bg-blue-500 text-white border-blue-500 ring-4 ring-blue-200';
      case 'available':
        return 'bg-white text-gray-700 border-gray-300 hover:border-blue-300 hover:bg-blue-50';
      case 'locked':
        return 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed';
      default:
        return 'bg-gray-100 text-gray-400 border-gray-200';
    }
  };

  const getDayStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4" />;
      case 'current':
        return <Star className="h-4 w-4" />;
      case 'available':
        return <Play className="h-4 w-4" />;
      case 'locked':
        return <Lock className="h-4 w-4" />;
      default:
        return null;
    }
  };

  if (!isSignedIn) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center pt-20">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            Please sign in to access this program
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

  if (loading) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center pt-20">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading program...</p>
        </div>
      </div>
    );
  }

  if (error || !enrollment) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center pt-20">
        <div className="text-center">
          <div className="text-red-500 mb-4">⚠️ {error || "Program not found"}</div>
          <Link href="/app/programs">
            <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
              Back to Programs
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
          <Link href="/app/programs" className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Programs
          </Link>
          
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                {enrollment.program.title}
              </h1>
              <div className="flex items-center text-gray-600 dark:text-gray-400 mb-4">
                <Target className="h-5 w-5 mr-2" />
                <span className="mr-6">{enrollment.program.target_role}</span>
                <Calendar className="h-5 w-5 mr-2" />
                <span>Day {enrollment.current_day} of 30</span>
              </div>
              <p className="text-lg text-gray-600 dark:text-gray-400 max-w-3xl">
                {enrollment.program.description}
              </p>
            </div>
            
            {/* Progress Card */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 min-w-[280px]">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Overall Progress</span>
                <TrendingUp className="h-5 w-5 text-blue-600" />
              </div>
              <div className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                {Math.round(enrollment.progress_percentage)}%
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 mb-4">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${enrollment.progress_percentage}%` }}
                ></div>
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {enrollment.completed_days.length} of 30 days completed
              </div>
            </div>
          </div>
        </motion.div>

        {/* 30-Day Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 border border-gray-200 dark:border-gray-700"
        >
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">
            30-Day Journey
          </h2>
          
          <div className="grid grid-cols-6 md:grid-cols-10 gap-3">
            {Array.from({ length: 30 }, (_, i) => {
              const dayNumber = i + 1;
              const status = getDayStatus(dayNumber);
              const day = enrollment.program.days.find(d => d.day_number === dayNumber);
              
              return (
                <motion.div
                  key={dayNumber}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3, delay: i * 0.02 }}
                >
                  {status === 'available' || status === 'current' || status === 'completed' ? (
                    <Link href={`/app/programs/${programId}/day/${dayNumber}`}>
                      <div className={`
                        aspect-square rounded-lg border-2 flex flex-col items-center justify-center p-2 transition-all duration-200 cursor-pointer
                        ${getDayStatusColor(status)}
                      `}>
                        <div className="text-sm font-bold mb-1">{dayNumber}</div>
                        <div className="text-xs opacity-75">{getDayStatusIcon(status)}</div>
                      </div>
                    </Link>
                  ) : (
                    <div className={`
                      aspect-square rounded-lg border-2 flex flex-col items-center justify-center p-2 transition-all duration-200
                      ${getDayStatusColor(status)}
                    `}>
                      <div className="text-sm font-bold mb-1">{dayNumber}</div>
                      <div className="text-xs opacity-75">{getDayStatusIcon(status)}</div>
                    </div>
                  )}
                  
                  {day && (
                    <div className="mt-1 text-xs text-center text-gray-600 dark:text-gray-400 leading-tight">
                      {day.title.split(' ').slice(0, 2).join(' ')}
                    </div>
                  )}
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        {/* Today's Suggestion */}
        {enrollment.current_day <= 30 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-8 border border-blue-200 dark:border-blue-800"
          >
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                  Suggested for Today: Day {enrollment.current_day}
                </h3>
                {enrollment.program.days.find(d => d.day_number === enrollment.current_day) && (
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    {enrollment.program.days.find(d => d.day_number === enrollment.current_day)?.title}
                  </p>
                )}
                <p className="text-sm text-gray-500 dark:text-gray-500">
                  Continue where you left off and maintain your momentum
                </p>
              </div>
              
              <Link href={`/app/programs/${programId}/day/${enrollment.current_day}`}>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-2"
                >
                  <Play className="h-5 w-5" />
                  Start Today
                </motion.button>
              </Link>
            </div>
          </motion.div>
        )}

        {/* Legend */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-8 bg-gray-50 dark:bg-gray-900 rounded-xl p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Legend</h3>
          <div className="grid md:grid-cols-4 gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-green-500 flex items-center justify-center">
                <CheckCircle className="h-4 w-4 text-white" />
              </div>
              <span className="text-sm text-gray-600 dark:text-gray-400">Completed</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-500 flex items-center justify-center ring-2 ring-blue-200">
                <Star className="h-4 w-4 text-white" />
              </div>
              <span className="text-sm text-gray-600 dark:text-gray-400">Current Day</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-white border-2 border-gray-300 flex items-center justify-center">
                <Play className="h-4 w-4 text-gray-700" />
              </div>
              <span className="text-sm text-gray-600 dark:text-gray-400">Available</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gray-100 border-2 border-gray-200 flex items-center justify-center">
                <Lock className="h-4 w-4 text-gray-400" />
              </div>
              <span className="text-sm text-gray-600 dark:text-gray-400">Locked</span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
