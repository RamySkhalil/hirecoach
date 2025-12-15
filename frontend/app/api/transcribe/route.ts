// app/api/transcribe/route.ts

// NOTE:
// This route is protected by Arcjet via middleware.ts
// - Global shield + bot protection applies to all routes
// - This route is NOT under /api/interviews/* so it does not have interview-specific rate limiting
// - It is used for voice transcription which may be used in interview contexts
// IMPORTANT: Do not change transcription logic here without considering Arcjet quotas and costs.

import { NextRequest, NextResponse } from "next/server";

// WARNING:
// This route currently does not enforce auth here.
// Security, rate limiting, and abuse protection are handled via middleware.ts (Arcjet) and any outer auth layers.

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const file = formData.get("file") as File | null;

    if (!file) {
      return NextResponse.json(
        {
          error: "No file provided",
          hint: "Expecting 'file' field in multipart form-data",
        },
        { status: 400 }
      );
    }

    // Build form-data for the backend FastAPI endpoint
    const backendForm = new FormData();
    backendForm.append("audio", file, file.name);

    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/media/stt`;

    const backendRes = await fetch(backendUrl, {
      method: "POST",
      body: backendForm,
    });

    if (!backendRes.ok) {
      let details: any = null;
      try {
        details = await backendRes.json();
      } catch {
        details = { detail: backendRes.statusText };
      }

      console.error("[/api/transcribe] Backend STT failed:", details);

      return NextResponse.json(
        {
          error: "Backend STT failed",
          details,
          hint: "Check FastAPI /media/stt and OpenAI Whisper config",
        },
        { status: 500 }
      );
    }

    const data = await backendRes.json();

    // Ensure a consistent shape for the frontend
    return NextResponse.json({ text: data.text || "" });
  } catch (err: any) {
    console.error("[/api/transcribe] ❌ Error:", err);
    return NextResponse.json(
      {
        error: "Transcription error on Next.js side",
        details: err?.message ?? String(err),
      },
      { status: 500 }
    );
  }
}
