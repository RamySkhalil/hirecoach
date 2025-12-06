"use client";

import Link from "next/link";
import { Sparkles, Crown } from "lucide-react";
import { useState, useEffect } from "react";
import { useUser } from "@clerk/nextjs";
import {
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
} from "@clerk/nextjs";
import ThemeSwitcher from "./ThemeSwitcher";

interface CurrentPlan {
  plan_code: string;
  plan_name: string;
  billing_period: string;
  status: string;
}

export default function Navbar() {
  const { user, isSignedIn } = useUser();
  const [currentPlan, setCurrentPlan] = useState<CurrentPlan | null>(null);

  useEffect(() => {
    if (isSignedIn && user) {
      fetchCurrentPlan();
    }
  }, [isSignedIn, user]);

  const fetchCurrentPlan = async () => {
    if (!user?.id) return;
    
    // Default to localhost if env var not set
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    try {
      const response = await fetch(
        `${apiUrl}/pricing/user/current-plan?user_id=${user.id}`
      );
      if (response.ok) {
        const data = await response.json();
        setCurrentPlan(data);
      } else {
        console.warn('Could not fetch current plan, defaulting to free');
        // Silently fail - user will see no badge
      }
    } catch (error) {
      // Silently handle - backend might not be running in dev
      console.debug("Backend not available:", error);
    }
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-lg border-b border-gray-200 dark:border-gray-800 transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="inline-flex p-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 group-hover:from-blue-700 group-hover:to-indigo-700 transition-all duration-300">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent">
              Interviewly
            </span>
          </Link>

          {/* Nav Links */}
          <div className="flex items-center gap-6" suppressHydrationWarning>
            {/* Always visible link */}
            <Link
              href="/#how-it-works"
              className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 font-medium transition-colors hidden sm:block"
            >
              How It Works
            </Link>
            
            <Link
              href="/pricing"
              className="text-gray-600 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 font-medium transition-colors hidden md:block"
            >
              Pricing
            </Link>
            
            <SignedIn>
              {/* Main Tools */}
              <Link
                href="/interview/setup"
                className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 font-medium transition-colors hidden lg:block"
              >
                Interview
              </Link>
              <Link
                href="/cv"
                className="text-gray-600 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400 font-medium transition-colors hidden lg:block"
              >
                CV Analyzer
              </Link>
              <Link
                href="/rewriter"
                className="text-gray-600 dark:text-gray-300 hover:text-amber-600 dark:hover:text-amber-400 font-medium transition-colors hidden lg:block"
              >
                CV Rewriter
              </Link>
              <Link
                href="/career"
                className="text-gray-600 dark:text-gray-300 hover:text-green-600 dark:hover:text-green-400 font-medium transition-colors hidden lg:block"
              >
                Career Coach
              </Link>
              
              {/* Primary CTA */}
              <Link
                href="/interview/setup"
                className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-6 py-2 rounded-lg font-medium shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
              >
                Start Practice
              </Link>
              
              {/* User Plan Badge & Profile */}
              <div className="flex items-center gap-3">
                {currentPlan && (
                  <Link href="/pricing" className="hidden md:block">
                    <div className={`px-3 py-1.5 rounded-full text-xs font-semibold flex items-center gap-1.5 transition-all hover:scale-105 cursor-pointer ${
                      currentPlan.plan_code === 'pro' 
                        ? 'bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-700 hover:shadow-md'
                        : currentPlan.plan_code === 'basic'
                        ? 'bg-gradient-to-r from-blue-100 to-cyan-100 dark:from-blue-900/30 dark:to-cyan-900/30 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-700 hover:shadow-md'
                        : 'bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-700 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:shadow-md'
                    }`}>
                      {currentPlan.plan_code !== 'free' && <Crown className="h-3 w-3" />}
                      {currentPlan.plan_name}
                    </div>
                  </Link>
                )}
                
                {/* Theme Switcher */}
                <ThemeSwitcher />
                
                <UserButton 
                  afterSignOutUrl="/"
                  appearance={{
                    elements: {
                      avatarBox: "h-10 w-10"
                    }
                  }}
                >
                  <UserButton.MenuItems>
                    <UserButton.Link
                      label="Pricing Plans"
                      labelIcon={<Crown className="h-4 w-4" />}
                      href="/pricing"
                    />
                  </UserButton.MenuItems>
                </UserButton>
              </div>
            </SignedIn>

            <SignedOut>
              {/* Theme Switcher for signed out users */}
              <ThemeSwitcher />
              
              <SignInButton mode="modal">
                <button className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 font-medium transition-colors px-4 py-2">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-6 py-2 rounded-lg font-medium shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300">
                  Sign Up Free
                </button>
              </SignUpButton>
            </SignedOut>
          </div>
        </div>
      </div>
    </nav>
  );
}
