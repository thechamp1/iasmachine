# Audit findings: previous instance's code against the documentation

Code audited as committed unmodified on `main` (commits `c16ae18`, `1f7b7d9`),
under `Other instance's python files/`. Checked against
`docs/AUDIT_CHECKLIST.md`; IDs below refer to it. All 74 delivered tests pass
as shipped. Findings are ordered by how much they matter for a gate-by-gate
model; each has a reproduction where one was run.

Files are referenced as `primitives/`, `units/` and `au/` for the three
directories `Simulation primitives`, `register-adder-complement gates-shift
counter` and `Other instance's arithmetic unit`.

---

## 1. DIFF: sign is lost from the 2⁺¹ stage after every addition, so any right shift of a negative number is wrong (R7, R11, H2, H3)

`au/arithmetic_unit.py` `_execute()` and `record()` run the four-gate round
trip but never copy the sign back into position 40 (2⁺¹) after the final Black
gate. Only `shift_right()` does that copy (line "sign retention"). The report
says that after an addition "the sign of the sum is now both in 2⁺¹ and 2⁰"
(p. 25) and that a right shift copies 2⁺¹ into 2⁰ and retains it (p. 27).
`register.py` `HalfRegister.load()` also forces position 40 to 0.

Reproduction:

```
load_ri(-8); shift_right(1)            -> 549755813884   (expected -4)
load_ri(0); load_riii(-8); add(); shift_right(1)
                                       -> 549755813884   (expected -4)
```

Every delivered shift test uses a positive value, which is why this passed.
Multiplication and division happen not to depend on it (multiply clears R₁ and
keeps 2⁺¹ = 0 by construction; divide only shifts left).

## 2. DIFF: multiplication runs three chain cycles per step instead of one (M2, S1, R4)

`multiply()` calls `record()` for the add, which is the two-cycle addition
sequence (Record + ShiftDownLeft, then ShiftUp + ShiftDownRight), and then
`shift_right(1)` as a third cycle. The report's multiplication step is a single
cycle: first half Record (multiplier digit 1) or Shift-up (digit 0), second
half Shift-down-right (p. 24–25, p. 141–142). When the multiplier digit is 0
the code still goes through the Adder path (Record with a zero addend); the
machine takes the direct Yellow path.

Measured: 117 to 121 chain cycles and 1228 to 1280 µs per multiplication.
Documented: 40 cycles (recognition number 40, p. 171).

## 3. DIFF: division runs two or three Records per step, all untimed shifts, and never uses the Reject path (D5, D6, S1, R12)

`divide()` for each of 38 iterations: shifts R₁ left by direct register calls
(no chain, no time), then `record()` (2 cycles) for the trial, and if the trial
fails another `record()` (2 cycles) to undo it. The machine's step is one
cycle: the Adder output (trial) is examined combinationally, the
Accept-Reject Selector chooses Record or Shift-up for the first half, and the
second half is Shift-down-left (p. 73, p. 141–142). Nothing is ever undone.
RII's quotient shifts are also applied directly without the chain.

Measured: 80 to 150 chain cycles and 1020 to 1913 µs per division.
Documented: 39 cycles (p. 171).

## 4. DIFF: division leaves r₃₉ in R₁; the machine leaves 2r₃₉ (D5, X7)

Because the code shifts left before each trial and stops after the last trial,
R₁ ends holding r₃₉. In the machine each cycle is trial then shift-down-left,
so after 39 cycles R₁ holds 2r₃₉, which is exactly the "2R, twice the
remainder" of order 0.11 with R = r₃₉. The `divide()` docstring records this
as an unresolved question about the source's terminology; the cycle structure
resolves it. The delivered tests assert `R == r39_ref`, encoding the deviation.

Reproduction: for X = −2³⁶, Y = 2³⁸ the final R₁ equals r₃₉ and not 2r₃₉.

The remainder identity to test after the fix: x = Q·y + 2⁻³⁹·R₁ with
Q = Σᵢ₌₀³⁸ 2⁻ⁱqᵢ (positive-quotient case), R₁ read with its 2⁺¹ sign.

## 5. DIFF: RII's 2⁰ digit after multiplication is 0, not 1 − b₀ (M6)

`_flush_rii_one_position()` performs the extra RII shift the end state needs,
but the vacated 2⁰ position stays at the Yellow-clear 0. Order 0.9 e) gives
R₂ = (1 − b₀), c₄₀, …, c₇₈. The test helper `combined_signed_result()` masks
that bit out, so the tests cannot see it. Figure 10's "special gate from 2⁰
column of R³ for multiplication" is the hardware for it.

## 6. DIFF: multiplication recognition number is 39, not 40 (S8, M2)

`multiply()` calls `shift_counter.start(39)`. The report gives 40 for
multiplication and 39 for division (p. 171). The shift counter is also never
consulted to stop anything: it is stepped by the Python loop and its
`done` flag is unused, so this is currently cosmetic.

## 7. DIFF: terminal multiplication corrections are separate two-cycle Records, and the RII flush is untimed (M4, M5, M8)

After the 39 steps the code does: untimed RII shift; if multiplier negative,
`record()` of −y (2 cycles); if multiplicand negative, `record()` of
1 + 2⁻³⁹ (2 cycles). The machine has one 40th cycle. Both corrections fit in
one Record (complement of y plus 2⁻³⁹ injection plus a 1 at 2⁰), and the
multiplier sign is what the observation post sees at stage 39 after 39 shifts.
How R₁ stays aligned during that cycle is not in the documentation (checklist
M8); the code's untimed flush is an unlabelled stand-in for that assumption.

## 8. DIFF: the 2⁺¹ column of Rᴵ is fed from the Adder carry-out, not from the lower 2⁺¹ toggle (N2, R7)

`register.py` `apply_green_gate()` stores the Adder's carry out of the 2⁰
stage in position 40. The report says that carry is lost (p. 14) and Figure 10
shows the Green gate of the extra column transmitting from the lower 2⁺¹
toggle up to the upper one. In the delivered code the caught carry is always
dropped by the following Red gate or is 0, so this has no numeric effect
today, but it is the wrong wiring and would mislead a future division model
that tries to use σ₋₁ (p. 31).

## 9. SIMPLIFIED: the shift counter and the chain's Counter Stop feedback (S5, S6, S9)

`shift_counter.py` is an integer counter with no True/False ranks, no
Fig. 30 state table, no wrap at 48, and no Counter Stop output. The chain is
started one cycle at a time from Python (`start_cycle`) rather than
free-running until coincidence. Timing-equivalent for now because the
combinational delay is modelled as 0, but the control loop of Fig. VI (chain
→ RI step → counter → recognition → stop) does not exist as signals.

## 10. SIMPLIFIED: end-around and left-shift zero fill are post-hoc register pokes (R8, R9)

`shift_right()` and `shift_left()` run the chain, then directly overwrite
`rii_lower.digits[39]`, `r_lower.digits[40]`, `r_lower.digits[0]` and
`rii_lower.digits[0]` after `run_all()`. Values are right; they are not
gate events and carry no time. Acceptable as a placeholder, but the audit
trail (the event log) does not show them.

## 11. NOTE: the Record half-cycle keeps Red Clear asserted for the whole 15 µs (N8, S2)

`sequencing_chain.py` models the Carry Delay as the first hop of the Record
half: Red Clear asserted at t = 0, chassis-5 toggle and Green Gate at 15 µs.
The April 1954 text only says the Green gate occurs about 15 µs after the add
is initiated. Whether the clear itself lasts 15 µs or terminates at 1.5 µs
with the gate command held off is not documented. Elapsed time is right either
way; flagged as an assumption, which the module's docstring already does.

## 12. NOTE: comment claims a source inconsistency that is not one

`multiply()`'s docstring says the source's "y¹ = y − 1" and "xy¹ = x(y + 1)"
are inconsistent. They are not: y¹ = y − 1 describes the bit pattern (sign
digit removed), which for negative y "acts as if it were (y − 1) + 2" = y + 1,
exactly as the report says for x on p. 19. The implemented y + 1 is correct.

## 13. OK: items that match the documentation

- Adder truth table, ripple carry, carry-in for the complement correction
  (N4, N5). `test_adder.py` checks the table row by row against p. 76.
- Complement Gates three modes and the absolute-value monitor (N5, N6).
- Two-row RI/RII with Red/Black/Yellow/Green semantics, transmit-0s /
  transmit-1s with the required preclears, and the addition round trip
  Green → Red → Yellow → Black (R1, R3, R4, R5, R11 apart from finding 1).
- Chain toggle order per branch and supertoggle sequence, 1.5 µs hops
  (S1, S2): matches the tube-table trace on pp. 146–152 exactly.
- Additive orders take 2 cycles and 25.5 µs (A2, N8).
- Right shift end-around Rᴵ 2⁻³⁹ → R₂ 2⁰; left shift 2⁰ → R₂ 2⁻³⁹, R₁ 2⁻³⁹
  made 0 (R8, R9), by value.
- RII shifts only when enabled (R10), via the `_rii_shifts_too` flag.
- Multiplication arithmetic for all four sign cases, by value against Python
  integers (M3, M4, M5 as arithmetic).
- Division recursion, quotient digit insertion at position 38 and left
  shifting, the sign digit reaching position 0, the forced final 1, and the
  accept/reject decision, by value (D2, D3, D6, D7).

## 14. NOT BUILT (as the workflow note says)

RIII as two registers R³ / R₃ (R2); Load R₂ path (O11); round-off multiply
(M7); the hold variant of multiply (M1); shift orders as orders (H1);
Order Interpreter, three-stage counter, Order Register, Memory, Dispatch
Counter, Local Control (all O and W items).

---

## Correction order proposed

1. Finding 1 (sign in 2⁺¹) and finding 8 (wiring of the extra column). Small,
   foundational, and they change what every later fix is built on.
2. Findings 2, 6, 7: restructure `multiply()` as 40 single-cycle steps
   through the chain, with the Accept/Reject choice made from the multiplier
   digit, the terminal cycle carrying both corrections and the (1 − b₀)
   insertion, and the M8 assumption written down in one place.
3. Findings 3, 4: restructure `divide()` as 39 single-cycle steps, trial
   observed on the Adder output, Accept or Reject chosen before the first
   half, Shift-down-left second half; final R₁ = 2r₃₉. Update the tests to
   the documented end state.
4. Finding 9: make the shift counter a signal-producing unit that stops the
   free-running chain (needed before Main Control exists).
5. Finding 10: turn the end-around and zero-fill into gate actions inside
   the chain's Black/Red gate events.
