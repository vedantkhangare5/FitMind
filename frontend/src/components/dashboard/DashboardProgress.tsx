"use client";

import { useState, useEffect } from "react";
import { TrendingUp, AlertCircle, ArrowRight } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import Link from "next/link";

interface ProgressSummaryData {
  current_weight: number | null;
  starting_weight: number | null;
  total_change_kg: number;
  percentage_change: number;
  trend: string;
  entries_count: number;
  note: string | null;
}

export function DashboardProgress() {
  const [data, setData] = useState<ProgressSummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const fetchProgress = async () => {
      try {
        const json = await api.getProgressSummary();
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
    fetchProgress();
    return () => { mounted = false; };
  }, []);

  if (loading) {
    return (
      <div className="p-6 rounded-3xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm animate-pulse flex items-center justify-center h-full min-h-[200px]">
        <div className="animate-spin h-6 w-6 border-2 border-amber-500 border-t-transparent rounded-full" />
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

  if (!data || data.entries_count === 0) {
    return (
      <div className="p-6 rounded-3xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm h-full flex flex-col justify-between group">
        <div>
          <div className="w-10 h-10 rounded-xl bg-amber-50 dark:bg-amber-950/50 text-amber-600 dark:text-amber-400 flex items-center justify-center mb-4">
            <TrendingUp className="w-5 h-5" />
          </div>
          <h2 className="text-lg font-semibold mb-2">Progress Summary</h2>
          <p className="text-zinc-500 dark:text-zinc-400 text-sm">No progress entries yet. Start tracking your weight to see your trend here.</p>
        </div>
        <Link href="/progress" className="mt-4 text-sm font-medium text-amber-600 dark:text-amber-400 flex items-center gap-1 group-hover:gap-2 transition-all">
          Log Progress <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  return (
    <div className="p-6 rounded-3xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm h-full flex flex-col justify-between group relative overflow-hidden">
      <Link href="/progress" className="absolute inset-0 z-10" />
      <div>
        <div className="flex justify-between items-start mb-4">
          <div className="w-10 h-10 rounded-xl bg-amber-50 dark:bg-amber-950/50 text-amber-600 dark:text-amber-400 flex items-center justify-center">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div className="text-right">
            <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-bold">Trend</p>
            <p className="font-semibold text-amber-600 dark:text-amber-400 capitalize">{data.trend.replace("_", " ")}</p>
          </div>
        </div>
        
        <h2 className="text-lg font-semibold mb-4">Progress Summary</h2>
        
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-xs text-zinc-500 mb-1">Current Weight</p>
            <p className="text-2xl font-bold">{data.current_weight} <span className="text-sm font-normal text-zinc-500">kg</span></p>
          </div>
          <div>
            <p className="text-xs text-zinc-500 mb-1">Total Change</p>
            <p className="text-2xl font-bold">
              {data.total_change_kg > 0 ? "+" : ""}{data.total_change_kg} <span className="text-sm font-normal text-zinc-500">kg</span>
            </p>
          </div>
        </div>

        {data.note && (
          <p className="text-xs text-zinc-500 bg-zinc-50 dark:bg-zinc-800/50 p-2 rounded-lg leading-relaxed">
            {data.note}
          </p>
        )}
      </div>
      
      <div className="mt-4 text-sm font-medium text-amber-600 dark:text-amber-400 flex items-center gap-1 group-hover:gap-2 transition-all">
        View History <ArrowRight className="w-4 h-4" />
      </div>
    </div>
  );
}
