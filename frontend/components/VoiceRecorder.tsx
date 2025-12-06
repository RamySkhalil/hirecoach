"use client";

import { useState, useRef, useEffect } from "react";
import { Mic, MicOff, Loader2, Volume2, VolumeX } from "lucide-react";
import { motion } from "framer-motion";

interface VoiceRecorderProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
  questionId?: number;
  questionText?: string;
}

export default function VoiceRecorder({
  onTranscript,
  disabled = false,
  questionId,
  questionText
}: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isPlayingQuestion, setIsPlayingQuestion] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    // Cleanup audio on unmount
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      setError(null);

      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError("Your browser does not support audio recording.");
        return;
      }
      
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Let the browser choose the mimeType (more robust than forcing webm/mp4)
      const mediaRecorder = new MediaRecorder(stream);
      console.log("[Recorder] Using mimeType:", mediaRecorder.mimeType);
      
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
        
        // Convert to blob and send to backend
        const audioBlob = new Blob(audioChunksRef.current, { 
          type: mediaRecorder.mimeType 
        });

        console.log("[Recorder] Final blob:", {
          size: audioBlob.size,
          type: audioBlob.type
        });

        if (audioBlob.size < 1000) {
          console.warn("[Recorder] Blob too small, skipping STT");
          setError("Recorded audio is too short or empty. Please try again and speak for 2–3 seconds.");
          setIsProcessing(false);
          return;
        }
        
        await transcribeAudio(audioBlob);
      };
      
      mediaRecorder.onerror = (event: any) => {
        console.error("[Recorder] MediaRecorder error:", event.error);
        setError("Recording failed. Please try again.");
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(); // default timeslice
      console.log("[Recorder] Recording started");
      setIsRecording(true);
      
    } catch (err: any) {
      console.error("Error starting recording:", err);
      setError("Failed to access microphone. Please check permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      console.log("[Recorder] Stopping recording");
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsProcessing(true);
    }
  };

  const transcribeAudio = async (audioBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");

      console.log("[Recorder] Sending to /media/stt:", {
        size: audioBlob.size,
        type: audioBlob.type
      });
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/media/stt`, {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to transcribe audio");
      }
      
      const data = await response.json();
      
      // Check if the response text contains error messages from backend
      if (
        data.text &&
        (data.text.includes("not configured") ||
          data.text.includes("Deepgram not") ||
          data.text.includes("Please add") ||
          data.text.includes("error"))
      ) {
        setError(data.text);
        return;
      }
      
      onTranscript(data.text);
      
    } catch (err: any) {
      console.error("Transcription error:", err);
      setError(
        err.message ||
          "Failed to transcribe audio. Please try again or type your answer."
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const playQuestionAudio = async () => {
    if (!questionId) return;
    
    try {
      setIsPlayingQuestion(true);
      setError(null);
      
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/interview/question/${questionId}/audio`
      );
      
      if (!response.ok) {
        throw new Error("Failed to get question audio");
      }
      
      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      
      // Create and play audio
      const audio = new Audio(audioUrl);
      audioRef.current = audio;
      
      audio.onended = () => {
        setIsPlayingQuestion(false);
        URL.revokeObjectURL(audioUrl);
      };
      
      audio.onerror = () => {
        setIsPlayingQuestion(false);
        setError("Failed to play audio");
        URL.revokeObjectURL(audioUrl);
      };
      
      await audio.play();
      
    } catch (err: any) {
      console.error("Error playing question audio:", err);
      setError("Text-to-speech not available. Please read the question.");
      setIsPlayingQuestion(false);
    }
  };

  const stopQuestionAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setIsPlayingQuestion(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Voice Controls */}
      <div className="flex items-center justify-center gap-4">
        {/* Play Question Audio Button */}
        {questionId && (
          <motion.button
            type="button"
            onClick={isPlayingQuestion ? stopQuestionAudio : playQuestionAudio}
            disabled={disabled || isRecording || isProcessing}
            whileHover={{ scale: disabled || isRecording || isProcessing ? 1 : 1.1 }}
            whileTap={{ scale: disabled || isRecording || isProcessing ? 1 : 0.9 }}
            className={`p-4 rounded-full transition-all duration-300 ${
              isPlayingQuestion
                ? "bg-gradient-to-r from-orange-500 to-red-600 text-white animate-pulse"
                : disabled || isRecording || isProcessing
                ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                : "bg-gradient-to-r from-blue-500 to-indigo-600 text-white hover:shadow-xl"
            }`}
            title={isPlayingQuestion ? "Stop audio" : "Listen to question"}
          >
            {isPlayingQuestion ? (
              <VolumeX className="h-6 w-6" />
            ) : (
              <Volume2 className="h-6 w-6" />
            )}
          </motion.button>
        )}

        {/* Record Answer Button */}
        <motion.button
          type="button"
          onClick={isRecording ? stopRecording : startRecording}
          disabled={disabled || isProcessing || isPlayingQuestion}
          whileHover={{ scale: disabled || isProcessing || isPlayingQuestion ? 1 : 1.1 }}
          whileTap={{ scale: disabled || isProcessing || isPlayingQuestion ? 1 : 0.9 }}
          className={`p-6 rounded-full transition-all duration-300 ${
            isRecording
              ? "bg-gradient-to-r from-red-500 to-red-600 text-white animate-pulse shadow-2xl"
              : disabled || isProcessing || isPlayingQuestion
              ? "bg-gray-200 text-gray-400 cursor-not-allowed"
              : "bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:shadow-xl"
          }`}
          title={isRecording ? "Stop recording" : "Start recording answer"}
        >
          {isProcessing ? (
            <Loader2 className="h-8 w-8 animate-spin" />
          ) : isRecording ? (
            <MicOff className="h-8 w-8" />
          ) : (
            <Mic className="h-8 w-8" />
          )}
        </motion.button>
      </div>

      {/* Status Text */}
      <div className="text-center">
        {isRecording && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-red-600 font-medium"
          >
            🎤 Recording... Click again to stop
          </motion.p>
        )}
        {isProcessing && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-blue-600 font-medium"
          >
            Processing your answer...
          </motion.p>
        )}
        {isPlayingQuestion && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-indigo-600 font-medium"
          >
            🔊 Playing question...
          </motion.p>
        )}
        {!isRecording && !isProcessing && !isPlayingQuestion && (
          <p className="text-gray-500 text-sm">
            Click the microphone to record your answer
          </p>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm"
        >
          {error}
        </motion.div>
      )}

      {/* Info */}
      <div className="text-center text-xs text-gray-400">
        <p>🎧 Use headphones for best experience</p>
        <p>Voice features require API keys (STT: Whisper, TTS: OpenAI)</p>
      </div>
    </div>
  );
}
