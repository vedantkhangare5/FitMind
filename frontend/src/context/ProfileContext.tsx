"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

type ProfileData = {
  age: number;
  sex: string;
  height_cm: number;
  weight_kg: number;
  activity_level: string;
  goal: string;
};

type DerivedMetrics = {
  bmi: number;
  bmi_category: string;
  bmr: number;
  tdee: number;
  calorie_target: number;
  protein_target_min: number;
  protein_target_max: number;
};

type ProfileResponse = {
  profile: ProfileData;
  updated_at: string;
  derived_metrics: DerivedMetrics;
};

type ProfileContextType = {
  profileData: ProfileResponse | null;
  loading: boolean;
  error: string | null;
  refreshProfile: () => Promise<void>;
  updateProfile: (data: Partial<ProfileData>) => Promise<void>;
  deleteProfile: () => Promise<void>;
};

const ProfileContext = createContext<ProfileContextType | undefined>(undefined);

export function ProfileProvider({ children }: { children: ReactNode }) {
  const [profileData, setProfileData] = useState<ProfileResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { setAuthStatus, isAuthenticated } = useAuth();



  const refreshProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getProfile();
      setProfileData(data);
      setAuthStatus(true);
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 401) {
          setAuthStatus(false);
          setProfileData(null);
          setError(null);
        } else if (err.status === 404) {
          setAuthStatus(true);
          setProfileData(null);
          setError(null);
        } else {
          setAuthStatus(true); // Assuming server error, keep session if they had one? Actually, we don't know. Let's just set error.
          setError(err.message);
        }
      } else {
        setError(err instanceof Error ? err.message : "Failed to load profile");
      }
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async (data: Partial<ProfileData>) => {
    try {
      setError(null);
      await api.updateProfile(data);
      await refreshProfile(); // Refresh to get the latest
    } catch (err) {
      if (err instanceof ApiError) {
        throw err;
      }
      throw new Error("Failed to update profile");
    }
  };

  const deleteProfile = async () => {
    try {
      setError(null);
      await api.deleteProfile();
      setProfileData(null);
    } catch (err) {
      if (err instanceof ApiError) {
        throw err;
      }
      throw new Error("Failed to delete profile");
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    refreshProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      setTimeout(() => setProfileData(null), 0);
    } else if (isAuthenticated && !profileData && !loading) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      refreshProfile();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  return (
    <ProfileContext.Provider
      value={{
        profileData,
        loading,
        error,
        refreshProfile,
        updateProfile,
        deleteProfile,
      }}
    >
      {children}
    </ProfileContext.Provider>
  );
}

export function useProfile() {
  const context = useContext(ProfileContext);
  if (context === undefined) {
    throw new Error("useProfile must be used within a ProfileProvider");
  }
  return context;
}
