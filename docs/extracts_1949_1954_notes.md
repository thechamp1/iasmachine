# Notes on the two PDF extracts (read from the page images)

Both files are scans. `1949reportextract.pdf` has no text layer;
`1954reportextract.pdf` has a rough OCR layer. Everything below was read
from the rendered pages, not from the OCR.

## docs/1949reportextract.pdf — Fifth Interim Progress Report, 1 January 1949

Bigelow, Goldstine, Melville, Panagos, Pomerene, Rosenberg, Rubinoff, Ware.
IAS ECP list of reports no. 12. Covers 1 July to 31 December 1948. The extract
is the title page, table of contents, preface and Chapter II "The Arithmetic
Organ" (printed pp. 26–32). Figure 2.1 (the two-stage adder circuit) is
referred to but is not in the extract; Figures 2.2.a and 2.2.b (register
loop test arrangements) are.

Relevant content:

- **Adder structure (pp. 27–29).** 40 identical stages, three inputs
  (resident digit from the accumulator, incident digit from the memory
  register through the complement gates, carry from the preceding stage) and
  two outputs (carry, sum digit). "Kirchoff" type: the carry from the
  previous stage enters as a unit of voltage, the resident and incident
  digits as units of current (5 ma each through a 10.5 k summing resistor);
  the summing point takes one of four levels 50 v apart. The carry gate (4.r)
  conducts iff at least two of the three inputs are 1; its plate drives the
  "In" carry cathode follower of the next stage. The digit resolver decides
  odd or even and "is then fed into one half of the augend register
  displacing what was there". A 27 µµf condenser bypasses the 22 k isolating
  resistor "to speed up the propagation of a carry". Complement gates and
  digit resolver were not complete as of 1 January 1949.
- **Adder timing (p. 30).** First operational tests "showed a carry
  propagation time of about 6 µs and a carry collapse time of about 5 µs.
  Furthermore the time to set the gates for an incident or resident digit is
  about 1 µs." Life test: resident all ones, incident all zeros with a 1 in
  the last digit, carry rippling through all 40 stages, ≥ 8 hours at about
  120 kc, no errors.
- **Register timing (pp. 31–32).** "A shift consists of two distinct
  operations: gating the information in one half of a register into the
  other half and then gating it back again shifted by one place right or
  left. Each of these operations can safely be performed in 1.5 µs and one
  can succeed the other with no spacing; thus a complete shift by one place
  can be safely performed in 3 µs." Three registers were looped into 120
  digits and run for about 10¹¹ shifts.

Bearing on the audit: the 6 µs carry propagation is the physical quantity
the Carry Delay Unit (≈15 µs to Green Gate) is sized against, so the 15 µs
is an engineered margin, not the ripple time itself. The 1.5 µs per register
operation is a 1949 measurement of the registers alone; the 1954 chain trace
gives ≈1.5 µs per clear termination and ≈1.5 µs per gate disable, i.e. about
3 µs per half cycle including the chain's own feedback. The two are
consistent and not the same quantity.

## docs/1954reportextract.pdf — Final Report on Contract DA-36-034-ORD-1023 (April 1954)

Extract: preface, table of contents, figures list, page I-1, and Appendix
pages I-57 to I-60. Covers 1 July 1952 to 30 June 1953. The table of
contents shows Part I (engineering) contains only IBM/drum input-output,
IBM and drum control, CRT testing and maintenance. There is no section on
the arithmetic unit; the introduction refers to the January 1954 Final
Report for the machine's description. Pages I-28 to I-35 of this report are
already transcribed in `apr 1954 report_pages_39-46/`.

### Appendix: Arithmetic Test Code (pp. I-57 to I-59), transcribed

> The arithmetic test code is intended to test for correct execution of the
> major machine orders. It is essentially a series of sub-routines, one for
> each order. Within each sub-routine standard operands are used by the order
> concerned and the result checked against a stored correct answer. In almost
> every case, two sets of operands are used: one to present maximum digit
> loads to the gate drivers concerned and one to present minimum loads. From
> a gate loading standpoint all numbers which may be handled by the order in
> question lie between these extremes.
>
> If a given subroutine elicits an error, a card (12 words) is punched out
> identifying the type of error and the order concerned as well as all
> quantities entering into the computation. Note that an operand can be
> correctly stored in the memory but transferred incorrectly into the
> arithmetic unit. Therefore the operands are first positioned in the
> arithmetic unit (e.g. the multiplier is transferred from the memory into
> R₂ in the multiplication cases) then are temporarily stored from this
> position (by the two orders R₂ → R₁, store for R₂ quantities such as the
> multiplier). It is these temporarily stored images of the operands which
> are provided at the error punch out.
>
> The sequence in which processes are tested involves some important
> considerations. The machine can detect its own errors only by using
> processes which may themselves be in error. The comparison of the computed
> value with the stored correct answer necessarily involves a subtraction;
> and the discrimination on the zero or non-zero error must be made by a
> conditional transfer of control. Therefore the transfer control orders are
> checked first. If these are correct, it is then possible to check the
> summation orders. If both are correct, then the other orders can be
> tested.

Arithmetic Test Sequence:

| | Test | Remarks |
|---|---|---|
| 1 | Total Sum of Memory = 0 | Memory contents check. |
| 2 | Transfer control | Tests all cases of conditional and unconditional transfers of control. |
| 3 | Summation (Digit) | Considering any stage of the adder, tests the 8 combinations of the two input digits and the carry. |
| 4 | Summation (Sign) | Tests the complement gate selector in the 8 combinations of the sign of the incoming number and the magnitude and +/− digits of the order. |
| 5 | R₂ to R₁ | Tests R₂ → R³ gating under minimum and maximum digit loads. (R³ → R₁ transfer has already been tested by 4). |
| 6 | 1 Shift Right, 2 Shift Left, 4 Shift Right, 8 Shift Left, 16 Shift Right, 32 Shift Left | Tests individual digits of the shift counting channel. |
| 7 | 31 Shift Right | Maximum digit load on shift count. |
| 8 | Gate loads | Tests all RI and RII gates under minimum and maximum digit loads. |
| 9 | Multiplication | Tests 8 combinations of sign of multiplier, sign of multiplicand, and Roundoff–No Roundoff. |
| 10 | Multiplication | Tests special case of small negative product which rounds to zero. |
| 11 | Multiplication | Alternating Accept-Reject (i.e. multiplier alternates zeros and ones). Supplements 9. |
| 12 | Division | Tests 4 combinations of sign of numerator and sign of denominator. |

(The Read Around Test Code on pp. I-59 to I-60 concerns memory spill and is
not transcribed.)

Bearing on the audit:

- Test 5 confirms that the R₂ → R₁ order works by an R₂ → R³ transfer
  followed by the R³ → R₁ path of the summation orders (checklist A3, H1).
- Test 10 is an oracle for round-off (M7): a small negative product, for
  example −2⁻⁴⁵, must give R₁ = 0 after round-off. That only happens if the
  2⁻⁴⁰ digit is added to the full 79-digit product with the carry
  propagating into R₁; truncating first would leave −2⁻³⁹.
- Test 11 uses the report's own words "Accept-Reject" for the multiplication
  step chosen by each multiplier digit, supporting checklist S3 and audit
  finding 2 (a 0 digit takes the Reject path, not the Adder path with a zero
  addend).
- Tests 3, 4, 6, 7, 9, 10, 11 and 12 can all be reproduced in the simulation
  test suite once the orders exist.
- Nothing in either extract describes the terminal multiplication cycle
  (checklist M8). Drawings B-1450, A-1446 and A-1486 remain the only cited
  sources for it.
