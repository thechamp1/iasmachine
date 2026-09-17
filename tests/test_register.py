"""
test_register.py

Tests for HalfRegister and its four gate transfers.
"""

from iasmachine.event_engine import EventQueue, EventLog
from iasmachine.register import HalfRegister, WIDTH


def make_pair():
    engine = EventQueue()
    log = EventLog()
    upper = HalfRegister("R^I", log, engine)
    lower = HalfRegister("R_I", log, engine)
    return engine, log, upper, lower


def digits_of(value, width=40):
    return [(value >> i) & 1 for i in range(width)]


def test_clear_to_1s_and_0s():
    engine, log, upper, lower = make_pair()
    upper.clear_to_1s()
    assert upper.as_int() == (1 << 40) - 1
    upper.clear_to_0s()
    assert upper.as_int() == 0


def test_green_gate_requires_prior_red_clear():
    engine, log, upper, lower = make_pair()  # not cleared to 1's
    try:
        upper.apply_green_gate(digits_of(17), carry_out=0)
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass


def test_green_gate_lands_sum_and_carry():
    engine, log, upper, lower = make_pair()
    upper.clear_to_1s()
    upper.apply_green_gate(digits_of(17), carry_out=1)
    assert upper.as_int() == 17
    assert upper.digits[40] == 1  # carry caught in the extra stage


def test_yellow_gate_requires_prior_black_clear():
    engine, log, upper, lower = make_pair()
    lower.digits = digits_of(5, width=WIDTH)
    upper.digits = digits_of(1, width=WIDTH)  # NOT cleared to 0 -- should reject
    try:
        upper.apply_yellow_gate(lower)
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass


def test_yellow_gate_copies_lower_into_upper_unchanged():
    engine, log, upper, lower = make_pair()
    lower.clear_to_1s()
    lower.apply_green_gate  # (not used here; just building a distinct pattern)
    lower.digits = digits_of(0b1011, width=WIDTH)
    upper.clear_to_0s()
    upper.apply_yellow_gate(lower)
    assert upper.digits == lower.digits


def test_red_gate_requires_prior_green_clear():
    engine, log, upper, lower = make_pair()
    upper.digits = digits_of(1, width=WIDTH)
    try:
        lower.apply_red_gate(upper)  # lower not cleared to 1
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass


def test_red_gate_shifts_toward_msb_and_drops_top_bit():
    # Red Gate "transmits 0's" against an all-1's destination, so a
    # single 0 in an otherwise-all-1's source is what's visible in the
    # (clear-dominant) output -- mostly-1's-with-one-hole is the
    # meaningful test pattern here, not mostly-0's-with-one-bit.
    engine, log, upper, lower = make_pair()
    upper.digits = [1] * WIDTH
    upper.digits[5] = 0
    # index 40 stays 1: this is the "drop the top bit" case -- if it
    # weren't dropped it would need position 41, which doesn't exist.
    lower.clear_to_1s()
    lower.apply_red_gate(upper)
    expected = [1] * WIDTH
    expected[6] = 0  # position 5 -> 6
    assert lower.digits == expected


def test_black_gate_requires_prior_yellow_clear():
    engine, log, upper, lower = make_pair()
    upper.digits = digits_of(1, width=WIDTH)
    lower.digits = digits_of(1, width=WIDTH)  # NOT cleared to 0 -- should reject
    try:
        lower.apply_black_gate(upper)
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass


def test_black_gate_shifts_toward_lsb_and_drops_bottom_bit():
    engine, log, upper, lower = make_pair()
    upper.digits = [0] * WIDTH
    upper.digits[5] = 1
    upper.digits[0] = 1  # bottom bit -- should be dropped
    lower.clear_to_0s()
    lower.apply_black_gate(upper)
    expected = [0] * WIDTH
    expected[4] = 1  # position 5 -> 4
    assert lower.digits == expected


def test_full_addition_round_trip_matches_adder_sum():
    """The key correctness property from the source: after the full
    Green -> Red -> Yellow -> Black round trip, R_I holds exactly the
    Adder's sum, for every position 0..39, with no off-by-one drift."""
    from iasmachine.adder import Adder40

    engine, log, upper, lower = make_pair()
    adder = Adder40()
    a, b = 0b1100110011, 0b0011001101
    sum_digits, carry_out, _ = adder.add(digits_of(a), digits_of(b))

    # Cycle 1: Green then Red
    upper.clear_to_1s()
    upper.apply_green_gate(sum_digits, carry_out)
    lower.clear_to_1s()
    lower.apply_red_gate(upper)

    # Cycle 2: Yellow then Black
    upper.clear_to_0s()
    upper.apply_yellow_gate(lower)
    lower.clear_to_0s()
    lower.apply_black_gate(upper)

    assert lower.as_int() == a + b
    assert lower.digits[:40] == sum_digits


if __name__ == "__main__":
    import sys
    import traceback

    tests = [
        test_clear_to_1s_and_0s,
        test_green_gate_requires_prior_red_clear,
        test_green_gate_lands_sum_and_carry,
        test_yellow_gate_requires_prior_black_clear,
        test_yellow_gate_copies_lower_into_upper_unchanged,
        test_red_gate_requires_prior_green_clear,
        test_red_gate_shifts_toward_msb_and_drops_top_bit,
        test_black_gate_requires_prior_yellow_clear,
        test_black_gate_shifts_toward_lsb_and_drops_bottom_bit,
        test_full_addition_round_trip_matches_adder_sum,
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
