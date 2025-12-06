"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { Mic, MicOff, Loader2, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";

interface WhisperVoiceInputProps {
  onTranscript: (text: string) => void;
  isActive: boolean;
  disabled?: boolean;
}

/**
 * Production-ready voice input using OpenAI Whisper for transcription.
 * 
 * Features:
 * - MediaRecorder API for audio capture
 * - Automatic silence detection
 * - OpenAI Whisper transcription
 * - Visual feedback during recording and transcription
 * - Error handling and recovery
 */
export default function WhisperVoiceInput({
  onTranscript,
  isActive,
  disabled = false
}: WhisperVoiceInputProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [volume, setVolume] = useState(0);
  const [silenceDetected, setSilenceDetected] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Silence detection threshold and duration
  const SILENCE_THRESHOLD = 0.05; // Volume threshold (0-1) - increased from 0.01 for better detection
  const SILENCE_DURATION = 2000; // 2 seconds of silence triggers auto-stop

  /**
   * Start recording audio from the microphone
   */
  const startRecording = useCallback(async () => {
    console.log('[Whisper] startRecording called, current state:', { isRecording, isTranscribing, isActive, disabled });
    try {
      setError(null);
      audioChunksRef.current = [];

      // Check if mediaDevices is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError("Your browser doesn't support audio recording. Please use Chrome, Edge, or Safari and access via localhost.");
        console.error('[Whisper] mediaDevices not supported');
        return;
      }

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      streamRef.current = stream;

      // Set up audio context for volume monitoring
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      analyser.fftSize = 256;

      audioContextRef.current = audioContext;
      analyserRef.current = analyser;

      // Start volume monitoring
      monitorVolume();

      // Create MediaRecorder
      const mimeType = getSupportedMimeType();
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType,
        audioBitsPerSecond: 128000,
      });

      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        console.log("[Whisper] Recording stopped, processing...");
        await processRecording();
      };

      mediaRecorder.onerror = (event: any) => {
        console.error("[Whisper] MediaRecorder error:", event.error);
        setError("Recording failed. Please try again.");
        stopRecording();
      };

      mediaRecorder.start(100); // Collect data every 100ms
      setIsRecording(true);
      setSilenceDetected(false);

      console.log("[Whisper] ✅ Recording started successfully with", mimeType);
      console.log("[Whisper] MediaRecorder state:", mediaRecorder.state);

    } catch (err: any) {
      console.error("[Whisper] Failed to start recording:", err);
      
      if (err.name === "NotAllowedError") {
        setError("Microphone access denied. Please allow microphone permission.");
      } else if (err.name === "NotFoundError") {
        setError("No microphone found. Please connect a microphone.");
      } else {
        setError("Failed to access microphone. Please check your browser settings.");
      }
    }
  }, [isRecording, isTranscribing, isActive, disabled]);

  /**
   * Stop recording and trigger transcription
   */
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }

    // Stop all audio tracks
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    // Stop audio context
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    // Cancel animation frame
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    // Cancel silence timeout
    if (silenceTimeoutRef.current) {
      clearTimeout(silenceTimeoutRef.current);
      silenceTimeoutRef.current = null;
    }

    setVolume(0);
    setSilenceDetected(false);
    
    console.log('[Whisper] stopRecording completed');
  }, [isRecording]);

  /**
   * Monitor audio volume for visual feedback and silence detection
   */
  const monitorVolume = () => {
    if (!analyserRef.current) return;

    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const checkVolume = () => {
      if (!analyserRef.current) return;

      analyserRef.current.getByteFrequencyData(dataArray);

      // Calculate average volume (0-255)
      const average = dataArray.reduce((sum, value) => sum + value, 0) / bufferLength;
      const normalizedVolume = average / 255; // Normalize to 0-1

      setVolume(normalizedVolume);
      
      // Log volume periodically (every ~1 second)
      if (Math.random() < 0.02) {
        console.log(`[Whisper] 📊 Volume: ${(normalizedVolume * 100).toFixed(1)}% (threshold: ${(SILENCE_THRESHOLD * 100).toFixed(1)}%)`);
      }

      // Silence detection
      if (normalizedVolume < SILENCE_THRESHOLD) {
        if (!silenceTimeoutRef.current) {
          silenceTimeoutRef.current = setTimeout(() => {
            console.log("[Whisper] Silence detected, auto-stopping...");
            setSilenceDetected(true);
            stopRecording();
          }, SILENCE_DURATION);
        }
      } else {
        // Reset silence timeout if sound detected
        if (silenceTimeoutRef.current) {
          clearTimeout(silenceTimeoutRef.current);
          silenceTimeoutRef.current = null;
        }
        setSilenceDetected(false);
      }

      animationFrameRef.current = requestAnimationFrame(checkVolume);
    };

    checkVolume();
  };

  /**
   * Process recorded audio and send to Whisper API
   */
  const processRecording = async () => {
    console.log(`[Whisper] processRecording called, chunks: ${audioChunksRef.current.length}`);
    
    if (audioChunksRef.current.length === 0) {
      console.warn("[Whisper] ⚠️ No audio data recorded - chunks array is empty");
      // Auto-restart if still active (continuous mode)
      if (isActive && !disabled) {
        console.log("[Whisper] Auto-restarting due to empty chunks...");
        setTimeout(() => startRecording(), 500);
      }
      return;
    }

    setIsTranscribing(true);
    console.log("[Whisper] 📤 Starting transcription process...");

    try {
      // Create audio blob from chunks
      const mimeType = getSupportedMimeType();
      const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });

      console.log(`[Whisper] 📦 Created blob: ${audioBlob.size} bytes, type: ${mimeType}`);
      console.log(`[Whisper] 🌐 Sending to /api/transcribe...`);

      // Send to Whisper API
      const transcript = await transcribeAudio(audioBlob);

      console.log(`[Whisper] 📝 Received transcript: "${transcript}"`);

      if (transcript && transcript.trim().length > 0) {
        console.log("[Whisper] ✅ Valid transcription, calling onTranscript");
        onTranscript(transcript);
      } else {
        console.warn("[Whisper] ⚠️ Empty transcription received");
        // Don't show error for empty transcription in continuous mode
      }

    } catch (err: any) {
      console.error("[Whisper] ❌ Transcription failed:", err);
      setError(err.message || "Transcription failed. Please try again.");
    } finally {
      setIsTranscribing(false);
      audioChunksRef.current = [];
      console.log("[Whisper] 🔄 Transcription complete, clearing chunks");
      
      // Auto-restart recording if still active (continuous mode like LiveKit)
      if (isActive && !disabled) {
        console.log("[Whisper] 🔄 Auto-restarting recording (continuous mode)");
        setTimeout(() => startRecording(), 500);
      } else {
        console.log("[Whisper] ⏸️ Not restarting (isActive:", isActive, "disabled:", disabled, ")");
      }
    }
  };

  /**
   * Send audio blob to OpenAI Whisper API
   */
  const transcribeAudio = async (blob: Blob): Promise<string> => {
    const formData = new FormData();
    // Next.js API route `/api/transcribe` expects field name "file"
    formData.append("file", blob, "audio.webm");

    const response = await fetch(`/api/transcribe`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('[Whisper] API Error Response:', errorData);
      console.error('[Whisper] Status:', response.status, response.statusText);
      
      const errorMsg = errorData.error || `Transcription failed: ${response.statusText}`;
      const details = errorData.details ? `\nDetails: ${errorData.details}` : '';
      const hint = errorData.hint ? `\nHint: ${errorData.hint}` : '';
      
      throw new Error(`${errorMsg}${details}${hint}`);
    }

    const data = await response.json();
    return data.text || "";
  };

  /**
   * Get the best supported MIME type for MediaRecorder
   */
  const getSupportedMimeType = (): string => {
    const types = [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/ogg;codecs=opus",
      "audio/ogg",
      "audio/mp4",
      "audio/wav",
    ];

    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        return type;
      }
    }

    return ""; // Browser will use default
  };

  // Handle isActive prop changes - AUTO-START recording when active
  useEffect(() => {
    if (isActive && !disabled && !isRecording && !isTranscribing) {
      // Auto-start recording when active (continuous mode like LiveKit)
      console.log('[Whisper] Auto-starting recording (continuous mode)');
      startRecording();
    } else if (!isActive && isRecording) {
      console.log('[Whisper] Stopping recording (inactive)');
      stopRecording();
    }
  }, [isActive, disabled, isRecording, isTranscribing, startRecording, stopRecording]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopRecording();
    };
  }, []);

  return (
    <div className="flex flex-col gap-2">
      {/* Auto-Recording Status with Manual Stop Button */}
      <div className="flex items-center gap-3">
        {/* Status Indicator */}
        <div className={`p-3 rounded-full ${
          isTranscribing
            ? "bg-blue-100"
            : isRecording
            ? "bg-red-100"
            : "bg-gray-100"
        }`}>
          {isTranscribing ? (
            <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
          ) : isRecording ? (
            <Mic className="h-5 w-5 text-red-600 animate-pulse" />
          ) : (
            <Mic className="h-5 w-5 text-gray-400" />
          )}
        </div>

        {/* Status Text */}
        <div className="flex-1">
          {isTranscribing ? (
            <p className="text-sm text-blue-600 font-medium flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              Transcribing your answer...
            </p>
          ) : isRecording ? (
            <p className="text-sm text-red-600 font-medium flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-red-600 rounded-full animate-pulse" />
              🎤 Listening... (auto-stops after 2s silence)
            </p>
          ) : (
            <p className="text-sm text-gray-600">
              Voice recording active - speak naturally
            </p>
          )}
        </div>
        
        {/* Manual Stop Button (backup if silence detection doesn't work) */}
        {isRecording && !isTranscribing && (
          <motion.button
            type="button"
            onClick={stopRecording}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-3 py-1.5 bg-red-600 text-white text-xs rounded-full hover:bg-red-700 transition-colors"
          >
            Stop & Transcribe
          </motion.button>
        )}
      </div>

      {/* Volume Indicator */}
      {isRecording && (
        <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-blue-500 to-indigo-600"
            initial={{ width: 0 }}
            animate={{ width: `${volume * 100}%` }}
            transition={{ duration: 0.1 }}
          />
        </div>
      )}

      {/* Silence Detection Warning */}
      {silenceDetected && (
        <p className="text-xs text-orange-600">
          Silence detected - recording will stop automatically
        </p>
      )}

      {/* Error Message */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg"
        >
          <AlertCircle className="h-4 w-4 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm text-red-800">{error}</p>
            <button
              onClick={() => setError(null)}
              className="text-xs text-red-600 hover:text-red-800 underline mt-1"
            >
              Dismiss
            </button>
          </div>
        </motion.div>
      )}

      {/* Browser Support Check */}
      {typeof window !== "undefined" &&
        !navigator.mediaDevices?.getUserMedia && (
          <p className="text-xs text-orange-600">
            ⚠️ Your browser may not support audio recording. Use Chrome, Edge,
            or Safari for best results.
          </p>
        )}
    </div>
  );
}

