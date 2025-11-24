# Clerk Authentication - Quick Setup Guide

## 🚀 5-Minute Setup

Follow these steps to enable authentication in your Interviewly app.

### Step 1: Get Your Clerk Keys (2 minutes)

1. **Go to** [https://dashboard.clerk.com/sign-up](https://dashboard.clerk.com/sign-up)

2. **Sign up** (it's free - no credit card required)

3. **Create an application**:
   - Name: "Interviewly" (or any name)
   - Click "Create application"

4. **Copy your keys**:
   - You'll see two keys on the screen:
     - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (starts with `pk_test_...` or `pk_live_...`)
     - `CLERK_SECRET_KEY` (starts with `sk_test_...` or `sk_live_...`)

### Step 2: Add Keys to .env.local (1 minute)

1. **Open** `frontend/.env.local` (should already exist with API_URL)

2. **Add your Clerk keys**:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
CLERK_SECRET_KEY=sk_test_your_secret_key_here
```

3. **Save** the file

### Step 3: Restart Frontend (30 seconds)

Stop your frontend (Ctrl+C) and restart:

```bash
cd frontend
npm run dev
```

### Step 4: Test It! (1 minute)

1. **Open** [http://localhost:3000](http://localhost:3000)

2. **Click** "Sign Up" in the navigation bar

3. **Create an account**:
   - Enter your email
   - Create a password
   - Or use Google/GitHub (if enabled)

4. **You're in!** You should now see:
   - Your profile photo in the top right
   - "Start Interview" button is accessible
   - User menu with sign out option

### ✅ That's It!

Your app now has:
- ✅ User sign up
- ✅ User sign in
- ✅ Protected routes
- ✅ User profile management
- ✅ Secure authentication

---

## 🎨 Optional: Customize Auth UI

### Change Auth Appearance

1. Go to [Clerk Dashboard](https://dashboard.clerk.com)
2. Select your application
3. Click "Customization" in sidebar
4. Choose:
   - **Theme**: Light/Dark
   - **Colors**: Match your brand
   - **Logo**: Upload your logo

### Enable Social Logins

1. In Clerk Dashboard → "User & Authentication" → "Social Connections"
2. Toggle on:
   - ✅ Google
   - ✅ GitHub
   - ✅ Facebook
   - ... and more

### Configure Email Settings

1. Clerk Dashboard → "User & Authentication" → "Email, Phone, Username"
2. Customize:
   - Required fields
   - Verification method
   - Password requirements

---

## 🔒 Security Notes

### Development (Current)
- Using `pk_test_...` and `sk_test_...` keys
- Perfect for local development
- Test mode in Clerk Dashboard

### Production (Later)
- Switch to `pk_live_...` and `sk_live_...` keys
- Update environment variables in production
- Enable HTTPS (required by Clerk)

---

## 🐛 Troubleshooting

### Issue: "Clerk: Missing publishable key"

**Solution:**
1. Check that `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` is in `frontend/.env.local`
2. Make sure it starts with `NEXT_PUBLIC_` (required for Next.js)
3. Restart frontend server

### Issue: Sign up button does nothing

**Solution:**
1. Open browser console (F12)
2. Check for errors
3. Verify keys are correct in Clerk Dashboard
4. Make sure you restarted frontend after adding keys

### Issue: Can't access protected pages

**Solution:**
1. Sign out completely
2. Sign back in
3. Clear browser cookies if needed
4. Check middleware.ts is in the root of frontend/

---

## 📚 What Was Added

### Files Modified:
1. ✅ `frontend/middleware.ts` - Route protection
2. ✅ `frontend/app/layout.tsx` - ClerkProvider wrapper
3. ✅ `frontend/components/Navbar.tsx` - Sign in/up buttons, user menu
4. ✅ `frontend/lib/api.ts` - Token passing to API
5. ✅ All interview pages - Auth token integration

### New Dependencies:
- ✅ `@clerk/nextjs` - Clerk Next.js SDK

### Environment Variables:
- ✅ `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` - Public key for frontend
- ✅ `CLERK_SECRET_KEY` - Secret key for server-side

---

## 🎯 Next Steps

Your authentication is ready! Now you can:

1. **Test the full flow**:
   - Sign up → Setup interview → Take interview → View report

2. **Invite test users**:
   - Go to Clerk Dashboard → Users → Invite

3. **Monitor usage**:
   - Clerk Dashboard shows sign-ups, sign-ins, active users

4. **Customize further**:
   - Add user profile fields
   - Enable MFA (multi-factor auth)
   - Set up webhooks

---

## 📞 Need Help?

- **Clerk Docs**: [https://clerk.com/docs](https://clerk.com/docs)
- **Clerk Discord**: [https://clerk.com/discord](https://clerk.com/discord)
- **Full Guide**: See `CLERK_AUTHENTICATION.md` in project root

---

**You're all set! 🎉**

Users can now sign up, sign in, and their interview sessions are protected and secure.

