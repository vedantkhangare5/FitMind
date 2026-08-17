"use client";

import { useState } from "react";
import { Activity, BookOpen, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { api, ApiError } from "@/lib/api";

interface Citation {
  document_id: string;
  title: string;
  source_name: string;
  source_url?: string;
  section?: string;
}

interface CoachingRecommendation {
  title: string;
  description: string;
  priority: string;
  evidence_ids: string[];
}

interface CoachResponse {
  summary: string;
  current_status: string;
  recommendations: CoachingRecommendation[];
  metrics: Record<string, unknown>;
  progress: Record<string, unknown>;
  citations: Citation[];
  generation_error: boolean;
  error_code?: string;
}

export function CoachingCard() {
  const [data, setData] = useState<CoachResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateCoaching = async () => {
    setLoading(true);
    setError(null);
    try {
      const json = await api.coach({});
      
      if (json.generation_error) {
        setError(`Coaching could not be generated. Error code: ${json.error_code}`);
      } else {
        setData(json);
      }
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unknown error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  const getCitationInfo = (docId: string, citations: Citation[]) => {
    const citation = citations.find((c) => c.document_id === docId);
    if (!citation) return docId;
    return `${citation.title} (${citation.source_name})`;
  };

  return (
    <div className="p-8 rounded-3xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm transition-all mt-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold flex items-center gap-2">
          <Activity className="w-6 h-6 text-emerald-600" />
          Your Fitness Focus
        </h2>
        <Button onClick={generateCoaching} disabled={loading} className="bg-zinc-900 dark:bg-white text-white dark:text-zinc-900">
          {loading ? "Generating..." : "Generate Coaching Summary"}
        </Button>
      </div>

      {error && (
        <div className="p-4 mb-6 rounded-xl bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 mt-0.5 shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {data && !error && (
        <div className="space-y-6">
          <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 text-emerald-900 dark:text-emerald-100">
            <h3 className="font-semibold mb-2">Summary</h3>
            <p className="text-sm leading-relaxed">{data.summary}</p>
          </div>

          <div className="p-4 rounded-xl border border-zinc-200 dark:border-zinc-800">
            <h3 className="font-semibold mb-2 text-zinc-700 dark:text-zinc-300">Current Status</h3>
            <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">{data.current_status}</p>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-4 text-zinc-800 dark:text-zinc-200">Action Plan</h3>
            <div className="grid gap-4">
              {data.recommendations.map((rec, idx) => (
                <div key={idx} className="p-5 rounded-2xl bg-zinc-50 dark:bg-zinc-800/50">
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                        rec.priority === "high"
                          ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                          : rec.priority === "medium"
                          ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                          : "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                      }`}
                    >
                      {rec.priority} priority
                    </span>
                    <h4 className="font-semibold text-zinc-900 dark:text-zinc-100">{rec.title}</h4>
                  </div>
                  <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-3">{rec.description}</p>
                  
                  {rec.evidence_ids && rec.evidence_ids.length > 0 && (
                    <div className="flex flex-col gap-1 mt-3 pt-3 border-t border-zinc-200 dark:border-zinc-700/50">
                      <p className="text-xs font-semibold text-zinc-500 flex items-center gap-1">
                        <BookOpen className="w-3 h-3" /> Evidence
                      </p>
                      {rec.evidence_ids.map((docId) => (
                        <p key={docId} className="text-xs text-zinc-500 truncate">
                          • {getCitationInfo(docId, data.citations)}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
