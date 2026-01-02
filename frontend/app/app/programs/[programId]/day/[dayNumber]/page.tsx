"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { 
  ArrowLeft,
  Calendar, 
  Target, 
  CheckCircle, 
  Clock,
  Play,
  BookOpen,
  Edit,
  Mic,
  MessageCircle,
  ChevronRight
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

export default function DayPage({ params }: { params: Promise<{ programId: string; dayNumber: string }> }) {
  const { programId, dayNumber: dayNumberStr } = use(params);
  const { getToken, isSignedIn } = useAuth();
  const router = useRouter();
  const [enrollment, setEnrollment] = useState<EnrollmentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completingTasks, setCompletingTasks] = useState<Set<string>>(new Set());
  const [completingDay, setCompletingDay] = useState(false);

  const dayNumber = parseInt(dayNumberStr);

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

  const completeTask = async (taskId: string) => {
    if (!enrollment || completingTasks.has(taskId)) return;

    setCompletingTasks(prev => new Set(prev).add(taskId));
    
    try {
      const token = await getToken();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/me/programs/${programId}/tasks/${taskId}/complete`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token && { Authorization: `Bearer ${token}` })
        },
        body: JSON.stringify({})
      });

      if (response.ok) {
        // Update local state
        setEnrollment(prev => prev ? {
          ...prev,
          task_progress: {
            ...prev.task_progress,
            [taskId]: true
          }
        } : null);
      } else {
        setError("Failed to mark task as complete");
      }
    } catch (err) {
      setError("Error completing task");
      console.error("Error completing task:", err);
    } finally {
      setCompletingTasks(prev => {
        const newSet = new Set(prev);
        newSet.delete(taskId);
        return newSet;
      });
    }
  };

  const completeDay = async () => {
    if (!enrollment || completingDay) return;

    setCompletingDay(true);
    
    try {
      const token = await getToken();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/me/programs/${programId}/days/${dayNumber}/complete`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token && { Authorization: `Bearer ${token}` })
        },
        body: JSON.stringify({})
      });

      if (response.ok) {
        // Redirect back to program overview
        router.push(`/app/programs/${programId}`);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Failed to complete day");
      }
    } catch (err) {
      setError("Error completing day");
      console.error("Error completing day:", err);
    } finally {
      setCompletingDay(false);
    }
  };

  const launchMockInterview = (task: Task) => {
    // For now, redirect to the regular interview setup page
    // In the future, this could include metadata about the program task
    const searchParams = new URLSearchParams();
    
    if (task.meta?.durationMin) {
      // Map duration to question count (rough estimation)
      const questionCount = Math.max(3, Math.min(10, Math.floor(task.meta.durationMin / 2)));
      searchParams.set('questions', questionCount.toString());
    }
    
    // Add program metadata (this would be used by the interview system)
    searchParams.set('program_id', programId);
    searchParams.set('task_id', task.id);
    searchParams.set('day_number', dayNumber.toString());
    
    router.push(`/interview/setup?${searchParams.toString()}`);
  };

  const getTaskIcon = (taskType: string) => {
    switch (taskType) {
      case 'read':
        return <BookOpen className="h-5 w-5" />;
      case 'practice':
        return <Edit className="h-5 w-5" />;
      case 'mock_interview':
        return <Mic className="h-5 w-5" />;
      case 'reflection':
        return <MessageCircle className="h-5 w-5" />;
      default:
        return <CheckCircle className="h-5 w-5" />;
    }
  };

  const getTaskColor = (taskType: string) => {
    switch (taskType) {
      case 'read':
        return 'from-blue-500 to-blue-600';
      case 'practice':
        return 'from-green-500 to-green-600';
      case 'mock_interview':
        return 'from-purple-500 to-purple-600';
      case 'reflection':
        return 'from-orange-500 to-orange-600';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  if (!isSignedIn) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center pt-20">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            Please sign in to access this day
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
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading day...</p>
        </div>
      </div>
    );
  }

  if (error || !enrollment) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center pt-20">
        <div className="text-center">
          <div className="text-red-500 mb-4">⚠️ {error || "Day not found"}</div>
          <Link href="/app/programs">
            <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
              Back to Programs
            </button>
          </Link>
        </div>
      </div>
    );
  }

  const day = enrollment.program.days.find(d => d.day_number === dayNumber);
  if (!day) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center pt-20">
        <div className="text-center">
          <div className="text-red-500 mb-4">⚠️ Day {dayNumber} not found</div>
          <Link href={`/app/programs/${programId}`}>
            <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
              Back to Program
            </button>
          </Link>
        </div>
      </div>
    );
  }

  const isTaskCompleted = (taskId: string) => enrollment.task_progress[taskId] || false;
  const allTasksCompleted = day.tasks.every(task => isTaskCompleted(task.id));
  const isDayCompleted = enrollment.completed_days.includes(dayNumber);

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 transition-colors duration-300">
      <div className="max-w-5xl mx-auto px-6 py-8 pt-24">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <Link href={`/app/programs/${programId}`} className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Program
          </Link>
          
          <div className="flex items-start justify-between mb-6">
            <div>
              <div className="flex items-center gap-4 mb-2">
                <span className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 px-3 py-1 rounded-full text-sm font-medium">
                  Day {dayNumber}
                </span>
                {isDayCompleted && (
                  <span className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1">
                    <CheckCircle className="h-3 w-3" />
                    Completed
                  </span>
                )}
              </div>
              <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                {day.title}
              </h1>
              <div className="flex items-center text-gray-600 dark:text-gray-400 mb-4">
                <Target className="h-5 w-5 mr-2" />
                <span>{enrollment.program.target_role}</span>
              </div>
              {day.focus_competencies && day.focus_competencies.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {day.focus_competencies.map((competency, index) => (
                    <span key={index} className="bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 px-2 py-1 rounded text-sm">
                      {competency}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </motion.div>

        {/* Tasks */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="space-y-6"
        >
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Today's Tasks
          </h2>
          
          {day.tasks
            .sort((a, b) => a.sort_order - b.sort_order)
            .map((task, index) => {
              const completed = isTaskCompleted(task.id);
              const isCompleting = completingTasks.has(task.id);
              
              return (
                <motion.div
                  key={task.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  className={`
                    bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700
                    ${completed ? 'ring-2 ring-green-200 dark:ring-green-800' : ''}
                  `}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <div className={`p-2 rounded-lg bg-gradient-to-r ${getTaskColor(task.task_type)} text-white`}>
                          {getTaskIcon(task.task_type)}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                              {task.title}
                            </h3>
                            {completed && <CheckCircle className="h-5 w-5 text-green-500" />}
                          </div>
                          <span className="text-sm text-gray-500 dark:text-gray-400 capitalize">
                            {task.task_type.replace('_', ' ')}
                          </span>
                        </div>
                      </div>
                      
                      {task.details && (
                        <p className="text-gray-600 dark:text-gray-400 mb-4 leading-relaxed">
                          {task.details}
                        </p>
                      )}
                      
                      {task.meta && (
                        <div className="flex flex-wrap gap-4 mb-4 text-sm text-gray-500 dark:text-gray-400">
                          {task.meta.estimatedMinutes && (
                            <div className="flex items-center gap-1">
                              <Clock className="h-4 w-4" />
                              <span>{task.meta.estimatedMinutes} min</span>
                            </div>
                          )}
                          {task.meta.durationMin && (
                            <div className="flex items-center gap-1">
                              <Clock className="h-4 w-4" />
                              <span>{task.meta.durationMin} min interview</span>
                            </div>
                          )}
                          {task.meta.exerciseCount && (
                            <div className="flex items-center gap-1">
                              <Edit className="h-4 w-4" />
                              <span>{task.meta.exerciseCount} exercises</span>
                            </div>
                          )}
                          {task.meta.questionCount && (
                            <div className="flex items-center gap-1">
                              <MessageCircle className="h-4 w-4" />
                              <span>{task.meta.questionCount} questions</span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                    
                    <div className="flex flex-col gap-2 ml-6">
                      {task.task_type === 'mock_interview' && (
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => launchMockInterview(task)}
                          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
                        >
                          <Play className="h-4 w-4" />
                          Start Interview
                        </motion.button>
                      )}
                      
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => completeTask(task.id)}
                        disabled={completed || isCompleting}
                        className={`
                          px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 disabled:cursor-not-allowed
                          ${completed 
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
                            : 'bg-blue-600 hover:bg-blue-700 text-white disabled:bg-blue-400'
                          }
                        `}
                      >
                        {isCompleting ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
                            Marking...
                          </>
                        ) : completed ? (
                          <>
                            <CheckCircle className="h-4 w-4" />
                            Completed
                          </>
                        ) : (
                          <>
                            <CheckCircle className="h-4 w-4" />
                            Mark Complete
                          </>
                        )}
                      </motion.button>
                    </div>
                  </div>
                </motion.div>
              );
            })}
        </motion.div>

        {/* Complete Day Button */}
        {allTasksCompleted && !isDayCompleted && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="mt-8 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl p-8 border border-green-200 dark:border-green-800"
          >
            <div className="text-center">
              <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                🎉 All tasks completed!
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Great job! You've finished all tasks for Day {dayNumber}. Mark this day as complete to continue your journey.
              </p>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={completeDay}
                disabled={completingDay}
                className="bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white px-8 py-4 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-2 mx-auto disabled:cursor-not-allowed"
              >
                {completingDay ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    Completing Day...
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-5 w-5" />
                    Complete Day {dayNumber}
                    <ChevronRight className="h-5 w-5" />
                  </>
                )}
              </motion.button>
            </div>
          </motion.div>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4"
          >
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
