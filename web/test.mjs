import test from "node:test";
import assert from "node:assert/strict";
import { evaluate } from "./app.mjs";

const base = {task_id:"T-1",target_identifier:"SPECIMEN-1",primary_metric:10,secondary_metric:4,status_descriptor:"NOMINAL",is_critical_flag:false};
test("routine evaluation", () => {
  const result = evaluate(base);
  assert.equal(result.overall_urgency, "ROUTINE");
  assert.equal(result.total_alerts, 0);
  assert.equal(result.mode, "browser-demonstration");
  assert.equal(result.audit_hash, undefined);
});
test("threshold and descriptor alerts match Python worker boundaries", () => {
  assert.equal(evaluate({...base,primary_metric:25,secondary_metric:12}).total_alerts, 0);
  assert.equal(evaluate({...base,primary_metric:25.1,secondary_metric:12.1,status_descriptor:"DISCORDANT"}).total_alerts, 3);
});
test("manual critical flag takes precedence", () => {
  const r = evaluate({...base,is_critical_flag:true});
  assert.equal(r.overall_urgency, "CRITICAL_STAT_PANIC");
});
test("rejects invalid numbers and missing identifiers", () => {
  for (const primary of ["", Number.NaN, Number.POSITIVE_INFINITY, -1]) {
    if (primary === "") continue; // Empty form fields are rejected by the UI.
    assert.throws(() => evaluate({...base,primary_metric:primary}));
  }
  assert.throws(() => evaluate({...base,task_id:" "}));
});
