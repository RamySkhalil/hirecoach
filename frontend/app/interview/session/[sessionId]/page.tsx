"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth, useUser } from "@clerk/nextjs";
import { motion, AnimatePresence } from "framer-motion";
import {
  Loader2,
  User,
  Bot,
  Video,
  VideoOff,
  Mic,
  Volume2,
  LogOut,
} from "lucide-react";
import { getSession } from "@/lib/api";

// LiveKit imports
import { 
  RoomAudioRenderer, 
  ControlBar, 
  GridLayout,
  ParticipantTile,
  useTracks,
  RoomContext 
} from "@livekit/components-react";
import { Room, Track } from "livekit-client";
import "@livekit/components-styles";

interface Message {
  role: "agent" | "user";
  content: string;
  score?: number;
  timestamp: Date;
}

export default function InterviewSession() {
  const router = useRouter();
  const params = useParams();
  const { getToken } = useAuth();
  const { user } = useUser();
  const sessionId = params.sessionId as string;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [leaving, setLeaving] = useState(false);

  const [totalQuestions, setTotalQuestions] = useState(0);
  const [currentIndex, setCurrentIndex] = useState(0);

  const [messages, setMessages] = useState<Message[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // LiveKit state
  const [livekitToken, setLivekitToken] = useState<string | null>(null);
  const [livekitUrl, setLivekitUrl] = useState<string | null>(null);
  const [livekitRoomName, setLivekitRoomName] = useState<string | null>(null);
  const [livekitError, setLivekitError] = useState<string | null>(null);
  const [videoEnabled, setVideoEnabled] = useState(true);
  const [isConnected, setIsConnected] = useState(false);  // Track connection state
  
  // Use ref to track handler registration (persists across renders without causing re-renders)
  const transcriptionHandlerRegistered = useRef(false);
  
  // LiveKit Room instance with optimized audio config
  const [roomInstance] = useState(() => new Room({
    adaptiveStream: true,
    dynacast: true,
  }));

  // Auto-scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load session details and LiveKit token on mount
  useEffect(() => {
    const loadSession = async () => {
      try {
        const token = await getToken();
        const session = await getSession(sessionId, token);
        setTotalQuestions(session.num_questions);
        setCurrentIndex(1); // Start at question 1
        setLoading(false);
      } catch (err: any) {
        setError(err.message || "Failed to load session");
        setLoading(false);
      }
    };

    const connectToLiveKit = async () => {
      if (!sessionId) return;
      
      // Prevent duplicate connections
      if (roomInstance.state === 'connected' || roomInstance.state === 'connecting') {
        console.log('⚠️ Already connected/connecting to LiveKit, skipping...');
        return;
      }
      
      try {
        const authToken = await getToken();
        const participantName = user?.fullName || user?.firstName || "Candidate";
        
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/livekit/token`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
            },
            body: JSON.stringify({
              session_id: sessionId,
              participant_name: participantName,
            }),
          }
        );

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: "Failed to get LiveKit token" }));
          throw new Error(errorData.detail || "Failed to connect to video room");
        }

        const data = await response.json();
        
        // Room name is interview-{sessionId} and must match the dispatch rule in LiveKit Cloud
        // and the Python agent (agent.py) so the AI interviewer joins this room.
        
        // Connect to the room with the token
        await roomInstance.connect(data.url, data.token);
        
        // Listen for room disconnection (when agent ends interview)
        roomInstance.on('disconnected', () => {
          console.log('🔚 Room disconnected - redirecting to report...');
          // Small delay to ensure backend saves the transcript
          setTimeout(() => {
            router.push(`/interview/report/${sessionId}`);
          }, 1000);
        });
        
        // Listen for transcription text streams (only register once per room instance)
        if (!transcriptionHandlerRegistered.current) {
          console.log('📝 Registering transcription handler...');
          roomInstance.registerTextStreamHandler('lk.transcription', async (reader, participantInfo) => {
            try {
              const message = await reader.readAll();
              
              // Check if this is a transcription by looking for transcription attributes
              const attributes = reader.info.attributes || {};
              const hasTranscriptionAttributes = 
                attributes['lk.segment_id'] || 
                attributes['lk.transcription_final'] ||
                attributes['lk.transcribed_track_id'];
              
              const isFinal = attributes['lk.transcription_final'] === 'true';
              
              console.log('🎤 Raw transcription event:', {
                message: message.substring(0, 50),
                participantIdentity: participantInfo.identity,
                participantName: participantInfo.name,
                hasTranscriptionAttributes,
                isFinal,
                attributes
              });
              
              if (hasTranscriptionAttributes && message && message.trim().length > 0) {
                // Determine if this is the agent/avatar speaking
                const participantIdentity = participantInfo.identity || '';
                const participantName = participantInfo.name || '';
                
                // The avatar or agent participant (identity starts with "agent-")
                const isAgent = 
                  participantIdentity.startsWith('agent-') ||
                  participantIdentity.includes('hedra') ||
                  participantIdentity.includes('avatar') ||
                  participantName.includes('Interview Coach') ||
                  participantName.includes('Agent');
                
                console.log('📝 Transcription processed:', {
                  text: message.substring(0, 50) + '...',
                  identity: participantIdentity,
                  name: participantName,
                  isAgent,
                  isFinal
                });

                // Only add final transcriptions to avoid duplicates
                if (isFinal) {
                  const newMessage: Message = {
                    role: isAgent ? "agent" : "user",
                    content: message,
                    timestamp: new Date()
                  };
                  
                  console.log('✅ Adding message to UI:', newMessage.role, '-', message.substring(0, 30));
                  
                  setMessages(prev => {
                    // Avoid adding duplicate messages
                    const isDuplicate = prev.some(m => 
                      m.content === newMessage.content && 
                      m.role === newMessage.role &&
                      Math.abs(m.timestamp.getTime() - newMessage.timestamp.getTime()) < 1000
                    );
                    
                    if (isDuplicate) {
                      console.log('⚠️ Duplicate message, skipping');
                      return prev;
                    }
                    return [...prev, newMessage];
                  });
                }
              }
            } catch (error) {
              console.error('Error reading transcription stream:', error);
            }
          });
          transcriptionHandlerRegistered.current = true;
          console.log('✅ Transcription handler registered');
        }
        
        // Only set state AFTER successful connection
        setLivekitToken(data.token);
        setLivekitUrl(data.url);
        setLivekitRoomName(data.room_name);
        setIsConnected(true);  // Mark as connected AFTER successful connection
        
        console.log("✅ LiveKit connected:", {
          room: data.room_name,
          url: data.url,
        });
      } catch (err: any) {
        console.error("❌ LiveKit connection error:", err);
        setLivekitError(err.message || "Video unavailable");
        // Don't fail the entire interview if LiveKit fails - fallback to text mode
      }
    };

    loadSession();
    connectToLiveKit();
    
    return () => {
      transcriptionHandlerRegistered.current = false;
      roomInstance.disconnect();
    };
  }, [sessionId, router, getToken, user, roomInstance]);

  const handleLeaveInterview = async () => {
    console.log('👋 Leaving interview - saving progress...');
    setLeaving(true);
    
    try {
      // Disconnect from LiveKit - this triggers backend save
      roomInstance.disconnect();
      console.log('⏳ Disconnected from LiveKit, waiting for transcript to save...');
      
      // Poll the report endpoint to check if transcript is saved and report is ready
      const maxAttempts = 10; // Try for up to 5 seconds (10 * 500ms)
      const pollInterval = 500; // Check every 500ms
      let reportReady = false;
      
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const token = await getToken();
      
      for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        console.log(`   Polling attempt ${attempt}/${maxAttempts}...`);
        
        try {
          const response = await fetch(
            `${apiUrl}/interview/session/${sessionId}/report`,
            {
              headers: token ? { Authorization: `Bearer ${token}` } : {}
            }
          );
          
          if (response.ok) {
            const data = await response.json();
            
            // Check if report is ready (has summary)
            if (data.summary) {
              console.log('✅ Report is ready!');
              reportReady = true;
              break;
            } else if (data.transcript_length && data.transcript_length > 0) {
              console.log(`   Transcript exists (${data.transcript_length} messages), but report not generated yet...`);
              // Continue polling - report might be generating
            } else {
              console.log(`   No transcript yet (attempt ${attempt}/${maxAttempts})...`);
            }
          } else {
            console.log(`   Report endpoint returned ${response.status}, continuing to poll...`);
          }
        } catch (error) {
          console.log(`   Polling error (attempt ${attempt}):`, error);
          // Continue polling
        }
        
        // Wait before next attempt (except on last attempt)
        if (attempt < maxAttempts) {
          await new Promise(resolve => setTimeout(resolve, pollInterval));
        }
      }
      
      if (reportReady) {
        console.log('📊 Report ready, navigating to report page...');
      } else {
        console.log('⚠️ Report not ready after polling, navigating anyway (report page will handle it)...');
      }
      
      // Navigate to report page (it will handle retry logic if needed)
      router.push(`/interview/report/${sessionId}`);
    } catch (error) {
      console.error('❌ Error leaving interview:', error);
      // Navigate anyway - report page will handle the error
      router.push(`/interview/report/${sessionId}`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center pt-20">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading interview session...</p>
        </div>
      </div>
    );
  }

  if (error) {
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
        <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 px-6 py-3">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                Question {currentIndex} of {totalQuestions}
              </span>
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                  {Math.round((currentIndex / totalQuestions) * 100)}% Complete
                </span>
                <motion.button
                  onClick={handleLeaveInterview}
                  disabled={leaving}
                  whileHover={{ scale: leaving ? 1 : 1.05 }}
                  whileTap={{ scale: leaving ? 1 : 0.95 }}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all shadow-md hover:shadow-lg text-sm ${
                    leaving 
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-red-600 hover:bg-red-700 text-white'
                  }`}
                >
                  {leaving ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <LogOut className="h-4 w-4" />
                      Leave & Get Report
                    </>
                  )}
                </motion.button>
              </div>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(currentIndex / totalQuestions) * 100}%` }}
                transition={{ duration: 0.5 }}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 h-2 rounded-full"
              />
            </div>
          </div>
        </div>

        {/* Main Content: Split Screen */}
        <div className="flex-1 overflow-hidden">
          <div className="h-full max-w-7xl mx-auto px-6 py-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Left Side: LiveKit Video Room */}
            <div className="h-full bg-gray-900 rounded-2xl shadow-xl overflow-hidden relative">
              {isConnected && videoEnabled ? (
                <RoomContext.Provider value={roomInstance}>
                  <div className="h-full flex flex-col" data-lk-theme="default">
                    {/* Video/Audio Grid - takes available space but leaves room for controls */}
                    <div className="flex-1 min-h-0 overflow-hidden">
                      <MyVideoConference />
                    </div>
                    
                    {/* Audio Renderer - CRITICAL for agent voice - must be at top level */}
                    <RoomAudioRenderer />
                    
                    {/* Controls - fixed at bottom */}
                    <div className="flex-shrink-0">
                      <ControlBar />
                    </div>
                  </div>
                </RoomContext.Provider>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-white p-8 text-center">
                  {!videoEnabled ? (
                    <>
                      <VideoOff className="h-16 w-16 mb-4 text-gray-400" />
                      <h3 className="text-xl font-semibold mb-2">Video Disabled</h3>
                      <p className="text-gray-400 mb-4">
                        You've turned off video mode. The interview continues in text mode.
                      </p>
                      <button
                        onClick={() => setVideoEnabled(true)}
                        className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors"
                      >
                        Enable Video
                      </button>
                    </>
                  ) : !isConnected && !livekitError ? (
                    <>
                      <Loader2 className="h-16 w-16 mb-4 text-blue-500 animate-spin" />
                      <h3 className="text-xl font-semibold mb-2">Connecting to interview room...</h3>
                      <p className="text-gray-400">
                        Room: {livekitRoomName || `interview-${sessionId}`}
                      </p>
                    </>
                  ) : livekitError ? (
                    <>
                      <Video className="h-16 w-16 mb-4 text-yellow-500" />
                      <h3 className="text-xl font-semibold mb-2">Video Unavailable</h3>
                      <p className="text-gray-400 mb-2">{livekitError}</p>
                      <p className="text-sm text-gray-500">Continuing in text mode</p>
                    </>
                  ) : (
                    <>
                      <Loader2 className="h-16 w-16 mb-4 text-blue-500 animate-spin" />
                      <h3 className="text-xl font-semibold mb-2">Initializing video...</h3>
                      <p className="text-gray-400">Please wait</p>
                    </>
                  )}
                  
                  {/* Video toggle button (if loaded but user wants to disable) */}
                  {videoEnabled && (isConnected || livekitError) && (
                    <button
                      onClick={() => setVideoEnabled(false)}
                      className="mt-6 px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg font-medium transition-colors text-sm"
                    >
                      Continue in Text Mode
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Right Side: Live Transcription Viewer */}
            <div className="h-full flex flex-col bg-white rounded-2xl shadow-xl overflow-hidden">
              {/* Header */}
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-4">
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  <Volume2 className="h-5 w-5" />
                  Live Transcription
                </h2>
                <p className="text-sm text-blue-100 mt-1">
                  Voice conversation is being transcribed in real-time
                </p>
              </div>

              {/* Transcription Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-gray-50 to-white">
                {messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center p-8">
                    <Mic className="h-16 w-16 text-gray-300 mb-4" />
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">
                      Start Speaking
                    </h3>
                    <p className="text-gray-500 text-sm max-w-sm">
                      The AI interviewer will greet you and ask questions. Your conversation will appear here in real-time.
                    </p>
                    <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-100">
                      <p className="text-xs text-blue-800 font-medium mb-2">💡 Tips:</p>
                      <ul className="text-xs text-blue-700 space-y-1 text-left">
                        <li>• Speak clearly and naturally</li>
                        <li>• Take your time to think</li>
                        <li>• The AI is here to help you improve</li>
                      </ul>
                    </div>
                  </div>
                ) : (
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
                          message.role === "agent"
                            ? "bg-gradient-to-br from-blue-600 to-indigo-600 shadow-md"
                            : "bg-gradient-to-br from-green-500 to-emerald-600 shadow-md"
                        }`}>
                          {message.role === "agent" ? (
                            <Bot className="h-5 w-5 text-white" />
                          ) : (
                            <User className="h-5 w-5 text-white" />
                          )}
                        </div>

                        {/* Message Bubble */}
                        <div className={`flex-1 max-w-[85%] ${message.role === "user" ? "text-right" : ""}`}>
                          <div className={`inline-block px-4 py-3 rounded-2xl shadow-sm ${
                            message.role === "agent"
                              ? "bg-white border border-gray-200 text-gray-900"
                              : "bg-gradient-to-r from-blue-600 to-indigo-600 text-white"
                          }`}>
                            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                            {message.score !== undefined && (
                              <div className={`mt-2 pt-2 border-t ${
                                message.role === "agent" ? "border-gray-200" : "border-blue-500"
                              }`}>
                                <div className="flex items-center gap-2">
                                  <div className={`text-xs font-semibold px-2 py-1 rounded-full ${
                                    message.score >= 80 ? "bg-green-100 text-green-800" :
                                    message.score >= 70 ? "bg-blue-100 text-blue-800" :
                                    message.score >= 60 ? "bg-yellow-100 text-yellow-800" :
                                    "bg-red-100 text-red-800"
                                  }`}>
                                    Score: {message.score}/100
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                          <p className="text-xs text-gray-400 mt-1 px-2">
                            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Footer - Status Info */}
              <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm text-gray-600">Recording</span>
                  </div>
                  <div className="h-4 w-px bg-gray-300"></div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Mic className="h-4 w-4" />
                    <span>Use your microphone to respond</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

// Helper component to handle audio/video tracks explicitly
function MyVideoConference() {
  // Get tracks - useTracks handles both audio and video automatically
  const tracks = useTracks(
    [
      { source: Track.Source.Camera, withPlaceholder: true },
      { source: Track.Source.ScreenShare, withPlaceholder: false },
    ],
    { onlySubscribed: false }
  );
  
  // Filter to show only the agent/avatar, hide user and backend agent
  const filteredTracks = tracks.filter(track => {
    const participantIdentity = track.participant?.identity || '';
    const isLocal = track.participant?.isLocal;
    
    // Debug: log all participants
    if (process.env.NODE_ENV === 'development') {
      console.log('Participant:', participantIdentity, 'isLocal:', isLocal, 'Kind:', track.participant?.kind);
    }
    
    // Hide the user's own video (local participant)
    if (isLocal) {
      return false;
    }
    
    // Hide the backend agent process participant (starts with "agent-")
    const isBackendAgent = participantIdentity.startsWith('agent-');
    
    return !isBackendAgent;
  });
  
  return (
    <div className="h-full w-full flex items-center justify-center bg-gray-950">
      {filteredTracks.length > 0 ? (
        <GridLayout 
          tracks={filteredTracks}
          style={{ height: '100%', width: '100%' }}
        >
          <ParticipantTile />
        </GridLayout>
      ) : (
        <div className="text-white text-center p-8">
          <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4" />
          <p>Waiting for AI Interview Coach to join...</p>
        </div>
      )}
    </div>
  );
}
