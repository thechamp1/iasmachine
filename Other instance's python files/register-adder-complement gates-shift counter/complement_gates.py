"""
complement_gates.py

The Complement Gate Chassis (O-1458a in the chassis list), which sits
between RIII and the Adder -- per source, pp.16-17:

  "This chassis permits one of three modes of communication between
  RIII and the Adder. If a number x is stored in RIII, then either the
  Complement Gates permit x, the complement of x, or 0 to enter the
  Adder; or, to be more precise, if x = (x0, x1, ..., x39), then either
  x or x-bar = (1-x0, 1-x1, ..., 1-x39) or 0 = (0, 0, ..., 0) is
  permitted to enter the Adder from RIII. If it is the middle case,
  then the Arithmetic Control also 'injects' a digit 2^-39 into the
  Adder. This, as we shall see, correctly handles the operation of
  subtraction."

This directly explains what Adder40's carry_in parameter is for, and
resolves what used to be a mischaracterized gap in adder.py's docstring
(see that module's history): subtraction is exactly
`adder.add(resident, complement_gates.apply(y, COMPLEMENT)[0], carry_in=1)`
-- a one-time carry injection, not a feedback/wraparound circuit.

ABSOLUTE VALUE: the source (p.26) also describes addition/subtraction
of |RIII|, handled by "a monitor which decides whether the Complement
Gates are to pass the number in RIII or its complement according as the
instruction requires" -- apply_absolute_value() below implements that
decision from the sign digit (index 39, the highest-order position;
1 = negative, per the source's representation convention, pp.14-15).
"""

PASS = "pass"
COMPLEMENT = "complement"
ZERO = "zero"

SIGN_DIGIT_INDEX = 39


class ComplementGates:
    def apply(self, source_digits, mode):
        """Returns (digits_to_adder, carry_in)."""
        if len(source_digits) != 40:
            raise ValueError("expected 40 digits")
        if mode == PASS:
            return list(source_digits), 0
        elif mode == COMPLEMENT:
            return [1 - d for d in source_digits], 1
        elif mode == ZERO:
            return [0] * 40, 0
        else:
            raise ValueError(f"unknown Complement Gates mode: {mode!r}")

    def apply_absolute_value(self, source_digits, negate=False):
        """PASS-or-COMPLEMENT decided by the sign digit, so the Adder
        receives |source_digits| (negate=False) or -|source_digits|
        (negate=True, for the 'subtract the absolute value' variant)."""
        is_negative = source_digits[SIGN_DIGIT_INDEX] == 1
        if negate:
            mode = PASS if is_negative else COMPLEMENT
        else:
            mode = COMPLEMENT if is_negative else PASS
        return self.apply(source_digits, mode)
