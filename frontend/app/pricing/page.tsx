"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import {
  Check, X, Sparkles, Zap, Crown, Gift, ArrowRight, Briefcase
} from "lucide-react";
import Link from "next/link";
import { useUser } from "@clerk/nextjs";
import { useCurrentUser } from "@/hooks/useCurrentUser";

interface PlanPrice {
  billing_period: string;
  price_cents: number;
  currency: string;
  trial_days: number;
  display_price: string;
}

interface PlanFeature {
  feature_code: string;
  monthly_quota: number | null;
  hard_cap: boolean;
  display_quota: string;
}

interface PricingPlan {
  code: string;
  name: string;
  description: string;
  sort_order: number;
  prices: PlanPrice[];
  features: PlanFeature[];
}

interface CurrentPlan {
  plan_code: string;
  plan_name: string;
  billing_period: string;
  status: string;
}

const FEATURE_NAMES: Record<string, string> = {
  cv_generate: "CV Generation",
  cv_analyze: "CV Analysis & ATS Score",
  cover_letter_generate: "Cover Letters",
  motivation_letter_generate: "Motivation Letters",
  mock_interview: "Mock Interviews",
  career_chat_messages: "Career Coaching Chat",
  job_tracking: "Job Application Tracking",
};

export default function PricingPage() {
  const { user, isSignedIn } = useUser();
  const { role } = useCurrentUser();
  const searchParams = useSearchParams();
  const upgrade = searchParams.get('upgrade');
  const [plans, setPlans] = useState<PricingPlan[]>([]);
  const [currentPlan, setCurrentPlan] = useState<CurrentPlan | null>(null);
  const [billingPeriod, setBillingPeriod] = useState<"monthly" | "yearly">("monthly");
  const [loading, setLoading] = useState(true);
  const [subscribing, setSubscribing] = useState<string | null>(null); // Track which plan is being subscribed to
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    fetchPlans();
    if (isSignedIn && user) {
      fetchCurrentPlan();
    }
  }, [isSignedIn, user]);

  const fetchPlans = async () => {
    // Default to localhost if env var not set
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    try {
      const response = await fetch(`${apiUrl}/pricing/plans`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setPlans(data);
    } catch (error) {
      console.error("Failed to fetch pricing plans:", error);
      // You could set some mock data here or show an error message
    } finally {
      setLoading(false);
    }
  };

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
        console.warn('Could not fetch current plan');
      }
    } catch (error) {
      // Silently handle - backend might not be running
      console.debug("Backend not available:", error);
    }
  };

  const getPrice = (plan: PricingPlan) => {
    const price = plan.prices.find(p => p.billing_period === billingPeriod);
    return price || plan.prices[0];
  };

  const getPlanIcon = (code: string) => {
    switch (code) {
      case "free":
        return <Gift className="h-8 w-8" />;
      case "basic":
        return <Zap className="h-8 w-8" />;
      case "pro":
        return <Sparkles className="h-8 w-8" />;
      case "enterprise":
        return <Crown className="h-8 w-8" />;
      default:
        return <Sparkles className="h-8 w-8" />;
    }
  };

  const getPlanGradient = (code: string) => {
    switch (code) {
      case "free":
        return "from-gray-500 to-gray-600";
      case "basic":
        return "from-blue-500 to-cyan-600";
      case "pro":
        return "from-purple-500 to-pink-600";
      case "enterprise":
        return "from-amber-500 to-orange-600";
      default:
        return "from-indigo-500 to-purple-600";
    }
  };

  const isPopular = (code: string) => code === "pro";

  const handleSubscribeToPlan = async (planCode: string) => {
    if (!isSignedIn || !user) {
      // Redirect to sign in if not authenticated
      window.location.href = "/sign-in";
      return;
    }

    setSubscribing(planCode);
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    try {
      const response = await fetch(`${apiUrl}/pricing/user/subscribe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user.id,
          plan_code: planCode,
          billing_period: billingPeriod,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to subscribe');
      }

      const data = await response.json();
      
      // Show success modal
      setSuccessMessage(`Successfully subscribed to ${data.subscription.plan_name} plan!`);
      setShowSuccessModal(true);
      
      // Refresh current plan
      await fetchCurrentPlan();
      
      // Auto-close modal and optionally redirect after 2 seconds
      setTimeout(() => {
        setShowSuccessModal(false);
        // Optionally redirect to interview setup or dashboard
        // window.location.href = '/interview/setup';
      }, 2000);
      
    } catch (error) {
      console.error('Subscription error:', error);
      alert(`❌ Failed to subscribe: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setSubscribing(null);
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 pt-20">
        <div className="max-w-7xl mx-auto px-6 py-16">
          <div className="text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-indigo-600 border-r-transparent"></div>
            <p className="mt-4 text-gray-600">Loading pricing plans...</p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-indigo-950 dark:to-purple-950 pt-20 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-6 py-16">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          {upgrade === 'recruiter' && role === 'CANDIDATE' ? (
            <>
              <div className="inline-flex items-center gap-2 bg-gradient-to-r from-emerald-100 to-green-100 dark:from-emerald-900/30 dark:to-green-900/30 text-emerald-700 dark:text-emerald-300 px-4 py-2 rounded-full text-sm font-medium mb-4 border border-emerald-200 dark:border-emerald-700">
                <Briefcase className="h-4 w-4" />
                Upgrade to Recruiter Account
              </div>
              <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-emerald-600 via-green-600 to-teal-600 bg-clip-text text-transparent">
                Unlock Recruiter Tools
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                Access powerful ATS features, candidate screening tools, and advanced analytics to find the perfect talent.
              </p>
            </>
          ) : (
            <>
              <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                Choose Your Plan
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                Invest in your career with AI-powered tools that actually work
              </p>
            </>
          )}
        </motion.div>

        {/* Billing Toggle */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex justify-center mb-12"
        >
          <div className="inline-flex items-center bg-white rounded-full p-1 shadow-lg border border-indigo-100">
            <button
              onClick={() => setBillingPeriod("monthly")}
              className={`px-6 py-2 rounded-full font-semibold transition-all ${
                billingPeriod === "monthly"
                  ? "bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-md"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingPeriod("yearly")}
              className={`px-6 py-2 rounded-full font-semibold transition-all relative ${
                billingPeriod === "yearly"
                  ? "bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-md"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Yearly
              <span className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-0.5 rounded-full">
                Save 17%
              </span>
            </button>
          </div>
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto mb-16">
          {plans.map((plan, index) => {
            const price = getPrice(plan);
            const popular = isPopular(plan.code);
            const isCurrentPlan = currentPlan?.plan_code === plan.code;

            return (
              <motion.div
                key={plan.code}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + index * 0.1 }}
                className={`relative bg-white rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 overflow-hidden ${
                  isCurrentPlan ? "ring-2 ring-green-500 transform scale-105" : 
                  popular ? "ring-2 ring-purple-500 transform scale-105" : ""
                }`}
              >
                {isCurrentPlan && (
                  <div className="absolute top-0 right-0 bg-gradient-to-r from-green-500 to-emerald-500 text-white text-xs font-bold px-4 py-1 rounded-bl-lg flex items-center gap-1">
                    <Crown className="h-3 w-3" />
                    CURRENT PLAN
                  </div>
                )}
                {!isCurrentPlan && popular && (
                  <div className="absolute top-0 right-0 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs font-bold px-4 py-1 rounded-bl-lg">
                    POPULAR
                  </div>
                )}

                <div className="p-8">
                  {/* Plan Icon */}
                  <div
                    className={`inline-flex p-4 rounded-2xl bg-gradient-to-r ${getPlanGradient(
                      plan.code
                    )} text-white mb-4`}
                  >
                    {getPlanIcon(plan.code)}
                  </div>

                  {/* Plan Name */}
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">
                    {plan.name}
                  </h3>

                  {/* Plan Description */}
                  <p className="text-gray-600 text-sm mb-6 min-h-[40px]">
                    {plan.description}
                  </p>

                  {/* Price */}
                  <div className="mb-6">
                    {price.price_cents === 0 ? (
                      <div className="text-4xl font-bold text-gray-900">
                        Free
                      </div>
                    ) : (
                      <div>
                        <div className="flex items-baseline gap-2">
                          <span className="text-4xl font-bold text-gray-900">
                            ${(price.price_cents / 100).toFixed(0)}
                          </span>
                          <span className="text-gray-600">
                            /{billingPeriod === "monthly" ? "mo" : "yr"}
                          </span>
                        </div>
                        {price.trial_days > 0 && (
                          <p className="text-sm text-green-600 mt-2">
                            {price.trial_days} days free trial
                          </p>
                        )}
                      </div>
                    )}
                  </div>

                  {/* CTA Button */}
                  {isCurrentPlan ? (
                    <motion.button
                      disabled
                      className="w-full py-3 rounded-lg font-semibold shadow-lg transition-all flex items-center justify-center gap-2 bg-gradient-to-r from-green-100 to-emerald-100 text-green-700 cursor-default border-2 border-green-500"
                    >
                      <Crown className="h-5 w-5" />
                      Current Plan
                    </motion.button>
                  ) : (
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => handleSubscribeToPlan(plan.code)}
                      disabled={subscribing !== null}
                      className={`w-full py-3 rounded-lg font-semibold shadow-lg transition-all flex items-center justify-center gap-2 ${
                        subscribing === plan.code
                          ? "bg-gradient-to-r from-gray-300 to-gray-400 text-gray-600 cursor-wait"
                          : popular
                          ? "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
                          : "bg-gradient-to-r from-gray-100 to-gray-200 hover:from-gray-200 hover:to-gray-300 text-gray-900"
                      }`}
                    >
                      {subscribing === plan.code ? (
                        <>
                          <div className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-solid border-current border-r-transparent"></div>
                          Processing...
                        </>
                      ) : (
                        <>
                          {price.price_cents === 0 ? "Start Free" : 
                           currentPlan && price.price_cents > 0 ? "Upgrade" : "Get Started"}
                          <ArrowRight className="h-5 w-5" />
                        </>
                      )}
                    </motion.button>
                  )}

                  {/* Features List */}
                  <div className="mt-8 space-y-3">
                    {plan.features.slice(0, 6).map((feature) => (
                      <div
                        key={feature.feature_code}
                        className="flex items-start gap-3"
                      >
                        {feature.monthly_quota !== 0 ? (
                          <Check className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                        ) : (
                          <X className="h-5 w-5 text-gray-300 flex-shrink-0 mt-0.5" />
                        )}
                        <div>
                          <p className="text-sm text-gray-700">
                            {FEATURE_NAMES[feature.feature_code] ||
                              feature.feature_code}
                          </p>
                          <p className="text-xs text-gray-500">
                            {feature.display_quota}
                            {feature.monthly_quota && billingPeriod === "monthly"
                              ? "/mo"
                              : ""}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* FAQ Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="max-w-3xl mx-auto"
        >
          <h2 className="text-3xl font-bold text-center mb-8 text-gray-900">
            Frequently Asked Questions
          </h2>
          <div className="space-y-4">
            {[
              {
                q: "Can I change plans later?",
                a: "Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately.",
              },
              {
                q: "What payment methods do you accept?",
                a: "We accept all major credit cards, debit cards, and support local payment methods.",
              },
              {
                q: "Is there a free trial?",
                a: "Yes! Basic, Pro, and Enterprise plans come with a free trial period. No credit card required for the Free plan.",
              },
              {
                q: "Can I cancel anytime?",
                a: "Absolutely. Cancel anytime from your account settings. No questions asked.",
              },
            ].map((faq, i) => (
              <div key={i} className="bg-white rounded-lg p-6 shadow-md">
                <h3 className="font-semibold text-gray-900 mb-2">{faq.q}</h3>
                <p className="text-gray-600">{faq.a}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Success Modal */}
      {showSuccessModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            className="bg-white rounded-2xl p-8 max-w-md mx-4 shadow-2xl"
          >
            <div className="text-center">
              {/* Success Icon */}
              <div className="mx-auto w-16 h-16 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-center mb-4">
                <Check className="h-8 w-8 text-white" />
              </div>
              
              {/* Success Message */}
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                Success! 🎉
              </h3>
              <p className="text-gray-600 mb-6">
                {successMessage}
              </p>
              
              {/* Action Buttons */}
              <div className="flex gap-3">
                <Link href="/interview/setup" className="flex-1">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="w-full py-3 rounded-lg font-semibold bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg"
                  >
                    Start Interview
                  </motion.button>
                </Link>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowSuccessModal(false)}
                  className="flex-1 py-3 rounded-lg font-semibold bg-gray-100 hover:bg-gray-200 text-gray-900"
                >
                  Close
                </motion.button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </main>
  );
}

