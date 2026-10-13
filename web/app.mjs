/**
 * Client-side demonstration of the deterministic threshold logic in agents/workers.py.
 * This is not a diagnostic, adequacy, or clinical decision-support engine.
 */
export function evaluate(payload) {
  const id = String(payload.task_id ?? "").trim();
  const target = String(payload.target_identifier ?? "").trim();
  const descriptor = String(payload.status_descriptor ?? "").trim();
  const primary = Number(payload.primary_metric);
  const secondary = Number(payload.secondary_metric);
  if (!id || !target) throw new Error("Task ID and target identifier are required.");
  if (id.length > 120 || target.length > 120 || descriptor.length > 200) {
    throw new Error("Text input exceeds the supported length.");
  }
  if (![primary, secondary].every(Number.isFinite) || primary < 0 || secondary < 0) {
    throw new Error("Measurements must be finite, non-negative numbers.");
  }

  const alerts = [];
  if (primary > 25) {
    alerts.push({
      worker: "InvariantQCWorker",
      urgency: "ELEVATED_RISK",
      summary: "Primary Metric Threshold Exceeded",
      details: `Primary measurement (${primary.toFixed(2)}) exceeds the prototype threshold (25.00).`
    });
  }
  if (payload.is_critical_flag || secondary > 12) {
    alerts.push({
      worker: "SafetyEscalationWorker",
      urgency: payload.is_critical_flag ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
      summary: "Threshold or manual priority flag",
      details: `Critical flag: ${Boolean(payload.is_critical_flag)}; secondary metric: ${secondary.toFixed(2)} (prototype threshold 12.00).`
    });
  }
  if (["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"].some(word => descriptor.toUpperCase().includes(word))) {
    alerts.push({
      worker: "ProtocolConformanceWorker",
      urgency: "ELEVATED_RISK",
      summary: "Descriptor flagged for review",
      details: "A review keyword is present in the supplied status descriptor."
    });
  }
  const critical = alerts.some(a => a.urgency === "CRITICAL_STAT_PANIC");
  const elevated = alerts.length > 0;
  return {
    mode: "browser-demonstration",
    disclaimer: "Experimental thresholds only. Not clinically validated. No HMAC audit signature is generated.",
    task_id: id,
    target_identifier: target,
    primary_metric: primary,
    secondary_metric: secondary,
    status_descriptor: descriptor,
    overall_urgency: critical ? "CRITICAL_STAT_PANIC" : elevated ? "ELEVATED_RISK" : "ROUTINE",
    integrity_status: critical ? "RECALIBRATION_REQUIRED" : elevated ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL",
    total_alerts: alerts.length,
    alerts
  };
}

if (typeof document !== "undefined") {
  const form = document.querySelector("#audit-form");
  const consoleEl = document.querySelector("#output");
  const status = document.querySelector("#system-status");
  const tasks = document.querySelector("#tasks-count");
  const alertCount = document.querySelector("#alerts-count");
  const exportButton = document.querySelector("#export-report");
  const clearButton = document.querySelector("#clear-report");
  let lastResult = null;
  let processed = 0;
  let cumulativeAlerts = 0;

  form.addEventListener("submit", event => {
    event.preventDefault();
    try {
      const primaryText = form.elements.primary_metric.value.trim();
      const secondaryText = form.elements.secondary_metric.value.trim();
      if (!primaryText || !secondaryText) throw new Error("Both measurements are required.");
      const result = evaluate({
        task_id: form.elements.task_id.value,
        target_identifier: form.elements.target_identifier.value,
        primary_metric: primaryText,
        secondary_metric: secondaryText,
        status_descriptor: form.elements.status_descriptor.value,
        is_critical_flag: form.elements.is_critical_flag.checked
      });
      lastResult = result;
      processed += 1;
      cumulativeAlerts += result.total_alerts;
      tasks.textContent = String(processed);
      alertCount.textContent = String(cumulativeAlerts);
      status.textContent = result.overall_urgency;
      consoleEl.textContent = JSON.stringify(result, null, 2);
      exportButton.disabled = false;
    } catch (error) {
      status.textContent = "INPUT ERROR";
      consoleEl.textContent = error instanceof Error ? error.message : "Unexpected input error.";
    }
  });

  clearButton.addEventListener("click", () => {
    lastResult = null;
    consoleEl.textContent = "No evaluation in this session.";
    status.textContent = "READY";
    exportButton.disabled = true;
  });

  exportButton.addEventListener("click", () => {
    if (!lastResult) return;
    const blob = new Blob([JSON.stringify(lastResult, null, 2) + "\n"], {type:"application/json"});
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "rose-evaluation.json";
    anchor.click();
    URL.revokeObjectURL(url);
  });
}
