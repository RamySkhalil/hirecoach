"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter, useParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2, Send, User, Bot } from "lucide-react";
import InterviewAvatar from "@/components/InterviewAvatar";
import WhisperVoiceInput from "@/components/WhisperVoiceInput";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ConversationalSessionData {
  sessionId: string;
  jobTitle: string;
  seniority: string;
  totalQuestions: number;
  questionsAsked: number;
  isComplete: boolean;
}

export default function ConversationalInterviewSession() {
  const router = useRouter();
  const params = useParams();
  const sessionId = params.sessionId as string;
  
  // Get query params for job info
  const searchParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
  const jobTitle = searchParams?.get('job_title') || 'Software Engineer';
  const seniority = searchParams?.get('seniority') || 'Senior';
  const numQuestions = parseInt(searchParams?.get('num_questions') || '5');

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [sessionData, setSessionData] = useState<ConversationalSessionData | null>(null);
  const [answer, setAnswer] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load existing conversational session (already started by setup page)
  useEffect(() => {
    const initSession = async () => {
      try {
        // Set session data from URL params
        setSessionData({
          sessionId: sessionId,
          jobTitle: jobTitle,
          seniority: seniority,
          totalQuestions: numQuestions,
          questionsAsked: 0,
          isComplete: false
        });
        
        // Create simple initial greeting
        const greeting = `Hello! Thank you for interviewing for the ${seniority} ${jobTitle} position. Let's begin by having you tell me a bit about yourself and your relevant experience.`;

        // Add AI's opening message to chat
        setMessages([{
          role: "assistant",
          content: greeting,
          timestamp: new Date()
        }]);

        setLoading(false);
      } catch (err: any) {
        setError(err.message || "Failed to initialize interview");
        setLoading(false);
      }
    };

    initSession();
  }, [sessionId, jobTitle, seniority, numQuestions]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sessionData || !answer.trim() || submitting) return;

    setSubmitting(true);
    setError(null);

    // Add user message to chat
    const userMessage: Message = {
      role: "user",
      content: answer,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    // Clear answer immediately for better UX
    setAnswer("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/interview/conversational/answer`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: sessionData.sessionId,
            answer: answer
          })
        }
      );

      if (!response.ok) {
        throw new Error("Failed to submit answer");
      }

      const data = await response.json();

      // Add AI's response to chat
      const aiMessage: Message = {
        role: "assistant",
        content: data.message,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);

      // Update session data
      setSessionData(prev => prev ? {
        ...prev,
        questionsAsked: data.questions_asked,
        isComplete: data.is_complete
      } : null);

      // If interview is complete, show completion message
      if (data.is_complete) {
        setTimeout(() => {
          router.push(`/interview/report/${sessionId}`);
        }, 2000);
      }

      setSubmitting(false);

    } catch (err: any) {
      setError(err.message || "Failed to submit answer");
      setSubmitting(false);
      
      // Add error message to chat
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "Sorry, there was an error processing your answer. Please try again.",
        timestamp: new Date()
      }]);
    }
  };

  // Handle continuous voice transcription
  const handleVoiceTranscript = (text: string) => {
    setAnswer(prev => {
      if (prev && !prev.endsWith(' ') && !prev.endsWith('.')) {
        return prev + ' ' + text;
      }
      return prev + text;
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center pt-20">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Starting your AI interview...</p>
        </div>
      </div>
    );
  }

  if (error && !sessionData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center pt-20">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => router.push("/interview/setup")}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-lg font-medium w-full"
          >
            Back to Setup
          </button>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 pt-20">
      <div className="h-[calc(100vh-5rem)] flex flex-col">
        {/* Progress Bar */}
        <div className="bg-white border-b border-gray-200 px-6 py-3">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-gray-700">
                🤖 Conversational AI Interview
              </span>
              <span className="text-sm font-medium text-blue-600">
                Question {sessionData?.questionsAsked || 0} of {sessionData?.totalQuestions || 5}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <motion.div
                initial={{ width: 0 }}
                animate={{ 
                  width: `${((sessionData?.questionsAsked || 0) / (sessionData?.totalQuestions || 5)) * 100}%` 
                }}
                transition={{ duration: 0.5 }}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 h-2 rounded-full"
              />
            </div>
          </div>
        </div>

        {/* Main Content: Split Screen */}
        <div className="flex-1 overflow-hidden">
          <div className="h-full max-w-7xl mx-auto px-6 py-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Left Side: Avatar */}
            <div className="h-full">
              <InterviewAvatar
                questionText={messages[messages.length - 1]?.role === "assistant" ? messages[messages.length - 1].content : ""}
                questionId={sessionData?.questionsAsked || 0}
                isWaiting={submitting}
              />
            </div>

            {/* Right Side: Conversation */}
            <div className="h-full flex flex-col bg-white rounded-2xl shadow-xl overflow-hidden">
              {/* Chat Header */}
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-4">
                <h2 className="text-lg font-semibold">AI Interview Conversation</h2>
                <p className="text-sm text-blue-100">
                  {sessionData?.jobTitle} • {sessionData?.seniority} Level
                </p>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                <AnimatePresence initial={false}>
                  {messages.map((message, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className={`flex gap-3 ${message.role === "user" ? "flex-row-reverse" : ""}`}
                    >
                      {/* Avatar */}
                      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                        message.role === "assistant"
                          ? "bg-gradient-to-br from-blue-600 to-indigo-600"
                          : "bg-gradient-to-br from-green-500 to-emerald-600"
                      }`}>
                        {message.role === "assistant" ? (
                          <Bot className="h-5 w-5 text-white" />
                        ) : (
                          <User className="h-5 w-5 text-white" />
                        )}
                      </div>

                      {/* Message Bubble */}
                      <div className={`flex-1 max-w-[80%] ${message.role === "user" ? "text-right" : ""}`}>
                        <div className={`inline-block px-4 py-3 rounded-2xl ${
                          message.role === "assistant"
                            ? "bg-gray-100 text-gray-900"
                            : "bg-gradient-to-r from-blue-600 to-indigo-600 text-white"
                        }`}>
                          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        </div>
                        <p className="text-xs text-gray-400 mt-1 px-2">
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="border-t border-gray-200 p-4 bg-gray-50 space-y-3">
                {/* Voice Input */}
                <WhisperVoiceInput
                  onTranscript={handleVoiceTranscript}
                  isActive={voiceEnabled && !submitting && !sessionData?.isComplete}
                  disabled={submitting || sessionData?.isComplete || false}
                />

                <form onSubmit={handleSubmit} className="flex gap-2">
                  {/* Text Input */}
                  <input
                    type="text"
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    placeholder={sessionData?.isComplete ? "Interview complete!" : "Record your answer or type here..."}
                    disabled={submitting || sessionData?.isComplete || false}
                    className="flex-1 px-4 py-3 border border-gray-200 rounded-full focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
                  />

                  {/* Send Button */}
                  <motion.button
                    type="submit"
                    disabled={submitting || !answer.trim() || sessionData?.isComplete || false}
                    whileHover={{ scale: (submitting || !answer.trim() || sessionData?.isComplete) ? 1 : 1.05 }}
                    whileTap={{ scale: (submitting || !answer.trim() || sessionData?.isComplete) ? 1 : 0.95 }}
                    className={`p-3 rounded-full transition-all ${
                      submitting || !answer.trim() || sessionData?.isComplete
                        ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                        : "bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:shadow-lg"
                    }`}
                  >
                    {submitting ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <Send className="h-5 w-5" />
                    )}
                  </motion.button>
                </form>

                {error && (
                  <p className="text-red-600 text-sm mt-2">{error}</p>
                )}

                {sessionData?.isComplete && (
                  <p className="text-green-600 text-sm text-center">
                    ✅ Interview complete! Redirecting to report...
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

