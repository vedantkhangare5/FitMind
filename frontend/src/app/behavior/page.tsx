"use client";

import Link from "next/link";
import { ArrowLeft, Activity } from "lucide-react";
import { NutritionLog } from "@/components/behavior/NutritionLog";
import { WorkoutLog } from "@/components/behavior/WorkoutLog";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";

interface BehaviorSummary {
  window_days: number;
  nutrition: {
    logged_days: number;
    coverage: number;
    avg_calories: number | null;
    avg_protein: number | null;
    calorie_target?: number;
    calorie_adherence?: number;
    protein_target?: number;
    protein_adherence?: number;
  };
  workouts: {
    logged_count: number;
    completed_count: number;
    target_frequency?: number;
    adherence?: number;
  };
}

export default function BehaviorPage() {
  const [summary, setSummary] = useState<BehaviorSummary | null>(null);

  const fetchSummary = async () => {
    try {
      const data = await api.getBehaviorSummary();
      setSummary(data);
    } catch (err) {
      console.error("Failed to fetch summary", err);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line
    fetchSummary();
  }, []);

  return (
    <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50">
      <div className="max-w-5xl mx-auto px-6 py-12">
        <Link
          href="/"
          className="inline-flex items-center text-sm text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors mb-8"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </Link>

        <header className="mb-12">
          <div className="w-16 h-16 rounded-2xl bg-blue-600 flex items-center justify-center text-white shadow-lg mb-6">
            <Activity className="w-8 h-8" />
          </div>
          <h1 className="text-4xl font-bold tracking-tight mb-4">
            Tracking: Behavior
          </h1>
          <p className="text-lg text-zinc-500 dark:text-zinc-400">
            Log your daily nutrition and workouts to track adherence over time.
          </p>
        </header>

        {summary && (
          <div className="mb-8 p-6 bg-white dark:bg-zinc-900 rounded-3xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
            <h2 className="text-lg font-semibold mb-4">7-Day Adherence Summary</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="p-4 bg-zinc-50 dark:bg-zinc-950 rounded-xl">
                <p className="text-sm text-zinc-500 mb-2">Nutrition (Logged {summary.nutrition.logged_days}/7 days)</p>
                {summary.nutrition.calorie_adherence !== undefined ? (
                  <p className="text-2xl font-bold">{summary.nutrition.calorie_adherence}% <span className="text-sm font-normal text-zinc-500">Calorie Adherence</span></p>
                ) : (
                  <p className="text-sm text-zinc-500">No targets or logs available.</p>
                )}
                {summary.nutrition.protein_adherence !== undefined && (
                  <p className="text-2xl font-bold mt-2">{summary.nutrition.protein_adherence}% <span className="text-sm font-normal text-zinc-500">Protein Adherence</span></p>
                )}
              </div>
              <div className="p-4 bg-zinc-50 dark:bg-zinc-950 rounded-xl">
                <p className="text-sm text-zinc-500 mb-2">Workouts (Last 7 Days)</p>
                <p className="text-2xl font-bold">{summary.workouts.completed_count} <span className="text-sm font-normal text-zinc-500">Completed</span></p>
              </div>
            </div>
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-8">
          <div onClick={fetchSummary}>
            <NutritionLog />
          </div>
          <div onClick={fetchSummary}>
            <WorkoutLog />
          </div>
        </div>
      </div>
    </main>
  );
}
