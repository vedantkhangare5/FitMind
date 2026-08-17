"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Activity, MessageSquare, ArrowRight, User, TrendingUp } from "lucide-react";
import { CoachingCard } from "@/components/assistant/CoachingCard";

interface ProfileData {
  age: number;
  sex: string;
  height_cm: number;
  weight_kg: number;
  activity_level: string;
  goal: string;
}

interface DerivedMetrics {
  bmi: number;
  bmi_category: string;
  bmr: number;
  tdee: number;
  calorie_target: number;
  protein_target_min: number;
  protein_target_max: number;
}

interface ProfileResponse {
  profile: ProfileData;
  updated_at: string;
  derived_metrics: DerivedMetrics;
}

const GOAL_LABELS: Record<string, string> = {
  lose_fat: "Lose Fat",
  maintain: "Maintain",
  build_muscle: "Build Muscle",
};

export default function DashboardPage() {
  const [profileData, setProfileData] = useState<ProfileResponse | null>(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [fetchError, setFetchError] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const apiUrl =
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${apiUrl}/api/profile`);
        if (res.ok) {
          const data: ProfileResponse = await res.json();
          setProfileData(data);
          setFetchError(false);
        } else {
          setFetchError(true);
        }
      } catch {
        setFetchError(true);
      } finally {
        setProfileLoading(false);
      }
    };
    fetchProfile();
  }, []);

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
            Experience the future of fitness planning. Deterministic math engine
            combined with grounded knowledge retrieval.
          </p>
        </header>

        <div className="max-w-3xl mx-auto space-y-6">
          {/* Profile Card — Full Width on Top */}
          <Link href="/profile" className="group block">
            <div className="p-8 rounded-3xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm hover:shadow-md hover:border-violet-500/30 transition-all">
              <div className="flex items-start gap-6">
                <div className="w-12 h-12 rounded-xl bg-violet-50 dark:bg-violet-950/50 text-violet-600 dark:text-violet-400 flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform">
                  <User className="w-6 h-6" />
                </div>
                <div className="flex-1 min-w-0">
                  <h2 className="text-2xl font-semibold mb-2 flex items-center gap-2">
                    Fitness Profile
                    <ArrowRight className="w-5 h-5 opacity-0 -ml-4 group-hover:opacity-100 group-hover:ml-0 transition-all text-violet-600" />
                  </h2>

                  {profileLoading ? (
                    <div className="flex items-center gap-2 text-zinc-400">
                      <div className="animate-spin h-4 w-4 border-2 border-violet-500 border-t-transparent rounded-full" />
                      <span className="text-sm">Loading profile...</span>
                    </div>
                  ) : fetchError ? (
                    <p className="text-red-500 dark:text-red-400">
                      Unable to load profile due to a network error.
                    </p>
                  ) : profileData ? (
                    <div>
                      <p className="text-zinc-500 dark:text-zinc-400 mb-4">
                        {profileData.profile.weight_kg} kg ·{" "}
                        {profileData.profile.height_cm} cm ·{" "}
                        {profileData.profile.age} yrs · Goal:{" "}
                        {GOAL_LABELS[profileData.profile.goal] ||
                          profileData.profile.goal}
                      </p>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        <div className="p-2.5 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg">
                          <p className="text-[10px] text-zinc-500 uppercase tracking-wider">
                            TDEE
                          </p>
                          <p className="text-lg font-bold">
                            {profileData.derived_metrics.tdee}{" "}
                            <span className="text-xs font-normal text-zinc-500">
                              kcal
                            </span>
                          </p>
                        </div>
                        <div className="p-2.5 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg">
                          <p className="text-[10px] text-zinc-500 uppercase tracking-wider">
                            Calories
                          </p>
                          <p className="text-lg font-bold">
                            {profileData.derived_metrics.calorie_target}{" "}
                            <span className="text-xs font-normal text-zinc-500">
                              kcal
                            </span>
                          </p>
                        </div>
                        <div className="p-2.5 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg">
                          <p className="text-[10px] text-zinc-500 uppercase tracking-wider">
                            Protein
                          </p>
                          <p className="text-lg font-bold">
                            {profileData.derived_metrics.protein_target_min}-
                            {profileData.derived_metrics.protein_target_max}{" "}
                            <span className="text-xs font-normal text-zinc-500">
                              g
                            </span>
                          </p>
                        </div>
                        <div className="p-2.5 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg">
                          <p className="text-[10px] text-zinc-500 uppercase tracking-wider">
                            BMI
                          </p>
                          <p className="text-lg font-bold">
                            {profileData.derived_metrics.bmi}{" "}
                            <span className="text-xs font-normal text-emerald-600">
                              {profileData.derived_metrics.bmi_category}
                            </span>
                          </p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="text-zinc-500 dark:text-zinc-400">
                      Create your fitness profile to get personalized guidance
                      from FitMind.
                    </p>
                  )}
                </div>
              </div>
            </div>
          </Link>

          <CoachingCard />

          {/* Features Grid — 3-Column */}
          <div className="grid md:grid-cols-3 gap-6">
            {/* Assistant Card */}
            <Link href="/assistant" className="group">
              <div className="h-full p-8 rounded-3xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm hover:shadow-md hover:border-emerald-500/30 transition-all">
                <div className="w-12 h-12 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <MessageSquare className="w-6 h-6" />
                </div>
                <h2 className="text-xl font-semibold mb-3 flex items-center gap-2">
                  FitMind Assistant
                  <ArrowRight className="w-5 h-5 opacity-0 -ml-4 group-hover:opacity-100 group-hover:ml-0 transition-all text-emerald-600" />
                </h2>
                <p className="text-zinc-500 dark:text-zinc-400 text-sm leading-relaxed">
                  Chat with your personalized AI fitness agent. Calculate
                  macros, verify nutrition safety, and answer questions.
                </p>
              </div>
            </Link>

            {/* Calculator Card */}
            <Link href="/calculator" className="group">
              <div className="h-full p-8 rounded-3xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm hover:shadow-md hover:border-blue-500/30 transition-all">
                <div className="w-12 h-12 rounded-xl bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <Activity className="w-6 h-6" />
                </div>
                <h2 className="text-xl font-semibold mb-3 flex items-center gap-2">
                  Manual Calculator
                  <ArrowRight className="w-5 h-5 opacity-0 -ml-4 group-hover:opacity-100 group-hover:ml-0 transition-all text-blue-600" />
                </h2>
                <p className="text-zinc-500 dark:text-zinc-400 text-sm leading-relaxed">
                  Direct access to the deterministic math engine for BMR, TDEE,
                  and optimal protein targets instantly.
                </p>
              </div>
            </Link>

            {/* Progress Card */}
            <Link href="/progress" className="group">
              <div className="h-full p-8 rounded-3xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm hover:shadow-md hover:border-amber-500/30 transition-all">
                <div className="w-12 h-12 rounded-xl bg-amber-50 dark:bg-amber-950/50 text-amber-600 dark:text-amber-400 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <TrendingUp className="w-6 h-6" />
                </div>
                <h2 className="text-xl font-semibold mb-3 flex items-center gap-2">
                  Progress History
                  <ArrowRight className="w-5 h-5 opacity-0 -ml-4 group-hover:opacity-100 group-hover:ml-0 transition-all text-amber-600" />
                </h2>
                <p className="text-zinc-500 dark:text-zinc-400 text-sm leading-relaxed">
                  Track your weight changes over time with deterministic trends
                  and a visual graph separated from your profile.
                </p>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}

