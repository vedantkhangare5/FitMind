"use client";

import { useState, useRef, useEffect } from "react";
import { Message, ChatMessage } from "./ChatMessage";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Send } from "lucide-react";

export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I'm FitMind, your AI fitness assistant. How can I help you reach your goals today?",
    }
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const query = inputValue.trim();
    setInputValue("");
    
    // Add user message
    setMessages(prev => [...prev, { role: "user", content: query }]);
    setIsLoading(true);

    // Add temporary loading message
    setMessages(prev => [...prev, { role: "assistant", content: "", isLoading: true }]);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/agent/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      const data = await res.json();

      // Remove loading message
      setMessages(prev => prev.slice(0, -1));

      if (!res.ok) {
        throw new Error(data.detail || "Failed to get response");
      }

      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          citations: data.citations,
          tool_calls: data.tool_calls,
          isError: data.generation_error,
          errorCode: data.error_code,
          profileUsed: data.profile_used,
        }
      ]);
    } catch (err: unknown) {
      // Remove loading message
      setMessages(prev => {
        const withoutLoading = prev.slice(0, -1);
        const isNetwork = err instanceof TypeError && err.message.includes("Failed to fetch");
        return [
          ...withoutLoading,
          {
            role: "assistant",
            content: isNetwork ? "Unable to connect to the FitMind service. Please check your network connection." : (err instanceof Error ? err.message : "An unknown error occurred."),
            isError: true,
            errorCode: isNetwork ? "NETWORK_ERROR" : "API_ERROR",
          }
        ];
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 scroll-smooth">
        <div className="max-w-4xl mx-auto flex flex-col">
          {messages.map((msg, idx) => (
            <ChatMessage key={idx} message={msg} />
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white/80 dark:bg-zinc-950/80 backdrop-blur-md border-t border-zinc-200 dark:border-zinc-800">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative flex items-center">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask FitMind about fitness, nutrition, or calculations..."
            className="pr-12 py-6 rounded-2xl bg-zinc-100/50 dark:bg-zinc-900/50 border-zinc-200 dark:border-zinc-800 text-base"
            disabled={isLoading}
          />
          <Button
            type="submit"
            className="absolute right-2 h-10 w-10 p-0 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white"
            disabled={!inputValue.trim() || isLoading}
          >
            <Send className="w-5 h-5" />
          </Button>
        </form>
        <p className="text-center text-xs text-zinc-500 mt-3">
          FitMind uses AI and can make mistakes. For serious health decisions, consult a professional.
        </p>
      </div>
    </div>
  );
}
