// api.ts — tiny client for REST + WebSocket
export type Event = { ts:number; proto:string; src?:string|null; dst?:string|null; mac?:string|null; extra?:any };

export async function fetchCounts(base = ''){
  const res = await fetch(`${base}/api/counts`);
  return res.json();
}
export async function fetchEvents(base = '', limit = 200){
  const res = await fetch(`${base}/api/events?limit=${limit}`);
  return res.json();
}
export function openStream(base = '', onEvent:(e:Event)=>void){
  const wsUrl = (base.startsWith('http') ? base.replace(/^http/, 'ws') : '') + '/ws';
  const ws = new WebSocket(wsUrl);
  ws.onmessage = (ev) => {
    try { const e = JSON.parse(String(ev.data)); onEvent(e); } catch {}
  };
  return ws;
}
