"""
adder.py

The Adder: forty stages of full-adder logic, per IAS Final Progress
Report, Jan 1954, pp. 74-79 ("Consider the first two columns... n and
n+1... reference should be made to the schematic, DWG No. 1334").

Digit ordering matches the source explicitly: index 0 is the lowest
order digit (2^-39 -- "the left column of the extreme left chassis...
operates upon the lowest order digits... and the order increases as we
go to the right"). Ripple carry propagates from index 0 toward index 39.

Modeled at the Boolean-logic level (project decision): the source's own
table gives Sum/Carry as a function of (Resident digit, Incident digit,
Carry-in) directly (p. 76); it also maps each of the four (Sum, Carry)
outcomes to a measured Adder output voltage (Vs = 215/161/108/53 volts,
p. 79), but that voltage mapping is the source's way of presenting the
same four outcomes for an analog reader, not a separate thing to
simulate -- TRUTH_TABLE below is transcribed from the digit-level table,
not the voltage table.

CORRECTION (this docstring previously mischaracterized subtraction --
flagging the fix rather than silently editing it away): the machine's
number representation is two's-complement-style (x-bar = x + 2 for
negative x, pp.15-17), not one's complement, and subtraction needs no
feedback/wraparound circuit at all. The source is explicit: to form
x - y, the Complement Gates pass (1 - y_i) for each digit of y, and
"the Arithmetic Control also 'injects' a digit 2^-39 into the Adder" --
i.e. it sets carry_in=1 at stage 0, nothing more. This module's
carry_in parameter already supports that directly: subtraction is just
`add(x_digits, complement_of_y_digits, carry_in=1)`. Chassis A-1454
("RI, RII End-Around Circuits"), which the previous version of this
docstring wrongly associated with subtraction, is actually unrelated --
it carries a bit shifted off one end of RI into RII (and vice versa)
for double-length shifts during multiplication/division, per Figs.
10/11 and pp.65-69. Nothing here needed a code change; the interface
already happened to be right.

NOT modeled yet (flagged, not silently dropped):
  - The Complement Gates chassis itself (selecting x, complement-of-x,
    or 0 from RIII before it reaches the Adder) -- this module takes
    already-complemented digits as a plain input array.
  - Any per-stage propagation-time figure. The source gives none -- this
    is exactly the gap the Carry Delay Unit (chassis A-1455) exists to
    paper over with one fixed, engineered constant rather than a
    derived physical settling time (see sequencing_chain.py). This
    module computes the full 40-stage ripple as pure combinational
    logic with no internal timing of its own; the only place Adder
    timing enters the overall simulation is the fixed Carry Delay
    figure applied to the Green Gate hop in sequencing_chain.py.
"""

STAGES = 40

# (resident_digit, incident_digit, carry_in) -> (sum, carry_out)
# Transcribed directly from the source's case table (p. 76):
#   Resident digit          | 0 0 0 0 1 1 1 1
#   Incident digit          | 0 0 1 1 0 0 1 1
#   Carry from next lower   | 0 1 0 1 0 1 0 1
#   Sum                     | 0 1 1 0 1 0 0 1
#   Carry to next stage     | 0 0 0 1 0 1 1 1
TRUTH_TABLE = {
    (0, 0, 0): (0, 0),
    (0, 0, 1): (1, 0),
    (0, 1, 0): (1, 0),
    (0, 1, 1): (0, 1),
    (1, 0, 0): (1, 0),
    (1, 0, 1): (0, 1),
    (1, 1, 0): (0, 1),
    (1, 1, 1): (1, 1),
}


class Adder40:
    """Pure combinational 40-stage ripple-carry adder, matching the
    source's stage-level truth table exactly. No internal timing of its
    own -- see module docstring."""

    def add(self, resident_digits, incident_digits, carry_in=0):
        if len(resident_digits) != STAGES or len(incident_digits) != STAGES:
            raise ValueError(f"expected {STAGES}-digit operands")
        if carry_in not in (0, 1):
            raise ValueError("carry_in must be 0 or 1")

        sum_digits = [0] * STAGES
        stage_carries = []  # carry INTO each stage, kept for inspection
        carry = carry_in
        for i in range(STAGES):
            stage_carries.append(carry)
            r = resident_digits[i]
            k = incident_digits[i]
            if r not in (0, 1) or k not in (0, 1):
                raise ValueError(f"stage {i}: digits must be 0 or 1, got r={r!r} k={k!r}")
            s, carry = TRUTH_TABLE[(r, k, carry)]
            sum_digits[i] = s
        return sum_digits, carry, stage_carries
