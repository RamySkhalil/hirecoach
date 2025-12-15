import { NextRequest, NextResponse } from "next/server";
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';
import arcjet, {
  shield,
  detectBot,
  tokenBucket,
} from "@arcjet/next";

// Define public routes (accessible without authentication)
const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/onboarding(.*)',  // Allow onboarding route
  '/jobs(.*)',  // Allow public job listings and applications
]);

// Global protection: shield + bot detection
const ajGlobal = arcjet({
  key: process.env.ARCJET_KEY!,
  rules: [
    shield({
      mode: "LIVE",
    }),
    detectBot({
      mode: "LIVE",
      allow: ["CATEGORY:SEARCH_ENGINE", "CATEGORY:PREVIEW"],
    }),
  ],
});

// Interview-related quota: protects expensive AI/LiveKit calls
const ajInterviewQuota = arcjet({
  key: process.env.ARCJET_KEY!,
  rules: [
    tokenBucket({
      mode: "LIVE",
      // we will key primarily on IP for safety,
      // to avoid messing with Clerk internals in middleware
      characteristics: ["ip", "route"],
      capacity: 20,    // 20 requests
      refillRate: 20,  // 20 tokens
      interval: 3600,  // per hour
    }),
  ],
});

// CV upload quota: protect ATS upload endpoint
const ajCvUploadQuota = arcjet({
  key: process.env.ARCJET_KEY!,
  rules: [
    tokenBucket({
      mode: "LIVE",
      characteristics: ["ip", "route"],
      capacity: 50,    // 50 uploads
      refillRate: 50,
      interval: 86400, // per day
    }),
  ],
});

// Create the Clerk middleware handler
const clerkHandler = clerkMiddleware(async (auth, request) => {
  if (!isPublicRoute(request)) {
    await auth.protect();
  }
});

// Main middleware function with Arcjet protection
export default async function middleware(req: NextRequest) {
  const path = req.nextUrl.pathname;

  // 1) Global Shield + bot protection for all routes
  const globalDecision = await ajGlobal.protect(req);
  if (globalDecision.isDenied()) {
    return NextResponse.json(
      { error: "Forbidden", reason: globalDecision.reason },
      { status: 403 },
    );
  }

  // 2) Interview-related quota: /api/interviews/*
  if (path.startsWith("/api/interviews/")) {
    const decision = await ajInterviewQuota.protect(req, {
      // For now, key is driven by IP + route via characteristics;
      // DO NOT integrate Clerk logic here to avoid breaking auth flow.
      requested: 1,
    });

    if (decision.isDenied()) {
      return NextResponse.json(
        { error: "Too Many Interview Requests", reason: decision.reason },
        { status: 429 },
      );
    }
  }

  // 3) CV upload quota: /api/ats/upload-cv
  if (path.startsWith("/api/ats/upload-cv")) {
    const decision = await ajCvUploadQuota.protect(req, {
      requested: 1,
    });

    if (decision.isDenied()) {
      return NextResponse.json(
        { error: "Too Many CV Uploads", reason: decision.reason },
        { status: 429 },
      );
    }
  }

  // 4) Pass through to existing Clerk middleware
  return clerkHandler(req);
}

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
};

