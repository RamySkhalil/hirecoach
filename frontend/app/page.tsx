"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { 
  Sparkles, Target, Award, TrendingUp, ArrowRight, CheckCircle2,
  Mic, Brain, MessageSquare, BarChart3, Clock, Shield, FileText, Zap, Wand2, Bot, Briefcase
} from "lucide-react";
import LindaChat from "@/components/LindaChat";

export default function Home() {
  return (
    <main className="min-h-screen bg-white dark:bg-gray-950 transition-colors duration-300">
      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden pt-20">
        {/* Background Gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-950 dark:to-indigo-950" />

        {/* Decorative Elements */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob" />
        <div className="absolute top-40 right-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000" />
        <div className="absolute -bottom-8 left-40 w-72 h-72 bg-indigo-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000" />

        {/* Content */}
        <div className="relative max-w-7xl mx-auto px-6 py-24 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-full shadow-lg border border-blue-100 dark:border-blue-900 mb-8">
              <Sparkles className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Powered by GPT-4o</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-6xl md:text-7xl font-bold mb-6">
              <span className="bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent">
                Land Your Dream Job
              </span>
              <br />
              <span className="bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400 bg-clip-text text-transparent">
                Or Hire Better With AI
              </span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-400 mb-8 max-w-3xl mx-auto leading-relaxed">
              Job seekers practice interviews & optimize CVs. Recruiters run AI-powered interviews and ATS screening. 
              Everything you need for your career journey.
            </p>

            {/* Feature Pills */}
            <div className="flex flex-wrap items-center justify-center gap-3 mb-12">
              <span className="px-4 py-2 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-full text-sm font-medium text-gray-700 dark:text-gray-300 shadow-md">
                🎤 AI Interview Coach
              </span>
              <span className="px-4 py-2 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-full text-sm font-medium text-gray-700 dark:text-gray-300 shadow-md">
                📄 CV Analyzer
              </span>
              <span className="px-4 py-2 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-full text-sm font-medium text-gray-700 dark:text-gray-300 shadow-md">
                ✨ CV Rewriter
              </span>
              <span className="px-4 py-2 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-full text-sm font-medium text-gray-700 dark:text-gray-300 shadow-md">
                🤖 AI Hiring Assistant
              </span>
              <span className="px-4 py-2 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-full text-sm font-medium text-gray-700 dark:text-gray-300 shadow-md">
                📊 ATS Screening
              </span>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/interview/setup">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-10 py-4 rounded-lg font-semibold text-lg shadow-xl hover:shadow-2xl transition-all duration-300 flex items-center gap-2"
                >
                  I'm a Candidate
                  <ArrowRight className="h-5 w-5" />
                </motion.button>
              </Link>
              <Link href="/onboarding/role">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 border-2 border-gray-200 dark:border-gray-700 px-10 py-4 rounded-lg font-semibold text-lg shadow-md hover:shadow-lg transition-all duration-300 flex items-center gap-2"
                >
                  <Briefcase className="h-5 w-5" />
                  I'm a Recruiter
                </motion.button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Main Features Section - 3 Tools */}
      <section className="py-24 bg-white dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-5xl font-bold mb-4 bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent">
              Your Complete Career Toolkit
            </h2>
            <p className="text-xl text-gray-600">
              Four powerful AI tools to help you land your dream job
            </p>
          </div>

          {/* Four Main Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
            {/* Interview Coach - Feature 1 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 border-2 border-blue-100 p-8 group hover:-translate-y-2"
            >
              <div className="inline-flex p-4 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600 mb-6 group-hover:scale-110 transition-transform duration-300">
                <Mic className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                AI Interview Coach
              </h3>
              <p className="text-gray-600 leading-relaxed mb-6">
                Practice with voice-enabled AI. Get instant feedback with detailed scoring on every answer.
              </p>
              <Link href="/interview/setup">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-6 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-2"
                >
                  Start Practicing
                  <ArrowRight className="h-5 w-5" />
                </motion.button>
              </Link>
              <div className="mt-6 pt-6 border-t border-blue-200">
                <div className="grid grid-cols-2 gap-2">
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-blue-600" />
                    Voice-Enabled
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-blue-600" />
                    Real-time Feedback
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-blue-600" />
                    Custom Questions
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-blue-600" />
                    Detailed Reports
                  </div>
                </div>
              </div>
            </motion.div>

            {/* CV Analyzer - Feature 2 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 border-2 border-purple-100 p-8 group hover:-translate-y-2"
            >
              <div className="inline-flex p-4 rounded-2xl bg-gradient-to-r from-purple-500 to-pink-600 mb-6 group-hover:scale-110 transition-transform duration-300">
                <FileText className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                CV Analyzer
              </h3>
              <p className="text-gray-600 leading-relaxed mb-6">
                Upload your CV for instant AI analysis with ATS scores, strengths, and suggestions.
              </p>
              <Link href="/cv">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-6 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-2"
                >
                  Analyze Now
                  <ArrowRight className="h-5 w-5" />
                </motion.button>
              </Link>
              <div className="mt-6 pt-6 border-t border-purple-200">
                <div className="grid grid-cols-2 gap-2">
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-purple-600" />
                    ATS Score
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-purple-600" />
                    Keyword Analysis
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-purple-600" />
                    AI-Powered
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-purple-600" />
                    Instant Results
                  </div>
                </div>
              </div>
            </motion.div>

            {/* CV Rewriter - Feature 3 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 border-2 border-amber-100 p-8 group hover:-translate-y-2"
            >
              <div className="inline-flex p-4 rounded-2xl bg-gradient-to-r from-amber-500 to-orange-600 mb-6 group-hover:scale-110 transition-transform duration-300">
                <Wand2 className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                CV Rewriter
              </h3>
              <p className="text-gray-600 leading-relaxed mb-6">
                Transform your CV with AI in multiple professional styles. Job-tailored and ATS-optimized.
              </p>
              <Link href="/rewriter">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="w-full bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 text-white px-6 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-2"
                >
                  Rewrite CV
                  <ArrowRight className="h-5 w-5" />
                </motion.button>
              </Link>
              <div className="mt-6 pt-6 border-t border-amber-200">
                <div className="grid grid-cols-2 gap-2">
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-amber-600" />
                    4 Styles
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-amber-600" />
                    Job Tailored
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-amber-600" />
                    ATS Optimized
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-amber-600" />
                    Download Ready
                  </div>
                </div>
              </div>
            </motion.div>

            {/* AI Career Agent - Feature 4 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 border-2 border-green-100 p-8 group hover:-translate-y-2"
            >
              <div className="inline-flex p-4 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-600 mb-6 group-hover:scale-110 transition-transform duration-300">
                <MessageSquare className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                AI Career Coach
              </h3>
              <p className="text-gray-600 leading-relaxed mb-6">
                Chat with your personal AI career advisor. Get guidance on career growth, skills, and job search.
              </p>
              <Link href="/career">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white px-6 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-2"
                >
                  Chat Now
                  <ArrowRight className="h-5 w-5" />
                </motion.button>
              </Link>
              <div className="mt-6 pt-6 border-t border-green-200">
                <div className="grid grid-cols-2 gap-2">
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    24/7 Available
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Personalized
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Career Guidance
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Job Strategy
                  </div>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Recruiter Banner */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.5 }}
            className="mt-12 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl shadow-xl p-8 text-white"
          >
            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
              <div>
                <h3 className="text-2xl font-bold mb-2">New for Recruiters</h3>
                <p className="text-indigo-100">
                  AI-powered ATS and video interviews. Screen candidates faster with automated CV-to-JD matching.
                </p>
              </div>
              <Link href="/onboarding/role">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-white text-indigo-600 px-8 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-2"
                >
                  Explore Recruiter Tools
                  <ArrowRight className="h-5 w-5" />
                </motion.button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-5xl font-bold mb-4 bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
              How It Works
            </h2>
            <p className="text-xl text-gray-600">
              Get interview-ready in three simple steps
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="text-center"
            >
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-3xl font-bold mb-6 shadow-lg">
                1
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                Choose Your Tool
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Practice interviews, analyze your CV, or get a professional rewrite. 
                All powered by GPT-4o AI.
              </p>
            </motion.div>

            {/* Step 2 */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="text-center"
            >
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-3xl font-bold mb-6 shadow-lg">
                2
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                Get AI Feedback
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Receive instant, detailed feedback on your performance or CV quality 
                with specific scores and actionable insights.
              </p>
            </motion.div>

            {/* Step 3 */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="text-center"
            >
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-3xl font-bold mb-6 shadow-lg">
                3
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                Improve & Succeed
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Apply suggestions, practice again, and track your progress 
                until you're fully confident and interview-ready.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Supporting Features */}
      <section className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-5xl font-bold mb-4 bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
              Powerful Features
            </h2>
            <p className="text-xl text-gray-600">
              Everything designed to help you succeed
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature: GPT-4o Powered */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 hover:-translate-y-2 transition-all duration-300"
            >
              <div className="inline-flex p-3 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 mb-4">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                GPT-4o Powered
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Leveraging OpenAI's latest GPT-4o model for the most accurate 
                and intelligent feedback possible.
              </p>
            </motion.div>

            {/* Feature: Voice-Enabled */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 hover:-translate-y-2 transition-all duration-300"
            >
              <div className="inline-flex p-3 rounded-xl bg-gradient-to-r from-green-500 to-emerald-600 mb-4">
                <MessageSquare className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                Voice-Enabled
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Practice speaking your answers naturally. Perfect for building 
                confidence in verbal communication.
              </p>
            </motion.div>

            {/* Feature: Instant Results */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 hover:-translate-y-2 transition-all duration-300"
            >
              <div className="inline-flex p-3 rounded-xl bg-gradient-to-r from-orange-500 to-red-600 mb-4">
                <Zap className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                Instant Results
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Get immediate analysis and feedback. No waiting - all results 
                are generated in real-time.
              </p>
            </motion.div>

            {/* Feature: Multiple Styles */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 hover:-translate-y-2 transition-all duration-300"
            >
              <div className="inline-flex p-3 rounded-xl bg-gradient-to-r from-purple-500 to-pink-600 mb-4">
                <Wand2 className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                Multiple Styles
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Choose from Modern, Minimal, Executive, or ATS Optimized styles 
                for your rewritten CV.
              </p>
            </motion.div>

            {/* Feature: 24/7 Available */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.5 }}
              className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 hover:-translate-y-2 transition-all duration-300"
            >
              <div className="inline-flex p-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 mb-4">
                <Clock className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                Practice Anytime
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Available 24/7 whenever you need it. Practice and improve 
                on your own schedule.
              </p>
            </motion.div>

            {/* Feature: Secure */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.6 }}
              className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 hover:-translate-y-2 transition-all duration-300"
            >
              <div className="inline-flex p-3 rounded-xl bg-gradient-to-r from-gray-700 to-slate-800 mb-4">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                Secure & Private
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Your data is encrypted and completely private. We never 
                share your information.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gradient-to-r from-blue-600 to-indigo-600">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8 text-center text-white">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
            >
              <div className="text-5xl font-bold mb-2">10K+</div>
              <div className="text-blue-100">Mock Interviews</div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
            >
              <div className="text-5xl font-bold mb-2">5K+</div>
              <div className="text-blue-100">CVs Analyzed</div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
            >
              <div className="text-5xl font-bold mb-2">3K+</div>
              <div className="text-blue-100">CVs Rewritten</div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
            >
              <div className="text-5xl font-bold mb-2">95%</div>
              <div className="text-blue-100">Success Rate</div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-white">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-5xl font-bold mb-6 bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
              Ready to Land Your Dream Job?
            </h2>
            <p className="text-xl text-gray-600 mb-8 leading-relaxed">
              Join thousands of successful job seekers who used our AI tools.
            </p>

            {/* Feature Highlights */}
            <div className="grid md:grid-cols-2 gap-4 mb-12 text-left max-w-2xl mx-auto">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-6 w-6 text-green-600 flex-shrink-0" />
                <span className="text-gray-700">Free to get started</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-6 w-6 text-green-600 flex-shrink-0" />
                <span className="text-gray-700">No credit card required</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-6 w-6 text-green-600 flex-shrink-0" />
                <span className="text-gray-700">GPT-4o powered</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-6 w-6 text-green-600 flex-shrink-0" />
                <span className="text-gray-700">Practice unlimited times</span>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/interview/setup">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-12 py-5 rounded-lg font-semibold text-lg shadow-xl hover:shadow-2xl transition-all duration-300 flex items-center justify-center gap-2"
                >
                  Start Interview Practice
                  <ArrowRight className="h-6 w-6" />
                </motion.button>
              </Link>
              <Link href="/cv">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-white hover:bg-gray-50 text-gray-700 border-2 border-gray-200 px-12 py-5 rounded-lg font-semibold text-lg shadow-md hover:shadow-lg transition-all duration-300 flex items-center justify-center gap-2"
                >
                  <FileText className="h-5 w-5" />
                  Analyze My CV
                </motion.button>
              </Link>
            </div>

            {/* Coming Soon Badge */}
            <div className="mt-16 pt-12 border-t border-gray-200">
              <p className="text-sm font-semibold text-gray-500 mb-4">COMING SOON</p>
              <div className="flex flex-wrap items-center justify-center gap-3">
                <span className="px-3 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm">
                  💌 Cover Letter Generator
                </span>
                <span className="px-3 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm">
                  🎯 Job Application Tracker
                </span>
                <span className="px-3 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm">
                  📊 Career Analytics Dashboard
                </span>
                <span className="px-3 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm">
                  🧑‍💼 Recruiter ATS Dashboard
                </span>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Sparkles className="h-6 w-6 text-blue-400" />
            <span className="text-2xl font-bold">Interviewly</span>
          </div>
          <p className="text-gray-400 mb-4">
            AI-powered career preparation platform
          </p>
          <p className="text-gray-500 text-sm">
            © 2024 Interviewly. All rights reserved.
          </p>
        </div>
      </footer>

      <style jsx>{`
        @keyframes blob {
          0% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
          100% {
            transform: translate(0px, 0px) scale(1);
          }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>

      {/* Linda Chat Support */}
      <LindaChat />
    </main>
  );
}
