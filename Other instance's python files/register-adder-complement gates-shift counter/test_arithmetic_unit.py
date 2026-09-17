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
