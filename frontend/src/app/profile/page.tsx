"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowLeft, User, Save, Trash2, Pencil, X, CheckCircle } from "lucide-react";

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

const ACTIVITY_OPTIONS = [
  { value: "sedentary", label: "Sedentary (little to no exercise)" },
  { value: "lightly_active", label: "Lightly Active (1-3 days/week)" },
  { value: "moderately_active", label: "Moderately Active (3-5 days/week)" },
  { value: "very_active", label: "Very Active (6-7 days/week)" },
  { value: "extra_active", label: "Extra Active (physical job)" },
];

const GOAL_OPTIONS = [
  { value: "lose_fat", label: "Lose Fat" },
  { value: "maintain", label: "Maintain" },
  { value: "build_muscle", label: "Build Muscle" },
];

const DEFAULT_FORM: ProfileData = {
  age: 25,
  sex: "male",
  height_cm: 175,
  weight_kg: 70,
  activity_level: "moderately_active",
  goal: "maintain",
};

export default function ProfilePage() {
  const [profileData, setProfileData] = useState<ProfileResponse | null>(null);
  const [formData, setFormData] = useState<ProfileData>(DEFAULT_FORM);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await fetch(`${apiUrl}/api/profile`);
        if (res.status === 404) {
          setProfileData(null);
          setIsEditing(true); // Show form for creation
          return;
        }
        if (!res.ok) throw new Error("Failed to load profile");
        const data: ProfileResponse = await res.json();
        setProfileData(data);
        setFormData(data.profile);
      } catch (err: unknown) {
        if (err instanceof Error) setError(err.message);
        else setError("An unknown error occurred");
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [apiUrl]);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccessMessage(null);
    try {
      const res = await fetch(`${apiUrl}/api/profile`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...formData,
          age: Number(formData.age),
          height_cm: Number(formData.height_cm),
          weight_kg: Number(formData.weight_kg),
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        if (data.detail) {
          if (typeof data.detail === "string") throw new Error(data.detail);
          throw new Error(JSON.stringify(data.detail, null, 2));
        }
        throw new Error("Failed to save profile");
      }
      setProfileData(data);
      setFormData(data.profile);
      setIsEditing(false);
      setSuccessMessage("Profile saved successfully!");
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError("An unknown error occurred");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    setError(null);
    try {
      const res = await fetch(`${apiUrl}/api/profile`, { method: "DELETE" });
      if (!res.ok && res.status !== 204) throw new Error("Failed to delete profile");
      setProfileData(null);
      setFormData(DEFAULT_FORM);
      setIsEditing(true);
      setSuccessMessage("Profile deleted.");
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError("An unknown error occurred");
    }
  };

  const handleCancel = () => {
    if (profileData) {
      setFormData(profileData.profile);
      setIsEditing(false);
    }
  };

  const formatActivityLevel = (val: string) =>
    ACTIVITY_OPTIONS.find((o) => o.value === val)?.label || val;

  const formatGoal = (val: string) =>
    GOAL_OPTIONS.find((o) => o.value === val)?.label || val;

  if (loading) {
    return (
      <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50 flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-3 border-emerald-500 border-t-transparent rounded-full" />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50">
      <div className="max-w-2xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/"
            className="text-emerald-600 hover:underline flex items-center gap-1 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back Home
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-violet-50 dark:bg-violet-950/50 text-violet-600 dark:text-violet-400 flex items-center justify-center">
              <User className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">
                Your Fitness Profile
              </h1>
              <p className="text-zinc-500 text-sm mt-0.5">
                {profileData
                  ? "Your personalization data for FitMind"
                  : "Create your profile to get personalized guidance"}
              </p>
            </div>
          </div>
        </div>

        {/* Success/Error Messages */}
        {successMessage && (
          <div className="mb-6 p-4 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800/30 rounded-xl flex items-center gap-2 text-emerald-700 dark:text-emerald-400 text-sm animate-in fade-in">
            <CheckCircle className="w-4 h-4 shrink-0" />
            {successMessage}
          </div>
        )}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-xl text-sm font-mono overflow-auto">
            {error}
          </div>
        )}

        {/* Profile View */}
        {profileData && !isEditing && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm overflow-hidden">
              {/* Profile Fields */}
              <div className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg">
                    <p className="text-xs text-zinc-500 uppercase tracking-wider">
                      Age
                    </p>
                    <p className="text-xl font-semibold mt-1">
                      {profileData.profile.age}{" "}
                      <span className="text-sm font-normal text-zinc-500">
                        years
                      </span>
                    </p>
                  </div>
                  <div className="p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg">
                    <p className="text-xs text-zinc-500 uppercase tracking-wider">
                      Sex
                    </p>
                    <p className="text-xl font-semibold mt-1 capitalize">
                      {profileData.profile.sex}
                    </p>
                  </div>
                  <div className="p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg">
                    <p className="text-xs text-zinc-500 uppercase tracking-wider">
                      Height
                    </p>
                    <p className="text-xl font-semibold mt-1">
                      {profileData.profile.height_cm}{" "}
                      <span className="text-sm font-normal text-zinc-500">
                        cm
                      </span>
                    </p>
                  </div>
                  <div className="p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg">
                    <p className="text-xs text-zinc-500 uppercase tracking-wider">
                      Weight
                    </p>
                    <p className="text-xl font-semibold mt-1">
                      {profileData.profile.weight_kg}{" "}
                      <span className="text-sm font-normal text-zinc-500">
                        kg
                      </span>
                    </p>
                  </div>
                </div>
                <div className="p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg">
                  <p className="text-xs text-zinc-500 uppercase tracking-wider">
                    Activity Level
                  </p>
                  <p className="text-lg font-semibold mt-1">
                    {formatActivityLevel(profileData.profile.activity_level)}
                  </p>
                </div>
                <div className="p-3 bg-violet-50 dark:bg-violet-900/10 rounded-lg border border-violet-100 dark:border-violet-800/20">
                  <p className="text-xs text-violet-600 dark:text-violet-500 uppercase tracking-wider">
                    Goal
                  </p>
                  <p className="text-lg font-semibold text-violet-700 dark:text-violet-400 mt-1">
                    {formatGoal(profileData.profile.goal)}
                  </p>
                </div>
              </div>

              {/* Derived Metrics */}
              <div className="border-t border-zinc-200 dark:border-zinc-800 p-6">
                <h2 className="text-sm font-medium text-zinc-500 uppercase tracking-wider mb-4">
                  Calculated for You
                </h2>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-100 dark:border-zinc-800">
                    <p className="text-xs text-zinc-500 uppercase tracking-wider">
                      BMI
                    </p>
                    <p className="text-2xl font-bold">
                      {profileData.derived_metrics.bmi}
                    </p>
                    <p className="text-xs font-medium text-emerald-600 dark:text-emerald-400">
                      {profileData.derived_metrics.bmi_category}
                    </p>
                  </div>
                  <div className="p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-100 dark:border-zinc-800">
                    <p className="text-xs text-zinc-500 uppercase tracking-wider">
                      BMR
                    </p>
                    <p className="text-2xl font-bold">
                      {profileData.derived_metrics.bmr}{" "}
                      <span className="text-sm font-normal text-zinc-500">
                        kcal
                      </span>
                    </p>
                  </div>
                  <div className="p-3 bg-emerald-50 dark:bg-emerald-900/10 rounded-lg border border-emerald-100 dark:border-emerald-800/20">
                    <p className="text-xs text-emerald-600 dark:text-emerald-500 uppercase tracking-wider">
                      TDEE
                    </p>
                    <p className="text-2xl font-bold text-emerald-700 dark:text-emerald-400">
                      {profileData.derived_metrics.tdee}{" "}
                      <span className="text-sm font-normal text-emerald-600 dark:text-emerald-500">
                        kcal
                      </span>
                    </p>
                  </div>
                  <div className="p-3 bg-emerald-50 dark:bg-emerald-900/10 rounded-lg border border-emerald-100 dark:border-emerald-800/20">
                    <p className="text-xs text-emerald-600 dark:text-emerald-500 uppercase tracking-wider">
                      Calorie Target
                    </p>
                    <p className="text-2xl font-bold text-emerald-700 dark:text-emerald-400">
                      {profileData.derived_metrics.calorie_target}{" "}
                      <span className="text-sm font-normal text-emerald-600 dark:text-emerald-500">
                        kcal
                      </span>
                    </p>
                  </div>
                  <div className="col-span-2 p-3 bg-blue-50 dark:bg-blue-900/10 rounded-lg border border-blue-100 dark:border-blue-800/20">
                    <p className="text-xs text-blue-600 dark:text-blue-500 uppercase tracking-wider">
                      Protein Target Range
                    </p>
                    <p className="text-2xl font-bold text-blue-700 dark:text-blue-400">
                      {profileData.derived_metrics.protein_target_min} -{" "}
                      {profileData.derived_metrics.protein_target_max}{" "}
                      <span className="text-sm font-normal text-blue-600 dark:text-blue-500">
                        grams
                      </span>
                    </p>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="border-t border-zinc-200 dark:border-zinc-800 p-6 flex gap-3">
                <button
                  onClick={() => setIsEditing(true)}
                  className="flex-1 flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3 rounded-xl transition-colors"
                >
                  <Pencil className="w-4 h-4" />
                  Edit Profile
                </button>
                <button
                  onClick={handleDelete}
                  className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-red-200 dark:border-red-800/30 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/10 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Updated timestamp */}
            <p className="text-center text-xs text-zinc-400">
              Last updated:{" "}
              {new Date(profileData.updated_at).toLocaleString()}
            </p>
          </div>
        )}

        {/* Profile Form (Create or Edit) */}
        {isEditing && (
          <div className="bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-6">
              {profileData ? "Edit Profile" : "Create Your Profile"}
            </h2>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Age</label>
                  <input
                    type="number"
                    value={formData.age}
                    onChange={(e) =>
                      setFormData({ ...formData, age: Number(e.target.value) })
                    }
                    className="w-full p-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-transparent focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none transition"
                    required
                    min={1}
                    max={119}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Sex</label>
                  <select
                    value={formData.sex}
                    onChange={(e) =>
                      setFormData({ ...formData, sex: e.target.value })
                    }
                    className="w-full p-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-transparent focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none transition"
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Height (cm)
                  </label>
                  <input
                    type="number"
                    value={formData.height_cm}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        height_cm: Number(e.target.value),
                      })
                    }
                    className="w-full p-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-transparent focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none transition"
                    required
                    min={51}
                    max={299}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Weight (kg)
                  </label>
                  <input
                    type="number"
                    value={formData.weight_kg}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        weight_kg: Number(e.target.value),
                      })
                    }
                    className="w-full p-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-transparent focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none transition"
                    required
                    min={11}
                    max={399}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  Activity Level
                </label>
                <select
                  value={formData.activity_level}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      activity_level: e.target.value,
                    })
                  }
                  className="w-full p-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-transparent focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none transition"
                >
                  {ACTIVITY_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Goal</label>
                <select
                  value={formData.goal}
                  onChange={(e) =>
                    setFormData({ ...formData, goal: e.target.value })
                  }
                  className="w-full p-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-transparent focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none transition"
                >
                  {GOAL_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="flex-1 flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3 rounded-xl transition-colors disabled:opacity-50"
                >
                  <Save className="w-4 h-4" />
                  {saving ? "Saving..." : "Save Profile"}
                </button>
                {profileData && (
                  <button
                    onClick={handleCancel}
                    className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl border border-zinc-300 dark:border-zinc-700 text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                  >
                    <X className="w-4 h-4" />
                    Cancel
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
