# Logging Utilities

*Module: [`vibex.utils.logger`](https://github.com/dustland/vibex/blob/main/src/vibex/utils/logger.py)*

Simple streaming-aware logging for VibeX.

## set_streaming_mode <a href="https://github.com/dustland/vibex/blob/main/src/vibex/utils/logger.py#L23" class="source-link" title="View source code">source</a>

```python
def set_streaming_mode(enabled: bool)
```

Enable/disable streaming mode to control console output.

## get_logger <a href="https://github.com/dustland/vibex/blob/main/src/vibex/utils/logger.py#L29" class="source-link" title="View source code">source</a>

```python
def get_logger(name: str, level: Optional[str] = None) -> logging.Logger
```

Get a configured logger instance.

Simple rule:
- If streaming mode is active: VibeX loggers go to file only, others suppressed
- If streaming mode is off: All loggers go to both console and file

**Args:**
    name: Logger name (usually __name__)
    level: Optional log level override

**Returns:**
    Configured logger instance

## setup_task_file_logging <a href="https://github.com/dustland/vibex/blob/main/src/vibex/utils/logger.py#L73" class="source-link" title="View source code">source</a>

```python
def setup_task_file_logging(log_file_path: str) -> None
```

Set up file logging for a specific task with rotation.

**Args:**
    log_file_path: Path to the log file

## setup_clean_chat_logging <a href="https://github.com/dustland/vibex/blob/main/src/vibex/utils/logger.py#L123" class="source-link" title="View source code">source</a>

```python
def setup_clean_chat_logging()
```

Configure logging for clean chat experience.

## configure_logging <a href="https://github.com/dustland/vibex/blob/main/src/vibex/utils/logger.py#L135" class="source-link" title="View source code">source</a>

```python
def configure_logging(level: str = 'INFO', format_string: Optional[str] = None)
```

Configure global logging settings.

## set_log_level <a href="https://github.com/dustland/vibex/blob/main/src/vibex/utils/logger.py#L172" class="source-link" title="View source code">source</a>

```python
def set_log_level(level: str)
```

Set log level for the entire application.
