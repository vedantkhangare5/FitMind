"use client";

import { useState } from "react";
import { Activity, BookOpen, AlertCircle, CheckCircle2, Zap } from "lucide-react";
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
  action_plan: string[];
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
    <div className="rounded-3xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-sm transition-all overflow-hidden">
      {/* Top Banner section */}
      <div className="p-8 border-b border-zinc-200 dark:border-zinc-800 bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-950/20 dark:to-teal-950/20">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-2 mb-2">
              <Zap className="w-6 h-6 text-emerald-600" />
              Intelligence Layer Coaching
            </h2>
            <p className="text-zinc-600 dark:text-zinc-400">
              Personalized insights and daily action plans powered by your latest metrics and behavior.
            </p>
          </div>
          <Button onClick={generateCoaching} disabled={loading} className="bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 shrink-0 shadow-md">
            {loading ? (
              <span className="flex items-center gap-2">
                <div className="animate-spin h-4 w-4 border-2 border-white dark:border-zinc-900 border-t-transparent rounded-full" />
                Generating...
              </span>
            ) : "Generate New Plan"}
          </Button>
        </div>
      </div>

      {error && (
        <div className="p-6">
          <div className="p-4 rounded-xl bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 mt-0.5 shrink-0" />
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {data && !error && (
        <div className="p-8">
          <div className="grid md:grid-cols-[1fr_300px] gap-8">
            {/* Left Column: Context & Recommendations */}
            <div className="space-y-6">
              <div className="p-5 rounded-2xl bg-zinc-50 dark:bg-zinc-800/50">
                <h3 className="font-semibold mb-2 flex items-center gap-2 text-zinc-800 dark:text-zinc-200">
                  <Activity className="w-4 h-4 text-emerald-600" />
                  Synthesis & Status
                </h3>
                <p className="text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed mb-4">
                  <span className="font-medium">Summary:</span> {data.summary}
                </p>
                <p className="text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed">
                  <span className="font-medium">Status:</span> {data.current_status}
                </p>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-4 text-zinc-800 dark:text-zinc-200">Strategic Recommendations</h3>
                <div className="grid gap-4">
                  {data.recommendations.map((rec, idx) => (
                    <div key={idx} className="p-5 rounded-2xl border border-zinc-200 dark:border-zinc-800">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-zinc-900 dark:text-zinc-100">{rec.title}</h4>
                        <span
                          className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                            rec.priority === "high"
                              ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                              : rec.priority === "medium"
                              ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                              : "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                          }`}
                        >
                          {rec.priority}
                        </span>
                      </div>
                      <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-3">{rec.description}</p>
                      
                      {rec.evidence_ids && rec.evidence_ids.length > 0 && (
                        <div className="flex flex-col gap-1 mt-3 pt-3 border-t border-zinc-100 dark:border-zinc-800">
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

            {/* Right Column: Today's Action Plan */}
            <div>
              <div className="bg-emerald-600 rounded-3xl p-6 text-white shadow-lg sticky top-6">
                <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5" />
                  Today&apos;s Action Plan
                </h3>
                <div className="space-y-4">
                  {data.action_plan.map((action, idx) => (
                    <div key={idx} className="flex gap-3 bg-white/10 p-4 rounded-2xl border border-white/20">
                      <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center shrink-0 font-bold text-sm">
                        {idx + 1}
                      </div>
                      <p className="text-sm font-medium leading-relaxed">{action}</p>
                    </div>
                  ))}
                </div>
                <div className="mt-6 pt-4 border-t border-white/20">
                  <p className="text-xs text-emerald-100 opacity-90 leading-tight">
                    Complete these 3 specific actions today to stay on track with your fitness goals.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {!data && !error && !loading && (
        <div className="p-12 text-center text-zinc-500 dark:text-zinc-400">
          <p>Click &quot;Generate New Plan&quot; to get your personalized daily strategy.</p>
        </div>
      )}
    </div>
  );
}
