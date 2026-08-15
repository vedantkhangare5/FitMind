"use client";

import Link from "next/link";
import { Activity, MessageSquare, ArrowRight } from "lucide-react";

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50">
      <div className="max-w-5xl mx-auto px-6 py-12 md:py-20">
        <header className="text-center mb-16">
          <div className="w-16 h-16 rounded-2xl bg-emerald-600 flex items-center justify-center text-white font-bold text-2xl tracking-tighter shadow-lg mx-auto mb-6">
            FM
          </div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4 text-balance">
            Your Intelligence Layer for Fitness
          </h1>
          <p className="text-lg text-zinc-500 dark:text-zinc-400 max-w-2xl mx-auto">
            Experience the future of fitness planning. Deterministic math engine combined with grounded knowledge retrieval.
          </p>
        </header>

        <div className="grid md:grid-cols-2 gap-6 max-w-3xl mx-auto">
          {/* Assistant Card */}
          <Link href="/assistant" className="group">
            <div className="h-full p-8 rounded-3xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm hover:shadow-md hover:border-emerald-500/30 transition-all">
              <div className="w-12 h-12 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <MessageSquare className="w-6 h-6" />
              </div>
              <h2 className="text-2xl font-semibold mb-3 flex items-center gap-2">
                FitMind Assistant
                <ArrowRight className="w-5 h-5 opacity-0 -ml-4 group-hover:opacity-100 group-hover:ml-0 transition-all text-emerald-600" />
              </h2>
              <p className="text-zinc-500 dark:text-zinc-400 leading-relaxed">
                Chat with your personalized AI fitness agent. It can calculate your macros, verify nutrition safety, and answer questions using verified scientific sources.
              </p>
            </div>
          </Link>

          {/* Calculator Card */}
          <Link href="/calculator" className="group">
            <div className="h-full p-8 rounded-3xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm hover:shadow-md hover:border-blue-500/30 transition-all">
              <div className="w-12 h-12 rounded-xl bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Activity className="w-6 h-6" />
              </div>
              <h2 className="text-2xl font-semibold mb-3 flex items-center gap-2">
                Manual Calculator
                <ArrowRight className="w-5 h-5 opacity-0 -ml-4 group-hover:opacity-100 group-hover:ml-0 transition-all text-blue-600" />
              </h2>
              <p className="text-zinc-500 dark:text-zinc-400 leading-relaxed">
                Direct access to the deterministic math engine. Calculate your BMR, TDEE, and optimal protein targets instantly without AI processing.
              </p>
            </div>
          </Link>
        </div>
      </div>
    </main>
  );
}
