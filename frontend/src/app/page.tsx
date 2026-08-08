"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [healthStatus, setHealthStatus] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function checkHealth() {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${apiUrl}/api/health`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setHealthStatus(data);
      } catch (e: unknown) {
        if (e instanceof Error) {
          setError(e.message);
        } else {
          setError("Failed to connect to backend");
        }
      } finally {
        setLoading(false);
      }
    }

    checkHealth();
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-8 bg-clip-text text-transparent bg-gradient-to-r from-emerald-500 to-teal-500">
          FitMind AI Foundation
        </h1>
        
        <div className="bg-white dark:bg-zinc-900 p-8 rounded-xl shadow-lg border border-zinc-200 dark:border-zinc-800 w-full max-w-md mx-auto">
          <h2 className="text-xl font-semibold mb-6 border-b border-zinc-200 dark:border-zinc-800 pb-2">
            Backend Connection Status
          </h2>
          
          {loading ? (
            <div className="flex items-center space-x-3 text-zinc-500">
              <div className="animate-spin h-5 w-5 border-2 border-emerald-500 border-t-transparent rounded-full"></div>
              <span>Connecting to FastAPI...</span>
            </div>
          ) : error ? (
            <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-4 rounded-lg border border-red-200 dark:border-red-800">
              <p className="font-bold mb-1">Connection Failed</p>
              <p className="text-sm">{error}</p>
              <p className="text-xs mt-3 pt-3 border-t border-red-200 dark:border-red-800 opacity-80">
                Is the backend running on localhost:8000?
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center space-x-2 text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/20 p-3 rounded-lg border border-emerald-200 dark:border-emerald-800/30">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                <span className="font-medium">Connected successfully!</span>
              </div>
              
              <div className="bg-zinc-100 dark:bg-zinc-800/50 p-4 rounded-lg font-mono text-xs overflow-auto">
                <pre>{JSON.stringify(healthStatus, null, 2)}</pre>
              </div>
            </div>
          )}

          <div className="mt-8 pt-6 border-t border-zinc-200 dark:border-zinc-800">
            <a 
              href="/calculator" 
              className="block w-full text-center bg-zinc-900 dark:bg-zinc-100 text-zinc-50 dark:text-zinc-900 font-medium py-2 rounded-lg hover:opacity-90 transition-opacity"
            >
              Test Fitness Engine &rarr;
            </a>
          </div>
        </div>
      </div>
    </main>
  );
}
