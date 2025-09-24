import React, { useEffect, useMemo, useState } from 'react';
import { fetchCounts, fetchEvents, openStream, type Event } from './api';
import StatCards from './components/StatCards';
import EventsTable from './components/EventsTable';
import TimelineChart from './components/TimelineChart';

export default function App(){
  const base = useMemo(() => '', []); // same origin; change if hosting separately
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [events, setEvents] = useState<Event[]>([]);

  useEffect(()=>{
    // Initial data
    fetchCounts(base).then((c) => setCounts(c.counts || {}));
    fetchEvents(base, 200).then((e) => setEvents(e));
    // Live stream
    const ws = openStream(base, (ev) => {
      setEvents((E) => [ev, ...E].slice(0, 200));
      // lightweight refresh of counts
      setCounts((C) => ({ ...C, [ev.proto]: (C[ev.proto]||0)+1 }));
    });
    return () => ws.close();
  }, [base]);

  return (
    <div className="container">
      <h1>Pi Sentinel Net</h1>
      <p>Local-only dashboard for LAN metadata (ARP/DHCP/DNS/mDNS). No payloads stored.</p>
      <StatCards counts={counts} />
      <TimelineChart events={events} />
      <EventsTable events={events} />
    </div>
  );
}
