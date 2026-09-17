"""
test_adder.py

Verifies Adder40 against the source's own case table row-by-row (so a
transcription slip in TRUTH_TABLE can't slip past self-consistent unit
tests alone), then against ordinary binary addition for full 40-bit
operands -- the source asserts this composition works ("We need not
worry about carries, as we have seen that these are all automatically
taken care of in the Adder") but never re-derives it for a multi-stage
case, so it's worth checking explicitly here.
"""

from iasmachine.adder import Adder40, TRUTH_TABLE, STAGES


def test_truth_table_matches_source_rows_exactly():
    # Transcribed straight from the printed table, p.76, left-to-right
    # as columns (1)-(8) -- kept separate from adder.py's own copy so a
    # typo in one isn't masked by the other.
    resident_row = [0, 0, 0, 0, 1, 1, 1, 1]
    incident_row = [0, 0, 1, 1, 0, 0, 1, 1]
    carry_row =    [0, 1, 0, 1, 0, 1, 0, 1]
    sum_row =      [0, 1, 1, 0, 1, 0, 0, 1]
    cout_row =     [0, 0, 0, 1, 0, 1, 1, 1]

    for i in range(8):
        key = (resident_row[i], incident_row[i], carry_row[i])
        s, c = TRUTH_TABLE[key]
        assert s == sum_row[i], f"case {i + 1}: expected sum {sum_row[i]}, got {s}"
        assert c == cout_row[i], f"case {i + 1}: expected carry {cout_row[i]}, got {c}"


def test_single_active_stage_uses_the_table():
    # NOTE: only stage 0's *own* sum/carry-out is checked against the
    # table here. The chain's overall carry_out after all 40 stages is
    # NOT the same thing when expected_cout==1 and the following stage
    # happens to be (0,0,1): that combination absorbs the carry (table
    # gives (1,0) for it), so it would be wrong to compare the full
    # ripple's final carry_out against a single stage's local carry-out.
    # stage_carries[1] is the carry stage 0 actually handed to stage 1,
    # which is the correct quantity to check.
    adder = Adder40()
    for (r, k, cin), (expected_sum, expected_cout) in TRUTH_TABLE.items():
        resident = [0] * STAGES
        incident = [0] * STAGES
        resident[0] = r
        incident[0] = k
        sum_digits, carry_out, stage_carries = adder.add(resident, incident, carry_in=cin)
        assert sum_digits[0] == expected_sum, (r, k, cin)
        assert stage_carries[0] == cin
        assert stage_carries[1] == expected_cout, (r, k, cin)


def int_to_digits(value, width=STAGES):
    """LSB-first bit list -- matches the source's 'index 0 is the
    lowest order digit' convention."""
    return [(value >> i) & 1 for i in range(width)]


def digits_to_int(digits):
    value = 0
    for i, d in enumerate(digits):
        value |= (d << i)
    return value


def test_multi_bit_addition_no_carry_out():
    adder = Adder40()
    a, b = 12345, 6789
    sum_digits, carry_out, _ = adder.add(int_to_digits(a), int_to_digits(b))
    assert digits_to_int(sum_digits) == a + b
    assert carry_out == 0


def test_multi_bit_addition_ripples_through_every_stage():
    adder = Adder40()
    max_val = (1 << STAGES) - 1
    a, b = max_val, 1  # forces the carry to ripple through all 40 stages
    sum_digits, carry_out, stage_carries = adder.add(int_to_digits(a), int_to_digits(b))
    assert digits_to_int(sum_digits) == 0, "should wrap to all-zero"
    assert carry_out == 1
    assert all(c == 1 for c in stage_carries[1:]), "carry should ripple through every stage"


def test_carry_in_to_stage_zero():
    adder = Adder40()
    sum_digits, carry_out, stage_carries = adder.add(
        int_to_digits(0), int_to_digits(0), carry_in=1
    )
    assert sum_digits[0] == 1
    assert carry_out == 0
    assert stage_carries[0] == 1


def test_rejects_wrong_width():
    adder = Adder40()
    try:
        adder.add([0] * 10, [0] * STAGES)
        assert False, "expected ValueError"
    except ValueError:
        pass


if __name__ == "__main__":
    import sys
    import traceback

    tests = [
        test_truth_table_matches_source_rows_exactly,
        test_single_active_stage_uses_the_table,
        test_multi_bit_addition_no_carry_out,
        test_multi_bit_addition_ripples_through_every_stage,
        test_carry_in_to_stage_zero,
        test_rejects_wrong_width,
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
