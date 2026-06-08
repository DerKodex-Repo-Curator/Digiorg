export default function SafetyStatus({ safety }) {
  return (
    <div className="safety-container">
      <h2>System</h2>
      <div className={`safety-indicator ${safety.safe ? "safe" : "unsafe"}`}>
        {safety.safe ? "✅ System within limits" : "⚠️ Violations detected"}
      </div>
      {!safety.safe && (
        <ul className="violations-list">
          {safety.violations.map((v, i) => (
            <li key={i} className="violation-item">{v.detail}</li>
          ))}
        </ul>
      )}
    </div>
  );
}