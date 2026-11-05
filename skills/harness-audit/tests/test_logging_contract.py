"""Project-owned contract checks for the copied lean-logging assets."""

import json
import logging
import signal
import sys
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import lean_log
import log_messages

VERSION = 1


class _JSONCollector(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.lines: list[dict[str, object]] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.lines.append(json.loads(self.format(record)))


class LoggingContract(unittest.TestCase):
    def test_default_and_trace_levels(self) -> None:
        self.assertEqual(lean_log.resolve_levels(env={}), (logging.INFO, logging.DEBUG))
        self.assertEqual(lean_log.resolve_levels(flags=("-vv",), env={}), (lean_log.TRACE, lean_log.TRACE))

    def test_asset_versions_and_local_imports(self) -> None:
        asset_dir = Path(__file__).resolve().parents[1] / "scripts"
        self.assertEqual(lean_log.VERSION, VERSION)
        self.assertEqual(log_messages.VERSION, VERSION)
        self.assertEqual(Path(lean_log.__file__).resolve(), asset_dir / "lean_log.py")
        self.assertEqual(Path(log_messages.__file__).resolve(), asset_dir / "log_messages.py")
        self.assertEqual(
            set(log_messages.MESSAGES),
            {"run.start", "run.end", "run.terminated", "run.error", "log.redacted", "progress"},
        )

    def test_unconfigured_buffer_is_bounded_and_reports_dropped_records(self) -> None:
        logger = logging.Logger("contract-buffer")
        for done in range(1005):
            lean_log.emit(logger, logging.INFO, "progress", phase="buffer", done=done, total=1005, elapsed=0.5)

        stream = StringIO()
        run = lean_log.configure(
            "contract",
            mode="service",
            env={},
            handle_signals=False,
            run_id="contract-buffer",
            logger=logger,
            console_stream=stream,
        )
        with run:
            pass

        records = [json.loads(line) for line in stream.getvalue().splitlines()]
        progress = [record for record in records if record["event"] == "progress"]
        self.assertEqual(len(progress), 1000)
        self.assertEqual([record["done"] for record in progress], list(range(5, 1005)))
        self.assertTrue(any(record["event"] == "logging.warning" and record["dropped"] == 5 for record in records))

    def test_files_catalog_events_and_redaction_on_custom_sink(self) -> None:
        secret = "CONTRACTSECRET123"
        with tempfile.TemporaryDirectory() as temp_dir:
            console = StringIO()
            custom = _JSONCollector()

            def custom_sink(ctx, catalog):
                custom.setFormatter(lean_log.JsonFormatter(ctx, catalog))
                return custom

            run = lean_log.configure(
                "contract",
                name="contract",
                env={"LOG_DIR": temp_dir},
                secrets=(secret,),
                clock=lambda: 1790961183.482,
                run_id="contract-run",
                host="contract-host",
                pid=4242,
                tz=UTC,
                handle_signals=False,
                logger=logging.Logger("contract"),
                console_stream=console,
                sinks=(custom_sink,),
            )
            with run:
                lean_log.emit(run.logger, logging.INFO, "progress", phase="contract", done=1, total=1, elapsed=0.5)
                lean_log.emit(run.logger, logging.ERROR, "run.error", kind="RuntimeError", message=f"failed {secret}")
                lean_log.emit(run.logger, logging.INFO, "login", header="Authorization: Basic dXNlcjpwYXNz")

            json_path = next(Path(temp_dir).glob("*.jsonl"))
            text_path = next(Path(temp_dir).glob("*.log"))
            records = [json.loads(line) for line in json_path.read_text(encoding="utf-8").splitlines()]
            events = {record["event"] for record in records}
            self.assertTrue({"run.start", "progress", "run.error", "log.redacted", "run.end"} <= events)
            self.assertTrue(all({"ts", "level", "run", "logger", "event", "msg"} <= record.keys() for record in records))
            self.assertEqual(run.catalog.fallback_events, set())
            self.assertGreaterEqual(records[-1]["masked"], 1)
            self.assertEqual(records[-1]["withheld"], 1)
            self.assertIn("[REDACTED]", json_path.read_text(encoding="utf-8"))
            self.assertNotIn(secret, json_path.read_text(encoding="utf-8"))
            self.assertNotIn(secret, text_path.read_text(encoding="utf-8"))
            self.assertNotIn(secret, console.getvalue())
            self.assertTrue(any(record["event"] == "run.error" and "[REDACTED]" in record["msg"] for record in custom.lines))
            self.assertTrue(any(record["event"] == "log.redacted" for record in custom.lines))

    def test_retention_keeps_newest_fifty_recent_runs(self) -> None:
        now = 1790961183.482
        now_utc = datetime.fromtimestamp(now, tz=UTC)
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            recent_stems = []
            for index in range(51):
                stamp = (now_utc - timedelta(days=2) + timedelta(seconds=index)).strftime("%Y-%m-%dT%H-%M-%S")
                stem = f"contract_contract_{stamp}"
                recent_stems.append(stem)
                (directory / f"{stem}.log").touch()
                (directory / f"{stem}.jsonl").touch()
            old_stamp = (now_utc - timedelta(days=31)).strftime("%Y-%m-%dT%H-%M-%S")
            old_stem = f"contract_contract_{old_stamp}"
            (directory / f"{old_stem}.log").touch()
            (directory / f"{old_stem}.jsonl").touch()

            run = lean_log.configure(
                "contract",
                name="contract",
                env={"LOG_DIR": temp_dir},
                clock=lambda: now,
                run_id="contract-retention",
                handle_signals=False,
                logger=logging.Logger("contract-retention"),
                console_stream=StringIO(),
            )
            with run:
                pass

            self.assertFalse((directory / f"{old_stem}.log").exists())
            self.assertFalse((directory / f"{recent_stems[0]}.log").exists())
            self.assertTrue(all((directory / f"{stem}.log").exists() for stem in recent_stems[1:]))
            self.assertEqual(len(list(directory.glob("*.jsonl"))), 51)

    def test_repeated_runs_do_not_duplicate_handlers(self) -> None:
        logger = logging.Logger("contract-idempotent")
        stream = StringIO()
        run_ids = ("contract-first", "contract-second")
        for run_id in run_ids:
            run = lean_log.configure(
                "contract",
                mode="service",
                env={},
                handle_signals=False,
                run_id=run_id,
                logger=logger,
                console_stream=stream,
            )
            with run:
                lean_log.emit(logger, logging.INFO, "progress", phase="contract", done=1, total=1, elapsed=0.5)
            self.assertEqual(logger.handlers, [])

        records = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual([record["event"] for record in records].count("run.start"), 2)
        self.assertEqual([record["event"] for record in records].count("progress"), 2)
        self.assertEqual({record["run"] for record in records}, set(run_ids))

    def test_termination_writes_closing_events(self) -> None:
        stream = StringIO()
        run = lean_log.configure(
            "contract",
            mode="service",
            env={},
            handle_signals=False,
            run_id="contract-termination",
            clock=lambda: 1790961183.482,
            logger=logging.Logger("contract-termination"),
            console_stream=stream,
        )
        with self.assertRaises(SystemExit) as caught:
            with run:
                raise lean_log.Terminated(signal.SIGTERM)
        records = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual(caught.exception.code, 143)
        self.assertEqual([record["event"] for record in records][-2:], ["run.terminated", "run.end"])
        self.assertEqual(records[-2]["signal"], "SIGTERM")
        self.assertEqual(records[-1]["exit_code"], 143)
        self.assertEqual(run.catalog.fallback_events, set())


if __name__ == "__main__":
    unittest.main(verbosity=2)
