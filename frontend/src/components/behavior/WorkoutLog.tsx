"use client";

import { useState, useEffect } from "react";
import { Plus, Trash2, CheckCircle2, Circle } from "lucide-react";
import { api } from "@/lib/api";

interface WorkoutEntry {
  id: number;
  date: string;
  workout_type: string;
  duration_minutes: number;
  completed: boolean;
}

export function WorkoutLog() {
  const [entries, setEntries] = useState<WorkoutEntry[]>([]);
  const [date, setDate] = useState("");
  const [workoutType, setWorkoutType] = useState("");
  const [duration, setDuration] = useState("");
  const [completed, setCompleted] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchLogs = async () => {
    try {
      const data = await api.getWorkoutLogs();
      setEntries(data);
    } catch (err) {
      console.error("Failed to fetch workout logs", err);
    }
  };

  useEffect(() => {
    const today = new Date().toISOString().split("T")[0];
    // eslint-disable-next-line
    setDate(today);
    fetchLogs();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await api.addWorkoutLog({
        date,
        workout_type: workoutType,
        duration_minutes: parseInt(duration),
        completed,
      });

      setWorkoutType("");
      setDuration("");
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

  const handleDelete = async (id: number) => {
    try {
      await api.deleteWorkoutLog(id);
      fetchLogs();
    } catch (err) {
      console.error("Failed to delete", err);
    }
  };

  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 shadow-sm">
      <h3 className="text-xl font-semibold mb-4">Workout Log</h3>

      {error && <p className="text-red-500 mb-4 text-sm">{error}</p>}

      <form onSubmit={handleSubmit} className="flex flex-wrap gap-4 mb-6 items-end">
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
        <div className="flex-1 min-w-[140px]">
          <label className="block text-sm font-medium mb-1">Type</label>
          <input
            type="text"
            required
            value={workoutType}
            onChange={(e) => setWorkoutType(e.target.value)}
            placeholder="e.g. Weightlifting"
            className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl px-4 py-2"
          />
        </div>
        <div className="flex-1 min-w-[100px]">
          <label className="block text-sm font-medium mb-1">Minutes</label>
          <input
            type="number"
            required
            min="1"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            placeholder="45"
            className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl px-4 py-2"
          />
        </div>
        <div className="flex items-center gap-2 mb-2">
          <input
            type="checkbox"
            id="completed"
            checked={completed}
            onChange={(e) => setCompleted(e.target.checked)}
            className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500"
          />
          <label htmlFor="completed" className="text-sm font-medium">Completed</label>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-xl font-medium transition-colors flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add
        </button>
      </form>

      <div className="space-y-3">
        {entries.length === 0 ? (
          <p className="text-zinc-500 text-sm">No workouts logged yet.</p>
        ) : (
          entries.map((entry) => (
            <div
              key={entry.id}
              className={`flex items-center justify-between p-4 rounded-xl ${
                entry.completed
                  ? "bg-blue-50 dark:bg-blue-950/30"
                  : "bg-zinc-50 dark:bg-zinc-800/50 opacity-70"
              }`}
            >
              <div className="flex items-center gap-4">
                {entry.completed ? (
                  <CheckCircle2 className="w-5 h-5 text-blue-500" />
                ) : (
                  <Circle className="w-5 h-5 text-zinc-400" />
                )}
                <div>
                  <p className="font-medium">
                    {entry.workout_type}
                    {!entry.completed && " (Skipped/Planned)"}
                  </p>
                  <p className="text-sm text-zinc-500">
                    {entry.date} · {entry.duration_minutes} min
                  </p>
                </div>
              </div>
              <button
                onClick={() => handleDelete(entry.id)}
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
