"""
shift_counter.py

The Shift Counter and Recognition Circuit (chassis C-1467), which
tracks the number of steps in a multiplication, division, or shift
order and signals completion.

Modeled functionally rather than at the gate level -- consistent with
this project's standing choice (see event_engine.py's docstring) of
Boolean-logic-level behavior over literal circuit simulation. The
source describes a genuine six-stage binary "scaling" counter with a
separate True/False toggle row and a twelve-input Recognition Circuit
comparator (pp.126-136, Fig. 30), but none of that circuit-level detail
changes the counter's observable behavior, which is exactly what a
plain integer count-and-compare gives: count up by one per step, signal
done when the count reaches a target.

The target is fixed at 40 for multiplication/division (p.127: "the
Shift Counter is only required to count to 40" -- 39 steps plus
clean-up, matched against the specific counts each operation actually
uses) and arbitrary (1-47) for explicit shift orders (source, Fig. III
description: "an input III.12 which sets up the required count; this
may be implicit as in the case of the multiplication and division
orders or explicit as in the case of the shift orders").
"""


class ShiftCounter:
    def __init__(self, log, engine):
        self._log = log
        self._engine = engine
        self.count = 0
        self.target = 0

    def start(self, target, note=""):
        self.count = 0
        self.target = target
        self._log.record(self._engine.now, "ShiftCounter", None, 0,
                          f"start, target={target}" + (f" ({note})" if note else ""))

    def step(self):
        self.count += 1
        if self.done:
            self._log.record(self._engine.now, "ShiftCounter", self.count - 1,
                              self.count, "target reached")
        return self.done

    @property
    def done(self):
        return self.count >= self.target
