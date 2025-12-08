"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send,
  Loader2,
  Bot,
  User,
  Sparkles,
  Lightbulb,
  TrendingUp,
  Target,
  BookOpen,
  Briefcase,
  Award,
  MessageSquare,
  Zap,
  FileText,
} from "lucide-react";
import { useAuth } from "@clerk/nextjs";

interface Message {
  role: "user" | "assistant";
  content: string;
  suggestions?: string[];
  action_items?: string[];
  timestamp: Date;
}

interface QuickTip {
  icon: any;
  title: string;
  topic: string;
  color: string;
  gradient: string;
}

export default function CareerAgent() {
  const { getToken } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I'm your AI Career Coach. I'm here to help you with career planning, job search strategies, resume optimization, interview preparation, and professional development. How can I assist you today?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const quickTips: QuickTip[] = [
    {
      icon: FileText,
      title: "Resume Tips",
      topic: "resume",
      color: "blue",
      gradient: "from-blue-500 to-cyan-500",
    },
    {
      icon: MessageSquare,
      title: "Interview Prep",
      topic: "interview",
      color: "purple",
      gradient: "from-purple-500 to-pink-500",
    },
    {
      icon: TrendingUp,
      title: "Salary Negotiation",
      topic: "salary",
      color: "green",
      gradient: "from-green-500 to-emerald-500",
    },
    {
      icon: BookOpen,
      title: "Skill Development",
      topic: "skills",
      color: "orange",
      gradient: "from-orange-500 to-red-500",
    },
  ];

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || input.trim();
    if (!textToSend || loading) return;

    // Add user message
    const userMessage: Message = {
      role: "user",
      content: textToSend,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const token = await getToken();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/career/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token && { Authorization: `Bearer ${token}` }),
          },
          body: JSON.stringify({
            message: textToSend,
            conversation_history: messages.slice(-10).map((m) => ({
              role: m.role,
              content: m.content,
            })),
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      const data = await response.json();

      // Add assistant message
      const assistantMessage: Message = {
        role: "assistant",
        content: data.message,
        suggestions: data.suggestions,
        action_items: data.action_items,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Chat error:", error);
      // Add error message
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "I apologize, but I'm having trouble connecting right now. Please try again in a moment.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickTip = async (topic: string) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/career/quick-tips?topic=${topic}`
      );
      const data = await response.json();
      
      const tipMessage = `Here are quick ${data.topic} tips:\n\n${data.tips.map((tip: string, idx: number) => `${idx + 1}. ${tip}`).join('\n\n')}`;
      
      const assistantMessage: Message = {
        role: "assistant",
        content: tipMessage,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Quick tips error:", error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const suggestedPrompts = [
    "How can I improve my resume?",
    "What skills should I learn for career growth?",
    "Help me prepare for a job interview",
    "How do I negotiate a better salary?",
    "What are the best career paths in tech?",
  ];

  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-indigo-950 dark:to-purple-950 pt-20 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800/80 backdrop-blur-sm rounded-full shadow-lg border border-indigo-200 mb-6">
            <Bot className="h-5 w-5 text-indigo-600" />
            <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">GPT-4o Powered</span>
            <Sparkles className="h-4 w-4 text-indigo-500" />
          </div>
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            AI Career Coach
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Your personal AI mentor for career growth, job search, and professional development
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Chat Section */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-2xl border border-indigo-100 overflow-hidden"
              style={{ height: "calc(100vh - 240px)", minHeight: "600px" }}
            >
              {/* Chat Header */}
              <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white px-6 py-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white dark:bg-gray-800/20 rounded-lg">
                    <Bot className="h-6 w-6" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold">AI Career Coach</h2>
                    <p className="text-sm text-indigo-100">Always here to help • Powered by GPT-4o</p>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6" style={{ height: "calc(100% - 180px)" }}>
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
                      <div
                        className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                          message.role === "assistant"
                            ? "bg-gradient-to-br from-indigo-600 to-purple-600"
                            : "bg-gradient-to-br from-pink-500 to-rose-600"
                        }`}
                      >
                        {message.role === "assistant" ? (
                          <Bot className="h-5 w-5 text-white" />
                        ) : (
                          <User className="h-5 w-5 text-white" />
                        )}
                      </div>

                      {/* Message Content */}
                      <div className={`flex-1 max-w-[80%] ${message.role === "user" ? "text-right" : ""}`}>
                        <div
                          className={`inline-block px-5 py-3 rounded-2xl ${
                            message.role === "assistant"
                              ? "bg-gradient-to-br from-indigo-50 to-purple-50 text-gray-900 dark:text-gray-100 border border-indigo-100"
                              : "bg-gradient-to-r from-pink-600 to-rose-600 text-white"
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                        </div>

                        {/* Suggestions */}
                        {message.suggestions && message.suggestions.length > 0 && (
                          <div className="mt-3 space-y-2">
                            {message.suggestions.map((suggestion, idx) => (
                              <div
                                key={idx}
                                className="inline-flex items-start gap-2 px-4 py-2 bg-purple-50 border border-purple-200 rounded-lg text-sm text-gray-700 dark:text-gray-300"
                              >
                                <Lightbulb className="h-4 w-4 text-purple-600 flex-shrink-0 mt-0.5" />
                                <span>{suggestion}</span>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Action Items */}
                        {message.action_items && message.action_items.length > 0 && (
                          <div className="mt-3 space-y-2">
                            {message.action_items.map((action, idx) => (
                              <div
                                key={idx}
                                className="inline-flex items-start gap-2 px-4 py-2 bg-green-50 border border-green-200 rounded-lg text-sm text-gray-700 dark:text-gray-300"
                              >
                                <Target className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                                <span>{action}</span>
                              </div>
                            ))}
                          </div>
                        )}

                        <p className="text-xs text-gray-400 mt-2 px-2">
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>

                {loading && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex gap-3"
                  >
                    <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center bg-gradient-to-br from-indigo-600 to-purple-600">
                      <Bot className="h-5 w-5 text-white" />
                    </div>
                    <div className="px-5 py-3 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl border border-indigo-100">
                      <Loader2 className="h-5 w-5 text-indigo-600 animate-spin" />
                    </div>
                  </motion.div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="border-t border-indigo-100 p-4 bg-gradient-to-r from-indigo-50 to-purple-50">
                <div className="flex gap-3">
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask me anything about your career..."
                    disabled={loading}
                    className="flex-1 px-4 py-3 border-2 border-indigo-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all outline-none disabled:bg-gray-100 dark:bg-gray-700 disabled:cursor-not-allowed resize-none bg-white dark:bg-gray-800"
                    rows={2}
                  />
                  <motion.button
                    type="button"
                    onClick={() => handleSend()}
                    disabled={loading || !input.trim()}
                    whileHover={{ scale: loading || !input.trim() ? 1 : 1.05 }}
                    whileTap={{ scale: loading || !input.trim() ? 1 : 0.95 }}
                    className={`px-6 rounded-xl font-semibold transition-all flex items-center gap-2 ${
                      loading || !input.trim()
                        ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                        : "bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl"
                    }`}
                  >
                    {loading ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <Send className="h-5 w-5" />
                    )}
                  </motion.button>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Tips */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-indigo-100"
            >
              <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
                <Zap className="h-5 w-5 text-indigo-600" />
                Quick Tips
              </h3>
              <div className="grid grid-cols-2 gap-3">
                {quickTips.map((tip) => (
                  <motion.button
                    key={tip.topic}
                    onClick={() => handleQuickTip(tip.topic)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`p-4 rounded-xl border-2 border-${tip.color}-200 bg-gradient-to-br ${tip.gradient} bg-opacity-10 hover:shadow-lg transition-all text-left`}
                  >
                    <tip.icon className={`h-6 w-6 text-${tip.color}-600 mb-2`} />
                    <div className="text-sm font-semibold text-gray-900 dark:text-gray-100">{tip.title}</div>
                  </motion.button>
                ))}
              </div>
            </motion.div>

            {/* Suggested Prompts */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-indigo-100"
            >
              <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-indigo-600" />
                Try Asking
              </h3>
              <div className="space-y-2">
                {suggestedPrompts.map((prompt, idx) => (
                  <motion.button
                    key={idx}
                    onClick={() => handleSend(prompt)}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="w-full text-left px-4 py-3 bg-gradient-to-r from-indigo-50 to-purple-50 hover:from-indigo-100 hover:to-purple-100 border border-indigo-200 rounded-lg text-sm text-gray-700 dark:text-gray-300 transition-all"
                  >
                    {prompt}
                  </motion.button>
                ))}
              </div>
            </motion.div>

            {/* Features */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
              className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl shadow-xl p-6 border-2 border-indigo-200"
            >
              <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">What I Can Help With</h3>
              <div className="space-y-3">
                {[
                  { icon: Briefcase, text: "Career path guidance" },
                  { icon: TrendingUp, text: "Job search strategies" },
                  { icon: Award, text: "Skills development" },
                  { icon: Target, text: "Interview preparation" },
                  { icon: BookOpen, text: "Resume optimization" },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center gap-3 text-sm text-gray-700 dark:text-gray-300">
                    <item.icon className="h-5 w-5 text-indigo-600" />
                    <span>{item.text}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </main>
  );
}

