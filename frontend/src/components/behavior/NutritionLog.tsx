"use client";

import { useState, useEffect } from "react";
import { Plus, Trash2 } from "lucide-react";

interface NutritionEntry {
  date: string;
  calories: number;
  protein_grams: number;
}

export function NutritionLog() {
  const [entries, setEntries] = useState<NutritionEntry[]>([]);
  const [date, setDate] = useState("");
  const [calories, setCalories] = useState("");
  const [protein, setProtein] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchLogs = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/behavior/nutrition`);
      if (res.ok) {
        const data = await res.json();
        setEntries(data);
      }
    } catch (err) {
      console.error("Failed to fetch nutrition logs", err);
    }
  };

  useEffect(() => {
    const today = new Date().toISOString().split("T")[0];
    // eslint-disable-next-line
    setDate(today);
    // eslint-disable-next-line
    fetchLogs();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/behavior/nutrition`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          date,
          calories: parseInt(calories),
          protein_grams: parseInt(protein),
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to save nutrition log");
      }

      setCalories("");
      setProtein("");
      fetchLogs();
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (dateToDelete: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      await fetch(`${apiUrl}/api/behavior/nutrition/${dateToDelete}`, {
        method: "DELETE",
      });
      fetchLogs();
    } catch (err) {
      console.error("Failed to delete", err);
    }
  };

  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 shadow-sm">
      <h3 className="text-xl font-semibold mb-4">Nutrition Log</h3>

      {error && <p className="text-red-500 mb-4 text-sm">{error}</p>}

      <form onSubmit={handleSubmit} className="flex flex-wrap gap-4 mb-6">
        <div className="flex-1 min-w-[140px]">
          <label className="block text-sm font-medium mb-1">Date</label>
          <input
            type="date"
            required
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl px-4 py-2"
          />
        </div>
        <div className="flex-1 min-w-[120px]">
          <label className="block text-sm font-medium mb-1">Calories</label>
          <input
            type="number"
            required
            min="1"
            value={calories}
            onChange={(e) => setCalories(e.target.value)}
            placeholder="e.g. 2000"
            className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl px-4 py-2"
          />
        </div>
        <div className="flex-1 min-w-[120px]">
          <label className="block text-sm font-medium mb-1">Protein (g)</label>
          <input
            type="number"
            required
            min="1"
            value={protein}
            onChange={(e) => setProtein(e.target.value)}
            placeholder="e.g. 150"
            className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl px-4 py-2"
          />
        </div>
        <div className="flex items-end">
          <button
            type="submit"
            disabled={loading}
            className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-xl font-medium transition-colors flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add
          </button>
        </div>
      </form>

      <div className="space-y-3">
        {entries.length === 0 ? (
          <p className="text-zinc-500 text-sm">No nutrition logs yet.</p>
        ) : (
          entries.map((entry) => (
            <div
              key={entry.date}
              className="flex items-center justify-between p-4 bg-zinc-50 dark:bg-zinc-800/50 rounded-xl"
            >
              <div>
                <p className="font-medium">{entry.date}</p>
                <p className="text-sm text-zinc-500">
                  {entry.calories} kcal · {entry.protein_grams}g protein
                </p>
              </div>
              <button
                onClick={() => handleDelete(entry.date)}
                className="text-red-500 hover:text-red-600 p-2"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
