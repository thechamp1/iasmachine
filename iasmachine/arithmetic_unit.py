"""
arithmetic_unit.py

The Arithmetic Organ so far: Record (Accept) through the Adder and
Complement Gates, general shift instructions on RI and RII together,
and the RI->RII end-around connections (Figs. 10, 11, I.5, I.6).

RESIDENT / INCIDENT WIRING (source, p.16 and Fig. I.4): the Adder's two
inputs are R_I ("Resident digit") and RIII by way of the Complement
Gates ("Incident digit"). This module reads R_I directly from
self.r_lower at the moment an operation starts (the Adder is analog/
combinational on the real machine -- its inputs are just whatever
voltages are present, so reading R_I's current value before any
clearing happens is faithful to that, not a simulation shortcut).

FOUR OPERATION VARIANTS (source, p.26) are exposed as add()/subtract()/
add_absolute_value()/subtract_absolute_value(), each optionally able to
preclear R_I to 0 first (the "transfer of a number (or its complement)
into R^I" variants) via preclear_resident=True.

SHIFTS (source, pp.26-27): shift_right(n)/shift_left(n) run RI and RII
together, one Sequencing Chain cycle per position, exactly as the
source states ("both RI and RII shift together... This amounts only to
an iteration n times of what is described above"). See shift_right()'s
and shift_left()'s own docstrings for the two extra hard-wired
connections (RI's own sign retention, and the RI->RII end-around) that
don't fall out of the plain per-register gate formulas and are
implemented as explicit extra steps.

STILL NOT MODELED, flagged rather than silently skipped:
  - RIII's own two-row, Discriminator-facing structure (it isn't a
    shifting register on the real machine -- see register.py's
    FlatRegister docstring), and the Yellow/Black gate transfers that
    would normally load it from Williams Memory. load_riii()/load_ri()/
    load_rii() are idealized instantaneous setters standing in for
    that until Memory exists.
  - RII's own Green Gate (wired to RIII per p.65, not to the Adder) and
    RIII's Red Gate (to the Dispatch Counter) -- separate connections
    from anything used here, not needed for shifts or Record.
  - The source's own flagged exception: "There is one exception to
    [RI and RII shifting together] in one of the terminal steps of a
    multiplication but this need not concern us here" -- true for the
    source's purposes, but will need resolving once multiplication is
    actually built.
  - Exactly what "the right-most stage of R^I is made 0" means for
    left shifts (source, p.27) -- see shift_left()'s docstring.
  - Main-Control-level instruction decode (which operation a given
    order selects) -- the caller picks directly for now.
"""

from iasmachine.event_engine import EventQueue, EventLog
from iasmachine.adder import Adder40
from iasmachine.sequencing_chain import SequencingChain
from iasmachine.register import HalfRegister, FlatRegister
from iasmachine.complement_gates import ComplementGates, PASS, COMPLEMENT, ZERO
from iasmachine.shift_counter import ShiftCounter


class ArithmeticUnit:
    def __init__(self):
        self.engine = EventQueue()
        self.log = EventLog()
        self.adder = Adder40()
        self.complement_gates = ComplementGates()
        self.r_upper = HalfRegister("R^I", self.log, self.engine)     # R^I
        self.r_lower = HalfRegister("R_I", self.log, self.engine)     # R_I
        self.rii_upper = HalfRegister("R^II", self.log, self.engine)  # R^II
        self.rii_lower = HalfRegister("R_II", self.log, self.engine)  # R_II
        self.riii = FlatRegister("RIII", self.log, self.engine)       # R3 (Incident)
        self.chain = SequencingChain(self.engine, self.log)
        self.shift_counter = ShiftCounter(self.log, self.engine)

        self._pending_sum = None
        self._pending_carry = None
        # See _on_active_line_change: True only while an actual
        # shift_left()/shift_right() cycle is running, so that Record's
        # own internal ShiftDownLeft realignment (which reuses the same
        # signal names) doesn't also perturb RII. Discovered by testing
        # multiply(), not anticipated in advance -- see this class's
        # docstring.
        self._rii_shifts_too = False
        self.chain.active_line.watch(self._on_active_line_change)

    def _on_active_line_change(self, old_value, new_value):
        # Red Clear / Green Gate are RI-only: they belong to Record,
        # the Adder path, and RII isn't involved in it (source, p.65:
        # RII's own Green Gates are wired to RIII, not the Adder --
        # that connection isn't modeled yet, see module docstring).
        if new_value == "Red Clear":
            self.r_upper.clear_to_1s()
        elif new_value == "Green Gate":
            if self._pending_sum is None:
                raise RuntimeError(
                    "Green Gate asserted with no Adder sum queued -- "
                    "an operation method should have set one"
                )
            self.r_upper.apply_green_gate(self._pending_sum, self._pending_carry)
            self._pending_sum = None
            self._pending_carry = None
        # The remaining four lines drive RI and RII TOGETHER only when
        # self._rii_shifts_too is set (source, p.27: "both RI and RII
        # shift together" -- true for an actual shift instruction, but
        # NOT true for Record's own second half-cycle, ShiftDownLeft,
        # which reuses the same Green-Clear/Red-Gate signal names purely
        # to realign the Adder's sum within RI and has nothing to do
        # with RII). Getting this distinction wrong was a real bug here:
        # multiply() interleaves Record (add) steps with real shifts,
        # and without this flag, every add step also silently shifted
        # RII, corrupting the multiplier/product it was building up.
        elif new_value == "Black Clear":
            self.r_upper.clear_to_0s()
            if self._rii_shifts_too:
                self.rii_upper.clear_to_0s()
        elif new_value == "Green Clear":
            self.r_lower.clear_to_1s()
            if self._rii_shifts_too:
                self.rii_lower.clear_to_1s()
        elif new_value == "Red Gate":
            self.r_lower.apply_red_gate(self.r_upper)
            if self._rii_shifts_too:
                self.rii_lower.apply_red_gate(self.rii_upper)
        elif new_value == "Yellow Clear":
            self.r_lower.clear_to_0s()
            if self._rii_shifts_too:
                self.rii_lower.clear_to_0s()
        elif new_value == "Black Gate":
            self.r_lower.apply_black_gate(self.r_upper)
            if self._rii_shifts_too:
                self.rii_lower.apply_black_gate(self.rii_upper)
        elif new_value == "Yellow Gate":
            self.r_upper.apply_yellow_gate(self.r_lower)
            if self._rii_shifts_too:
                self.rii_upper.apply_yellow_gate(self.rii_lower)

    # --- idealized loads, standing in for Memory (see module docstring) ---

    def load_ri(self, value, width=40):
        digits = [(value >> i) & 1 for i in range(width)]
        self.r_lower.load(digits)

    def load_riii(self, value, width=40):
        digits = [(value >> i) & 1 for i in range(width)]
        self.riii.load(digits)

    def load_rii(self, value, width=40):
        digits = [(value >> i) & 1 for i in range(width)]
        self.rii_lower.load(digits)

    # --- shift instructions (source, pp.26-27; Figs. I.5/I.6, 10, 11) ---

    def shift_right(self, n=1):
        """Right shift RI and RII together, n times (source: 1<=n<=47
        by a single order). Each single-position shift is one
        Sequencing Chain cycle: ShiftUp then ShiftDownRight.

        Two extra hard-wired connections beyond the plain per-register
        gate formulas, both implemented here explicitly since neither
        falls out of the general Red/Black gate index arithmetic:

          - RI's own sign retention (p.27): "The information stored in
            2^+1 of RI is... shifted into 2^0. It is ALSO retained in
            2^+1." The shift into 2^0 (our r_lower[39]) already happens
            via the ordinary Black Gate formula; the retention at 2^+1
            (r_lower[40]) does not, since nothing in that formula maps
            into position 40 -- it's copied explicitly below.

          - The RI -> RII end-around (Figs. 10/11, p.69): "the contents
            of 2^-39 R_1 is shifted into the 0-th stage of R_2" -- RI's
            departing LSB (r_lower[0], captured BEFORE the cycle, since
            the real tap reads it via the Yellow Gate step at the start
            of the same cycle) overrides whatever RII's own Black Gate
            step would otherwise leave in its sign position (rii_lower[39]).
        """
        for _ in range(n):
            if self.chain.supertoggle.value != "idle":
                raise RuntimeError("cannot shift while a cycle is running")
            end_around_bit = self.r_lower.digits[0]

            self._rii_shifts_too = True
            try:
                self.chain.start_cycle(first_half="ShiftUp", second_half="ShiftDownRight")
                self.engine.run_all()
            finally:
                self._rii_shifts_too = False

            self.r_lower.digits[40] = self.r_upper.digits[40]  # sign retention
            self.rii_lower.digits[39] = end_around_bit          # end-around

    def shift_left(self, n=1):
        """Left shift RI and RII together, n times. Each single-position
        shift is one Sequencing Chain cycle: ShiftUp then ShiftDownLeft.

        R_I's newly-vacated LSB (position 0) is forced to 0 after the
        Red Gate step. This is NOT optional bookkeeping: Red Gate
        "transmits 0's" against an all-1's preclear, and position 0 has
        no source mapped to it under the shift-by-+1 formula (see
        register.py), so without this it would be left at the spurious
        1 the Green Clear put there -- confirmed empirically (a plain
        shift_left(1) of 5 produced 11, not 10, before this fix was
        added). The source describes a fix for this ("the left shift is
        performed analogously to that for the right shift but the
        right-most stage of R^I is made 0", p.27) but names R^I where
        the right-shift passage it's explicitly contrasted with was
        unambiguous about which half-register was meant and this one
        isn't, from what's been read so far -- forcing R^I's position 0
        to 0 doesn't reach R_I[0] under Red Gate's index mapping either
        way, so I couldn't reconcile the exact wording with the index
        arithmetic. What's implemented below is the behaviorally
        required fix (R_I[0] = 0, matching "the left shift is exactly a
        multiplication by 2"), not a confirmed transcription of the
        source's own mechanism -- flagged rather than presented as
        settled.

        End-around (Fig. I.6, p.65): RI's departing sign digit
        (r_lower[39], captured before the cycle) overrides whatever
        RII's own Red Gate step would otherwise leave at its LSB
        (rii_lower[0]) -- which happens to also be exactly the fix
        RII's own position 0 would otherwise need for the same reason
        as RI's, so no separate correction is needed there.
        """
        for _ in range(n):
            if self.chain.supertoggle.value != "idle":
                raise RuntimeError("cannot shift while a cycle is running")
            end_around_bit = self.r_lower.digits[39]

            self._rii_shifts_too = True
            try:
                self.chain.start_cycle(first_half="ShiftUp", second_half="ShiftDownLeft")
                self.engine.run_all()
            finally:
                self._rii_shifts_too = False

            self.r_lower.digits[0] = 0                 # see docstring
            self.rii_lower.digits[0] = end_around_bit  # end-around (see docstring)

    # --- multiplication (source, pp.17-20; order 0.9/0.10) ---

    def _flush_rii_one_position(self):
        """RII's own internal right-shift by one position, with RI
        left completely untouched -- used once at the end of
        multiply(). RI's value is already final and exactly correct
        after the 39 main steps (matches the source's own p_39 = xy
        derivation, pp.17-19 -- verified directly: RI is unchanged by
        this call). RII, however, needs one more internal repositioning
        shift to land its 39 accumulated end-around bits in their final
        resting positions -- confirmed empirically against the smallest
        possible nonzero product (2^-39 * 2^-39), which only lands at
        RII's bit 0 with this extra shift.

        This is NOT the same as shift_right(1): that shifts RI and RII
        together and would incorrectly move RI's already-correct value
        one place further. It's also applied directly rather than
        through the Sequencing Chain (no simulated timing/delay) --
        there's no chassis in the sources read so far that this step
        can be attributed to, so making up a duration for it would be
        worse than leaving it untimed and flagged as such.
        """
        self._rii_shifts_too = True
        try:
            self.rii_upper.clear_to_0s()
            self.rii_upper.apply_yellow_gate(self.rii_lower)
            self.rii_lower.clear_to_0s()
            self.rii_lower.apply_black_gate(self.rii_upper)
        finally:
            self._rii_shifts_too = False

    def _shift_ri_only(self, direction):
        """RI's own internal shift by one position, with RII completely
        untouched and no RI->RII end-around -- used by divide(), where
        the source explicitly says this channel is suppressed ("the
        channel from RI to RII which normally transmits for a left
        shift is suppressed", p.27). direction is 'left' or 'right'.
        Applied directly (no Sequencing Chain timing), same rationale
        as _flush_rii_one_position().
        """
        self.r_upper.clear_to_0s()
        self.r_upper.apply_yellow_gate(self.r_lower)
        if direction == "left":
            self.r_lower.clear_to_1s()
            self.r_lower.apply_red_gate(self.r_upper)
            self.r_lower.digits[0] = 0  # see shift_left()'s docstring
        elif direction == "right":
            self.r_lower.clear_to_0s()
            self.r_lower.apply_black_gate(self.r_upper)
            self.r_lower.digits[40] = self.r_upper.digits[40]  # sign retention
        else:
            raise ValueError("direction must be 'left' or 'right'")

    def _shift_rii_only_left_with_insert(self, bit):
        """RII's own internal left-shift by one position, with RI
        untouched, inserting `bit` at the newly-vacated LSB (position
        0) instead of forcing it to 0 -- used by divide() to build up
        the quotient digit by digit, per p.27: "the quotient digits are
        inserted seriatim into position 38 of RII and shifted left."
        (Report-page numbering has position 0 as the sign digit and
        increasing index toward the LSB, so "position 38" there is
        position 1 in this codebase's LSB-at-0 convention -- one above
        the very bottom, not the bottom itself. Tried inserting at
        position 0 first; only position 1 reproduces the source's own
        completion condition and end state under testing -- see
        divide()'s docstring.)
        """
        self.rii_upper.clear_to_0s()
        self.rii_upper.apply_yellow_gate(self.rii_lower)
        self.rii_lower.clear_to_1s()
        self.rii_lower.apply_red_gate(self.rii_upper)
        self.rii_lower.digits[0] = 0
        self.rii_lower.digits[1] = bit

    # --- division (source, pp.27-31; order 0.11) ---

    def divide(self):
        """
        Divide RI (dividend) by RIII (divisor), leaving the quotient in
        RII and the remainder-related value in RI, per order 0.11.
        Requires |dividend| < |divisor| (source's own precondition,
        p.27) -- not enforced here, but the result is meaningless if
        violated, same as on the real machine.

        ALGORITHM (source, pp.27-31, non-restoring-with-explicit-
        revert division): for i=1..39, form s = 2*r_{i-1} -(sgn xy) y
        (left shift then add-or-subtract depending on the sign of x*y),
        then compare sign(s) to sign(x) (an invariant: sign(r_i) always
        equals sign(x), p.28-29) to get p_{i-1}. If the signs agree,
        keep s as r_i; if not, the subtract/add was wrong and gets
        undone, leaving r_i = 2r_{i-1}. q_i = p_i (or 1-p_i if sgn(xy)
        is negative) is the i-th quotient digit.

        p_0 = 0 is given directly (not computed), making q_0 a fixed
        value (0 or 1 depending on sgn(xy) alone) and r_1 = 2r_0 = x
        exactly -- so the loop below starts from r=x directly for its
        first REAL (sign-checking) step and only runs 38 times, for
        q_1..q_38, matching the source's own count ("39 steps
        determining the sign and 38 information digits").

        RI/RII do NOT shift together here -- the source is explicit
        that the normal RI->RII channel is suppressed during division,
        replaced by quotient digits being inserted directly. See
        _shift_ri_only()/_shift_rii_only_left_with_insert().

        NOT SOURCED, found by testing (same situation as multiply()'s
        RII-only flush): the source states quotient digits are
        "inserted seriatim into position 38 of RII" -- in this
        codebase's LSB-at-0 indexing that's position 1, one above the
        very bottom, not position 0 as a naive reading might suggest.
        Tested this against the order's own listed end state, "R2 =
        q0,q1,...,q38,1": reading that left-to-right in the source's
        own sign-first convention (matching how "RI = c0,...,c39" was
        confirmed earlier to list c0, the most significant digit,
        first), q0 is the MOST significant entry and the final "1" is
        the LEAST significant -- i.e. q0 ends up at position 39 (the
        leading stage) and the forced "1" at position 0 (the very LSB),
        the reverse of my first assumption. With insertion at position
        1, q0 (inserted before the main loop) naturally migrates to
        position 39 after exactly 38 more shifts, matching "the
        operation continues until the sign digit of the quotient
        reaches position 0 [of RII, in the source's own sign-first
        indexing]" -- so no separate handling for q0's final position
        is needed; only the trailing "1" (position 0) is set explicitly,
        after the loop.

        REMAINDER: RI ends up holding r_39 directly (the recurrence's
        own r value, unscaled) -- confirmed against an independent
        Fraction-based reimplementation of formulas (1)-(3), matching
        exactly across 1000+ random trials, and that reimplementation's
        r_39 in turn satisfies the source's own defining relation, eq.
        4 (x = sgn(xy)*P*y + R, R = 2^-38*r_39) exactly. That formal R
        is astronomically tiny (an artifact of the telescoping-sum
        proof technique, not a hardware-meaningful value) -- so it
        isn't literally "2R" in RI's own terms, and I could not
        reconcile RI's final value with the order spec's "R1 = 2R"
        phrase by any simple scale factor. Flagged as an open question
        about the source's own terminology (perhaps a different,
        practical "remainder" notion than eq. 4's R), not a gap in this
        implementation -- the r-sequence itself is verified correct.

        LAST-PLACE ROUNDING: initial confusion here (worth recording,
        since it cost a lot of debugging time) turned out to be a test
        methodology error, not a simulation bug: the raw 39-digit
        quotient (q_0..q_38, no rounding) differs from what this method
        actually produces by exactly one ULP (2^-39) in every case
        tested, in the same direction, every time -- which is exactly
        the documented rounding rule ("the 39th such digit is
        automatically made 1", p.30) adding one more digit's worth on
        top of the raw sum, not an inherent last-place error. Verified
        against an independent Fraction-based transcription of formulas
        (1)-(3) across 1000 random cases: the remainder matches exactly
        every time, and the quotient matches to exactly +1 ULP (the
        rounding digit) every time -- see test_arithmetic_unit.py.
        """
        if self.chain.supertoggle.value != "idle":
            raise RuntimeError("cannot divide while a cycle is running")

        x = list(self.r_lower.digits[:40])  # dividend
        y = list(self.riii.digits)          # divisor
        x_negative = x[39] == 1
        y_negative = y[39] == 1
        sgn_xy_negative = x_negative != y_negative

        q0 = 0 if not sgn_xy_negative else 1
        self.rii_lower.clear_to_0s()
        self._shift_rii_only_left_with_insert(q0)

        self.r_lower.load(x)  # r_1 = 2*r_0 = x exactly -- see docstring
        self.shift_counter.start(39, note="divide")
        self.shift_counter.step()  # step 1 (q_0) already accounted for above

        for _ in range(38):
            self._shift_ri_only("left")  # r := 2*r_{i-1}

            resident = self.r_lower.digits[:40]
            if sgn_xy_negative:
                addend, carry_in = y, 0            # -(sgn xy) = +1 -> add y
            else:
                addend, carry_in = self.complement_gates.apply(y, COMPLEMENT)  # -(sgn xy) = -1 -> subtract y
            self.record(resident, addend, carry_in=carry_in)

            s_negative = self.r_lower.digits[39] == 1
            p = 1 if s_negative == x_negative else 0

            if p == 0:
                resident = self.r_lower.digits[:40]
                if sgn_xy_negative:
                    addend, carry_in = self.complement_gates.apply(y, COMPLEMENT)  # undo the add
                else:
                    addend, carry_in = y, 0                                        # undo the subtract
                self.record(resident, addend, carry_in=carry_in)

            q_i = p if not sgn_xy_negative else 1 - p
            self._shift_rii_only_left_with_insert(q_i)
            self.shift_counter.step()

        self.rii_lower.digits[0] = 1  # rounding digit -- see docstring

    def multiply(self):
        """
        Multiply RII (the multiplier) by RIII (the multiplicand),
        leaving the 78-digit product spread across RI (upper 40
        digits) and RII (lower digits), per order 0.9 ("Multiply
        No-Round-Off", "clear" case -- RI precleared to 0).

        CORE ALGORITHM (source, pp.17-19, unsigned case): for each of
        the 39 non-sign digits of the multiplier, examined starting
        from the LSB, add the multiplicand into RI if the current
        multiplier digit is 1 (0 otherwise), then shift RI/RII right
        together by one. Examining RII's own bit 0 at each step and
        then shifting is exactly what shift_right()'s existing RI->RII
        end-around already does the physical work for -- this loop
        doesn't add any new register plumbing, only the conditional-add
        orchestration on top of it. This is, per the source, precisely
        why that end-around wiring exists in the first place.

        SIGN CORRECTIONS (source, pp.19-20): if the multiplicand (RIII)
        is negative, each step's addend is replaced (0 becomes a
        constant "1" at weight 2^0, y becomes y' = y with its own sign
        digit forced to 0), with a final correction of (1 + 2^-39)
        added afterward. If the multiplier (RII) is negative, the
        multiplicand is subtracted once more after the 39 steps.

        NOTE ON SOURCING: the source's own derivation of the y'
        correction states "y1 = y - 1" and then, two lines later, uses
        "xy1 = x(y+1)" -- these are inconsistent, and y+1 is what's
        implemented here, since it's what the rest of that derivation
        (down to the stated final result xy + (1-2^-39)) is internally
        consistent with. Tested against plain integer multiplication
        across all four sign combinations in test_arithmetic_unit.py,
        not just derived by hand -- see that file for how thoroughly
        this was checked given the transcription question.

        NOT implemented: round-off (order 0.10, a different final
        correction) and the "clear digit = 0" variant that adds RI's
        prior contents into the first partial product.
        """
        if self.chain.supertoggle.value != "idle":
            raise RuntimeError("cannot multiply while a cycle is running")

        y = list(self.riii.digits)
        y_negative = y[39] == 1
        y_prime = list(y)
        y_prime[39] = 0  # y with its own sign digit forced to 0

        one_const = [0] * 40
        one_const[39] = 1  # weight 2^0 only

        zero_const = [0] * 40

        x_negative = self.rii_lower.digits[39] == 1  # multiplier's sign, read before it's consumed

        self.r_lower.clear_to_0s(note="multiply: clear RI (start)")
        self.shift_counter.start(39, note="multiply")

        for _ in range(39):
            multiplier_bit = self.rii_lower.digits[0]
            if y_negative:
                addend = y_prime if multiplier_bit == 1 else one_const
            else:
                addend = y if multiplier_bit == 1 else zero_const
            resident = self.r_lower.digits[:40]
            self.record(resident, addend, carry_in=0)
            self.shift_right(1)
            self.shift_counter.step()

        # RI is already exactly correct here (p_39 = xy per the source's
        # own derivation) -- only RII needs the extra repositioning
        # shift below. See _flush_rii_one_position()'s docstring: this
        # was found by testing, not derived from the source text.
        self._flush_rii_one_position()

        if x_negative:
            resident = self.r_lower.digits[:40]
            addend, carry_in = self.complement_gates.apply(y, COMPLEMENT)
            self.record(resident, addend, carry_in=carry_in)

        if y_negative:
            correction = [0] * 40
            correction[39] = 1
            correction[0] = 1
            resident = self.r_lower.digits[:40]
            self.record(resident, correction, carry_in=0)

    # --- the four operation variants (source, p.26) ---

    def add(self, preclear_resident=False):
        return self._execute(PASS, preclear_resident)

    def subtract(self, preclear_resident=False):
        return self._execute(COMPLEMENT, preclear_resident)

    def add_absolute_value(self, preclear_resident=False):
        return self._execute("abs", preclear_resident, negate=False)

    def subtract_absolute_value(self, preclear_resident=False):
        return self._execute("abs", preclear_resident, negate=True)

    def _execute(self, mode, preclear_resident, negate=False):
        if self.chain.supertoggle.value != "idle":
            raise RuntimeError("cannot start a new cycle while one is running")

        if preclear_resident:
            self.r_lower.clear_to_0s(note="preclear before transfer")

        resident_digits = self.r_lower.digits[:40]
        if mode == "abs":
            incident_digits, carry_in = self.complement_gates.apply_absolute_value(
                self.riii.digits, negate=negate
            )
        else:
            incident_digits, carry_in = self.complement_gates.apply(self.riii.digits, mode)

        sum_digits, carry_out, stage_carries = self.adder.add(
            resident_digits, incident_digits, carry_in
        )
        self._pending_sum = sum_digits
        self._pending_carry = carry_out

        self.chain.start_cycle(first_half="Record", second_half="ShiftDownLeft")
        self.engine.run_all()

        self.chain.start_cycle(first_half="ShiftUp", second_half="ShiftDownRight")
        self.engine.run_all()

        return carry_out, stage_carries

    # --- kept for direct low-level testing against raw digit arrays ---

    def record(self, resident_digits, incident_digits, carry_in=0):
        """Low-level entry point bypassing RIII/Complement Gates
        entirely -- useful for testing the Adder/cycle wiring in
        isolation. Prefer add()/subtract()/etc. for anything meant to
        resemble a real instruction."""
        if self.chain.supertoggle.value != "idle":
            raise RuntimeError("cannot start a new cycle while one is running")

        sum_digits, carry_out, stage_carries = self.adder.add(
            resident_digits, incident_digits, carry_in
        )
        self._pending_sum = sum_digits
        self._pending_carry = carry_out

        self.chain.start_cycle(first_half="Record", second_half="ShiftDownLeft")
        self.engine.run_all()

        self.chain.start_cycle(first_half="ShiftUp", second_half="ShiftDownRight")
        self.engine.run_all()

        return carry_out, stage_carries
