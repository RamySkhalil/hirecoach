# Clerk Authentication Integration

This document describes the Clerk authentication integration in Interviewly.

## Overview

Interviewly uses [Clerk](https://clerk.com) for user authentication. Clerk provides:
- 🔐 Secure authentication (email, social logins, magic links)
- 👤 User management
- 🎨 Beautiful pre-built UI components
- 🔑 JWT tokens for API authorization
- 📱 Mobile-ready

## Setup

### 1. Prerequisites

- Clerk account (free tier available)
- API keys from Clerk Dashboard

### 2. Frontend Configuration

Add these environment variables to `frontend/.env.local`:

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. How It Works

#### Frontend (Next.js + Clerk)

1. **ClerkProvider Wrapper** (`frontend/app/layout.tsx`)
   - Wraps the entire app to provide auth context
   
2. **Middleware Protection** (`frontend/middleware.ts`)
   - Protects routes automatically
   - Public routes: `/`, `/sign-in`, `/sign-up`
   - Protected routes: `/interview/*`

3. **Auth Hooks** (in pages)
   - `useAuth()` - Get user auth state and token
   - `getToken()` - Get JWT for API calls

4. **UI Components** (`frontend/components/Navbar.tsx`)
   - `<SignedIn>` - Show content only when signed in
   - `<SignedOut>` - Show content only when signed out
   - `<SignInButton>` - Pre-built sign in button
   - `<SignUpButton>` - Pre-built sign up button
   - `<UserButton>` - User profile dropdown

#### Token Flow

```
User Action → Frontend
                ↓
        getToken() from Clerk
                ↓
        Add to Authorization header
                ↓
        API Request to Backend
                ↓
        Backend validates token (future)
```

## Usage Examples

### Protected Page Component

```typescript
"use client";

import { useAuth } from "@clerk/nextjs";

export default function ProtectedPage() {
  const { getToken, userId, isLoaded } = useAuth();

  const handleApiCall = async () => {
    const token = await getToken();
    
    const response = await fetch('/api/endpoint', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
  };

  if (!isLoaded) {
    return <div>Loading...</div>;
  }

  return <div>Protected Content</div>;
}
```

### API Client with Auth

```typescript
// lib/api.ts
export async function startInterview(
  data: InterviewStartRequest,
  token?: string | null
) {
  const response = await fetch(`${API_URL}/interview/start`, {
    method: 'POST',
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  return response.json();
}
```

## Backend Integration (Optional)

For full backend token validation, install backend dependencies:

```bash
cd backend
pip install pyjwt[crypto] cryptography
```

Then add token validation middleware (see `backend/app/auth.py` for implementation).

## Current Implementation Status

✅ **Completed:**
- Frontend auth setup (ClerkProvider)
- Protected routes (middleware)
- Sign in/sign up UI
- User profile dropdown
- Token passing to API

⏳ **Optional (Future):**
- Backend JWT validation
- User model with Clerk user_id
- User-specific interview history
- Role-based access control

## Routes

| Route | Access | Description |
|-------|--------|-------------|
| `/` | Public | Landing page |
| `/sign-in` | Public | Sign in page (Clerk) |
| `/sign-up` | Public | Sign up page (Clerk) |
| `/interview/setup` | Protected | Start interview |
| `/interview/session/[id]` | Protected | Interview session |
| `/interview/report/[id]` | Protected | Interview report |

## User Experience

### Not Signed In
1. User visits app
2. Sees landing page
3. Clicks "Start Interview"
4. Redirected to sign in
5. After sign in → setup page

### Signed In
1. User visits app
2. Sees profile photo in navbar
3. Clicks "Start Interview" → direct access
4. Can view profile/settings via UserButton

## Customization

### Styling Clerk Components

Update appearance in Clerk Dashboard → Customization, or use the `appearance` prop:

```typescript
<UserButton 
  appearance={{
    elements: {
      avatarBox: "h-10 w-10",
      userButtonPopoverCard: "bg-white shadow-xl"
    }
  }}
/>
```

### Custom Auth Pages

For fully custom sign in/up pages, create:
- `frontend/app/sign-in/[[...sign-in]]/page.tsx`
- `frontend/app/sign-up/[[...sign-up]]/page.tsx`

## Security

- ✅ Tokens are short-lived JWT
- ✅ HTTPS in production (required)
- ✅ Automatic token refresh
- ✅ Secure httpOnly cookies
- ✅ CSRF protection built-in

## Troubleshooting

### Issue: "Clerk: Missing publishable key"

**Solution:** Add `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` to `frontend/.env.local`

### Issue: Middleware not protecting routes

**Solution:** Check `matcher` in `middleware.ts` and ensure routes match patterns

### Issue: Token not being sent

**Solution:** Make sure `useAuth()` is called in client component (`"use client"`)

### Issue: Redirect loop

**Solution:** Ensure public routes are listed in `isPublicRoute()` matcher

## Resources

- [Clerk Documentation](https://clerk.com/docs)
- [Clerk Next.js Quickstart](https://clerk.com/docs/quickstarts/nextjs)
- [Clerk Dashboard](https://dashboard.clerk.com)

## Support

For authentication issues:
1. Check Clerk Dashboard logs
2. Verify environment variables
3. Check browser console for errors
4. Review middleware configuration

---

**Last Updated:** Nov 2024

