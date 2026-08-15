import { Activity, Search, XCircle } from "lucide-react";

export interface ToolCallRecord {
  tool_name: string;
  status: "success" | "error";
  result?: {
    success: boolean;
    data?: unknown;
    error?: unknown;
  } | null;
  duration_ms?: number | null;
}

interface ToolActivityProps {
  toolCalls: ToolCallRecord[];
}

export function ToolActivity({ toolCalls }: ToolActivityProps) {
  if (!toolCalls || toolCalls.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 mb-3">
      {toolCalls.map((call, idx) => {
        let label = "Tool execution";
        let Icon = Activity;
        let colorClass = "text-emerald-600 bg-emerald-50 border-emerald-200 dark:text-emerald-400 dark:bg-emerald-950/30 dark:border-emerald-900/50";

        if (call.tool_name === "search_knowledge") {
          label = "Knowledge search";
          Icon = Search;
        } else if (call.tool_name.startsWith("calculate_")) {
          label = "Fitness calculation";
          Icon = Activity;
        } else if (call.tool_name === "validate_calorie_target") {
          label = "Calorie safety check";
          Icon = Activity;
        }

        if (call.status === "error" || (call.result && !call.result.success)) {
          colorClass = "text-red-600 bg-red-50 border-red-200 dark:text-red-400 dark:bg-red-950/30 dark:border-red-900/50";
          Icon = XCircle;
        }

        return (
          <div
            key={idx}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${colorClass}`}
          >
            <Icon className="w-3.5 h-3.5" />
            <span>{(call.status === "success" && (!call.result || call.result.success !== false)) ? "✓" : "✗"} {label}</span>
          </div>
        );
      })}
    </div>
  );
}
