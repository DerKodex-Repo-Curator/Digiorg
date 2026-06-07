const EVENT_COLORS = {
  tick:               "#6b7280",
  feed:               "#4ade80",
  sleep:              "#818cf8",
  clean:              "#38bdf8",
  birth:              "#f59e0b",
  death:              "#ef4444",
  revive:             "#fbbf24",
  autonomous_action:  "#a78bfa",
  brain_thought:      "#67e8f9",
  safety_alert:       "#fb923c",
  directive_created:  "#86efac",
  directive_updated:  "#93c5fd",
};

export default function EventLog({ events }) {
  return (
    <div className="event-log">
      {events.map((e) => (
        <div key={e.id} className="event-item">
          <span className="event-type" style={{ color: EVENT_COLORS[e.event_type] || "#9ca3af" }}>
            {e.event_type}
          </span>
          <span className="event-desc">{e.description}</span>
          <span className="event-time">{new Date(e.created_at).toLocaleTimeString()}</span>
        </div>
      ))}
    </div>
  );
}