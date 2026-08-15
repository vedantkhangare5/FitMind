import { ToolCallRecord } from "./ToolActivity";
import { AlertCircle } from "lucide-react";

interface CalculationCardProps {
  toolCalls: ToolCallRecord[];
}

export function CalculationCard({ toolCalls }: CalculationCardProps) {
  if (!toolCalls || toolCalls.length === 0) return null;

  // Extract results from successful calculation tools
  let bmr: number | undefined;
  let tdee: number | undefined;
  let proteinMin: number | undefined;
  let proteinMax: number | undefined;
  let warnings: string[] = [];

  for (const call of toolCalls) {
    if (call.status === "success" && call.result?.success && call.result.data) {
      const data = call.result.data as Record<string, unknown>;
      if (typeof data.bmr === "number") bmr = data.bmr;
      if (typeof data.tdee === "number") tdee = data.tdee;
      if (typeof data.protein_target_min === "number") proteinMin = data.protein_target_min;
      if (typeof data.protein_target_max === "number") proteinMax = data.protein_target_max;
      
      if (Array.isArray(data.warnings) && data.warnings.length > 0) {
        warnings = [...warnings, ...(data.warnings as string[])];
      }
    }
  }

  // If no calculations were actually performed or returned data, render nothing
  if (bmr === undefined && tdee === undefined && proteinMin === undefined && warnings.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 mb-2 space-y-4">
      {warnings.length > 0 && (
        <div className="p-3 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/50 rounded-lg">
          <h4 className="font-bold text-amber-800 dark:text-amber-400 flex items-center gap-1.5 text-sm">
            <AlertCircle className="w-4 h-4" />
            Safety Notice
          </h4>
          <ul className="list-disc ml-6 mt-1.5 text-sm text-amber-700 dark:text-amber-300 space-y-1">
            {warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      {(bmr !== undefined || tdee !== undefined || proteinMin !== undefined) && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {bmr !== undefined && (
            <div className="p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-100 dark:border-zinc-800">
              <p className="text-xs text-zinc-500 uppercase tracking-wider mb-1">BMR</p>
              <p className="text-xl font-bold">{bmr} <span className="text-xs font-normal text-zinc-500">kcal</span></p>
            </div>
          )}
          {tdee !== undefined && (
            <div className="p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-100 dark:border-zinc-800">
              <p className="text-xs text-zinc-500 uppercase tracking-wider mb-1">TDEE</p>
              <p className="text-xl font-bold">{tdee} <span className="text-xs font-normal text-zinc-500">kcal</span></p>
            </div>
          )}
          {proteinMin !== undefined && proteinMax !== undefined && (
            <div className="col-span-2 p-3 bg-blue-50 dark:bg-blue-900/10 rounded-lg border border-blue-100 dark:border-blue-800/20">
              <p className="text-xs text-blue-600 dark:text-blue-500 uppercase tracking-wider mb-1">Protein Target</p>
              <p className="text-xl font-bold text-blue-700 dark:text-blue-400">
                {proteinMin} - {proteinMax} <span className="text-xs font-normal text-blue-600 dark:text-blue-500">g/day</span>
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
