// NOTE:
// This CV upload endpoint is protected by Arcjet via middleware.ts:
// - Global Shield + bot / abuse protection
// - Rate limiting for /api/ats/upload-cv (50 uploads per day per IP)
// IMPORTANT: CV upload logic below must remain compatible with this protection.

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";

// Auth / role check:
// This route forwards the Clerk auth token to the FastAPI backend, which handles
// authentication and authorization. Arcjet middleware has already run before this handler
// (WAF + rate limiting). The backend may enforce additional role-based access controls.
// DO NOT add new auth logic here without considering the backend's auth requirements.

export async function POST(req: NextRequest) {
  try {
    // Get auth token from Clerk (if available) to forward to backend
    const { getToken } = auth();
    const token = await getToken();

    // Parse the incoming form data
    const formData = await req.formData();

    // Forward to FastAPI backend CV upload endpoint
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/cv/upload`;

    // STORAGE NOTE:
    // - The FastAPI backend handles CV file storage (local filesystem or R2/S3).
    // - CVs should be stored in a private bucket/location, not publicly accessible.
    // - Access to CV files should be via signed/presigned URLs, not direct bucket URLs.
    // - Do NOT expose raw storage keys, internal file paths, or bucket names to the client.
    // - The backend is responsible for validating file types, sizes, and generating secure access URLs.

    // Build headers for backend request
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    // Forward the request to FastAPI backend
    const backendResponse = await fetch(backendUrl, {
      method: "POST",
      headers,
      body: formData,
    });

    // Get response data
    const responseData = await backendResponse.json().catch(() => ({
      detail: backendResponse.statusText || "Backend request failed",
    }));

    // Return the backend response with same status code
    return NextResponse.json(responseData, {
      status: backendResponse.status,
    });
  } catch (error: any) {
    console.error("[/api/ats/upload-cv] Error:", error);
    return NextResponse.json(
      {
        error: "CV upload failed",
        detail: error?.message || "Internal server error",
      },
      { status: 500 }
    );
  }
}

