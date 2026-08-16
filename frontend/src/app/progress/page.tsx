"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowLeft, Trash2 } from "lucide-react";
import { ProgressChart } from "@/components/progress/ProgressChart";
import { Button } from "@/components/ui/Button";

interface ProgressEntry {
  id: number;
  weight_kg: number;
  recorded_at: string;
}

interface ProgressSummary {
  current_weight: number | null;
  starting_weight: number | null;
  total_change_kg: number | null;
  percentage_change: number | null;
  trend: string;
  entries_count: number;
  note: string | null;
}

interface ProgressHistoryResponse {
  entries: ProgressEntry[];
  summary: ProgressSummary;
}

const TREND_LABELS: Record<string, { label: string, color: string }> = {
  insufficient_data: { label: "Need More Data", color: "text-zinc-500 bg-zinc-100 dark:bg-zinc-800" },
  losing: { label: "Trending Down", color: "text-emerald-600 bg-emerald-50 dark:bg-emerald-950/50" },
  gaining: { label: "Trending Up", color: "text-blue-600 bg-blue-50 dark:bg-blue-950/50" },
  stable: { label: "Stable", color: "text-violet-600 bg-violet-50 dark:bg-violet-950/50" }
};

export default function ProgressPage() {
  const [data, setData] = useState<ProgressHistoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [newWeight, setNewWeight] = useState("");
  const [adding, setAdding] = useState(false);

  const fetchData = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/progress`);
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchData();
  }, []);

  const handleAddEntry = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newWeight || isNaN(Number(newWeight))) return;

    setAdding(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/progress`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ weight_kg: Number(newWeight) }),
      });
      if (res.ok) {
        setNewWeight("");
        await fetchData();
      }
    } finally {
      setAdding(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this entry?")) return;
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/progress/${id}`, {
        method: "DELETE",
      });
      if (res.ok) {
        await fetchData();
      }
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950 p-6 flex items-center justify-center">
        <div className="animate-spin h-6 w-6 border-2 border-violet-500 border-t-transparent rounded-full" />
      </main>
    );
  }

  const summary = data?.summary;
  const entries = data?.entries || [];

  return (
    <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50">
      <div className="max-w-4xl mx-auto px-6 py-12 md:py-20 space-y-8">
        
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link href="/" className="p-2 rounded-full hover:bg-zinc-200 dark:hover:bg-zinc-800 transition-colors">
            <ArrowLeft className="w-6 h-6" />
          </Link>
          <h1 className="text-3xl font-bold tracking-tight">Progress History</h1>
        </div>

        {/* Summary Cards */}
        {summary && summary.entries_count > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-6 rounded-2xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm">
              <p className="text-sm text-zinc-500 mb-1">Current Weight</p>
              <p className="text-3xl font-bold">{summary.current_weight} <span className="text-base font-normal text-zinc-500">kg</span></p>
            </div>
            <div className="p-6 rounded-2xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm">
              <p className="text-sm text-zinc-500 mb-1">Total Change</p>
              <p className="text-3xl font-bold">
                {summary.total_change_kg! > 0 ? "+" : ""}{summary.total_change_kg} <span className="text-base font-normal text-zinc-500">kg</span>
              </p>
            </div>
            <div className="p-6 rounded-2xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm">
              <p className="text-sm text-zinc-500 mb-1">Percentage</p>
              <p className="text-3xl font-bold">
                {summary.percentage_change! > 0 ? "+" : ""}{summary.percentage_change}%
              </p>
            </div>
            <div className="p-6 rounded-2xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm flex flex-col justify-center items-start">
              <p className="text-sm text-zinc-500 mb-2">Trend Estimate</p>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${TREND_LABELS[summary.trend]?.color || TREND_LABELS["stable"].color}`}>
                {TREND_LABELS[summary.trend]?.label || "Stable"}
              </span>
            </div>
          </div>
        )}

        {summary?.note && (
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 rounded-xl text-sm border border-blue-200 dark:border-blue-800">
            {summary.note}
          </div>
        )}

        {/* Chart */}
        <section>
          <h2 className="text-xl font-semibold mb-4">Weight Trend</h2>
          <ProgressChart data={entries} />
        </section>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Add Entry Form */}
          <section className="md:col-span-1">
            <div className="p-6 rounded-2xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm sticky top-6">
              <h2 className="text-lg font-semibold mb-4">Log Weight</h2>
              <form onSubmit={handleAddEntry} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                    Weight (kg)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="20"
                    max="500"
                    required
                    value={newWeight}
                    onChange={(e) => setNewWeight(e.target.value)}
                    className="w-full px-4 py-2 bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl focus:ring-2 focus:ring-violet-500 outline-none transition-all"
                    placeholder="e.g. 75.5"
                  />
                </div>
                <Button type="submit" className="w-full" disabled={adding}>
                  {adding ? "Saving..." : "Save Entry"}
                </Button>
                <p className="text-xs text-zinc-500 text-center mt-4">
                  Entries are logged with the current time.
                </p>
              </form>
            </div>
          </section>

          {/* History List */}
          <section className="md:col-span-2">
            <h2 className="text-lg font-semibold mb-4">History Log</h2>
            <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl overflow-hidden shadow-sm">
              {entries.length === 0 ? (
                <div className="p-8 text-center text-zinc-500">
                  No entries recorded yet.
                </div>
              ) : (
                <div className="divide-y divide-zinc-200 dark:divide-zinc-800">
                  {[...entries].reverse().map((entry) => (
                    <div key={entry.id} className="flex items-center justify-between p-4 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors">
                      <div>
                        <p className="font-semibold text-lg">{entry.weight_kg} kg</p>
                        <p className="text-sm text-zinc-500">
                          {new Date(entry.recorded_at).toLocaleString()}
                        </p>
                      </div>
                      <button
                        onClick={() => handleDelete(entry.id)}
                        className="p-2 text-zinc-400 hover:text-red-500 transition-colors"
                        aria-label="Delete entry"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
