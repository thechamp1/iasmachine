# IAS machine simulation: audit checklist derived from the documentation

Built from a complete read of `docs/iasreport/iasfinalreport.md` (text and all
62 page images) and `docs/apr 1954 report_pages_39-46/report_pages_39-46.md`,
before looking at any code. Every item cites where it comes from. Page numbers
written `p. NN` are the `<!-- p. NN -->` markers in the markdown (physical PDF
pages). Figure page numbers in the images are printed numbers (PDF page − 14);
text recovered from figure pages is in
`docs/iasreport/figure_page_text_supplement.md`.

Each item is something the simulation must get right, or an ambiguity that
the code must have resolved by assumption. Status columns are for the audit.

Legend for status: `?` not yet checked · `OK` matches · `DIFF` deviates ·
`ASSUMED` documentation underdetermines it, code's choice must be documented.

---

## N. Number representation and the adder

| ID | Requirement | Source | Status |
|---|---|---|---|
| N1 | Word = 40 binary digits; digit 0 is the sign, digits 1..39 have weights 2⁻¹..2⁻³⁹. Binary point immediately after the sign. | p. 13–14 | OK |
| N2 | The Adder treats the sign as a digit of weight 2⁰. All 40 stages add and carry identically; a carry out of the 2⁰ stage is lost (arithmetic modulo 2). Exception noted for division (see D-items). | p. 14 | DIFF (finding 8) |
| N3 | Numbers satisfy −1 ≤ x < 1. Negative x is represented by x + 2 (two's complement of the 40-digit pattern). Sign 1 = negative. | p. 14–15 | OK |
| N4 | Adder inputs: Resident digit from R₁ (lower RI), Incident digit from R³ via the Complement Gates. Output per stage is one of four levels (sum 0/1, carry 0/1); the Digit Resolver reduces it to sum 0/1. Sum and carry per the 8-case table. | p. 74–79 | OK |
| N5 | Complement Gates let one of three things into the Adder from R³: x, its one's complement, or 0. For the complement case Arithmetic Control also injects a 2⁻³⁹ carry ("complement correction"), giving x − y exactly. | p. 17, Fig. I.2 | OK |
| N6 | Absolute-value variants: a "monitor" decides from the sign of the number in R³ whether the number or its complement is passed. Digit 4 (#/Abs) and digit 5 (+/−) affect only the Complement Gate setting, not order timing. | p. 26, p. 180 | OK |
| N7 | Digit Resolver drives the RI Green gates. Green gates transmit 0s only, so Rᴵ (upper RI) must be Red-cleared to 1s before the Green gate opens. | p. 60, p. 81, p. 140 | OK |
| N8 | Carry Delay: the Green gate (recording the sum) occurs about 15 µs after the add is initiated, because of the imposed Carry Delay (chassis "Del", Dwg. A-1455). This is the one timing figure taken from the April 1954 report. | Apr. 1954 p. I-31; chassis list | OK |

## R. Registers, gates and shifting

| ID | Requirement | Source | Status |
|---|---|---|---|
| R1 | RI and RII are each two rows of 40 toggles: upper Rᴵ / Rᴵᴵ (transient) and lower R₁ / R₂ (storage). All storage longer than a few µs is in the lower row. | p. 21–22, p. 59–60 | OK |
| R2 | RIII is not a shifting register. It holds two independent 40-digit registers: R³ (number register, feeds the Adder through the Complement Gates and feeds the RII Green gates) and R₃ (order-word register, feeds the Order Interpreter, the address gates G.1–G.4 and the Recognition Circuit). Memory reads are steered into R³ or R₃ by the WO signal. Orders 0.15–0.17 list different end contents for R³ and R₃, so the simulation must model both. | p. 62–65, p. 123, p. 41–42, Figs. V, VI | NOT BUILT |
| R3 | Gate colours and clears (archetype register): Red = shift down LEFT (top row i → bottom row i−1), transmits 0s; clears top to 1. Black = shift down RIGHT (top i → bottom i+1), transmits 1s; clears top to 0. Yellow = shift up, transmits 1s; clears bottom to 0. Green = shift up (in RI/RII actually "in from outside"), transmits 0s; clears bottom to 1. | p. 60–62, Fig. 8 | OK |
| R4 | Half-cycle vocabulary: Record (Accept) = Red clear, Green gate. Shift up (Reject) = Black clear, Yellow gate. Shift down left = Green clear, Red gate. Shift down right = Yellow clear, Black gate. A "cycle" = clear, gate, clear, gate: first half is Record or Shift-up, second half is Shift-down-left or Shift-down-right. | p. 141–142 | OK |
| R5 | Right shift of one = Black clear, Yellow gate, Yellow clear, Black gate. Left shift of one = Black clear, Yellow gate, Green clear, Red gate. | p. 62 | OK |
| R6 | In RI the Green gates bring the Digit Resolver output into Rᴵ. In RII the Green gates bring R³ into R₂ (used by Load R₂ and by the R₂→R³ path's inverse). | p. 65, Fig. XI | NOT BUILT |
| R7 | RI has an extra 2⁺¹ column (chassis "2¹R¹", Dwg. A-1446). On a left shift the 2⁰ digit moves into 2⁺¹ and is held. On a right shift 2⁺¹ is copied into 2⁰ AND retained in 2⁺¹ (sign propagation). | p. 23, p. 26–27, p. 66–68, Fig. 10 | DIFF (finding 1) |
| R8 | End-around on right shifts: the 2⁻³⁹ digit of Rᴵ (upper) is delivered by the Black gate into 2⁰ of R₂; R₂'s 2⁰ must have been cleared to 0 first. RII's own 2⁻³⁹ is lost. | p. 24–25, p. 27, p. 69, Fig. 11 | OK |
| R9 | Left shift: 2⁰ of RI goes into 2⁻³⁹ of RII (RI → RII only). The right-most stage of R₁ is made 0 (so left shift = exactly ×2 while in range). This RI→RII channel is suppressed during division. | p. 24, p. 26, p. 30, Fig. I.6 | OK |
| R10 | RII shifts only when Control enables it: RII's Yellow-gate driver T₄ is driven by a Yes/No signal (+10 = No, −10 = Yes). RI and RII shift together in shift orders and multiplication, except in one terminal step of multiplication. | p. 27, Fig. 13 note | OK |
| R11 | Addition data path (2 cycles): Green (sum → Rᴵ, aligned), Red (→ R₁ shifted left, sign into 2⁺¹), Yellow (→ Rᴵ), Black (→ R₁ shifted right, aligned). The sum's sign ends in both 2⁺¹ and 2⁰. | p. 22–23, p. 25 | DIFF (finding 1) |
| R12 | The Accept/Reject choice (Adder path vs direct Yellow path) for every order is made by the Accept-Reject Selector (Dwg. O-1463); the Left/Right choice of the second half cycle by the LR chassis, which also selects Yellow vs Green clear of R₁. | p. 71–73, Fig. 12 | DIFF (finding 3: no Reject path in division) |
| R13 | The R₁ Clear Selector receives "↓ at sync" and "C/H" from Main Control: the pre-clear of R₁ to 0 for "clear" orders happens at the sync (Up) time, before the Memory phase completes. | Fig. 12 labels; Fig. XII digit 8 | NOT BUILT |
| R14 | Physical clear: a clear bus must stay below +70 v for ≈1 µs. Super-toggles switch in half the ordinary toggle time. | p. 54 | NOT BUILT |

## S. Gate-Clear Sequencing Chain and Shift Counter (arithmetic timing)

| ID | Requirement | Source | Status |
|---|---|---|---|
| S1 | The chain is self-perpetuating: each clear is fed back and terminates itself while enabling the next gate; each gate is fed back, terminates itself, and enables the next clear. Order within a cycle: (Red or Black clear) → (Green or Yellow gate) → (Yellow or Green clear) → (Black or Red gate). | p. 142–152 | OK |
| S2 | Lags: ≈1.5 µs between initiation and termination of a clear; a gate is disabled ≈1.5 µs after it is enabled. So a half cycle ≈ 3 µs and a plain shift cycle ≈ 6 µs; a Record half-cycle additionally waits the Carry Delay (N8). | p. 148, p. 150 | OK |
| S3 | Red vs Black clear at the start of a cycle is decided by the content of 2⁻³⁹R₂ (multiplier digit) in multiplication; Yellow vs Green clear at the second half by the "multiply/divide" toggle (right vs left shift). | p. 147, p. 151 | DIFF (finding 2: digit 0 still takes Adder path) |
| S4 | The chain is armed (set up) by the order digits (III.α) and started by the M→R³ Gate (Williams orders) or the R₂→R³ Gate (non-Williams orders), after a delay equal to the M→R³ Gate duration. | p. 171, p. 173, Fig. III, Fig. VI | NOT BUILT |
| S5 | Counter Stop signal: +10 v while the Shift Counter differs from the "number to be recognized"; falls to −27 v at coincidence. −27 v holds the chain quiescent; the chain runs while it is +10 v. | p. 138–140, p. 142–146 | SIMPLIFIED (finding 9) |
| S6 | Shift Counter: scaling type, six stages (2⁰..2⁵), two ranks True and False. Prepared by clearing T to 000000 and F to 01111 (2⁰ = 0, others 1). Counts once per RI cycle (input is a pair of pulses E₀′ then E₀″ per item). The 2⁵ stage is simplified: the counter reads 1..47 correctly and returns to 32 on the 48th count. Fig. 30 gives the full T and F contents for counts 0..40. | p. 127–136, Fig. 29, Fig. 30 | SIMPLIFIED (finding 9) |
| S7 | The Shift Counter is cleared to zero by the memory Sync signal every time the Memory is used. | Apr. 1954 p. I-31 | NOT BUILT |
| S8 | Recognition Circuit compares the T rank with a 6-digit number: for Williams orders it is implicit (2 for additive orders, 40 for multiplication, 39 for division), impressed by not-Up; for non-Williams orders it is the low six address digits (4–9 or 24–29) of the order read out of R₃. | p. 136–140, p. 171, p. 173 | DIFF (finding 6) |
| S9 | Coincidence stops the chain, resets T_Y/O and advances the three-stage counter (completion signal III.C). | p. 171, Fig. VI | SIMPLIFIED (finding 9) |

## A. Additive orders (0.1–0.8, 0.19, 0.23)

| ID | Requirement | Source | Status |
|---|---|---|---|
| A1 | Orders 1–8: operand from memory to R³; R₁ ← (0 or a) ± (b or |b|). End: R₁ result, R₂ unchanged, R³ = b, memory unchanged. Clear variants pre-clear R₁ to 0. Minus-clear gives 2 − b (i.e. −b mod 2). | p. 32–37 | OK |
| A2 | Additive orders take 2 chain cycles (recognition number 2): cycle 1 = Record + shift down left; cycle 2 = Shift up + shift down right. | p. 25, p. 171 | OK |
| A3 | 0.23 R₂→R₁ (8 variants, shift count n from digits 4–9, 1 ≤ n ≤ 47): R₂ is first transferred to R³ (all non-Williams orders do this), then the chain runs n cycles alternating Accept+left / Reject+right. End: R₁ = 2g(a) + (n+1)f(b) for n odd, g(a) + n·f(b)/2 for n even; R₂ = b; R³ = b. This formula is an oracle for the alternation in A2. | p. 46–47, p. 173 | NOT BUILT |
| A4 | 0.19 Quick Sum: first phase only, digit 19 = 1, step digit 1; performs the chosen order 1–8 at x, then x+1, ..., 1023; the second-phase order must be a transfer because the order counter no longer holds the next location. End R₁ = b₁₀₂₃ (clear variants) or a + Σ f(b) (hold variants); R³ = b₁₀₂₃. | p. 43–44 | NOT BUILT |
| A5 | Step digit (digit 10/30) = 0 stops the machine after the order is executed; if it is then changed to 1 the order is re-done and the machine proceeds. Store orders and Quick Sum require step = 1. | p. 32, p. 40, p. 43 | NOT BUILT |

## M. Multiplication (0.9, 0.10)

| ID | Requirement | Source | Status |
|---|---|---|---|
| M1 | Multiplier a is in R₂ beforehand (loaded by 0.12). Multiplicand b comes from memory to R³. R₁ is pre-cleared to 0 if the clear digit is 1; otherwise the initial R₁ content c is added into the first partial product, giving ab + 2⁻³⁹·c (text prints "d"). | p. 17, p. 24, p. 37 | PARTIAL (clear variant only) |
| M2 | Recognition number is 40 (40 chain cycles). A multiplication step is one cycle: Record (add) if 2⁻³⁹R₂ = 1 else Shift-up, followed by shift down RIGHT; RI and RII shift right together; the 2⁻³⁹ digit of Rᴵ enters 2⁰ of R₂. The digit of the multiplier just examined is lost. 39 such steps consume digits a₃₉ … a₁. | p. 24–25, p. 141, p. 171 | DIFF (finding 2) |
| M3 | Both positive: 2pᵢ = pᵢ₋₁ + (a₄₀₋ᵢ ? b : 0), pᵢ = 2pᵢ/2 with the sign digit made 0. 0 ≤ 2pᵢ < 2 always, no carry beyond 2⁰. p₃₉ = ab. | p. 18 | OK |
| M4 | Multiplicand negative (b₀ = 1): during the 39 steps use b¹ = b with its sign digit replaced by 0; when the multiplier digit is 0 add the number 1 (a 2⁰ digit) instead of 0. After 39 steps the result is ab + 1 − 2⁻³⁹; the final correction is +1 + 2⁻³⁹ (mod 2). | p. 19–20 | OK (value) |
| M5 | Multiplier negative (a₀ = 1): ignore the sign digit during the 39 steps (result ab + b), then one more step subtracts b. The sign digit a₀ reaches the observation post (stage 39 of R₂) exactly after the 39 right shifts, so the 40th cycle can examine it. | p. 19, p. 24–25 | OK (value) |
| M6 | End state, no round-off, clear case: R₁ = c₀..c₃₉; R₂ = (1 − b₀), c₄₀, …, c₇₈ where ab = c₀…c₇₈ (79 digits) and b₀ is the multiplicand sign; R³ = b. Hence R₂ has been shifted 40 times and its 2⁰ receives the complement of the multiplicand sign on the last shift (Fig. 10 shows a "special gate from 2⁰ column of R³ for multiplication" on the Black-gate path), while R₁ ends aligned after net 39 right shifts. | p. 38, Fig. 10 | DIFF (finding 5) |
| M7 | Round-off (0.10): a 1 is added at 2⁻⁴⁰ to the 79-digit product after all carries, then R₁ keeps 39 digits. End: R₁ = γ₀..γ₃₉, R₂ = (1 − b₀), (c₄₀ + 1), c₄₁, …, c₇₈ with the whole 79-digit number increased by 2⁻⁴⁰ (carry into R₁ when c₄₀ = 1). | p. 30, p. 38 | NOT BUILT |
| M8 | ASSUMED: the text does not say how the 40th (terminal) cycle leaves R₁ un-shifted while R₂ shifts (p. 27 only says one terminal step is an exception to "RI and RII shift together"). Chassis UnX ("end correction for multiplication"), X1-2 ("multiplication control"), Dwg. B-1450 ("Multiplication Terminate") and A-1486 ("Multiplication Variants") hold the answer and are not in the docs. Whatever the code does here is an assumption; it must reproduce M6/M7 and the 40-count. | p. 27, chassis list, drawings list | ASSUMED, untimed (finding 7) |

## D. Division (0.11)

| ID | Requirement | Source | Status |
|---|---|---|---|
| D1 | Dividend x = N in R₁, divisor y = D from memory to R³, with |x| < |y|. Recognition number 39. | p. 27, p. 38–39, p. 171 | DIFF (finding 3: cycle count) |
| D2 | Recursion: r₀ = x/2; rᵢ = 2rᵢ₋₁ − (sgn xy)·y·pᵢ₋₁, where pᵢ₋₁ = 1 if sgn x = sgn(2rᵢ₋₁ − (sgn xy)·y) (accept the trial), else 0 (reject, rᵢ = 2rᵢ₋₁). Remainder keeps the sign of x and |rᵢ| < |y|. p₀ = 0 follows automatically since |x| < |y| (step 1 is always a reject). | p. 27–29, p. 31 | OK |
| D3 | Trial operand: subtract y if x and y have the same sign, add y if they differ (the Complement Gates pass y or its complement accordingly; note the ÷ order code has digits 4 and 5 both 1). | p. 27–28, order table | OK |
| D4 | Accept/reject decision is made on the 2⁺¹ digit σ₋₁ (sign of s regarded as a 41-digit number s = σ₋₁ + σ₀/2 + …): accept when σ₋₁ = (1 − sgn x)/2, i.e. the sign of the trial result equals the sign of x. This is why the carry out of 2⁰ is not simply lost in division. | p. 14, p. 31 | OK (value; σ₀ used, see finding 8) |
| D5 | Data path per step: R₁ holds 2rᵢ₋₁ at the start of each cycle (r₀ = x/2 so R₁ starts as x). Record (trial ± y, aligned) or Shift-up, then shift down LEFT (doubling). After 39 cycles R₁ = 2r₃₉, which is what 0.11 calls "2R, twice the remainder". Identity to test: x = Q·y + 2⁻³⁸·r₃₉ (sgn xy = +1). | p. 29–30, p. 39 | DIFF (findings 3, 4) |
| D6 | Quotient digits qᵢ = pᵢ if sgn xy = +1, else 1 − pᵢ. Each qᵢ is inserted into position 38 of R₂ and R₂ is shifted left; the normal RI→RII left-shift channel is suppressed. The operation continues until the sign digit q₀ reaches position 0 of R₂. Position 39 is automatically made 1. End: R₂ = q₀, q₁, …, q₃₈, 1; R³ = D. | p. 30, p. 39 | OK |
| D7 | For sgn xy = −1 the quotient is 2 − P − 2⁻³⁸, i.e. the complement of P "wrong in the last place"; the forced final 1 is the adopted rounding. 39 steps determine the sign and 38 information digits. | p. 29–30 | OK |

## H. Shift orders (0.20–0.22)

| ID | Requirement | Source | Status |
|---|---|---|---|
| H1 | Count n from digits 4–9 (24–29), 1 ≤ n ≤ 47; n = 0 executes as 1. Digits 0–3 irrelevant. These are non-Williams orders: R₂ → R³ transfer first, chain started by the R₂→R³ Gate, count taken from the address digits. | p. 44, p. 173 | NOT BUILT |
| H2 | Right shift by 1 (clear digit 0): R₁ = a₀, a₀, a₁, …, a₃₈; R₂ = a₃₉, b₀, …, b₃₈; R³ = b₀…b₃₉. Iterated n times. | p. 44 | DIFF (finding 1) |
| H3 | Right shift with clear digit 1: R₁ = a₀, 0, …, 0; R₂ = 0, b₀, …, b₃₈. The sign still propagates from 2⁺¹ although R₁ was cleared. | p. 45 | DIFF (finding 1) |
| H4 | Left shift by 1 (clear 0): R₂ = b₁, …, b₃₉, a₀; R₃ = b₀…b₃₉; R₁ = a₁, …, a₃₉ followed by — see X3 (text says the 2⁻³⁹ stage is made 0; the order listing prints a₀). Iterated n times. With clear digit 1: R₁ = 0…0, R₂ = b₁…b₃₉, 0. | p. 26, p. 45–46 | OK |
| H5 | Left 1 then right 1: R₁ = a₀…a₃₉ (recovered via 2⁺¹); R₂ = 0, b₁, …, b₃₉; R³ = b₁, …, b₃₉, a₀. Confirms the 2⁻³⁹ of R₁ after a left shift is 0 and that R₂ → R³ happens at the start of each non-Williams order. | p. 46 | OK |
| H6 | 0.21 Right shift round-off "is not yet available" (should not be implemented as functional). | p. 45 | NOT BUILT |

## O. Order format, decoding and the Control

| ID | Requirement | Source | Status |
|---|---|---|---|
| O1 | Order word = two 20-digit orders; left (digits 0–19) executed first, then right (20–39). Digits 0–9 (20–29) address, 10–19 (30–39) operation. | p. 32 | NOT BUILT |
| O2 | Operation digits (order table): d0 step; d1 ext/int; d2 arith(non-Wms)/Wms; d3 AT/NAT; d4 #/abs; d5 +R/−L; d6 ×÷/Σ; d7 no-RO/RO; d8 hold/clear; d9 spare (=1 only for Quick Sum). Full bit patterns for orders 1–29 are in the supplement. | order table image (printed p. 41) | NOT BUILT |
| O3 | Decode tree (Fig. XII), in time order: d1 → d2 → (d8 preclear R₁ → 0) → d3 → d6 → d5 → d7. Non-Wms: d6=0 shift (d5 right/left, d7 RO), d6=1 R₂→R₁. Wms AT: d6=0 transfer (d5 unconditional/conditional), d6=1 store. Wms NAT: d6=0 (d5=0 ×, d7 RO; d5=1 ÷), d6=1 (d7=0 Σ orders 1–8, d7=1 Load R₂). | Fig. XII | NOT BUILT |
| O4 | Digit 2 = 0 (orders 20–23) selects the Non-Williams Control: "yes Arithmetic" → R₂→R³ Gate (via toggles TT₁, TT₂ whose reaction times set the clear/gate durations). Digit 3 = 0 (orders 13–18) means arithmetically trivial: no chain activity; transfers end at II.G, stores end when II.10 ends (t₂). | p. 161–163, p. 173, Figs. VII, X, XI | NOT BUILT |
| O5 | Williams order sequence: order digits in R₃ → "yes Williams" (through T_Y/O = 0) → Memory Control acknowledges with Up (II.10): sets T_Y/O = 1, lets the address digits into the Address Generator, and (transfer orders) lets T.C. set T_L. Then I_t: with T_L = 0 → M→R³ Gate (operand to the number register); with T_L = 1 → M→R₃ Gate (new order word), which after delay δ resets T_L and stores address+1 in the Order Register. M→R³ Gate then starts the chain after a delay equal to its own duration. | p. 168–171, Fig. VI | NOT BUILT |
| O6 | Timing definitions (Fig. VIII): t₁ start of the memory phase (Williams) or of the R₂→R³ Gate (non-Williams); t₂ = time after which the address digits are no longer needed (gate B.1/G.3 disabled) and effective end of trivial orders; t₃ end of non-trivial orders. Up ("sync") lasts t₁→t₂ (trivial) or t₁→t₃ (non-trivial); after that is Down. | Fig. VIII page | NOT BUILT |
| O7 | Three-stage counter L, R, F built from toggles T_O/1, T_T, T_F, T_L; one count needs Up then Down. State table: Down 0000; 1st-half Up 0100; Down 1100; 2nd-half Up 1000; Down 1010; Fetch Up 1011; Down 0001; M→R₃ Gate 0000 (order T_O/1, T_T, T_F, T_L). T_O/1 = 0 enables G.2 (left order), = 1 enables G.4 (right order). | p. 176, Fig. IX | NOT BUILT |
| O8 | Fetch: when both halves are done (F(1)), gates G.1–G.4 are disabled, a false "yes Williams" is produced, the address comes from the Order Register through B.0, the word goes to R₃ via M→R₃ Gate, and the Order Register is set to address+1 (modulo 1024) by the Dispatch Counter's adder. A fetch cycle may be followed immediately by an action cycle. | p. 119, p. 165–168, p. 171–172, Fig. V | NOT BUILT |
| O9 | Transfer orders 15–18: address = location of next order word. Step digit 0 → same phase as the current order; 1 → opposite phase. End (unconditional): R₁, R₂ unchanged, R³ = b, R₃ = b. Conditional (17, 18): transfer iff R₁ ≥ 0 (sign digit 0). Case A (a ≥ 0): R³ = 0, R₃ = b. Case B (a < 0): R³ = b, R₃ unchanged. | p. 41–42 | NOT BUILT |
| O10 | Store (13): R₁ → memory x; end R³ = 0 (the Digit Resolver must present R₁ + 0; R₁ lower must be intact and either R³ zero or the complement gates nulled). Store Clear (14): additionally R₁ = 0, memory x = 0. Step digit must be 1. | p. 40–41; Apr. 1954 p. I-31 | NOT BUILT |
| O11 | Load R₂ (12): Up handles "Clear R₂ to 1"; M→R³ Gate then permits "Gate R³ to R₂" (Green gates transmit 0s). End R₂ = b, R³ = b; R₁ unchanged, or 0 if the clear digit is 1 (but see X2). | p. 39–40, Fig. XI | NOT BUILT |
| O12 | Orders read from memory arrive in RIII through Yellow/Black gates from the Discriminator; Main Control's WO signal directs the word to R³ (number) or R₃ (order). | p. 65, p. 123 | NOT BUILT |
| O13 | Order 19 (Quick Sum) and orders 24–29 (I/O, drum) are outside the 1952 core; priming orders 24–25 are second-phase only and also execute the analogous order 1–18; I/O orders 26–29 must be first phase with a transfer in the second phase. Their register effects are listed on p. 47–50. Not required for a core simulation, but if present they must not be confused with the internal orders (d1 = 0). | p. 47–50 | NOT BUILT |

## W. Williams memory and its Local Control (timing seen by the arithmetic unit)

| ID | Requirement | Source | Status |
|---|---|---|---|
| W1 | 1024 words of 40 digits: 40 CRTs, 32 × 32 spots each. Address = 10 digits; 2⁰..2⁴ horizontal, 2⁵..2⁹ vertical. | p. 83, p. 113–114 | NOT BUILT |
| W2 | Memory Clock: multivibrator, 40 kc used (range 4–143 kc), so one memory cycle = 25 µs. Clock pulse 0.9 µs. | p. 89–93, Fig. 18, Fig. 19 | NOT BUILT |
| W3 | Pulser chain per cycle (durations, µs): Clock 0.9 → SD 1.2 → {I 1.75, TT 1.55, HT 2.6} → (HT_t) TD 1.7 → (TD_t) {HH 4.25, TH 4.75} → (TH_t) Ā 1 → (Ā_t) Cl 1 → (Cl_t) B 1. Each termination pulse ≈ 0.5 µs. Circuit delay ≈ 0.05 µs, rise ≈ 0.25 µs. | p. 97, p. 113, Fig. 17, Fig. 19 | NOT BUILT |
| W4 | Regenerate and action cycles alternate; only a fetch may be followed by a second action cycle. Main Control's "Yes" must arrive before TD_t of the regenerate cycle (before Ā of a fetch cycle); Read/Write before B. | p. 119, p. 122 | NOT BUILT |
| W5 | Local Control sequence once Yes is seen: TD_t sets Synch; Ā sets Action; then BCl_A (Cl) and Synch off; B_A + Acknowledge Yes (resets Yes/No to No; if Read, B_A also = Clear RIII; if Write, sets Routine to Write); ACl_A at next Cl T₁; A_A at next TD (if Read, A_A also = Gate into RIII); Ā turns Action off (unless Yes was re-asserted, fetch case); Finish; BCl_R, B_R (Routine back to Read), ACl_R, A_R. | p. 120–123, Fig. 26 | NOT BUILT |
| W6 | Consequence for the arithmetic unit: an operand requested at an arbitrary phase arrives in RIII at the TD of the cycle after the one in which Action was set, i.e. between roughly one and two memory cycles (25–50 µs) after the request. The machine is asynchronous elsewhere; only the memory imposes this synchronisation. | p. 118, p. 161–162, Figs. 27–28 | NOT BUILT |
| W7 | Dispatch Counter: three ranks T_R (restore/regeneration address), T_D (dispatch, drives deflection), T_O (order counter). Adder type with a permanently wired carry into 2⁰. Sequence: Ā decides R or O; Cl → B-clear of T_D; B → B gates (T_D ← T_R or T_O); Cl T₁ (next cycle) clears T_R/T_O to 1s; TD-time pulse opens the A gates (T_R/T_O ← T_D + 1). Order Counter counts modulo 1024. B₃ gate loads an address from R₃ into T_D. | p. 152–158, p. 165, Fig. 14 | NOT BUILT |
| W8 | Regeneration of the whole store must complete within ≈1/30 s (upper bound 0.1 s). | p. 152–153 | NOT BUILT |

## X. Ambiguities and transcription issues (must be resolved explicitly)

| ID | Issue | Where |
|---|---|---|
| X1 | Figure pages with body text that the markdown omitted: printed pp. 61 (Fig. 13 note), 78, 86, 87a, 89, 96, 97, 148, 150, 153, 158, 160, 161, 163. Recovered in `figure_page_text_supplement.md`. The p. 150 and p. 160 text define the III.α / III.12 / III.13 interfaces and the Up/Down/sync timing; the p. 163 text defines the RII Load unit. |
| X2 | Load R₂ (order 12): the order table image prints digit 8 as a fixed 0, but 0.12 c) says the clear digit may be 1 and then pre-clears R₁. Check what the code does for order 12 with d8 = 1. |
| X3 | Left shift: p. 26 says the right-most stage of R₁ is made 0; 0.22 e) lists R₁ = a₁, …, a₃₉, a₀. 0.22 e″ (left then right recovers a₀…a₃₉ with R₂ = 0, b₁, …, b₃₉) is consistent only with the 2⁻³⁹ stage being 0. Treat the printed a₀ as a typo unless the page image says otherwise. |
| X4 | 0.8 (minus absolute hold) end state is printed as R₁ = a − b; from 0.19's definition f(b) = −|b| for 0.8 it must be a − |b|. |
| X5 | 0.9 c) prints "ab + 2⁻³⁹d" where c is the initial R₁ content; read as 2⁻³⁹c. How the sign digit of c is treated (as a 2⁰ arithmetic digit, given "sign made 0" on each right shift) is not stated. |
| X6 | p. 20 indexes the multiplier digit as x₃₉₋ᵢ once, x₄₀₋ᵢ elsewhere. Use x₄₀₋ᵢ (step i examines digit 40−i, i = 1..39). |
| X7 | Division remainder naming: Chapter I's recursion leaves r₃₉ in the register with x = Qy + 2⁻³⁸r₃₉; 0.11 says R₁ = "2R". With the data path of D5 (R₁ holds 2rᵢ), R₁ = 2r₃₉ and the two statements agree if R ≡ r₃₉. Confirm the code's final R₁ equals 2r₃₉ and not r₃₉ or 2⁻³⁸r₃₉. |
| X8 | Which physical row of RIII is R³ and which is R₃ is lost in the OCR (superscript vs subscript). Behaviourally irrelevant as long as both exist and are steered by WO. |
| X9 | The markdown duplicates 0.5 and 0.6 (pp. 34–35). Harmless. |
| X10 | The mechanism of the terminal multiplication cycle (M8) and of the round-off carry path (chassis "RII Op", "CyIA/CyIB": 2⁻³⁹ R₂ input and carry) is in drawings not included. Any gate-level implementation is an assumption. |
| X11 | Figs. 27 and 28 (Local Control timing charts) are scanned too coarsely to read edge times; use the textual sequence W5 and the pulse table W3. |

---

## How to use this list

1. Baseline commit of the other instance's code, unmodified.
2. Check N and R items first (foundation), then S, then A, then H, then M and D.
3. For each item mark OK / DIFF / ASSUMED with a pointer to the code, and for
   DIFF add a test that fails before the fix and passes after.
4. Oracles: Python integers for A/M/D end states (including M6/M7 low halves
   and D5's identity); the 0.23 formula for the accept/reject alternation;
   Fig. 30 for the shift counter; the count numbers 2 / 40 / 39 / n for the
   chain; the 1.5 µs lags, ≈15 µs carry delay, and 25 µs memory cycle for
   the timing model.
