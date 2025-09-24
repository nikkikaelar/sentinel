import React from 'react';

export default function StatCards({ counts }:{ counts: Record<string, number> }){
  const keys = Object.keys(counts).sort();
  return (
    <div style={{display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:12}}>
      {keys.map(k => (
        <div className="card" key={k}>
          <div style={{fontSize:12, color:'#6b7280'}}>{k}</div>
          <div style={{fontSize:24, fontWeight:700}}>{counts[k]}</div>
        </div>
      ))}
    </div>
  );
}
