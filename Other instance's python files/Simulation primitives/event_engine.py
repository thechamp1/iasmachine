"""
event_engine.py

Minimal discrete-event simulation engine for the IAS gate-by-gate emulator.

Project decision log (agreed before writing this):
  - Fidelity level: Boolean logic signals with documented propagation
    delays attached to each transition -- NOT literal analog voltages.
    Voltage figures in the primary sources (IAS Final Progress Report,
    Jan 1954; IAS report, Apr 1954) are used only to derive delay
    constants and logical thresholds; they are never simulated as
    continuous state here.
  - v1 scope: CPU + memory core only. Drum/IBM I/O control (T_STT,
    T_BLOCK, Sync chain) is deferred to a later phase.
  - Time unit throughout: microseconds (float), matching how every
    primary-source timing figure found so far is expressed.

This module has no knowledge of the IAS machine at all -- it is a
general small event-queue + signal-log substrate. Machine-specific
modules (sequencing_chain.py, etc.) build on top of it.
"""

import heapq
import itertools


class EventQueue:
    """A time-ordered queue of zero-argument callbacks."""

    def __init__(self):
        self._heap = []
        self._counter = itertools.count()  # stable tie-breaker
        self.now = 0.0

    def schedule(self, delay, callback, label=None):
        """Schedule `callback` to run `delay` microseconds from now.
        Returns the absolute time it was scheduled for."""
        if delay < 0:
            raise ValueError(f"negative delay: {delay!r}")
        t = self.now + delay
        seq = next(self._counter)
        heapq.heappush(self._heap, (t, seq, callback, label))
        return t

    def step(self):
        """Process exactly one event. Returns False if the queue is empty."""
        if not self._heap:
            return False
        t, seq, callback, label = heapq.heappop(self._heap)
        self.now = t
        callback()
        return True

    def run_until(self, end_time):
        """Process events up to and including end_time."""
        while self._heap and self._heap[0][0] <= end_time:
            self.step()

    def run_all(self, max_events=100_000):
        """Drain the queue completely. Only safe for finite scenarios --
        raises if something is scheduling events forever."""
        n = 0
        while self.step():
            n += 1
            if n >= max_events:
                raise RuntimeError(
                    "event queue did not drain after "
                    f"{max_events} events -- possible runaway feedback loop"
                )

    def is_idle(self):
        return not self._heap


class EventLog:
    """Structured, timestamped log of signal transitions.

    This is the seam a future GUI/visualizer is meant to consume: it is
    deliberately just data (a list of tuples), with no dependency in
    either direction between this class and any rendering code. The
    simulation core never needs to know a GUI exists; the GUI (whenever
    it's built) never needs to know how the simulation works internally.
    """

    def __init__(self):
        self.entries = []  # (time, signal_name, old_value, new_value, note)

    def record(self, time, signal_name, old_value, new_value, note=""):
        self.entries.append((time, signal_name, old_value, new_value, note))

    def __iter__(self):
        return iter(self.entries)

    def __len__(self):
        return len(self.entries)

    def pretty(self):
        lines = []
        for t, name, old, new, note in self.entries:
            suffix = f"   ({note})" if note else ""
            lines.append(
                f"t={t:8.2f}us  {name:20s} {old!s:>6} -> {new!s:<6}{suffix}"
            )
        return "\n".join(lines)


class Signal:
    """A single named logic signal (Boolean, or a small enum/None for
    multi-state lines like 'which gate is active').

    A Signal does not schedule its own delays: the delay for a given
    transition is a property of the *circuit path* driving it (the same
    toggle is cleared via different feedback paths with different lags
    in the real machine), so callers schedule transitions explicitly via
    the owning EventQueue and then call `set_now` when the event fires.
    """

    def __init__(self, name, initial, log: EventLog, engine: EventQueue):
        self.name = name
        self.value = initial
        self._log = log
        self._engine = engine
        self._watchers = []  # callables invoked (old, new) on committed change

    def watch(self, fn):
        self._watchers.append(fn)

    def set_now(self, new_value, note=""):
        """Commit a value change at the current simulated time. Used from
        inside a callback that the engine has already popped at the
        correct time -- not for scheduling future changes."""
        old = self.value
        if old == new_value:
            return
        self.value = new_value
        self._log.record(self._engine.now, self.name, old, new_value, note)
        for fn in self._watchers:
            fn(old, new_value)

    def __repr__(self):
        return f"<Signal {self.name}={self.value!r}>"
