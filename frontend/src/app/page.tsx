"use client";

import Link from "next/link";
import { MessageSquare, ArrowRight, User, Calculator } from "lucide-react";
import { CoachingCard } from "@/components/assistant/CoachingCard";
import { useProfile } from "@/context/ProfileContext";
import { useAuth } from "@/context/AuthContext";
import { LogOut } from "lucide-react";
import { DashboardProgress } from "@/components/dashboard/DashboardProgress";
import { DashboardBehavior } from "@/components/dashboard/DashboardBehavior";

const GOAL_LABELS: Record<string, string> = {
  lose_fat: "Lose Fat",
  maintain: "Maintain",
  build_muscle: "Build Muscle",
};

export default function DashboardPage() {
  const { profileData, loading: profileLoading, error: fetchError } = useProfile();
  const { logout } = useAuth();

  return (
    <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50 pb-20">
      <div className="max-w-5xl mx-auto px-6 py-12 md:py-16">
        <header className="flex justify-between items-center mb-12">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-emerald-600 flex items-center justify-center text-white font-bold text-xl tracking-tighter shadow-lg">
              FM
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Welcome to your intelligence layer for fitness.</p>
            </div>
          </div>
          <button 
            onClick={logout}
            className="flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-900 dark:hover:text-white transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </header>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {/* Profile Card */}
          <Link href="/profile" className="group block h-full">
            <div className="p-6 rounded-3xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm hover:shadow-md hover:border-violet-500/30 transition-all h-full flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-violet-50 dark:bg-violet-950/50 text-violet-600 dark:text-violet-400 flex items-center justify-center shrink-0">
                    <User className="w-5 h-5" />
                  </div>
                  <h2 className="text-lg font-semibold flex items-center gap-2">
                    Fitness Profile
                    <ArrowRight className="w-4 h-4 opacity-0 -ml-4 group-hover:opacity-100 group-hover:ml-0 transition-all text-violet-600" />
                  </h2>
                </div>

                {profileLoading ? (
                  <div className="flex items-center gap-2 text-zinc-400 h-24">
                    <div className="animate-spin h-4 w-4 border-2 border-violet-500 border-t-transparent rounded-full" />
                    <span className="text-sm">Loading profile...</span>
                  </div>
                ) : fetchError ? (
                  <p className="text-red-500 dark:text-red-400 text-sm">{fetchError}</p>
                ) : profileData ? (
                  <div>
                    <div className="flex justify-between items-end mb-6">
                      <div>
                        <p className="text-3xl font-bold">{profileData.profile.weight_kg} <span className="text-sm font-normal text-zinc-500">kg</span></p>
                        <p className="text-xs text-zinc-500 dark:text-zinc-400 uppercase tracking-wider font-bold mt-1">Current Weight</p>
                      </div>
                      <div className="text-right">
                        <span className="text-xs font-bold px-2 py-1 rounded-full bg-violet-50 dark:bg-violet-950/50 text-violet-600 dark:text-violet-400 border border-violet-200 dark:border-violet-800">
                          {GOAL_LABELS[profileData.profile.goal] || profileData.profile.goal}
                        </span>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-4 gap-2">
                      <div className="p-2 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg text-center">
                        <p className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">TDEE</p>
                        <p className="text-sm font-bold">{profileData.derived_metrics.tdee}</p>
                      </div>
                      <div className="p-2 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg text-center">
                        <p className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">Cals</p>
                        <p className="text-sm font-bold text-violet-600 dark:text-violet-400">{profileData.derived_metrics.calorie_target}</p>
                      </div>
                      <div className="p-2 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg text-center">
                        <p className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">Prot</p>
                        <p className="text-sm font-bold">{profileData.derived_metrics.protein_target_min}g</p>
                      </div>
                      <div className="p-2 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg text-center">
                        <p className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">BMI</p>
                        <p className="text-sm font-bold text-emerald-600">{profileData.derived_metrics.bmi}</p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-zinc-500 dark:text-zinc-400 text-sm">
                    Create your fitness profile to get personalized guidance from FitMind.
                  </p>
                )}
              </div>
            </div>
          </Link>
          
          <div className="grid grid-rows-2 gap-6">
            <DashboardProgress />
            <DashboardBehavior />
          </div>
        </div>

        {/* Action Plan & Coaching */}
        <div className="mb-6">
          <CoachingCard />
        </div>

        {/* Utility Cards */}
        <div className="grid md:grid-cols-2 gap-6 mt-6">
          <Link href="/assistant" className="group">
            <div className="h-full p-6 rounded-3xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm hover:shadow-md hover:border-emerald-500/30 transition-all">
              <div className="flex items-center gap-4 mb-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <MessageSquare className="w-5 h-5" />
                </div>
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  FitMind Assistant
                  <ArrowRight className="w-4 h-4 opacity-0 -ml-4 group-hover:opacity-100 group-hover:ml-0 transition-all text-emerald-600" />
                </h2>
              </div>
              <p className="text-zinc-500 dark:text-zinc-400 text-sm leading-relaxed">
                Chat with your personalized AI fitness agent. Calculate macros, verify nutrition safety, and ask evidence-based questions.
              </p>
            </div>
          </Link>

          <Link href="/calculator" className="group">
            <div className="h-full p-6 rounded-3xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm hover:shadow-md hover:border-blue-500/30 transition-all">
              <div className="flex items-center gap-4 mb-3">
                <div className="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Calculator className="w-5 h-5" />
                </div>
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  Manual Calculator
                  <ArrowRight className="w-4 h-4 opacity-0 -ml-4 group-hover:opacity-100 group-hover:ml-0 transition-all text-blue-600" />
                </h2>
              </div>
              <p className="text-zinc-500 dark:text-zinc-400 text-sm leading-relaxed">
                Direct access to the deterministic math engine for BMR, TDEE, and optimal protein targets instantly.
              </p>
            </div>
          </Link>
        </div>
      </div>
    </main>
  );
}
