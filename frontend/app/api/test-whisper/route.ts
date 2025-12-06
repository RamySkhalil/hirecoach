import { NextResponse } from "next/server";
import OpenAI from "openai";

/**
 * Simple test endpoint to verify OpenAI Whisper is configured correctly
 */
export async function GET() {
  try {
    // Check if API key exists
    if (!process.env.OPENAI_API_KEY) {
      return NextResponse.json({
        success: false,
        error: "OPENAI_API_KEY not found in environment",
        hint: "Add OPENAI_API_KEY to frontend/.env.local"
      });
    }

    // Check key format
    const keyPreview = process.env.OPENAI_API_KEY.substring(0, 10) + "...";
    const keyLength = process.env.OPENAI_API_KEY.length;

    // Try to initialize OpenAI client
    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });

    return NextResponse.json({
      success: true,
      message: "OpenAI configuration looks good!",
      keyPreview,
      keyLength,
      hint: "API key is present. If transcription still fails, check:\n1. API key is valid (not expired)\n2. You have credits in your OpenAI account\n3. Network connectivity"
    });

  } catch (err: any) {
    return NextResponse.json({
      success: false,
      error: err?.message || "Unknown error",
      hint: "Failed to initialize OpenAI client"
    });
  }
}

