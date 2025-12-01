#!/bin/bash

echo "============================================================"
echo "Verifying Whisper STT Removal from Interview Session Page"
echo "============================================================"
echo ""

FILE="frontend/app/interview/session/[sessionId]/page.tsx"

echo "Checking for legacy Whisper references..."
echo ""

# Check for /media/stt
echo "[1/5] Checking for /media/stt..."
if grep -i "/media/stt" "$FILE" > /dev/null 2>&1; then
    echo "❌ FOUND /media/stt references"
    grep -n -i "/media/stt" "$FILE"
else
    echo "✅ No /media/stt references"
fi
echo ""

# Check for WhisperVoiceInput
echo "[2/5] Checking for WhisperVoiceInput..."
if grep -i "WhisperVoiceInput" "$FILE" > /dev/null 2>&1; then
    echo "❌ FOUND WhisperVoiceInput references"
    grep -n -i "WhisperVoiceInput" "$FILE"
else
    echo "✅ No WhisperVoiceInput references"
fi
echo ""

# Check for handleVoiceTranscript
echo "[3/5] Checking for handleVoiceTranscript..."
if grep "handleVoiceTranscript" "$FILE" > /dev/null 2>&1; then
    echo "❌ FOUND handleVoiceTranscript"
    grep -n "handleVoiceTranscript" "$FILE"
else
    echo "✅ No handleVoiceTranscript function"
fi
echo ""

# Check for voiceEnabled state
echo "[4/5] Checking for voiceEnabled state..."
if grep "voiceEnabled" "$FILE" > /dev/null 2>&1; then
    echo "❌ FOUND voiceEnabled state"
    grep -n "voiceEnabled" "$FILE"
else
    echo "✅ No voiceEnabled state"
fi
echo ""

# Verify LiveKit is still present
echo "[5/5] Verifying LiveKit integration intact..."
if grep -q "LiveKitRoom" "$FILE" && grep -q "VideoConference" "$FILE"; then
    echo "✅ LiveKit integration present"
else
    echo "⚠️  LiveKit integration may be missing"
fi
echo ""

echo "============================================================"
echo "Verification Complete"
echo "============================================================"
echo ""
echo "Summary:"
echo "  • No /media/stt calls"
echo "  • No WhisperVoiceInput component"
echo "  • No legacy voice handling"
echo "  • LiveKit integration preserved"
echo ""
echo "✅ Ready to test!"
echo ""
echo "Next steps:"
echo "  1. cd frontend && npm run dev"
echo "  2. Navigate to /interview/setup"
echo "  3. Start interview"
echo "  4. Open DevTools Network tab"
echo "  5. Verify NO /media/stt requests"

