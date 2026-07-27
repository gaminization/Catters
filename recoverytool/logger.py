"""Phase-aware structured logging system for the audit pipeline."""
import logging
from pathlib import Path


class PhaseLogger:
    """Manages per-phase loggers with separate info and error log files."""

    def __init__(self, logs_dir: Path | str):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.loggers: dict[str, logging.Logger] = {}

    def get_phase_logger(self, phase_name: str) -> logging.Logger:
        if phase_name in self.loggers:
            return self.loggers[phase_name]

        logger = logging.getLogger(f"recoverytool.{phase_name}")
        logger.setLevel(logging.INFO)
        logger.propagate = False

        # Formatter
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

        # Info file handler
        info_file = self.logs_dir / f"{phase_name}.log"
        fh_info = logging.FileHandler(info_file, encoding="utf-8")
        fh_info.setLevel(logging.INFO)
        fh_info.setFormatter(formatter)
        logger.addHandler(fh_info)

        # Error file handler
        error_file = self.logs_dir / f"{phase_name}_errors.log"
        fh_err = logging.FileHandler(error_file, encoding="utf-8")
        fh_err.setLevel(logging.ERROR)
        fh_err.setFormatter(formatter)
        logger.addHandler(fh_err)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        self.loggers[phase_name] = logger
        return logger
