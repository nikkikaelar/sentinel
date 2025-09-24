import React, { useEffect, useRef } from 'react';
import { Chart } from 'chart.js/auto';
import type { Event } from '../api';

export default function TimelineChart({ events }:{ events: Event[] }){
  const ref = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<Chart | null>(null);
  useEffect(()=>{
    if(!ref.current) return;
    const ctx = ref.current.getContext('2d'); if(!ctx) return;
    // Simple per-minute bucket counts
    const buckets = new Map<string, number>();
    for (const e of events) {
      const d = new Date(e.ts);
      const key = `${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`;
      buckets.set(key, (buckets.get(key) || 0) + 1);
    }
    const labels = Array.from(buckets.keys());
    const data = Array.from(buckets.values());

    chartRef.current?.destroy();
    chartRef.current = new Chart(ctx, {
      type: 'line',
      data: { labels, datasets: [{ label: 'Events/min', data }] },
      options: { responsive: true, animation: false, scales: { y: { beginAtZero: true } } }
    });

    return () => chartRef.current?.destroy();
  }, [events]);

  return <div className="card" style={{marginTop:12}}><canvas ref={ref} height={120}></canvas></div>;
}
