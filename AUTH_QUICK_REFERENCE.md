# 🔐 Auth Quick Reference

## One-Page Cheat Sheet

### ✅ What's Done
- Frontend authentication with Clerk
- Route protection
- Sign up/in/out UI
- Token passing to API
- All interview pages protected

### 🔑 Environment Variables

**File:** `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

**Status:** ✅ Already configured in your project!

### 🚀 How to Start

```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Then:** Visit [http://localhost:3000](http://localhost:3000)

### 🧪 Quick Test

1. Click "Sign Up" → Create account
2. Check navbar → Should see profile photo
3. Click "Start Interview" → Should work
4. Complete interview → Should work
5. Click profile → Sign out

**Expected:** Everything works, no errors!

### 📍 Routes

| Route | Public? | Description |
|-------|---------|-------------|
| `/` | ✅ Yes | Landing page |
| `/sign-in` | ✅ Yes | Clerk sign in |
| `/sign-up` | ✅ Yes | Clerk sign up |
| `/interview/setup` | ❌ No | Protected - start interview |
| `/interview/session/[id]` | ❌ No | Protected - take interview |
| `/interview/report/[id]` | ❌ No | Protected - view report |

### 🎨 UI Components

```typescript
import {
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
  useAuth
} from "@clerk/nextjs";

// Show/hide based on auth state
<SignedIn>Content for logged in users</SignedIn>
<SignedOut>Content for guests</SignedOut>

// Get auth token
const { getToken } = useAuth();
const token = await getToken();
```

### 🔧 How It Works

```
User visits protected route
         ↓
Middleware checks auth
         ↓
Not signed in? → Redirect to /sign-in
         ↓
After sign in → Redirect back to intended page
         ↓
Signed in? → Allow access
         ↓
Get token with getToken()
         ↓
Pass token to API calls
```

### 📋 Common Tasks

#### Add Protected Route
Edit `frontend/middleware.ts`:
```typescript
const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/new-public-route',  // Add here
]);
```

#### Get User Info
```typescript
const { userId, user, isLoaded } = useAuth();

if (isLoaded && userId) {
  console.log("User ID:", userId);
  console.log("User email:", user?.primaryEmailAddress);
}
```

#### Make Authenticated API Call
```typescript
const { getToken } = useAuth();
const token = await getToken();

await fetch('/api/endpoint', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### 🐛 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| "Missing publishable key" | Check `.env.local` has `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` |
| Sign up button does nothing | Restart frontend after adding env vars |
| Can't access protected pages | Sign out and sign in again |
| Redirect loop | Check public routes in `middleware.ts` |

### 📚 Documentation

- **Quick Setup:** `CLERK_SETUP_GUIDE.md`
- **Full Details:** `CLERK_AUTHENTICATION.md`
- **Summary:** `AUTHENTICATION_IMPLEMENTATION_SUMMARY.md`

### 🎯 Status

**All Features:** ✅ Working

**Test Coverage:**
- ✅ Sign up
- ✅ Sign in  
- ✅ Sign out
- ✅ Route protection
- ✅ Token passing
- ✅ UI components

**No Issues Found** 🎉

### 📞 Help

- Clerk Dashboard: [dashboard.clerk.com](https://dashboard.clerk.com)
- Clerk Docs: [clerk.com/docs](https://clerk.com/docs)

---

**That's everything you need to know!** 🚀

