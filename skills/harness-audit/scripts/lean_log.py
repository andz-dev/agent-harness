# lean-logging asset: lean_log.py, version 1 (2026-10-03). Copy once into a project; the project owns the copy.
"""Readable, parseable logging on the standard library: one record, one sentence, every sink.

Python 3.14 or newer, standard library only. This module never raises into the caller from `emit`.
"""

from __future__ import annotations

import json
import logging
import os
import re
import signal
import string
import subprocess
import sys
import time
import traceback
from collections import deque
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta, tzinfo
from pathlib import Path
from secrets import token_hex
from threading import Lock

try:
    from .log_messages import MESSAGES as MANDATORY_MESSAGES
except ImportError:
    from log_messages import MESSAGES as MANDATORY_MESSAGES

if sys.version_info < (3, 14):
    raise RuntimeError("lean_log needs Python 3.14 or newer; run it with `uv run --python 3.14`")

VERSION = 1
TRACE = 5
LEVEL_NAMES = {
    TRACE: "TRACE",
    logging.DEBUG: "DEBUG",
    logging.INFO: "INFO",
    logging.WARNING: "WARNING",
    logging.ERROR: "ERROR",
    logging.CRITICAL: "CRITICAL",
}
FILE_LEVELS = {"info": logging.INFO, "debug": logging.DEBUG, "trace": TRACE}
RESERVED_KEYS = ("ts", "level", "run", "logger", "event", "msg")
LEVEL_WIDTH = 8
UNPRINTABLE = "<unprintable {}>"


def safe_str(value: object) -> str:
    try:
        return str(value)
    except Exception:
        return UNPRINTABLE.format(type(value).__name__)


# ---------------------------------------------------------------- levels


def _file_level_from_name(name: str) -> int:
    try:
        return FILE_LEVELS[name.strip().lower()]
    except KeyError:
        raise ValueError(f"unknown log level {name!r}; choose from {', '.join(FILE_LEVELS)}") from None


def resolve_levels(flags: Iterable[str] = (), env: Mapping[str, str] | None = None) -> tuple[int, int]:
    """Return (console_level, file_level).

    The file always records DEBUG; `-vv` deepens both to TRACE. `--log-level X` or `LOG_LEVEL` sets the file only,
    the flag winning over the environment. `-q` and `-v` are one signed counter on the console.
    """
    env = os.environ if env is None else env
    net, flag_level, args = 0, None, list(flags)
    for i, arg in enumerate(args):
        if arg.startswith("--log-level="):
            flag_level = arg.split("=", 1)[1]
        elif arg == "--log-level" and i + 1 < len(args):
            flag_level = args[i + 1]
        elif arg.startswith("-") and not arg.startswith("--") and len(arg) > 1 and set(arg[1:]) == {"v"}:
            net += len(arg) - 1
        elif arg.startswith("-") and not arg.startswith("--") and len(arg) > 1 and set(arg[1:]) == {"q"}:
            net -= len(arg) - 1
    console = {-2: logging.ERROR, -1: logging.WARNING, 0: logging.INFO, 1: logging.DEBUG}.get(max(net, -2) if net < 2 else 1, logging.INFO)
    if net >= 2:
        console = TRACE
    explicit = flag_level or env.get("LOG_LEVEL")
    file_level = _file_level_from_name(explicit) if explicit else (TRACE if net >= 2 else logging.DEBUG)
    return console, file_level


# ---------------------------------------------------------------- message catalog

_FORMATTER = string.Formatter()


def _text(value: object) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    if isinstance(value, (list, tuple)):
        return ", ".join(_text(v) for v in value) or "none"
    if isinstance(value, dict):
        return " ".join(f"{k}={_text(v)}" for k, v in value.items()) or "none"
    return safe_str(value)


def _one_line(text: str) -> str:
    return text.replace("\r", " ").replace("\n", "\\n")


class Catalog:
    """One `{field}` sentence template per event. Events that needed the fallback are collected for the contract test."""

    def __init__(self, templates: Mapping[str, str] | None = None) -> None:
        self.templates: dict[str, str] = {"logging.warning": "Logging warning: {message}"}
        self.templates.update(templates or {})
        self.fallback_events: set[str] = set()

    def render(self, event: str, fields: Mapping[str, object]) -> str:
        template = self.templates.get(event)
        used: set[str] = set()
        head = None
        if template is not None:
            try:
                names = {n for _, n, spec, conv in _FORMATTER.parse(template) if n is not None}
                if any(spec or conv for _, n, spec, conv in _FORMATTER.parse(template) if n is not None):
                    raise ValueError("format specs are not supported")
                used = names
                head = template.format_map({n: _text(fields[n]) if n in fields else "-" for n in names})
            except Exception:
                head = None
        if head is None:
            self.fallback_events.add(event)
            head, used = event, set()
        rest = ", ".join(f"{k}={_text(v)}" for k, v in fields.items() if k not in used and v is not None)
        return _one_line(f"{head} ({rest})" if rest else head)


# ---------------------------------------------------------------- context and records


@dataclass
class Context:
    """Run-wide values: identity, clock and bound fields. Injected in tests, filled by `configure()` later."""

    name: str = "app"
    run_id: str = ""
    host: str = ""
    pid: int = 0
    tz: tzinfo | None = None
    clock: Callable[[], float] = time.time
    bound: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class _EarlyRecord:
    level: int
    event: str
    fields: dict[str, object]
    timestamp: float


class EarlyBuffer:
    """Keep the newest 1000 records until configure() attaches the run's sinks."""

    limit = 1000

    def __init__(self) -> None:
        self._records: deque[_EarlyRecord] = deque()
        self._dropped = 0
        self._lock = Lock()

    def add(self, level: int, event: str, fields: Mapping[str, object], timestamp: float) -> None:
        with self._lock:
            if len(self._records) == self.limit:
                self._records.popleft()
                self._dropped += 1
            self._records.append(_EarlyRecord(level, event, dict(fields), timestamp))

    def drain(self) -> tuple[tuple[_EarlyRecord, ...], int]:
        with self._lock:
            records = tuple(self._records)
            dropped = self._dropped
            self._records.clear()
            self._dropped = 0
        return records, dropped


_context: Context | None = None
_early_buffer = EarlyBuffer()


def _set_context(ctx: Context | None) -> None:
    global _context
    _context = ctx


def bind(**fields: object) -> None:
    """Add constant fields to every later record of the run."""
    if _context is not None:
        _context.bound.update(fields)


def emit(logger: logging.Logger, level: int, event: str, /, **fields: object) -> None:
    """Write one record. The event is positional-only so a field may be called `event`; this call never raises."""
    try:
        if _context is None:
            _early_buffer.add(level, event, fields, time.time())
            return
        _write_record(logger, level, event, fields, _context.clock())
    except Exception:
        pass


def _write_record(logger: logging.Logger, level: int, event: str, fields: Mapping[str, object], timestamp: float) -> None:
    try:
        if logger.isEnabledFor(level):
            logger.log(level, event, extra={"lean_event": event, "lean_fields": dict(fields), "lean_ts": timestamp, "lean_msg": None})
    except Exception:
        pass


def _fields(record: logging.LogRecord) -> dict[str, object]:
    return getattr(record, "lean_fields", {})


def _event(record: logging.LogRecord) -> str:
    return getattr(record, "lean_event", record.getMessage())


def _timestamp(record: logging.LogRecord) -> float:
    return getattr(record, "lean_ts", record.created)


def sentence(record: logging.LogRecord, catalog: Catalog) -> str:
    """The sentence of a record, rendered once and cached so every sink shows the same text."""
    cached = getattr(record, "lean_msg", None)
    if cached is None:
        cached = catalog.render(_event(record), _fields(record))
        record.lean_msg = cached
    return cached


def level_name(levelno: int) -> str:
    return LEVEL_NAMES.get(levelno, f"LEVEL{levelno}")


class JsonFormatter(logging.Formatter):
    """JSON Lines: ts (UTC, Z, ms), level, run, bound fields, logger, event, msg, then the fields."""

    def __init__(self, ctx: Context, catalog: Catalog) -> None:
        super().__init__()
        self.ctx, self.catalog = ctx, catalog

    def format(self, record: logging.LogRecord) -> str:
        stamp = datetime.fromtimestamp(_timestamp(record), tz=UTC).isoformat(timespec="milliseconds")
        line: dict[str, object] = {"ts": stamp.replace("+00:00", "Z"), "level": level_name(record.levelno), "run": self.ctx.run_id}
        for key, value in self.ctx.bound.items():
            line[f"f_{key}" if key in RESERVED_KEYS else key] = value
        line["logger"], line["event"], line["msg"] = record.name, _event(record), sentence(record, self.catalog)
        for key, value in _fields(record).items():
            line[f"f_{key}" if key in RESERVED_KEYS else key] = value
        return json.dumps(line, ensure_ascii=False, default=safe_str)


class TextFormatter(logging.Formatter):
    """Journal style: `<local time +HH:MM> <host> <name>[<pid>]: LEVEL event: sentence`."""

    def __init__(self, ctx: Context, catalog: Catalog) -> None:
        super().__init__()
        self.ctx, self.catalog = ctx, catalog

    def format(self, record: logging.LogRecord) -> str:
        moment = datetime.fromtimestamp(_timestamp(record), tz=self.ctx.tz).astimezone(self.ctx.tz)
        stamp = moment.isoformat(timespec="seconds")
        return (
            f"{stamp} {self.ctx.host} {self.ctx.name}[{self.ctx.pid}]: "
            f"{level_name(record.levelno):<{LEVEL_WIDTH}} {_event(record)}: {sentence(record, self.catalog)}"
        )


class SDFormatter(logging.Formatter):
    """Compact syslog-priority stream format."""

    PRIORITIES = {TRACE: 7, logging.DEBUG: 7, logging.INFO: 6, logging.WARNING: 4, logging.ERROR: 3, logging.CRITICAL: 2}

    def __init__(self, catalog: Catalog) -> None:
        super().__init__()
        self.catalog = catalog

    def format(self, record: logging.LogRecord) -> str:
        priority = self.PRIORITIES.get(record.levelno, 7)
        return f"<{priority}>{_event(record)}: {sentence(record, self.catalog)}"


class StreamSink:
    """Create a redaction-ready stream handler for JSON Lines, text or syslog-priority output."""

    FORMATS = {"json", "text", "sd"}

    @classmethod
    def handler(cls, ctx: Context, catalog: Catalog, format_name: str, stream) -> logging.Handler:
        if format_name not in cls.FORMATS:
            raise ValueError(f"unknown LOG_FORMAT {format_name!r}; choose from json, text, sd")
        handler = logging.StreamHandler(stream)
        formatter = {"json": JsonFormatter(ctx, catalog), "text": TextFormatter(ctx, catalog), "sd": SDFormatter(catalog)}[format_name]
        handler.setFormatter(formatter)
        return handler


class _OwnedStreamHandler(logging.StreamHandler):
    """StreamHandler that owns the descriptor created for one log file."""

    def close(self) -> None:
        try:
            if self.stream is not None:
                self.stream.close()
        finally:
            super().close()


def _make_private_dirs(directory: Path) -> None:
    """Create `directory` and any missing parents with mode 0700; a folder that already exists keeps its mode."""
    missing = []
    for candidate in (directory, *directory.parents):
        if candidate.exists():
            break
        missing.append(candidate)
    for candidate in reversed(missing):
        try:
            candidate.mkdir(mode=0o700)
        except FileExistsError:
            continue
        candidate.chmod(0o700)  # mkdir's mode is cut by the umask on some systems


def default_log_dir(start: Path | str | None = None) -> Path:
    """`.data/logs` under the Git top level of `start` (default: the working directory), else under `start` itself.

    Always absolute, so a test or tool run from a subfolder never writes a second `.data/logs` there.
    """
    here = Path(start or Path.cwd()).resolve()
    try:
        done = subprocess.run(
            ["git", "-C", str(here), "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=10, check=False
        )
        top = Path(done.stdout.strip()) if done.returncode == 0 and done.stdout.strip() else here
        if not top.is_dir():  # anything but a real folder (a stubbed git, odd output) falls back
            top = here
    except (OSError, subprocess.SubprocessError):
        top = here
    return top / ".data" / "logs"


class RunFiles:
    """Create one exclusive text/JSONL pair and sweep this app-command's old runs."""

    FILE_PATTERN = re.compile(r"^(?P<stamp>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})(?:-(?P<suffix>\d+))?\.(?P<ext>log|jsonl)$")

    def __init__(self, directory: Path, name: str, command: str, now: float) -> None:
        self.directory = Path(directory)
        self.name = self._component(name)
        self.command = self._component(command)
        self.now = datetime.fromtimestamp(now, tz=UTC)
        self.prefix = f"{self.name}_{self.command}_"
        self.warnings: list[tuple[str, str]] = []

    @staticmethod
    def _component(value: str) -> str:
        component = re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-")
        return component or "app"

    def _matching_files(self) -> dict[tuple[datetime, int], list[Path]]:
        runs: dict[tuple[datetime, int], list[Path]] = {}
        try:
            entries = self.directory.iterdir()
            for path in entries:
                if not path.name.startswith(self.prefix) or not path.is_file():
                    continue
                match = self.FILE_PATTERN.fullmatch(path.name[len(self.prefix) :])
                if match is None:
                    continue
                try:
                    stamp = datetime.strptime(match.group("stamp"), "%Y-%m-%dT%H-%M-%S").replace(tzinfo=UTC)
                except ValueError:
                    continue
                key = (stamp, int(match.group("suffix") or 1))
                runs.setdefault(key, []).append(path)
        except OSError as exc:
            self.warnings.append((str(self.directory), str(exc)))
        return runs

    def _sweep(self) -> None:
        runs = self._matching_files()
        ordered = sorted(runs)
        newest = set(ordered[-50:])
        cutoff = self.now - timedelta(days=30)
        for key, paths in runs.items():
            if key[0] >= cutoff and key in newest:
                continue
            for path in paths:
                try:
                    path.unlink()
                except OSError as exc:
                    self.warnings.append((str(path), str(exc)))

    def sweep(self) -> None:
        """Apply retention to this app-command's matching run files."""
        self._sweep()

    @staticmethod
    def _close_created(created: list[tuple[Path, _OwnedStreamHandler]]) -> None:
        for path, handler in created:
            handler.close()
            try:
                path.unlink()
            except OSError:
                pass

    def open(self) -> tuple[tuple[Path, Path] | None, tuple[logging.Handler, ...]]:
        try:
            _make_private_dirs(self.directory)
        except OSError as exc:
            self.warnings.append((str(self.directory), str(exc)))
            return None, ()

        self.sweep()
        stamp = self.now.strftime("%Y-%m-%dT%H-%M-%S")
        suffix = 1
        while True:
            collision = "" if suffix == 1 else f"-{suffix}"
            stem = f"{self.prefix}{stamp}{collision}"
            paths = (self.directory / f"{stem}.log", self.directory / f"{stem}.jsonl")
            created: list[tuple[Path, _OwnedStreamHandler]] = []
            try:
                for path in paths:
                    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                    try:
                        os.fchmod(descriptor, 0o600)
                        stream = os.fdopen(descriptor, "a", encoding="utf-8")
                    except OSError:
                        try:
                            os.close(descriptor)
                        except OSError:
                            pass
                        try:
                            path.unlink()
                        except OSError:
                            pass
                        raise
                    created.append((path, _OwnedStreamHandler(stream)))
                return paths, tuple(handler for _, handler in created)
            except FileExistsError:
                self._close_created(created)
                suffix += 1
            except OSError as exc:
                self._close_created(created)
                self.warnings.append((str(paths[len(created)]), str(exc)))
                return None, ()


class _FiniteFileFilter(logging.Filter):
    def __init__(self, cutoff: float) -> None:
        super().__init__()
        self.cutoff = cutoff

    def filter(self, record: logging.LogRecord) -> bool:
        return _timestamp(record) < self.cutoff


class _FiniteConsoleFilter(logging.Filter):
    def __init__(self, handler: logging.StreamHandler, cutoff: float) -> None:
        super().__init__()
        self.handler, self.cutoff = handler, cutoff
        self.switched = False

    def filter(self, record: logging.LogRecord) -> bool:
        if not self.switched and _timestamp(record) >= self.cutoff:
            self.handler.setStream(sys.stdout)
            self.switched = True
        return True


# ---------------------------------------------------------------- redaction (option C)

MASK = "[REDACTED]"
MIN_SECRET_LENGTH = 8
DENY_FIELDS = frozenset({"password", "passwd", "token", "secret", "authorization", "api_key", "apikey", "cookie"})
# Boundaries are certain: the secret is cut out and the record stays.
MASK_PATTERNS = (
    (re.compile(r"(?i)\b(token|password|passwd|secret|api[_-]?key)=([^&\s)]+)"), r"\1=" + MASK),
    (re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+"), "Bearer " + MASK),
    (re.compile(r"(://[^/\s:@]+:)[^@\s/]+@"), r"\1" + MASK + "@"),
)
# Boundaries are unclear: the whole record is withheld.
WITHHOLD_PATTERNS = (("authorization", re.compile(r"(?i)authorization\s*:|\bbasic\s+[A-Za-z0-9+/=]{12,}")),)


class _Withhold(Exception):
    def __init__(self, pattern: str) -> None:
        super().__init__(pattern)
        self.pattern = pattern


def _normalize(name: str) -> str:
    return re.sub(r"[-\s]", "_", name.lower())


class Redactor(logging.Filter):
    """Keeps secrets out of every sink. Attach one instance to every handler, custom ones included.

    A deny-listed field value, a certain pattern and a known secret are masked and the record stays; an unclear
    match or any failure withholds the record. `filter` never raises. `masked` and `withheld` are run totals.
    """

    def __init__(self, deny_fields: Iterable[str] = (), patterns: Iterable[str] = (), secrets: Iterable[str] = ()) -> None:
        super().__init__()
        self.deny = DENY_FIELDS | {_normalize(n) for n in deny_fields}
        self.patterns = [(re.compile(p), MASK) for p in patterns]
        self.secrets = tuple(s for s in secrets if isinstance(s, str) and len(s) >= MIN_SECRET_LENGTH)
        self.masked = 0
        self.withheld = 0

    def _scrub(self, text: str) -> str:
        for cls, pattern in WITHHOLD_PATTERNS:
            if pattern.search(text):
                raise _Withhold(cls)
        for secret in self.secrets:
            found = text.count(secret)
            if found:
                self.masked += found
                text = text.replace(secret, MASK)
        for pattern, replacement in (*MASK_PATTERNS, *self.patterns):
            text, found = pattern.subn(replacement, text)
            self.masked += found
        return text

    def _clean(self, value: object) -> object:
        if isinstance(value, str):
            return self._scrub(value)
        if isinstance(value, dict):
            return {k: self._clean_item(k, v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [self._clean(v) for v in value]
        return value

    def _clean_item(self, key: object, value: object) -> object:
        if isinstance(key, str) and _normalize(key) in self.deny:
            if value != MASK:
                self.masked += 1
            return MASK
        return self._clean(value)

    def _withhold(self, record: logging.LogRecord, pattern: str) -> None:
        source = _event(record)
        record.lean_event = "log.redacted"
        record.lean_fields = {
            "pattern": pattern,
            "source_event": source if source.replace(".", "").replace("_", "").isalnum() else "unknown",
        }
        record.lean_msg = None
        record.msg = "log.redacted"
        self.withheld += 1

    def filter(self, record: logging.LogRecord) -> bool:
        if getattr(record, "lean_redacted", False):
            return True
        try:
            record.lean_fields = {k: self._clean_item(k, v) for k, v in _fields(record).items()}
        except _Withhold as caught:
            self._withhold(record, caught.pattern)
        except Exception:
            self._withhold(record, "error")
        record.lean_redacted = True
        return True


# ---------------------------------------------------------------- run lifecycle, signals, heartbeat


class Terminated(BaseException):
    """Raised by the signal handler; a BaseException so ordinary `except Exception` code does not swallow it."""

    def __init__(self, signum: int) -> None:
        super().__init__(signum)
        self.signum = signum


class SignalGuard:
    """Installs SIGTERM, SIGHUP and SIGINT handlers that raise `Terminated`, and restores the old ones."""

    SIGNALS = tuple(getattr(signal, n) for n in ("SIGTERM", "SIGHUP", "SIGINT") if hasattr(signal, n))

    def __init__(self) -> None:
        self._previous: dict[int, object] = {}

    @staticmethod
    def _handler(signum: int, _frame: object) -> None:
        raise Terminated(signum)

    def install(self) -> None:
        try:
            for signum in self.SIGNALS:
                self._previous[signum] = signal.signal(signum, self._handler)
        except ValueError:  # not the main thread: leave the signals alone
            self.restore()

    def restore(self) -> None:
        for signum, previous in self._previous.items():
            signal.signal(signum, previous)
        self._previous.clear()


class Heartbeat:
    """Progress records for a long phase: INFO at most once per `info_every` seconds, DEBUG every `debug_every` items."""

    def __init__(
        self,
        logger: logging.Logger,
        phase: str,
        total: int | None = None,
        *,
        debug_every: int = 50,
        info_every: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.logger, self.phase, self.total = logger, phase, total
        self.debug_every, self.info_every, self.clock = debug_every, info_every, clock
        self.started = self.last_info = clock()

    def tick(self, done: int) -> None:
        elapsed = round(self.clock() - self.started, 1)
        if self.debug_every and done % self.debug_every == 0:
            emit(self.logger, logging.DEBUG, "progress", phase=self.phase, done=done, total=self.total, elapsed=elapsed)
        if self.clock() - self.last_info >= self.info_every:
            self.last_info = self.clock()
            emit(self.logger, logging.INFO, "progress", phase=self.phase, done=done, total=self.total, elapsed=elapsed)


class ConsoleFormatter(logging.Formatter):
    """`HH:MM:SS LEVEL sentence` for people at a terminal."""

    def __init__(self, ctx: Context, catalog: Catalog) -> None:
        super().__init__()
        self.ctx, self.catalog = ctx, catalog

    def format(self, record: logging.LogRecord) -> str:
        moment = datetime.fromtimestamp(_timestamp(record), tz=self.ctx.tz).astimezone(self.ctx.tz)
        return f"{moment:%H:%M:%S} {level_name(record.levelno):<{LEVEL_WIDTH}} {sentence(record, self.catalog)}"


def end_level(exit_code: int, abnormal: bool = False) -> int:
    """run.end level: INFO for 0, WARNING for 1, ERROR for 2 or more, a signal or a crash."""
    if abnormal or exit_code >= 2:
        return logging.ERROR
    return logging.WARNING if exit_code == 1 else logging.INFO


class Run:
    """One process invocation: `run.start` at configure, `run.end` on every exit path, signals turned into records."""

    def __init__(
        self,
        ctx: Context,
        catalog: Catalog,
        redactor: Redactor,
        logger: logging.Logger,
        *,
        console_level: int,
        file_level: int,
        guard: SignalGuard | None,
        debug_every: int,
        info_every: float,
    ) -> None:
        self.ctx, self.catalog, self.redactor, self.logger = ctx, catalog, redactor, logger
        self.console_level, self.file_level = console_level, file_level
        self.guard, self.debug_every, self.info_every = guard, debug_every, info_every
        self.exit_code = 0
        self.handlers: list[logging.Handler] = []
        self._ended = False

    def add_handler(
        self, handler: logging.Handler, formatter: logging.Formatter | None = None, level: int | None = None
    ) -> logging.Handler:
        """Attach a handler (the module's own or a custom one) with the redaction filter on it."""
        if formatter is not None:
            handler.setFormatter(formatter)
        if level is not None:
            handler.setLevel(level)
        handler.addFilter(self.redactor)
        self.logger.addHandler(handler)
        self.handlers.append(handler)
        return handler

    def heartbeat(self, phase: str, total: int | None = None, *, clock: Callable[[], float] = time.monotonic) -> Heartbeat:
        return Heartbeat(self.logger, phase, total, debug_every=self.debug_every, info_every=self.info_every, clock=clock)

    def finish(self, exit_code: int | None = None, *, abnormal: bool = False) -> None:
        """Write `run.end` once, with the exit code and the redaction counts, and flush every handler."""
        if self._ended:
            return
        self._ended = True
        if exit_code is not None:
            self.exit_code = exit_code
        emit(
            self.logger,
            end_level(self.exit_code, abnormal),
            "run.end",
            exit_code=self.exit_code,
            masked=self.redactor.masked,
            withheld=self.redactor.withheld,
        )
        for handler in self.handlers:
            handler.flush()

    def close(self) -> None:
        if self.guard is not None:
            self.guard.restore()
        for handler in self.handlers:
            self.logger.removeHandler(handler)
            handler.close()
        self.handlers.clear()
        if _context is self.ctx:
            _set_context(None)

    def __enter__(self) -> Run:
        return self

    def __exit__(self, exc_type, exc, _tb) -> bool:
        try:
            if exc is None:
                self.finish()
            elif isinstance(exc, Terminated):
                emit(self.logger, logging.ERROR, "run.terminated", signal=signal.Signals(exc.signum).name)
                self.finish(128 + exc.signum, abnormal=True)
            elif isinstance(exc, SystemExit):
                code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
                self.finish(code)
            else:
                emit(self.logger, logging.ERROR, "run.error", kind=type(exc).__name__, message=safe_str(exc))
                emit(
                    self.logger,
                    logging.DEBUG,
                    "run.error",
                    kind=type(exc).__name__,
                    message=safe_str(exc),
                    traceback="".join(traceback.format_exception(exc)),
                )
                self.finish(1, abnormal=True)
        finally:
            self.close()
        if isinstance(exc, Terminated):
            raise SystemExit(128 + exc.signum)
        return False


def configure(
    command: str,
    *,
    mode: str = "finite",
    name: str | None = None,
    version: str = "",
    flags: Iterable[str] = (),
    env: Mapping[str, str] | None = None,
    messages: Mapping[str, str] | None = None,
    deny_fields: Iterable[str] = (),
    patterns: Iterable[str] = (),
    secrets: Iterable[str] = (),
    clock: Callable[[], float] | None = None,
    run_id: str | None = None,
    host: str | None = None,
    pid: int | None = None,
    tz: tzinfo | None = None,
    handle_signals: bool = True,
    logger: logging.Logger | None = None,
    console_stream=None,
    heartbeat_debug_every: int = 50,
    heartbeat_info_every: float = 60.0,
    log_files: Iterable[str] = (),
    sinks: Iterable[Callable[[Context, Catalog], logging.Handler]] = (),
) -> Run:
    """Open a run: levels, redaction, console, custom sinks, signals, then `run.start`. Use the result as a context manager.

    A sink is a factory `(context, catalog) -> handler`; the handler is created before `run.start`, so it sees every record,
    and it gets the redaction filter like the module's own handlers.
    """
    if mode not in {"finite", "service"}:
        raise ValueError("mode must be 'finite' or 'service'")
    environment = os.environ if env is None else env
    console_level, file_level = resolve_levels(flags, environment)
    if mode == "service":
        console_level = (
            _file_level_from_name(environment["LOG_LEVEL"]) if environment.get("LOG_LEVEL") else resolve_levels(flags, environment)[0]
        )
    stream_format = environment.get("LOG_FORMAT", "json" if mode == "service" else "text")
    if stream_format not in StreamSink.FORMATS:
        raise ValueError(f"unknown LOG_FORMAT {stream_format!r}; choose from json, text, sd")
    now = (clock or time.time)()
    program = name or Path(sys.argv[0]).stem or "app"
    ctx = Context(
        name=program,
        run_id=run_id or f"{datetime.fromtimestamp(now, tz=UTC):%Y%m%dT%H%M%SZ}-{token_hex(2)}",
        host=host if host is not None else os.uname().nodename,
        pid=pid if pid is not None else os.getpid(),
        tz=tz,
        clock=clock or time.time,
    )
    catalog_messages = dict(MANDATORY_MESSAGES)
    catalog_messages.update(messages or {})
    catalog = Catalog(catalog_messages)
    logger = logger or logging.getLogger(program)
    logger.setLevel(TRACE)
    logger.propagate = False
    guard = SignalGuard() if handle_signals else None
    run = Run(
        ctx,
        catalog,
        Redactor(deny_fields, patterns, secrets),
        logger,
        console_level=console_level,
        file_level=file_level,
        guard=guard,
        debug_every=heartbeat_debug_every,
        info_every=heartbeat_info_every,
    )
    _set_context(ctx)
    stream = console_stream if console_stream is not None else (sys.stdout if mode == "service" else sys.stderr)
    if mode == "service" or "LOG_FORMAT" in environment:
        console_handler = run.add_handler(StreamSink.handler(ctx, catalog, stream_format, stream), level=console_level)
    else:
        console_handler = run.add_handler(logging.StreamHandler(stream), ConsoleFormatter(ctx, catalog), console_level)

    log_dir = environment.get("LOG_DIR")
    if mode == "finite" or log_dir:
        files = RunFiles(Path(log_dir or "logs"), program, command, now)
        file_paths, file_handlers = files.open()
        if file_paths is not None:
            run.add_handler(file_handlers[0], TextFormatter(ctx, catalog), file_level)
            run.add_handler(file_handlers[1], JsonFormatter(ctx, catalog), file_level)
            if mode == "finite":
                cutoff = now + 24 * 60 * 60
                console_handler.addFilter(_FiniteConsoleFilter(console_handler, cutoff))
                for handler in file_handlers:
                    handler.addFilter(_FiniteFileFilter(cutoff))
    else:
        files = None
    for make_handler in sinks:
        run.add_handler(make_handler(ctx, catalog))
    if guard is not None:
        guard.install()
    active_log_files = [str(path) for path in (file_paths or ())] if mode == "finite" or log_dir else []
    active_log_files.extend(str(path) for path in log_files)
    emit(
        logger,
        logging.INFO,
        "run.start",
        command=command,
        version=version,
        file_level=level_name(file_level),
        console_level=level_name(console_level),
        log_files=active_log_files,
    )
    if files is not None:
        for path, reason in files.warnings:
            emit(logger, logging.WARNING, "logging.warning", message=f"unable to use {path}: {reason}", path=path, reason=reason)
    early_records, dropped = _early_buffer.drain()
    for record in early_records:
        _write_record(logger, record.level, record.event, record.fields, record.timestamp)
    if dropped:
        emit(
            logger,
            logging.WARNING,
            "logging.warning",
            message=f"Dropped {dropped} early log records because the 1000-record buffer was full",
            dropped=dropped,
        )
    return run


#: Fields every shared run opener masks; a caller adds its own through `deny_fields`.
RAW_CONTENT_FIELDS = ("content", "contents", "raw", "body")
#: A home-directory path is masked on every sink; a caller adds broader patterns through `patterns`.
PRIVATE_PATH = r"(?:/home|/Users)/[^\s'\"]+"


class _StartContext(logging.Filter):
    """Reduces the `run.start` log file paths to names and adds the Asset Root source when given."""

    def __init__(self, source: str | None) -> None:
        super().__init__()
        self.source = source

    def filter(self, record: logging.LogRecord) -> bool:
        if getattr(record, "lean_event", None) == "run.start":
            fields = dict(record.lean_fields)
            if self.source:
                fields["asset_root_source"] = self.source
            fields["log_files"] = [Path(str(path)).name for path in fields.get("log_files", ())]
            record.lean_fields = fields
        return True


def open_run(
    tool: str,
    log_dir: Path | None,
    catalog: Mapping[str, str],
    *,
    command: str = "run",
    flags: Iterable[str] = (),
    env: Mapping[str, str] | None = None,
    version: str = "",
    deny_fields: Iterable[str] = (),
    patterns: Iterable[str] = (),
    asset_root_source: str | None = None,
    **options: object,
) -> Run:
    """The one run opener of this repository: a finite run with redacted sinks, or console only without a directory.

    `tool` names the program (file names start with it), `catalog` extends the mandatory templates, and `log_dir`
    is where the readable and JSON Lines files go; `None` logs to the console on stderr and creates no files. The
    default directory and permissions are the caller's concern. Other keywords go to `configure`.
    """
    environment = dict(os.environ if env is None else env)
    if log_dir is None:
        environment.pop("LOG_DIR", None)
        environment.setdefault("LOG_FORMAT", "text")
        options.setdefault("console_stream", sys.stderr)
        mode = "service"
    else:
        environment.setdefault("LOG_DIR", str(log_dir))
        mode = "finite"
    logger = options.pop("logger", None) or logging.getLogger(tool)
    start = _StartContext(asset_root_source)
    logger.addFilter(start)
    try:
        return configure(
            command,
            mode=mode,
            name=tool,
            version=version,
            flags=tuple(flags),
            env=environment,
            messages=catalog,
            deny_fields=(*RAW_CONTENT_FIELDS, *deny_fields),
            patterns=(PRIVATE_PATH, *patterns),
            logger=logger,
            **options,
        )
    finally:
        logger.removeFilter(start)
