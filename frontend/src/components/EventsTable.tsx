import React from 'react';
import type { Event } from '../api';

export default function EventsTable({ events }:{ events: Event[] }){
  return (
    <div className="card" style={{marginTop:12}}>
      <table className="table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Proto</th>
            <th>Src</th>
            <th>Dst</th>
            <th>MAC</th>
            <th>Extra</th>
          </tr>
        </thead>
        <tbody>
          {events.map((e, i) => (
            <tr key={i}>
              <td>{new Date(e.ts).toLocaleTimeString()}</td>
              <td><span className="badge">{e.proto}</span></td>
              <td>{e.src || '-'}</td>
              <td>{e.dst || '-'}</td>
              <td>{e.mac || '-'}</td>
              <td><code style={{fontSize:12}}>{JSON.stringify(e.extra || {})}</code></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
