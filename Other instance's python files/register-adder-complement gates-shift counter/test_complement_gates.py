"""
test_complement_gates.py
"""

from complement_gates import ComplementGates, PASS, COMPLEMENT, ZERO


def digits_of(value, width=40):
    return [(value >> i) & 1 for i in range(width)]


def test_pass_mode_returns_unchanged_with_no_carry():
    gates = ComplementGates()
    src = digits_of(0b1010)
    out, carry_in = gates.apply(src, PASS)
    assert out == src
    assert carry_in == 0


def test_complement_mode_inverts_every_bit_and_injects_carry():
    gates = ComplementGates()
    src = digits_of(0b1010)
    out, carry_in = gates.apply(src, COMPLEMENT)
    assert out == [1 - d for d in src]
    assert carry_in == 1


def test_zero_mode_returns_all_zero_with_no_carry():
    gates = ComplementGates()
    src = digits_of(0b1010)
    out, carry_in = gates.apply(src, ZERO)
    assert out == [0] * 40
    assert carry_in == 0


def test_unknown_mode_rejected():
    gates = ComplementGates()
    try:
        gates.apply(digits_of(0), "nonsense")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_subtraction_via_adder_matches_ordinary_arithmetic():
    """The actual point of this module: x - y should come out right
    when routed through the Adder exactly as the source describes."""
    from adder import Adder40

    adder = Adder40()
    gates = ComplementGates()
    x, y = 100, 37
    y_digits, carry_in = gates.apply(digits_of(y), COMPLEMENT)
    sum_digits, carry_out, _ = adder.add(digits_of(x), y_digits, carry_in)
    result = sum(d << i for i, d in enumerate(sum_digits))
    assert result == x - y


def test_absolute_value_passes_positive_and_complements_negative():
    gates = ComplementGates()

    positive = digits_of(5)  # sign digit (index 39) is 0
    out, carry_in = gates.apply_absolute_value(positive)
    assert out == positive
    assert carry_in == 0

    negative = digits_of(5)
    negative[39] = 1  # force the sign digit on, regardless of magnitude bits
    out, carry_in = gates.apply_absolute_value(negative)
    assert out == [1 - d for d in negative]
    assert carry_in == 1


def test_absolute_value_negate_flips_the_selection():
    gates = ComplementGates()
    positive = digits_of(5)
    out, carry_in = gates.apply_absolute_value(positive, negate=True)
    assert out == [1 - d for d in positive]
    assert carry_in == 1


if __name__ == "__main__":
    import sys
    import traceback

    tests = [
        test_pass_mode_returns_unchanged_with_no_carry,
        test_complement_mode_inverts_every_bit_and_injects_carry,
        test_zero_mode_returns_all_zero_with_no_carry,
        test_unknown_mode_rejected,
        test_subtraction_via_adder_matches_ordinary_arithmetic,
        test_absolute_value_passes_positive_and_complements_negative,
        test_absolute_value_negate_flips_the_selection,
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
