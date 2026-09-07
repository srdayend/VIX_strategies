"""VIX futures term-structure analysis and strategy research tools."""

import warnings

import pandas as pd
from pandas.errors import ChainedAssignmentError  # type: ignore[attr-defined]

# Opt into pandas Copy-on-Write semantics, which is the default in pandas 3.0.
# Under CoW, `df[col] = value` is always a safe new-column assignment, but
# pandas 2.2+ still emits ChainedAssignmentError as a transition noise on some
# safe patterns (false positives that disappear in 3.0). Silence that one
# warning class so the package output stays clean during the 2.x → 3.0 window.
pd.options.mode.copy_on_write = True
warnings.filterwarnings("ignore", category=ChainedAssignmentError)

__all__ = []
