"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Volume2, VolumeX } from "lucide-react";

interface InterviewAvatarProps {
  questionText: string;
  questionId: number;
  isWaiting?: boolean;
}

export default function InterviewAvatar({
  questionText,
  questionId,
  isWaiting = false
}: InterviewAvatarProps) {
  const questionTtsEnabled =
    process.env.NEXT_PUBLIC_ENABLE_QUESTION_TTS === "true";
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [audioError, setAudioError] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const hasPlayedRef = useRef(false);

  // Auto-play question when it changes (only try once to avoid repeated errors)
  useEffect(() => {
    if (
      questionTtsEnabled &&
      questionText &&
      questionId &&
      !hasPlayedRef.current &&
      !audioError
    ) {
      hasPlayedRef.current = true;
      playQuestionAudio();
    }
  }, [questionId, questionTtsEnabled]);

  // Reset on new question
  useEffect(() => {
    hasPlayedRef.current = false;
    setAudioError(null);
  }, [questionId]);

  const playQuestionAudio = async () => {
    if (!questionTtsEnabled) {
      return;
    }

    try {
      setIsPlaying(true);
      setAudioError(null);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/interview/question/${questionId}/audio`
      );

      if (!response.ok) {
        // TTS not available - this is expected without API key
        setAudioError("Voice not configured");
        setIsPlaying(false);
        return;
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);

      const audio = new Audio(audioUrl);
      audioRef.current = audio;
      audio.muted = isMuted;

      audio.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
      };

      audio.onerror = () => {
        setIsPlaying(false);
        setAudioError("Audio playback failed");
        URL.revokeObjectURL(audioUrl);
      };

      await audio.play();
    } catch (err: any) {
      // Silently handle - TTS is optional feature
      setAudioError("Voice not configured");
      setIsPlaying(false);
    }
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
    if (audioRef.current) {
      audioRef.current.muted = !isMuted;
    }
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setIsPlaying(false);
    }
  };

  return (
    <div className="relative h-full bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl overflow-hidden">
      {/* Avatar/Video Area */}
      <div className="absolute inset-0 flex items-center justify-center">
        {/* Animated Avatar Placeholder */}
        <div className="relative">
          {/* Main Avatar Circle */}
          <motion.div
            animate={{
              scale: isPlaying ? [1, 1.05, 1] : 1,
              opacity: isWaiting ? 0.5 : 1,
            }}
            transition={{
              duration: isPlaying ? 1.5 : 0.3,
              repeat: isPlaying ? Infinity : 0,
            }}
            className="w-48 h-48 rounded-full bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 flex items-center justify-center shadow-2xl"
          >
            {/* Inner Circle */}
            <div className="w-40 h-40 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
              {/* AI Icon */}
              <svg
                className="w-20 h-20 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            </div>
          </motion.div>

          {/* Audio Wave Animation */}
          <AnimatePresence>
            {isPlaying && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-16 flex items-end gap-1"
              >
                {[...Array(5)].map((_, i) => (
                  <motion.div
                    key={i}
                    animate={{
                      height: ["12px", "32px", "12px"],
                    }}
                    transition={{
                      duration: 0.8,
                      repeat: Infinity,
                      delay: i * 0.1,
                    }}
                    className="w-2 bg-gradient-to-t from-blue-500 to-indigo-600 rounded-full"
                    style={{ height: "12px" }}
                  />
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Pulse Effect */}
          {isPlaying && (
            <>
              <motion.div
                animate={{
                  scale: [1, 1.5, 1.5],
                  opacity: [0.5, 0, 0],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                }}
                className="absolute inset-0 rounded-full border-4 border-blue-500"
              />
              <motion.div
                animate={{
                  scale: [1, 1.8, 1.8],
                  opacity: [0.3, 0, 0],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  delay: 0.5,
                }}
                className="absolute inset-0 rounded-full border-4 border-indigo-500"
              />
            </>
          )}
        </div>
      </div>

      {/* Controls Overlay */}
      <div className="absolute top-4 right-4 flex gap-2">
        {/* Mute Button */}
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={toggleMute}
          className="p-3 rounded-full bg-black/50 backdrop-blur-sm text-white hover:bg-black/70 transition-all"
          title={isMuted ? "Unmute" : "Mute"}
        >
          {isMuted ? (
            <VolumeX className="h-5 w-5" />
          ) : (
            <Volume2 className="h-5 w-5" />
          )}
        </motion.button>
      </div>

      {/* Status Indicator */}
      <div className="absolute bottom-4 left-4 right-4">
        {isPlaying && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-black/50 backdrop-blur-sm rounded-full px-4 py-2 text-white text-sm text-center"
          >
            🎙️ AI Interviewer is speaking...
          </motion.div>
        )}
        {isWaiting && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-black/50 backdrop-blur-sm rounded-full px-4 py-2 text-white text-sm text-center"
          >
            ⏳ Processing your answer...
          </motion.div>
        )}
        {audioError && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-yellow-500/70 backdrop-blur-sm rounded-lg px-4 py-3 text-white text-xs text-center"
          >
            <div className="font-semibold mb-1">💡 Voice Feature Not Configured</div>
            <div className="text-yellow-100">
              {audioError}. Questions will show as text only.
              <br />
              Add your API key to backend/.env to enable voice.
            </div>
          </motion.div>
        )}
        {!questionTtsEnabled && !audioError && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-black/50 backdrop-blur-sm rounded-full px-4 py-2 text-white text-sm text-center"
          >
            💬 Voice auto-play disabled. Read the question on the right →
          </motion.div>
        )}
        {!isPlaying && !isWaiting && !audioError && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-black/50 backdrop-blur-sm rounded-full px-4 py-2 text-white text-sm text-center"
          >
            💬 Read the question on the right →
          </motion.div>
        )}
      </div>

      {/* Branding */}
      <div className="absolute top-4 left-4">
        <div className="bg-black/50 backdrop-blur-sm rounded-full px-3 py-1 text-white text-xs font-medium">
          AI Interviewer
        </div>
      </div>
    </div>
  );
}

