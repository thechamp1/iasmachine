"""
sequencing_chain.py

Gate-Clear Sequencing Chain (drawing C-1449; chassis 1-5 + supertoggle),
per IAS Final Progress Report, Jan 1954, pp. 145-152 ("The Gate-Clear
Sequencing Chain" -- tube-by-tube trace).

OPERATION NAMES (p. 141-142 of the same report; this is the update from
the previous version of this module, which used arbitrary bit labels):

    Record (Accept):    Red Clear,    Green Gate    -- through the Adder
    Shift up (Reject):  Black Clear,  Yellow Gate   -- direct, no Adder
    Shift down left:    Green Clear,  Red Gate
    Shift down right:   Yellow Clear, Black Gate

  "Obviously the first half cycle is either a 'Record' or a 'Shift Up',
  while the second is either 'Shift Down Left' or 'Shift Down Right'."
  Record is the only one of the four that involves the Adder ("the
  Adder and Digit Resolver form the sum ... and transmit this sum by
  way of a set of gates (the Green gates of RI) to R-I"), which is
  exactly why the Carry Delay only applies to that branch below.

SOURCING NOTES for the delay constants:

  - FEEDBACK_HOP_DELAY_US = 1.5 is given explicitly, twice, for the two
    feedback hops of the fully tube-table-worked "Black Clear" (Shift
    Up) example: "Lags through the circuits cause an interval of 1.5
    usec. to elapse between the initiation and termination of the
    Black Clear" (hop 1), and "the disabling of the Yellow gate occurs
    about 1.5 usec. after its enabling" (hop 2).

  - CARRY_DELAY_US = 15.0 comes from a DIFFERENT document (IAS report,
    Apr 1954, pp. I-30/I-31): "Green Gate (which accepts the
    information into RI) does not occur until about 15 microseconds
    after T-BLOCK turn-on, because of the imposed Carry Delay." That
    passage describes a Magnetic-Drum read-in specifically, not the
    general Record operation traced in the Jan 1954 report -- but both
    describe the same physical event (Green Gate opening to accept an
    Adder sum into RI), so treating 15us as the general Record-branch
    figure is a reasoned generalization, not a literally-restated
    universal constant. Flagged here rather than presented as
    independently confirmed for every arithmetic order.

  - The SECOND hop of the Record branch (Green Gate closing, chassis-1
    toggle flip, supertoggle flip) is NOT covered by the 15us figure --
    that figure is specifically about when Green Gate *opens*. Absent
    a documented figure for how it closes, this module falls back to
    FEEDBACK_HOP_DELAY_US for that hop, same as every other branch's
    second hop. Flagged as an assumption, not a sourced number.

  - COMBINATIONAL_DELAY_US: no explicit lag is documented for the pure
    combinational step where Counter Stop causes the first Clear line
    to assert (as opposed to the two feedback hops above, which involve
    a toggle physically changing state). Modeled as 0.0 pending further
    sourcing.

  - TOGGLE ORDER IS BRANCH-DEPENDENT, confirmed directly from the
    source's worked/prose descriptions of all four branches -- see the
    FIRST_HALF / SECOND_HALF tables below. Record and Shift Up (the
    first-half pair) differ in which toggle moves first; so do Shift
    Down Left and Shift Down Right (the second-half pair).
"""

from iasmachine.event_engine import EventQueue, EventLog, Signal

FEEDBACK_HOP_DELAY_US = 1.5    # documented, Jan54 report pp.148-149
CARRY_DELAY_US = 15.0          # documented (as an effect), Apr54 report -- see docstring
COMBINATIONAL_DELAY_US = 0.0   # NOT documented -- see module docstring

# operation name -> (clear_name, first_toggle, gate_name, second_toggle,
#                     toggle_value_after_this_half, hop1_delay)
FIRST_HALF = {
    "ShiftUp": ("Black Clear", "r1", "Yellow Gate", "r2", 0, FEEDBACK_HOP_DELAY_US),
    "Record":  ("Red Clear",   "r2", "Green Gate",  "r1", 0, CARRY_DELAY_US),
}
SECOND_HALF = {
    "ShiftDownRight": ("Yellow Clear", "r1", "Black Gate", "r2", 1, FEEDBACK_HOP_DELAY_US),
    "ShiftDownLeft":  ("Green Clear",  "r2", "Red Gate",   "r1", 1, FEEDBACK_HOP_DELAY_US),
}


class SequencingChain:
    """One full instruction cycle of the Gate-Clear Sequencing Chain:
    two half-cycles, each a Clear followed by a Gate, mediated by the
    toggles in chassis 1 and 5 and the supertoggle."""

    def __init__(self, engine: EventQueue, log: EventLog):
        self.engine = engine
        self.log = log

        self.r1 = Signal("chassis1_toggle", 1, log, engine)   # "the toggle in chassis (1)"
        self.r2 = Signal("chassis5_toggle", 1, log, engine)   # "the toggle in chassis (5)"
        # 'idle' before the first Counter Stop pulse of a cycle -- the
        # source describes this as "both sections of the supertoggle
        # tube cut off", a state distinct from logical 0 or 1.
        self.supertoggle = Signal("supertoggle", "idle", log, engine)
        self.active_line = Signal("active_line", None, log, engine)  # None when quiescent

        self._toggles = {"r1": self.r1, "r2": self.r2}

    def start_cycle(self, first_half, second_half):
        """
        Raise Counter Stop to begin one full instruction cycle.

        first_half:  "Record" or "ShiftUp"
        second_half: "ShiftDownLeft" or "ShiftDownRight"
        """
        if first_half not in FIRST_HALF:
            raise ValueError(f"first_half must be one of {list(FIRST_HALF)}")
        if second_half not in SECOND_HALF:
            raise ValueError(f"second_half must be one of {list(SECOND_HALF)}")
        if self.supertoggle.value != "idle":
            raise RuntimeError(
                "start_cycle called while chain is not idle "
                f"(supertoggle={self.supertoggle.value!r})"
            )
        self._second_half = second_half

        def _counter_stop_raised():
            self.supertoggle.set_now(1, note="Counter Stop raised")
            self._run_half(FIRST_HALF[first_half], on_done=self._begin_second_half)

        self.engine.schedule(COMBINATIONAL_DELAY_US, _counter_stop_raised)

    def _begin_second_half(self):
        self._run_half(SECOND_HALF[self._second_half], on_done=self._finish_cycle)

    def _finish_cycle(self):
        self.supertoggle.set_now("idle", note="cycle complete")

    def _run_half(self, spec, on_done):
        clear_name, first_tog, gate_name, second_tog, value, hop1_delay = spec

        self._assert_line(clear_name)

        def _hop_one():
            self._toggles[first_tog].set_now(value, note=f"cleared/set by {clear_name}")
            self._deassert_and_assert(clear_name, gate_name)

            def _hop_two():
                self._toggles[second_tog].set_now(value, note=f"cleared/set by {gate_name}")
                self._deassert(gate_name)
                self.supertoggle.set_now(value, note=f"flipped by {gate_name} termination")
                on_done()

            self.engine.schedule(FEEDBACK_HOP_DELAY_US, _hop_two)

        self.engine.schedule(hop1_delay, _hop_one)

    def _assert_line(self, name):
        self.active_line.set_now(name, note="asserted")

    def _deassert(self, name):
        assert self.active_line.value == name, (
            f"expected {name!r} active, found {self.active_line.value!r}"
        )
        self.active_line.set_now(None, note=f"{name} terminated")

    def _deassert_and_assert(self, old, new):
        self._deassert(old)
        self._assert_line(new)
