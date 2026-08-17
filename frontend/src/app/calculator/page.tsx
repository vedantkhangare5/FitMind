"use client";

import { useState } from "react";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";

interface FitnessResponse {
  bmi: number;
  bmi_category: string;
  bmr: number;
  tdee: number;
  calorie_target: number;
  protein_target_min: number;
  protein_target_max: number;
  warnings: string[];
}

export default function CalculatorPage() {
  const [formData, setFormData] = useState({
    age: 30,
    sex: "male",
    height_cm: 175,
    weight_kg: 70,
    activity_level: "moderately_active",
    goal: "lose_fat"
  });

  const [result, setResult] = useState<FitnessResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await api.calculateFitness({
        ...formData,
        age: Number(formData.age),
        height_cm: Number(formData.height_cm),
        weight_kg: Number(formData.weight_kg),
      });

      setResult(data);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        if (err.code === "VALIDATION_ERROR" || err.details) {
            setError(JSON.stringify(err.details || err.message, null, 2));
        } else {
            setError(err.message);
        }
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unknown error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen p-8 bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <Link href="/" className="text-emerald-600 hover:underline flex items-center gap-1">
            &larr; Back Home
          </Link>
          <h1 className="text-3xl font-bold mt-4">Fitness Calculator</h1>
          <p className="text-zinc-500 mt-2">Deterministic math engine (No AI involved here)</p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* FORM */}
          <div className="bg-white dark:bg-zinc-900 p-6 rounded-xl shadow-sm border border-zinc-200 dark:border-zinc-800">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Age</label>
                  <input
                    type="number"
                    value={formData.age}
                    onChange={e => setFormData({...formData, age: Number(e.target.value)})}
                    className="w-full p-2 border border-zinc-300 dark:border-zinc-700 rounded bg-transparent"
                    required min={1} max={120}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Sex</label>
                  <select
                    value={formData.sex}
                    onChange={e => setFormData({...formData, sex: e.target.value})}
                    className="w-full p-2 border border-zinc-300 dark:border-zinc-700 rounded bg-transparent"
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Height (cm)</label>
                  <input
                    type="number"
                    value={formData.height_cm}
                    onChange={e => setFormData({...formData, height_cm: Number(e.target.value)})}
                    className="w-full p-2 border border-zinc-300 dark:border-zinc-700 rounded bg-transparent"
                    required min={50} max={300}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Weight (kg)</label>
                  <input
                    type="number"
                    value={formData.weight_kg}
                    onChange={e => setFormData({...formData, weight_kg: Number(e.target.value)})}
                    className="w-full p-2 border border-zinc-300 dark:border-zinc-700 rounded bg-transparent"
                    required min={10} max={400}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Activity Level</label>
                <select
                  value={formData.activity_level}
                  onChange={e => setFormData({...formData, activity_level: e.target.value})}
                  className="w-full p-2 border border-zinc-300 dark:border-zinc-700 rounded bg-transparent"
                >
                  <option value="sedentary">Sedentary (little to no exercise)</option>
                  <option value="lightly_active">Lightly Active (1-3 days/week)</option>
                  <option value="moderately_active">Moderately Active (3-5 days/week)</option>
                  <option value="very_active">Very Active (6-7 days/week)</option>
                  <option value="extra_active">Extra Active (physical job)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Goal</label>
                <select
                  value={formData.goal}
                  onChange={e => setFormData({...formData, goal: e.target.value})}
                  className="w-full p-2 border border-zinc-300 dark:border-zinc-700 rounded bg-transparent"
                >
                  <option value="lose_fat">Lose Fat</option>
                  <option value="maintain">Maintain</option>
                  <option value="build_muscle">Build Muscle</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3 rounded-lg transition-colors disabled:opacity-50"
              >
                {loading ? "Calculating..." : "Calculate"}
              </button>
            </form>
          </div>

          {/* RESULTS */}
          <div className="bg-white dark:bg-zinc-900 p-6 rounded-xl shadow-sm border border-zinc-200 dark:border-zinc-800 h-fit">
            <h2 className="text-xl font-semibold mb-4 border-b border-zinc-200 dark:border-zinc-800 pb-2">Results</h2>
            
            {error && (
              <div className="p-4 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm font-mono overflow-auto mb-4">
                {error}
              </div>
            )}

            {!result && !error && !loading && (
              <p className="text-zinc-500 italic">Fill out the form and hit Calculate to see results.</p>
            )}

            {result && (
              <div className="space-y-4">
                {result.warnings.length > 0 && (
                  <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/30 rounded-lg">
                    <h3 className="font-bold text-amber-800 dark:text-amber-400 flex items-center gap-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                      Safety Warning
                    </h3>
                    <ul className="list-disc ml-5 mt-2 text-sm text-amber-700 dark:text-amber-300 space-y-1">
                      {result.warnings.map((w, i) => <li key={i}>{w}</li>)}
                    </ul>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-100 dark:border-zinc-800">
                    <p className="text-xs text-zinc-500 uppercase tracking-wider">BMI</p>
                    <p className="text-2xl font-bold">{result.bmi}</p>
                    <p className="text-xs font-medium text-emerald-600 dark:text-emerald-400">{result.bmi_category}</p>
                  </div>
                  <div className="p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-100 dark:border-zinc-800">
                    <p className="text-xs text-zinc-500 uppercase tracking-wider">BMR</p>
                    <p className="text-2xl font-bold">{result.bmr} <span className="text-sm font-normal text-zinc-500">kcal</span></p>
                  </div>
                  <div className="p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-100 dark:border-zinc-800">
                    <p className="text-xs text-zinc-500 uppercase tracking-wider">TDEE</p>
                    <p className="text-2xl font-bold">{result.tdee} <span className="text-sm font-normal text-zinc-500">kcal</span></p>
                  </div>
                  <div className="p-3 bg-emerald-50 dark:bg-emerald-900/10 rounded-lg border border-emerald-100 dark:border-emerald-800/20">
                    <p className="text-xs text-emerald-600 dark:text-emerald-500 uppercase tracking-wider">Calorie Target</p>
                    <p className="text-2xl font-bold text-emerald-700 dark:text-emerald-400">{result.calorie_target} <span className="text-sm font-normal text-emerald-600 dark:text-emerald-500">kcal</span></p>
                  </div>
                  <div className="col-span-2 p-3 bg-blue-50 dark:bg-blue-900/10 rounded-lg border border-blue-100 dark:border-blue-800/20">
                    <p className="text-xs text-blue-600 dark:text-blue-500 uppercase tracking-wider">Protein Target Range</p>
                    <p className="text-2xl font-bold text-blue-700 dark:text-blue-400">
                      {result.protein_target_min} - {result.protein_target_max} <span className="text-sm font-normal text-blue-600 dark:text-blue-500">grams</span>
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
