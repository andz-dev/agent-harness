"""Default sentence templates for the six mandatory lean-logging events."""

VERSION = 1

MESSAGES = {
    "run.start": "{command} {version} started, file level {file_level}, console level {console_level}, log files {log_files}",
    "run.end": "Run ended with exit code {exit_code}, masked {masked}, withheld {withheld}",
    "run.terminated": "Terminated by {signal}",
    "run.error": "Run failed ({kind}): {message}",
    "log.redacted": "Record withheld (pattern {pattern}, event {source_event})",
    "progress": "{phase}: {done} of {total} done, {elapsed} s",
}
