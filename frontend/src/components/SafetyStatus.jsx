export default function SafetyStatus({ safety }) {
  return (
    <div className="safety-container">
      <h2>Sistema</h2>
      <div className={`safety-indicator ${safety.safe ? "safe" : "unsafe"}`}>
        {safety.safe ? "✅ Sistema dentro de límites" : "⚠️ Violaciones detectadas"}
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