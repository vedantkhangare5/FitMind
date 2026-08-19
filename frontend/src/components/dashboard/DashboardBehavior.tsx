"use client";

import { useState, useEffect } from "react";
import { Activity, AlertCircle, ArrowRight } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import Link from "next/link";

interface BehaviorSummaryData {
  nutrition: {
    average_calories: number;
    average_protein: number;
    adherence: string;
  };
  workouts: {
    total_minutes: number;
    completed_workouts: number;
  };
  days_covered: number;
}

export function DashboardBehavior() {
  const [data, setData] = useState<BehaviorSummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const fetchBehavior = async () => {
      try {
        const json = await api.getBehaviorSummary();
        if (mounted) setData(json);
      } catch (err: unknown) {
        if (mounted) {
          if (err instanceof ApiError) setError(err.message);
          else if (err instanceof Error) setError(err.message);
          else setError("An unknown error occurred.");
        }
      } finally {
        if (mounted) setLoading(false);
      }
    };
    fetchBehavior();
    return () => { mounted = false; };
  }, []);

  if (loading) {
    return (
      <div className="p-6 rounded-3xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm animate-pulse flex items-center justify-center h-full min-h-[200px]">
        <div className="animate-spin h-6 w-6 border-2 border-pink-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 rounded-3xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm flex flex-col items-center justify-center h-full text-center text-red-500">
        <AlertCircle className="w-8 h-8 mb-2 opacity-50" />
        <p className="text-sm">{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-6 rounded-3xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm h-full flex flex-col justify-between group">
        <div>
          <div className="w-10 h-10 rounded-xl bg-pink-50 dark:bg-pink-950/50 text-pink-600 dark:text-pink-400 flex items-center justify-center mb-4">
            <Activity className="w-5 h-5" />
          </div>
          <h2 className="text-lg font-semibold mb-2">Behavior Summary</h2>
          <p className="text-zinc-500 dark:text-zinc-400 text-sm">No behavior data yet.</p>
        </div>
      </div>
    );
  }

  const getAdherenceColor = (adherence: string) => {
    switch (adherence) {
      case "High": return "text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/50";
      case "Moderate": return "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/50";
      case "Low": return "text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/50";
      default: return "text-zinc-600 dark:text-zinc-400 bg-zinc-50 dark:bg-zinc-800/50";
    }
  };

  return (
    <div className="p-6 rounded-3xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm h-full flex flex-col justify-between group relative overflow-hidden">
      <Link href="/behavior" className="absolute inset-0 z-10" />
      <div>
        <div className="flex justify-between items-start mb-4">
          <div className="w-10 h-10 rounded-xl bg-pink-50 dark:bg-pink-950/50 text-pink-600 dark:text-pink-400 flex items-center justify-center">
            <Activity className="w-5 h-5" />
          </div>
          <div className="text-right">
            <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-bold mb-1">Adherence</p>
            <span className={`text-xs font-bold px-2 py-1 rounded-full ${getAdherenceColor(data.nutrition.adherence)}`}>
              {data.nutrition.adherence}
            </span>
          </div>
        </div>
        
        <h2 className="text-lg font-semibold mb-1">7-Day Behavior</h2>
        <p className="text-xs text-zinc-500 mb-4">Averages over {data.days_covered} days</p>
        
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-xs text-zinc-500 mb-1">Avg Calories</p>
            <p className="text-lg font-bold">{Math.round(data.nutrition.average_calories)} <span className="text-xs font-normal text-zinc-500">kcal</span></p>
          </div>
          <div>
            <p className="text-xs text-zinc-500 mb-1">Avg Protein</p>
            <p className="text-lg font-bold">{Math.round(data.nutrition.average_protein)} <span className="text-xs font-normal text-zinc-500">g</span></p>
          </div>
          <div>
            <p className="text-xs text-zinc-500 mb-1">Workouts</p>
            <p className="text-lg font-bold">{data.workouts.completed_workouts} <span className="text-xs font-normal text-zinc-500">done</span></p>
          </div>
          <div>
            <p className="text-xs text-zinc-500 mb-1">Active Time</p>
            <p className="text-lg font-bold">{data.workouts.total_minutes} <span className="text-xs font-normal text-zinc-500">min</span></p>
          </div>
        </div>
      </div>
      
      <div className="mt-4 text-sm font-medium text-pink-600 dark:text-pink-400 flex items-center gap-1 group-hover:gap-2 transition-all">
        Log Behavior <ArrowRight className="w-4 h-4" />
      </div>
    </div>
  );
}
