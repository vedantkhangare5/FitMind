import ReactMarkdown from "react-markdown";
import { Citation, CitationsList } from "./CitationsList";
import { ToolCallRecord, ToolActivity } from "./ToolActivity";
import { CalculationCard } from "./CalculationCard";
import { ProfileBadge } from "./ProfileBadge";
import { AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export interface Message {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  tool_calls?: ToolCallRecord[];
  isError?: boolean;
  errorCode?: string;
  isLoading?: boolean;
  profileUsed?: boolean;
}

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex w-full justify-end mb-6">
        <div className="max-w-[85%] rounded-2xl rounded-tr-sm bg-emerald-600 px-5 py-3.5 text-white shadow-sm">
          <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
        </div>
      </div>
    );
  }

  // Assistant message
  return (
    <div className="flex w-full justify-start mb-6">
      <div className={cn(
        "max-w-[90%] sm:max-w-[85%] rounded-2xl rounded-tl-sm px-5 py-4 shadow-sm border",
        message.isError 
          ? "bg-red-50 border-red-100 text-red-900 dark:bg-red-950/30 dark:border-red-900/50 dark:text-red-200" 
          : "bg-white border-zinc-200 text-zinc-900 dark:bg-zinc-900 dark:border-zinc-800 dark:text-zinc-100"
      )}>
        
        {/* Profile Badge */}
        {message.profileUsed && <ProfileBadge profileUsed={true} />}

        {/* Safe Tool Activity Badges */}
        {message.tool_calls && message.tool_calls.length > 0 && (
          <ToolActivity toolCalls={message.tool_calls} />
        )}

        {/* Loading State */}
        {message.isLoading ? (
          <div className="flex items-center gap-2 text-zinc-500 py-2">
            <div className="animate-spin h-4 w-4 border-2 border-emerald-500 border-t-transparent rounded-full"></div>
            <span className="text-sm font-medium">FitMind is working...</span>
          </div>
        ) : message.isError ? (
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-sm mb-1">
                {message.errorCode === "CITATION_VALIDATION_FAILED" && "Verification Failed"}
                {message.errorCode === "MODEL_RATE_LIMIT" && "System Busy"}
                {message.errorCode === "INSUFFICIENT_CONTEXT" && "Insufficient Information"}
                {!["CITATION_VALIDATION_FAILED", "MODEL_RATE_LIMIT", "INSUFFICIENT_CONTEXT"].includes(message.errorCode || "") && "Error"}
              </p>
              <p className="text-sm opacity-90 leading-relaxed">{message.content}</p>
            </div>
          </div>
        ) : (
          <div className="prose prose-sm dark:prose-invert prose-emerald max-w-none">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}

        {/* Structured Calculation Results */}
        {!message.isLoading && !message.isError && message.tool_calls && (
          <CalculationCard toolCalls={message.tool_calls} />
        )}

        {/* Citations List */}
        {!message.isLoading && !message.isError && message.citations && message.citations.length > 0 && (
          <CitationsList citations={message.citations} />
        )}
      </div>
    </div>
  );
}
