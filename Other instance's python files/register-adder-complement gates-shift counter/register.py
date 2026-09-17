"""
register.py

RI is not one register but two: R^I ("upper") and R_I ("lower"), per
IAS Final Progress Report, Jan 1954, pp.20-27 and pp.60-69 (Figs. I.1-
I.6, 8, 11, 12). This replaces the earlier single flat 40-bit Register
class, which conflated the two.

WIDTH = 41, not 40: positions 0..39 hold the normal digits (index 0 =
2^-39, the LSB, matching the Adder's own convention; index 39 = 2^0,
the sign digit), and position 40 is the extra "2^+1" stage the source
gives an explicit reason for (chassis A-1446, "Extra RI stage for
shifts"; Fig. 10, "extra column... in which the digit held in the 0-th
can be held in the case of a left shift, instead of being lost"). BOTH
R^I and R_I get this extra position here -- see arithmetic_unit.py's
docstring for the round-trip derivation showing why R_I needs it too,
not only R^I.

GATE SEMANTICS -- source, pp.60-65, cross-confirmed by Figs. 8, 11, 12
and the chassis parts list (BCR/GrCR/RCR/YCR clear-driver chassis):

    Green:  Adder -> R^I,  same position,         transmits 0's, needs R^I precleared to 1 (Red Clear)
    Red:    R^I -> R_I,    shift toward MSB (+1),  transmits 0's, needs R_I precleared to 1 (Green Clear)
    Yellow: R_I -> R^I,    same position,         transmits 1's, needs R^I precleared to 0 (Black Clear)
    Black:  R^I -> R_I,    shift toward LSB (-1),  transmits 1's, needs R_I precleared to 0 (Yellow Clear)

"Transmits 0's" (Green/Red) means: the destination must already be all
1's; each destination bit whose mapped source digit is 0 gets cleared;
positions with no source mapped to them (the ends exposed by the +1/-1
shift) are simply left at 1. "Transmits 1's" (Yellow/Black) is the
mirror image against an all-0 destination.
"""

WIDTH = 41  # 0..39 = the normal 40 digits, 40 = the extra "2^+1" stage


class FlatRegister:
    """A plain 40-digit register with no shift/gate machinery of its
    own -- for RIII in its role as the Adder's other operand source.

    RIII is explicitly NOT a shifting register (source, p.63: "RIII, on
    the other hand, should not be thought of as a Shifting Register at
    all. The two rows of toggles in RIII actually form two independent
    Registers, which form part of the means of communication between
    the Williams Memory and the rest of the machine.") That two-row,
    Discriminator-facing structure is a Memory-interface concern we
    haven't built yet (Memory doesn't exist in this simulation), so
    this class only models the one thing currently needed: a 40-digit
    value that the Complement Gates can read from. `load()` is an
    idealized instantaneous set standing in for what would, on the real
    machine, arrive via the Yellow/Black gates from the Williams
    Memory Discriminator -- flagged here, not modeled as a timed
    transfer.
    """

    def __init__(self, name, log, engine, initial=None):
        self.name = name
        self._log = log
        self._engine = engine
        self.digits = list(initial) if initial is not None else [0] * 40
        if len(self.digits) != 40:
            raise ValueError(f"{name}: expected 40 digits")

    def load(self, digits, note="load (idealized -- stands in for Memory)"):
        if len(digits) != 40:
            raise ValueError(f"{self.name}: expected 40 digits")
        old_val = self.as_int()
        self.digits = list(digits)
        if self.as_int() != old_val:
            self._log.record(self._engine.now, self.name, old_val, self.as_int(), note)

    def as_int(self):
        return sum(d << i for i, d in enumerate(self.digits))

    def __repr__(self):
        return f"<FlatRegister {self.name}={self.as_int()}>"


class HalfRegister:
    def __init__(self, name, log, engine, initial=None):
        self.name = name
        self._log = log
        self._engine = engine
        self.digits = list(initial) if initial is not None else [0] * WIDTH
        if len(self.digits) != WIDTH:
            raise ValueError(f"{name}: expected {WIDTH} digits")

    def clear_to_1s(self, note="clear to 1's"):
        self._set_all([1] * WIDTH, note)

    def clear_to_0s(self, note="clear to 0's"):
        self._set_all([0] * WIDTH, note)

    def load(self, digits_40, note="load (idealized -- stands in for Memory)"):
        """Set the register directly to a 40-digit value (extra
        position 40 forced to 0), bypassing all gate preconditions.
        Real hardware never does this -- every real write goes through
        one of the four gates below -- so this exists purely as a
        test/setup convenience until Memory exists to load registers
        the way the real machine does."""
        if len(digits_40) != 40:
            raise ValueError(f"{self.name}: expected 40 digits")
        self._set_all(list(digits_40) + [0], note)

    def apply_green_gate(self, sum_digits, carry_out, note="Green Gate"):
        """Adder -> R^I. sum_digits: the 40 Adder outputs. carry_out:
        the Adder's carry out of stage 39, caught in the extra
        position 40 rather than corrupting/being lost against sum[39]."""
        if len(sum_digits) != 40:
            raise ValueError("expected 40 sum digits")
        source = list(sum_digits) + [1 if carry_out else 0]
        self._transmit_0s(source, shift=0, note=note)

    def apply_yellow_gate(self, source_register, note="Yellow Gate"):
        """R_I -> R^I, same position, transmits 1's."""
        self._transmit_1s(source_register.digits, shift=0, note=note)

    def apply_red_gate(self, source_register, note="Red Gate"):
        """R^I -> R_I, shifted toward the MSB by one position (Red =
        shift left). The source's own top position (40) has nowhere to
        go here and is dropped; the destination's position 0 has no
        source mapped to it and is left at the 1 the preceding Green
        Clear put there (harmless -- see arithmetic_unit.py)."""
        self._transmit_0s(source_register.digits, shift=1, note=note)

    def apply_black_gate(self, source_register, note="Black Gate"):
        """R^I -> R_I, shifted toward the LSB by one position (Black =
        shift right). The source's own position 0 has nowhere to go
        and is dropped; the destination's top position (40) has no
        source mapped to it and is left at the 0 the preceding Yellow
        Clear put there."""
        self._transmit_1s(source_register.digits, shift=-1, note=note)

    def _transmit_0s(self, source, shift, note):
        if any(d != 1 for d in self.digits):
            raise RuntimeError(
                f"{self.name}: this gate transmits 0's and requires the "
                f"register already cleared to 1's -- found {self.digits}"
            )
        new_digits = list(self.digits)
        for src_idx, val in enumerate(source):
            dst_idx = src_idx + shift
            if 0 <= dst_idx < WIDTH and val == 0:
                new_digits[dst_idx] = 0
        self._set_all(new_digits, note)

    def _transmit_1s(self, source, shift, note):
        if any(d != 0 for d in self.digits):
            raise RuntimeError(
                f"{self.name}: this gate transmits 1's and requires the "
                f"register already cleared to 0's -- found {self.digits}"
            )
        new_digits = list(self.digits)
        for src_idx, val in enumerate(source):
            dst_idx = src_idx + shift
            if 0 <= dst_idx < WIDTH and val == 1:
                new_digits[dst_idx] = 1
        self._set_all(new_digits, note)

    def _set_all(self, new_digits, note):
        old_val = self.as_int()
        changed = new_digits != self.digits
        self.digits = list(new_digits)
        if changed:
            self._log.record(self._engine.now, self.name, old_val, self.as_int(), note)

    def as_int(self):
        # Only positions 0..39 count as the register's numeric value;
        # position 40 is a transient staging bit, not part of the number.
        return sum(d << i for i, d in enumerate(self.digits[:40]))

    def __repr__(self):
        return f"<HalfRegister {self.name}={self.as_int()}>"
