"""VIX futures term-structure analysis and strategy research tools."""

import warnings

import pandas as pd
try:
    from pandas.errors import ChainedAssignmentError, OptionError  # type: ignore[attr-defined]
except ImportError:  # pandas < 2.2
    ChainedAssignmentError = None
    from pandas.errors import OptionError

# Opt into pandas Copy-on-Write semantics, which is the default in pandas 3.0.
# Under CoW, `df[col] = value` is always a safe new-column assignment, but
# pandas 2.2+ still emits ChainedAssignmentError as a transition noise on some
# safe patterns (false positives that disappear in 3.0). Silence that one
# warning class so the package output stays clean during the 2.x → 3.0 window.
try:
    pd.options.mode.copy_on_write = True
except OptionError:
    pass
if ChainedAssignmentError is not None:
    warnings.filterwarnings("ignore", category=ChainedAssignmentError)

__all__ = []
