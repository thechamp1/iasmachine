"""
test_sequencing_chain.py

Golden-trace tests for the Gate-Clear Sequencing Chain, updated to the
real operation names (Record / ShiftUp / ShiftDownLeft / ShiftDownRight,
per Jan 1954 report pp.141-142) and to check the Carry Delay wiring for
the Record branch.
"""

from event_engine import EventQueue, EventLog
from sequencing_chain import SequencingChain, FEEDBACK_HOP_DELAY_US, CARRY_DELAY_US


def make_chain():
    engine = EventQueue()
    log = EventLog()
    chain = SequencingChain(engine, log)
    return engine, log, chain


def test_shiftup_worked_example():
    """The fully tube-table-verified example from the source (Black
    Clear = ShiftUp): chassis-1 toggle flips first at t=1.5us, chassis-5
    second at t=3.0us. Uses the plain 1.5us circuit lag throughout,
    since Shift Up never touches the Adder."""
    engine, log, chain = make_chain()

    assert chain.r1.value == 1
    assert chain.r2.value == 1
    assert chain.supertoggle.value == "idle"

    chain.start_cycle(first_half="ShiftUp", second_half="ShiftDownRight")

    engine.run_until(1.49)
    assert chain.active_line.value == "Black Clear"
    assert chain.r1.value == 1
    assert chain.supertoggle.value == 1

    engine.run_until(1.5)
    assert chain.r1.value == 0, "chassis-1 toggle should clear first for Shift Up"
    assert chain.active_line.value == "Yellow Gate"
    assert chain.r2.value == 1

    engine.run_until(3.0)
    assert chain.r2.value == 0, "chassis-5 toggle clears second for Shift Up"
    assert chain.supertoggle.value == 0
    # second half begins immediately (COMBINATIONAL_DELAY_US == 0)
    assert chain.active_line.value == "Yellow Clear"

    toggle_flip_times = [
        t for (t, name, old, new, note) in log
        if name in ("chassis1_toggle", "chassis5_toggle")
    ]
    assert toggle_flip_times == [1.5, 3.0]


def test_record_swaps_toggle_order_and_uses_carry_delay():
    """Record (Red Clear/Green Gate) is the Adder path. Source, prose:
    'flip the toggle in chassis (5) to 0, terminate the Clear, enable
    the Green Gate, flip the toggle in chassis (1) to 0, disable the
    Green Gate, flip the supertoggle to 0' -- chassis-5 first, opposite
    order from Shift Up. And Green Gate should not open until the Carry
    Delay (15us) has elapsed, not the plain 1.5us circuit lag."""
    engine, log, chain = make_chain()
    chain.start_cycle(first_half="Record", second_half="ShiftDownRight")

    # Just before the Carry Delay elapses, nothing should have moved yet.
    engine.run_until(CARRY_DELAY_US - 0.01)
    assert chain.active_line.value == "Red Clear"
    assert chain.r1.value == 1
    assert chain.r2.value == 1

    engine.run_until(CARRY_DELAY_US)
    assert chain.r2.value == 0, "chassis-5 toggle should clear FIRST for Record"
    assert chain.r1.value == 1, "chassis-1 toggle should not have moved yet"
    assert chain.active_line.value == "Green Gate"

    # Green Gate's own termination is not carry-delay-gated (see module
    # docstring) -- plain circuit lag applies for this second hop.
    engine.run_until(CARRY_DELAY_US + FEEDBACK_HOP_DELAY_US)
    assert chain.r1.value == 0, "chassis-1 toggle clears SECOND for Record"
    assert chain.supertoggle.value == 0

    toggle_flip_times = [
        t for (t, name, old, new, note) in log
        if name in ("chassis1_toggle", "chassis5_toggle")
    ]
    assert toggle_flip_times == [15.0, 16.5]


def test_full_cycle_returns_to_ready_state():
    for first in ("ShiftUp", "Record"):
        for second in ("ShiftDownLeft", "ShiftDownRight"):
            engine, log, chain = make_chain()
            chain.start_cycle(first_half=first, second_half=second)
            engine.run_all()

            assert chain.r1.value == 1, (first, second)
            assert chain.r2.value == 1, (first, second)
            assert chain.supertoggle.value == "idle", (first, second)
            assert chain.active_line.value is None, (first, second)

            expected_total = (
                (CARRY_DELAY_US if first == "Record" else FEEDBACK_HOP_DELAY_US)
                + FEEDBACK_HOP_DELAY_US  # first half, hop 2
                + FEEDBACK_HOP_DELAY_US  # second half, hop 1 (never carry-delayed)
                + FEEDBACK_HOP_DELAY_US  # second half, hop 2
            )
            assert engine.now == expected_total, (first, second, engine.now)


def test_cannot_start_cycle_while_running():
    engine, log, chain = make_chain()
    chain.start_cycle(first_half="ShiftUp", second_half="ShiftDownRight")
    engine.run_until(1.5)  # mid-cycle, not idle
    try:
        chain.start_cycle(first_half="ShiftUp", second_half="ShiftDownRight")
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass


def test_rejects_unknown_operation_names():
    engine, log, chain = make_chain()
    try:
        chain.start_cycle(first_half="BlackClear", second_half="ShiftDownRight")
        assert False, "expected ValueError"
    except ValueError:
        pass


if __name__ == "__main__":
    import sys
    import traceback

    tests = [
        test_shiftup_worked_example,
        test_record_swaps_toggle_order_and_uses_carry_delay,
        test_full_cycle_returns_to_ready_state,
        test_cannot_start_cycle_while_running,
        test_rejects_unknown_operation_names,
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
