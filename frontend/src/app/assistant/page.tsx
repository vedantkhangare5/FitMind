"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { ChatContainer } from "@/components/assistant/ChatContainer";

export default function AssistantPage() {
  return (
    <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50 flex flex-col">
      {/* Header */}
      <header className="h-16 border-b border-zinc-200 dark:border-zinc-800 bg-white/50 dark:bg-zinc-950/50 backdrop-blur-md flex items-center px-4 sm:px-6 flex-shrink-0 z-10">
        <Link href="/" className="flex items-center gap-2 text-zinc-600 hover:text-emerald-600 transition-colors">
          <ArrowLeft className="w-5 h-5" />
          <span className="font-medium text-sm">Back to Dashboard</span>
        </Link>
        
        <div className="mx-auto flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center text-white font-bold tracking-tighter shadow-sm">
            FM
          </div>
          <h1 className="font-semibold tracking-tight">FitMind Assistant</h1>
        </div>
        
        <div className="w-[140px]"></div> {/* Spacer for centering */}
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-hidden relative">
        <ChatContainer />
      </div>
    </main>
  );
}
