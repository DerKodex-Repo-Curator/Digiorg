export default function StatBar({ label, value, color, warning, danger, invert = false }) {
  const isDanger = invert ? value >= danger : value <= danger;
  const isWarning = invert ? value >= warning : value <= warning;
  const barColor = isDanger ? "#ef4444" : isWarning ? "#f59e0b" : color;

  return (
    <div className="stat-bar">
      <div className="stat-header">
        <span className="stat-label">{label}</span>
        <span className="stat-value" style={{ color: barColor }}>{value}</span>
      </div>
      <div className="stat-track">
        <div className="stat-fill" style={{ width: `${value}%`, backgroundColor: barColor }} />
      </div>
    </div>
  );
}