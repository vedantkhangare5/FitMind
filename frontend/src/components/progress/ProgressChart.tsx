"use client";

import { useMemo } from "react";

interface ProgressEntry {
  id: number;
  weight_kg: number;
  recorded_at: string;
}

interface ProgressChartProps {
  data: ProgressEntry[];
}

export function ProgressChart({ data }: ProgressChartProps) {
  const chartData = useMemo(() => {
    if (data.length === 0) return null;

    // Parse dates and sort chronologically just in case
    const parsedData = data.map((d) => ({
      ...d,
      timestamp: new Date(d.recorded_at).getTime(),
    })).sort((a, b) => a.timestamp - b.timestamp);

    const weights = parsedData.map((d) => d.weight_kg);
    const times = parsedData.map((d) => d.timestamp);

    const minWeight = Math.min(...weights);
    const maxWeight = Math.max(...weights);
    
    // Add 2kg padding top and bottom, or at least 1kg if flat
    const weightPadding = Math.max(2, (maxWeight - minWeight) * 0.2);
    const yMin = minWeight - weightPadding;
    const yMax = maxWeight + weightPadding;

    const minTime = Math.min(...times);
    const maxTime = Math.max(...times);
    
    // If only one data point or all data points are on the exact same millisecond
    const timeRange = maxTime === minTime ? 86400000 : maxTime - minTime; 
    
    const viewBoxWidth = 1000;
    const viewBoxHeight = 400;

    const getCoordinates = (timestamp: number, weight: number) => {
      // If minTime === maxTime, center the point at x = width / 2
      const x = maxTime === minTime 
        ? viewBoxWidth / 2 
        : ((timestamp - minTime) / timeRange) * viewBoxWidth;
        
      const y = viewBoxHeight - ((weight - yMin) / (yMax - yMin)) * viewBoxHeight;
      return { x, y };
    };

    const points = parsedData.map((d) => getCoordinates(d.timestamp, d.weight_kg));

    // Generate SVG path string
    const pathD = points.length > 1
      ? `M ${points.map((p) => `${p.x},${p.y}`).join(" L ")}`
      : "";

    return { points, pathD, viewBoxWidth, viewBoxHeight, minWeight, maxWeight };
  }, [data]);

  if (!chartData) {
    return (
      <div className="w-full h-64 bg-zinc-50 dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 flex items-center justify-center text-zinc-500">
        No progress data yet. Add an entry below to see your trend.
      </div>
    );
  }

  const { points, pathD, viewBoxWidth, viewBoxHeight } = chartData;

  return (
    <div className="w-full relative overflow-hidden rounded-2xl bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 shadow-sm p-4">
      {/* Aspect ratio container for SVG */}
      <div className="w-full" style={{ aspectRatio: '1000/400' }}>
        <svg
          viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
          className="w-full h-full overflow-visible"
          preserveAspectRatio="none"
          role="img"
          aria-label="Weight Progress Chart"
        >
          {/* Grid lines */}
          <line x1="0" y1={viewBoxHeight * 0.25} x2={viewBoxWidth} y2={viewBoxHeight * 0.25} stroke="currentColor" className="text-zinc-100 dark:text-zinc-800" strokeWidth="2" strokeDasharray="5,5" />
          <line x1="0" y1={viewBoxHeight * 0.5} x2={viewBoxWidth} y2={viewBoxHeight * 0.5} stroke="currentColor" className="text-zinc-100 dark:text-zinc-800" strokeWidth="2" strokeDasharray="5,5" />
          <line x1="0" y1={viewBoxHeight * 0.75} x2={viewBoxWidth} y2={viewBoxHeight * 0.75} stroke="currentColor" className="text-zinc-100 dark:text-zinc-800" strokeWidth="2" strokeDasharray="5,5" />
          
          {/* Line Path */}
          {points.length > 1 && (
            <path
              d={pathD}
              fill="none"
              stroke="url(#gradient)"
              strokeWidth="6"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="drop-shadow-md"
            />
          )}

          {/* Data Points */}
          {points.map((p, i) => (
            <circle
              key={i}
              cx={p.x}
              cy={p.y}
              r="6"
              fill="currentColor"
              className="text-violet-500"
              strokeWidth="3"
              stroke="white"
            />
          ))}

          {/* Definitions */}
          <defs>
            <linearGradient id="gradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#8b5cf6" />
              <stop offset="100%" stopColor="#6366f1" />
            </linearGradient>
          </defs>
        </svg>
      </div>
    </div>
  );
}
