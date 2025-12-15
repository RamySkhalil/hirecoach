"use client";

import { useState, useRef, useEffect } from "react";
import { MessageSquare, X, Send, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@clerk/nextjs";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const STORAGE_KEY = "linda_chat_conversation_id";

export default function LindaChat() {
  const { getToken, isSignedIn, userId } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [hasLoadedInitialHistory, setHasLoadedInitialHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Load conversation ID from localStorage on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedId = localStorage.getItem(STORAGE_KEY);
      if (storedId) {
        setConversationId(storedId);
      }
    }
  }, []);

  // Save conversation ID to localStorage whenever it changes
  useEffect(() => {
    if (typeof window !== "undefined" && conversationId) {
      localStorage.setItem(STORAGE_KEY, conversationId);
    }
  }, [conversationId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Load conversation history when opening chat
  useEffect(() => {
    const loadHistory = async () => {
      if (!isOpen) {
        // Reset loading flag when chat is closed
        setHasLoadedInitialHistory(false);
        return;
      }

      // If we've already loaded history for this conversation, don't reload
      if (hasLoadedInitialHistory && messages.length > 0) {
        return;
      }

      // For authenticated users without a conversation_id, try to get the most recent conversation
      if (isSignedIn && !conversationId) {
        setIsLoadingHistory(true);
        try {
          const token = await getToken();
          // Try to get the most recent conversation
          const conversationsResponse = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/support/conversations?limit=1`,
            {
              method: "GET",
              headers: {
                "Content-Type": "application/json",
                ...(token && { Authorization: `Bearer ${token}` }),
              },
            }
          );

          if (conversationsResponse.ok) {
            const conversationsData = await conversationsResponse.json();
            if (conversationsData.conversations && conversationsData.conversations.length > 0) {
              const recentConvId = conversationsData.conversations[0].conversation_id;
              setConversationId(recentConvId);
              if (typeof window !== "undefined") {
                localStorage.setItem(STORAGE_KEY, recentConvId);
              }
              // Load messages for this conversation
              const historyResponse = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/support/history?conversation_id=${recentConvId}`,
                {
                  method: "GET",
                  headers: {
                    "Content-Type": "application/json",
                    ...(token && { Authorization: `Bearer ${token}` }),
                  },
                }
              );

              if (historyResponse.ok) {
                const historyData = await historyResponse.json();
                if (historyData.messages && historyData.messages.length > 0) {
                  setMessages(historyData.messages);
                  setHasLoadedInitialHistory(true);
                  setIsLoadingHistory(false);
                  return;
                }
              }
            }
          }
        } catch (error) {
          console.error("Failed to load recent conversation:", error);
        } finally {
          setIsLoadingHistory(false);
        }
      }

      // Load history if we have a conversation_id
      if (conversationId) {
        setIsLoadingHistory(true);
        try {
          const token = await getToken();
          const response = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/support/history?conversation_id=${conversationId}`,
            {
              method: "GET",
              headers: {
                "Content-Type": "application/json",
                ...(token && { Authorization: `Bearer ${token}` }),
              },
            }
          );

          if (response.ok) {
            const data = await response.json();
            if (data.messages && data.messages.length > 0) {
              setMessages(data.messages);
            } else {
              // No history found, show welcome message
              setMessages([
                {
                  role: "assistant",
                  content: "Hi! I'm Linda, your Interviewly support assistant. How can I help you with our platform today?",
                },
              ]);
            }
          } else {
            // If history load fails, show welcome message
            if (messages.length === 0) {
              setMessages([
                {
                  role: "assistant",
                  content: "Hi! I'm Linda, your Interviewly support assistant. How can I help you with our platform today?",
                },
              ]);
            }
          }
        } catch (error) {
          console.error("Failed to load conversation history:", error);
          if (messages.length === 0) {
            setMessages([
              {
                role: "assistant",
                content: "Hi! I'm Linda, your Interviewly support assistant. How can I help you with our platform today?",
              },
            ]);
          }
        } finally {
          setIsLoadingHistory(false);
          setHasLoadedInitialHistory(true);
        }
      } else {
        // No conversation ID and not authenticated or no recent conversation found
        if (messages.length === 0) {
          setMessages([
            {
              role: "assistant",
              content: "Hi! I'm Linda, your Interviewly support assistant. How can I help you with our platform today?",
            },
          ]);
          setHasLoadedInitialHistory(true);
        }
      }
    };

    loadHistory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, conversationId, isSignedIn]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const token = await getToken();
      
      // Build conversation history (only for non-authenticated users or fallback)
      const conversationHistory = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/support/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token && { Authorization: `Bearer ${token}` }),
          },
          body: JSON.stringify({
            message: userMessage,
            conversation_history: conversationHistory,
            conversation_id: conversationId,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to get response from Linda");
      }

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.message },
      ]);
      
      // Update conversation ID if returned (for new conversations)
      if (data.conversation_id) {
        setConversationId(data.conversation_id);
        if (typeof window !== "undefined") {
          localStorage.setItem(STORAGE_KEY, data.conversation_id);
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "I'm sorry, I'm having trouble connecting right now. Please try again in a moment.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Chat Button */}
      {!isOpen && (
        <motion.button
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 rounded-full shadow-2xl hover:shadow-3xl transition-all duration-300 flex items-center justify-center group"
          aria-label="Open chat with Linda"
        >
          <MessageSquare className="h-6 w-6 group-hover:scale-110 transition-transform" />
          <span className="absolute -top-1 -right-1 h-3 w-3 bg-green-400 rounded-full animate-pulse"></span>
        </motion.button>
      )}

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            className="fixed bottom-6 right-6 z-50 w-96 h-[600px] bg-white dark:bg-gray-800 rounded-2xl shadow-2xl flex flex-col border border-gray-200 dark:border-gray-700"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 rounded-t-2xl flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-white/20 flex items-center justify-center">
                  <MessageSquare className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-semibold">Linda</h3>
                  <p className="text-xs text-blue-100">Support Assistant</p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="hover:bg-white/20 rounded-full p-1 transition-colors"
                aria-label="Close chat"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {isLoadingHistory && (
                <div className="flex justify-center items-center py-4">
                  <Loader2 className="h-5 w-5 animate-spin text-gray-400" />
                </div>
              )}
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                      message.role === "user"
                        ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white"
                        : "bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    }`}
                  >
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">
                      {message.content}
                    </p>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl px-4 py-2">
                    <Loader2 className="h-5 w-5 animate-spin text-gray-400" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700">
              <div className="flex gap-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  disabled={isLoading}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white disabled:opacity-50"
                />
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-4 py-2 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {isLoading ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Send className="h-5 w-5" />
                  )}
                </button>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
                Linda can help with Interviewly questions only
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

