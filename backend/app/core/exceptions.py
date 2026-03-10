"""Application exceptions."""


class TerminalError(Exception):
    """Base exception for terminal backend."""


class SymbolNotFoundError(TerminalError):
    """Symbol does not exist or is not supported (e.g. not linear perpetual)."""


class ValidationError(TerminalError):
    """Request validation failed (e.g. invalid qty)."""


class ExchangeError(TerminalError):
    """Bybit API returned an error."""
