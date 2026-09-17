"""
test_arithmetic_unit.py

Integration tests for the ArithmeticUnit, covering both:
  - the low-level record() entry point (raw digit arrays, bypassing
    RIII/Complement Gates) from the previous milestone, kept working, and
  - the new register-based operations (add/subtract/add_absolute_value/
    subtract_absolute_value) that read from actual RI/RIII state.
"""

from arithmetic_unit import ArithmeticUnit
from sequencing_chain import CARRY_DELAY_US, FEEDBACK_HOP_DELAY_US
from fractions import Fraction
import random


def digits_of(value, width=40):
    return [(value >> i) & 1 for i in range(width)]


def to_signed(value, width=40):
    """Interpret a 40-bit pattern as this machine represents negatives
    (x-bar = x + 2 for x<0, source pp.14-15) -- i.e. plain two's
    complement over `width` bits, for checking results in tests."""
    if value & (1 << (width - 1)):
        return value - (1 << width)
    return value


def from_signed(value, width=40):
    return value % (1 << width)


# ---- low-level record() (unchanged behavior from the previous milestone) ----

def test_record_computes_correct_sum():
    unit = ArithmeticUnit()
    carry_out, _ = unit.record(digits_of(11), digits_of(6))
    assert unit.r_lower.as_int() == 17


# ---- new register-based operations ----

def test_add_reads_from_ri_and_riii():
    unit = ArithmeticUnit()
    unit.load_ri(1234)
    unit.load_riii(4321)
    unit.add()
    assert unit.r_lower.as_int() == 5555


def test_subtract_gives_correct_difference_for_positive_result():
    unit = ArithmeticUnit()
    unit.load_ri(100)
    unit.load_riii(37)
    unit.subtract()
    assert unit.r_lower.as_int() == 63


def test_subtract_gives_correct_difference_for_negative_result():
    unit = ArithmeticUnit()
    unit.load_ri(from_signed(10))
    unit.load_riii(from_signed(37))
    unit.subtract()
    assert to_signed(unit.r_lower.as_int()) == 10 - 37


def test_add_absolute_value_of_negative_riii():
    unit = ArithmeticUnit()
    unit.load_ri(from_signed(10))
    unit.load_riii(from_signed(-7))  # |RIII| = 7, so this should ADD 7
    unit.add_absolute_value()
    assert to_signed(unit.r_lower.as_int()) == 10 + 7


def test_add_absolute_value_of_positive_riii_is_plain_add():
    unit = ArithmeticUnit()
    unit.load_ri(from_signed(10))
    unit.load_riii(from_signed(7))
    unit.add_absolute_value()
    assert to_signed(unit.r_lower.as_int()) == 10 + 7


def test_subtract_absolute_value_of_negative_riii():
    unit = ArithmeticUnit()
    unit.load_ri(from_signed(10))
    unit.load_riii(from_signed(-7))  # |RIII| = 7, so this should SUBTRACT 7
    unit.subtract_absolute_value()
    assert to_signed(unit.r_lower.as_int()) == 10 - 7


def test_preclear_resident_implements_transfer_variant():
    """Source, p.26, case 2: 'the addition of RIII and R^I precleared
    to 0 ... i.e. the transfer of a number into R^I' -- with R_I forced
    to 0 first, add() should just deposit RIII's value unchanged."""
    unit = ArithmeticUnit()
    unit.load_ri(999)  # should be wiped out by preclear_resident
    unit.load_riii(4321)
    unit.add(preclear_resident=True)
    assert unit.r_lower.as_int() == 4321


def test_cannot_execute_while_running():
    unit = ArithmeticUnit()
    unit.load_ri(1)
    unit.load_riii(1)
    unit.chain.start_cycle(first_half="Record", second_half="ShiftDownLeft")
    unit.engine.run_until(1.0)  # mid-cycle
    try:
        unit.add()
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass


# ---- shifts (RI and RII together, plus end-around) ----

def test_single_right_shift_divides_by_two():
    unit = ArithmeticUnit()
    unit.load_ri(10)
    unit.shift_right(1)
    assert unit.r_lower.as_int() == 5


def test_single_left_shift_multiplies_by_two():
    unit = ArithmeticUnit()
    unit.load_ri(5)
    unit.shift_left(1)
    assert unit.r_lower.as_int() == 10


def test_repeated_shift_matches_n_single_shifts():
    unit = ArithmeticUnit()
    unit.load_ri(0b11000)
    unit.shift_right(3)
    assert unit.r_lower.as_int() == 0b11


def test_right_shift_end_around_carries_ri_lsb_into_rii_sign():
    unit = ArithmeticUnit()
    unit.load_ri(1)   # odd -- LSB is 1, about to be shifted out
    unit.load_rii(0)
    unit.shift_right(1)
    assert unit.r_lower.as_int() == 0        # 1 >> 1 == 0
    assert unit.rii_lower.digits[39] == 1    # RI's departing LSB landed here
    assert unit.rii_lower.as_int() == (1 << 39)


def test_right_shift_end_around_does_not_fire_when_ri_lsb_is_zero():
    unit = ArithmeticUnit()
    unit.load_ri(2)   # even -- LSB is 0
    unit.load_rii(0)
    unit.shift_right(1)
    assert unit.rii_lower.digits[39] == 0


def test_left_shift_end_around_carries_ri_sign_into_rii_lsb():
    unit = ArithmeticUnit()
    unit.load_ri(1 << 39)  # sign digit set, about to shift out of range
    unit.load_rii(0)
    unit.shift_left(1)
    assert unit.r_lower.as_int() == 0     # shifted out of the normal 40 bits...
    assert unit.r_lower.digits[40] == 1   # ...caught in the extra stage (Fig. 10)
    assert unit.rii_lower.digits[0] == 1  # ...and carried into RII's LSB
    assert unit.rii_lower.as_int() == 1


def test_left_then_right_shift_round_trip_recovers_original_value():
    """General sanity check: shifting left n times then right n times
    should recover the original value, for values that don't overflow
    the 40-bit range during the left shifts."""
    import random
    rng = random.Random(1)
    for _ in range(10):
        n = rng.randint(1, 5)
        # keep the value small enough that n left-shifts won't overflow
        value = rng.randint(0, (1 << (39 - n)) - 1)
        unit = ArithmeticUnit()
        unit.load_ri(value)
        unit.shift_left(n)
        unit.shift_right(n)
        assert unit.r_lower.as_int() == value, (value, n)


def test_cannot_shift_while_running():
    unit = ArithmeticUnit()
    unit.load_ri(1)
    unit.chain.start_cycle(first_half="ShiftUp", second_half="ShiftDownRight")
    unit.engine.run_until(0.5)  # mid-cycle
    try:
        unit.shift_right(1)
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass


# ---- multiplication ----

def combined_signed_result(unit, width=40):
    """RI (upper) and RII (lower) combined into the true signed
    product. NOTE: the scale is RI * 2^(width-1) + RII's low
    (width-1) bits, NOT RI * 2^width + RII -- RII's own top bit
    (position 39) is reserved for a special value the source
    describes (order 0.9: "R2 = (1-b0), c40,...,c78" -- the sign
    position of RII is forced to 1 minus the multiplicand's sign digit,
    not a natural product bit), and RI's own final value is one power
    of two more significant than a naive RI:RII concatenation would
    suggest. This was worked out by testing against known products
    (starting from the smallest possible nonzero one, 2^-39 * 2^-39),
    not assumed in advance -- an earlier, wrong version of this helper
    used RI<<40 and happened to pass a same-sign test case only because
    RI was 0 in that particular example, which hid the error."""
    ri_signed = to_signed(unit.r_lower.as_int(), width)
    rii_masked = unit.rii_lower.as_int() & ((1 << (width - 1)) - 1)
    return ri_signed * (1 << (width - 1)) + rii_masked


def test_multiply_positive_times_positive():
    unit = ArithmeticUnit()
    unit.load_rii(from_signed(11))
    unit.load_riii(from_signed(6))
    unit.multiply()
    assert combined_signed_result(unit) == 11 * 6


def test_multiply_negative_times_positive():
    unit = ArithmeticUnit()
    unit.load_rii(from_signed(-11))
    unit.load_riii(from_signed(6))
    unit.multiply()
    assert combined_signed_result(unit) == -11 * 6


def test_multiply_positive_times_negative():
    unit = ArithmeticUnit()
    unit.load_rii(from_signed(11))
    unit.load_riii(from_signed(-6))
    unit.multiply()
    assert combined_signed_result(unit) == 11 * -6


def test_multiply_negative_times_negative():
    unit = ArithmeticUnit()
    unit.load_rii(from_signed(-11))
    unit.load_riii(from_signed(-6))
    unit.multiply()
    assert combined_signed_result(unit) == -11 * -6


def test_multiply_matches_python_for_many_random_signed_values():
    import random
    rng = random.Random(2)
    max_mag = (1 << 39) - 1  # keep values within the 40-bit signed range
    for _ in range(30):
        x = rng.randint(-max_mag, max_mag)
        y = rng.randint(-max_mag, max_mag)
        unit = ArithmeticUnit()
        unit.load_rii(from_signed(x))
        unit.load_riii(from_signed(y))
        unit.multiply()
        assert combined_signed_result(unit) == x * y, (x, y)


def test_multiply_by_zero():
    unit = ArithmeticUnit()
    unit.load_rii(from_signed(0))
    unit.load_riii(from_signed(-42))
    unit.multiply()
    assert combined_signed_result(unit) == 0


def test_cannot_multiply_while_running():
    unit = ArithmeticUnit()
    unit.load_rii(1)
    unit.load_riii(1)
    unit.chain.start_cycle(first_half="Record", second_half="ShiftDownLeft")
    unit.engine.run_until(1.0)
    try:
        unit.multiply()
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass


# ---- division ----
#
# Verification strategy: an independent Fraction-based transcription of
# formulas (1)-(3) from the source (pp.27-29), used as ground truth
# rather than re-deriving expected values by hand. The remainder is
# checked for an exact match; the quotient is checked to match to
# within exactly +1 ULP (2^-39), which is the documented rounding rule
# ("the 39th such digit is automatically made 1", p.30) rather than an
# error -- see divide()'s own docstring for how this was confirmed.

def _reference_divide(X, Y, width=39):
    x = Fraction(X, 1 << width)
    y = Fraction(Y, 1 << width)
    sgn_xy = (1 if x >= 0 else -1) * (1 if y >= 0 else -1)
    r = [x / 2]
    p = [0]
    q = [0 if sgn_xy > 0 else 1]
    for i in range(1, 39):
        r.append(2 * r[i - 1] - sgn_xy * y * p[i - 1])
        s = 2 * r[i] - sgn_xy * y
        p.append(1 if (r[i] >= 0) == (s >= 0) else 0)
        q.append(p[i] if sgn_xy > 0 else 1 - p[i])
    r.append(2 * r[38] - sgn_xy * y * p[38])
    P = sum(Fraction(1, 2 ** i) * p[i] for i in range(39))
    raw_q = sum(Fraction(1, 2 ** i) * q[i] for i in range(39))
    if raw_q >= 1:
        raw_q -= 2  # fold into the same signed representation as to_signed()
    return raw_q, r[39], P, sgn_xy


def _run_divide(X, Y):
    unit = ArithmeticUnit()
    unit.load_ri(from_signed(X))
    unit.load_riii(from_signed(Y))
    unit.divide()
    Q = Fraction(to_signed(unit.rii_lower.as_int()), 1 << 39)
    R = Fraction(to_signed(unit.r_lower.as_int()), 1 << 39)
    return Q, R


def test_divide_simple_positive_case():
    # 0.25 / 0.5 = 0.5 exactly, remainder 0 (plus the documented +2^-39
    # rounding digit -- see divide()'s docstring)
    Q, R = _run_divide(1 << 37, 1 << 38)
    assert Q == Fraction(1, 2) + Fraction(1, 1 << 39)
    assert R == 0


def test_divide_matches_reference_across_all_sign_combinations():
    cases = [
        (1 << 37, -(1 << 38)),   # x positive, y negative
        (-(1 << 36), 1 << 38),   # x negative, y positive
        (-(1 << 36), -(1 << 38)),  # both negative
        (1 << 37, 1 << 38),      # both positive
    ]
    for X, Y in cases:
        Q, R = _run_divide(X, Y)
        raw_q_ref, r39_ref, _, _ = _reference_divide(X, Y)
        assert R == r39_ref, (X, Y)
        assert Q - raw_q_ref == Fraction(1, 1 << 39), (X, Y)  # +1 ULP rounding digit


def test_divide_matches_reference_for_many_random_values():
    rng = random.Random(2024)
    max_mag = (1 << 39) - 1
    for _ in range(50):
        Y = rng.randint(1, max_mag)
        X = rng.randint(-Y + 1, Y - 1)  # enforce |x| < |y|
        if rng.random() < 0.5:
            Y = -Y
        Q, R = _run_divide(X, Y)
        raw_q_ref, r39_ref, _, _ = _reference_divide(X, Y)
        assert R == r39_ref, (X, Y)
        assert Q - raw_q_ref == Fraction(1, 1 << 39), (X, Y)


def test_divide_satisfies_the_sources_own_defining_relation():
    """Independent check using the source's own eq. 4, x = sgn(xy)*P*y
    + R where R = 2^-(n-1)*r_n (n=39) -- this R is an academically tiny
    quantity (an artifact of the telescoping-sum proof technique, pp.
    28-29), NOT the same thing as what ends up in RI at the end of
    divide() (see that method's docstring for the open question about
    reconciling this with the order spec's "R1 = 2R"). This test
    exists specifically to confirm the r-sequence itself is being
    computed correctly, independent of how it's later interpreted."""
    rng = random.Random(7)
    max_mag = (1 << 39) - 1
    for _ in range(30):
        Y = rng.randint(1, max_mag)
        X = rng.randint(-Y + 1, Y - 1)
        if rng.random() < 0.5:
            Y = -Y
        Q, R = _run_divide(X, Y)
        _, r39_ref, P, sgn_xy = _reference_divide(X, Y)
        assert R == r39_ref, (X, Y)  # simulation matches the reference recurrence exactly
        x_frac = Fraction(X, 1 << 39)
        y_frac = Fraction(Y, 1 << 39)
        R_formal = Fraction(1, 1 << 38) * r39_ref  # the source's own eq. 4 scaling
        assert x_frac == sgn_xy * P * y_frac + R_formal, (X, Y)


def test_cannot_divide_while_running():
    unit = ArithmeticUnit()
    unit.load_ri(1)
    unit.load_riii(2)
    unit.chain.start_cycle(first_half="ShiftUp", second_half="ShiftDownRight")
    unit.engine.run_until(0.5)
    try:
        unit.divide()
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass


if __name__ == "__main__":
    import sys
    import traceback

    tests = [
        test_record_computes_correct_sum,
        test_add_reads_from_ri_and_riii,
        test_subtract_gives_correct_difference_for_positive_result,
        test_subtract_gives_correct_difference_for_negative_result,
        test_add_absolute_value_of_negative_riii,
        test_add_absolute_value_of_positive_riii_is_plain_add,
        test_subtract_absolute_value_of_negative_riii,
        test_preclear_resident_implements_transfer_variant,
        test_cannot_execute_while_running,
        test_single_right_shift_divides_by_two,
        test_single_left_shift_multiplies_by_two,
        test_repeated_shift_matches_n_single_shifts,
        test_right_shift_end_around_carries_ri_lsb_into_rii_sign,
        test_right_shift_end_around_does_not_fire_when_ri_lsb_is_zero,
        test_left_shift_end_around_carries_ri_sign_into_rii_lsb,
        test_left_then_right_shift_round_trip_recovers_original_value,
        test_cannot_shift_while_running,
        test_multiply_positive_times_positive,
        test_multiply_negative_times_positive,
        test_multiply_positive_times_negative,
        test_multiply_negative_times_negative,
        test_multiply_matches_python_for_many_random_signed_values,
        test_multiply_by_zero,
        test_cannot_multiply_while_running,
        test_divide_simple_positive_case,
        test_divide_matches_reference_across_all_sign_combinations,
        test_divide_matches_reference_for_many_random_values,
        test_divide_satisfies_the_sources_own_defining_relation,
        test_cannot_divide_while_running,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL  {t.__name__}")
            traceback.print_exc()
    if failed:
        print(f"\n{failed}/{len(tests)} tests failed")
        sys.exit(1)
    else:
        print(f"\nAll {len(tests)} tests passed")
