"""
Command Line Interface for Cytology Rose Agent.
"""
import argparse
import csv
import json
import sys
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from agents.base import AuditLogger, SecurityException

supervisor = SystemSupervisor(model_provider="mock")


def _first_nonempty(row, *names):
    for name in names:
        if row.get(name) not in (None, ""):
            return row[name]
    return None


def _csv_bool(value):
    if isinstance(value, bool):
        return value
    normalized = str(value or "false").strip().lower()
    if normalized in ("true", "1", "yes", "y", "on"):
        return True
    if normalized in ("false", "0", "no", "n", "off"):
        return False
    raise ValueError(f"Invalid boolean value: {value!r}")



def main(argv=None):
    parser = argparse.ArgumentParser(prog="cytology-rose-agent", description="Cytology Rose Agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Audit
    p_audit = subparsers.add_parser("audit", help="Run single task evaluation")
    p_audit.add_argument("--task-id", default="TASK-2026-001")
    p_audit.add_argument("--target", default="KEY-TARGET-01")
    p_audit.add_argument("--primary", type=float, default=28.5)
    p_audit.add_argument("--secondary", type=float, default=14.2)
    p_audit.add_argument("--critical", action="store_true")
    p_audit.add_argument("--status", default="DISCORDANT")

    # Chat
    p_chat = subparsers.add_parser("chat", help="System configuration query")
    p_chat.add_argument("query", nargs="+")

    # Batch
    p_batch = subparsers.add_parser("batch", help="Batch process CSV records")
    p_batch.add_argument("-i", "--input", required=True)
    p_batch.add_argument("-o", "--output", default="results.csv")

    # Verify Audit
    subparsers.add_parser("verify-audit", help="Verify HMAC audit trail integrity")

    # Serve
    p_serve = subparsers.add_parser("serve", help="Launch FastAPI REST server")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)

    if args.command == "audit":
        payload = SystemTaskPayload(
            task_id=args.task_id,
            target_identifier=args.target,
            primary_metric=args.primary,
            secondary_metric=args.secondary,
            status_descriptor=args.status,
            is_critical_flag=args.critical,
        )
        dossier = supervisor.process_task(payload)
        print("=" * 80)
        print(f"  CYTOLOGY ROSE AGENT")
        print(f"  Domain: Digital Pathology & Histology Systems | Standard: CAP Cancer Protocols / DICOM WSI PS3.16")
        print(f"  Dossier ID: {dossier.dossier_id} | Urgency: [{dossier.overall_urgency.value}]")
        print("=" * 80)
        for a in dossier.alerts:
            print(f"\n  [{a.urgency.value}] from {a.origin_worker}:")
            print(f"  Summary: {a.summary}")
            print(f"  Details: {a.technical_details}")
            print(f"  Action:  {a.actionable_remediation}")
        print(f"\n  HMAC-SHA256 Audit Hash: {dossier.audit_hash}")
        print("=" * 80)
        return 0

    if args.command == "chat":
        ans = supervisor.query_supervisory_chat(" ".join(args.query))
        print(f"\n[Cytology Rose Agent Supervisor]:\n{ans}\n")
        return 0

    if args.command == "verify-audit":
        trail = AuditLogger.get_trail()
        valid = AuditLogger.verify_integrity()
        print(f"Audit Trail Blocks: {len(trail)} | Cryptographic Integrity Verified: {valid}")
        return 0

    if args.command == "batch":
        try:
            with open(args.input, mode="r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                fieldnames = list(reader.fieldnames or [])
                if not fieldnames:
                    raise ValueError("CSV file has no header row")
                rows = list(reader)
        except (OSError, UnicodeError, csv.Error, ValueError) as exc:
            print(f"Unable to read CSV: {exc}", file=sys.stderr)
            return 1

        out_fields = list(dict.fromkeys(
            fieldnames + ["overall_urgency", "integrity_status", "total_alerts", "audit_hash"]
        ))
        out_rows = []
        for index, row in enumerate(rows, start=2):
            try:
                primary = _first_nonempty(row, "primary_metric", "metric_primary")
                secondary = _first_nonempty(row, "secondary_metric", "metric_secondary")
                if primary is None:
                    raise ValueError("primary_metric (or metric_primary) is required")
                payload = SystemTaskPayload(
                    task_id=_first_nonempty(row, "task_id", "case_id") or f"TASK-{index}",
                    target_identifier=_first_nonempty(
                        row, "target_identifier", "patient_synthetic_id"
                    ) or f"TARGET-{index}",
                    primary_metric=float(primary),
                    secondary_metric=float(secondary) if secondary is not None else 0.0,
                    status_descriptor=_first_nonempty(
                        row, "status_descriptor", "status_flag", "status_text"
                    ) or "NOMINAL",
                    is_critical_flag=_csv_bool(_first_nonempty(
                        row, "is_critical_flag", "is_stat", "critical_flag"
                    )),
                )
                dossier = supervisor.process_task(payload)
            except (ValueError, TypeError, SecurityException) as exc:
                print(f"CSV row {index}: {exc}", file=sys.stderr)
                return 1
            row_dict = dict(row)
            row_dict.update(
                overall_urgency=dossier.overall_urgency.value,
                integrity_status=dossier.integrity_status.value,
                total_alerts=dossier.total_alerts,
                audit_hash=dossier.audit_hash,
            )
            out_rows.append(row_dict)

        try:
            with open(args.output, mode="w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=out_fields)
                writer.writeheader()
                writer.writerows(out_rows)
        except OSError as exc:
            print(f"Unable to write CSV: {exc}", file=sys.stderr)
            return 1
        print(f"Processed {len(out_rows)} records -> {args.output}")
        return 0

    if args.command == "serve":
        import uvicorn
        from agents.api import app
        print(f"Starting Cytology Rose Agent API server on http://{args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
