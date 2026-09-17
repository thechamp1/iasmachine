# Supplement: body text recovered from figure pages

The main transcription (`iasfinalreport.md`) marks a number of figure pages as
"the page carries no additional body text". Inspection of the page images shows
that several of those pages do carry body text, in some cases text that matters
for the logical design (control signal names, the meaning of Up/Down and the
sync pulse, the RII Load unit, the Shift Counter / Gate-Clear Chain interfaces).
This file transcribes that text from the images so it can be searched.

Page numbers are the printed page numbers visible on the page images. The
corresponding `<!-- p. NN -->` marker in `iasfinalreport.md` is the printed
number plus 14.

---

## Printed p. 61 (md p. 72) — note under Fig. 13 (RII Gate Chassis)

Labels at top of drawing: "FROM CONTROL CHAIN — B, R, G, Y".

> In RII Gate Chassis, T₁, T₂, T₃ are connected as shown, but T₄ is driven by
> the Yes-No signal from the Control: +10 = No, −10 = Yes.
>
> Each gate bus drives 16 grids, 4 in each chassis.

(T₄ is the Yellow-gate driver-driver. RII's shift-up path is therefore enabled
only when Control says "Yes"; this is how RII is made to shift together with RI
in some orders and not in others.)

## Printed p. 56 (md p. 67) — labels on Fig. 10 (extra 2⁺¹ column of RI)

- Upper toggle "2⁺¹ Rᴵ", cleared by the Black Clear bus (to 0) and Red Clear
  bus (to 1).
- "Black Gate Command Bus" drives the Black gate from 2⁺¹ Rᴵ into the 2⁰
  column of R₁ ("BLACK GATE INTO 2⁰ COLUMN OF R₁").
- The same Black-gate tube has a second input labelled
  "SPECIAL GATE FROM 2⁰ COLUMN OF R³ FOR MULTIPLICATION".
- "Green Gate Command Bus" drives a Green gate from the lower toggle 2⁺¹ R₁
  up into 2⁺¹ Rᴵ (the reverse direction from every other Green gate in RI).
- Lower toggle "2⁺¹ R₁", cleared by the Yellow Clear bus (to 0) and Green Clear
  bus (to 1); its output goes "TO RED GATE IN 2⁰ COLUMN IN Rᴵ".
- "Yellow gate in 2⁰ column" and "Yellow Gate Bus".

## Printed p. 57 (md p. 68) — labels on Fig. 11 (end-around, RI 2⁻³⁹ → RII 2⁰)

- "2⁻³⁹ Rᴵ" upper toggle (Black Clear / Red Clear) → "Yellow Gate Command"
  tube → cathode follower (27K + 33K to −300) → dashed wire back to the
  "Black Gate Command" tube of the "2⁰ R₂" toggle (Green Clear / Yellow Clear).
- "2⁻³⁹ R₁" lower toggle (Yellow Clear / Green Clear).

## Printed p. 59 (md p. 70) — labels on Fig. 12 (Dwg. A-1452, R₁ Clear Selector)

- Inputs from "MAIN CONTROL, M3-A": "↓ at sync." and "C/H" (clear/hold).
- "R from LR-A2" and "L from LR-A8" (Left-Right selector chassis).
- "Unconditional φ₂ invite from Ch3-A2" (Gate-Clear Chain chassis 3).
- Outputs: "Yellow Clear R₁ Command to YCR₁-F5;6" and
  "Green Clear R₁ Command to GrCR₁-F5;6".
- Note on drawing: grid suppressors 1K-½W, plate suppressors 100Ω-½W, tubes
  6J6, 6AL5 and 5670. Drawn F. Fell, 2-23-53.

## Printed p. 70 (md p. 82) — labels on Fig. 14 (Williams Memory Block Diagram)

Main Control ↔ W.M. Local Control:
- From Local Control to Main Control: Clear RIII, Gate RIII, Finish,
  Acknowledge "Yes".
- From Main Control to Local Control: Read/Write, Yes/No.
- "Shift control / not order counter / RIII" and "From RIII (10 digits)" →
  gate B₃ → Dispatch Counter.
- Local Control → (B_A, ACl_A, A_A) → selector block → (B_O, ACl_A, A_A) →
  Dispatch Counter.
- Local Control → (BCl_R, B_R, ACl_R, A_R, BCl_A) → Dispatch Counter.
- Dispatch Counter → Deflection Generator.

Timing pulses listed: CLOCK ≡ Cl T₁, I (Inspect), TT, HT, SD, TD, HH, TH, Ā,
CL, B. Discriminator Pulse Routine Generator outputs: SA₁, SO₁, SA₂, SO₂,
Strobe. Discriminator: "Out to RIII", "In from RI". Twitch Generator and
Deflection Generator drive X and Y.

## Printed p. 78 (md p. 90) — Fig. 18 page (Memory Clock waveforms)

> trailing edge is the important feature of the output as it affects the rest
> of the circuit.
>
> [Fig. 18: waveform I between +30 and +150 (t₀, t₁, t₂); waveform II between
> 0 and +500 (t₂, t₃); waveform III between +50 and +100; output waveform IV
> between −10 and +10.]
>
> (t₂t₃ is approximately .9 microsecond; the time between pulses depends upon
> the p.r.r. chosen)
>
> To insure against spurious triggering of the multivibrator by noise, the
> whole Memory Clock is housed in a metal box, and low pass filters are
> inserted in the leads by which power is brought in, as shown in the
> schematic. The dually controlled 500k variable resistors and the condensor
> switching arrangement make it possible to vary the repetition rate of the
> multivibrator from 4kcps to 143 kcps. The [p. 79: present p.r.r. is 40 kc.]

## Printed p. 86 (md p. 98) — Fig. 19 (pulse durations, microseconds)

| Pulse | Duration (µs) | Levels (v) |
|---|---|---|
| Clock (Clear T₁) | 0.9 | −10 / +15 |
| SD | 1.2 | −10 / +12 |
| TT | 1.55 | −10 / +10 |
| I | 1.75 | −10 / +12 |
| HT | 2.6 | −10.5 / +22.5 |
| TD | 1.7 | −10 / +12 |
| HH | 4.25 | −10.5 / +12.5 |
| TH | 4.75 | −10.5 / +12.5 |
| Ā | 1 | −9.5 / +12.5 |
| CL | 1 | −9.5 / +12.5 |
| B | 1 | −9.5 / +12.5 |

Relative start times as drawn: SD starts at the end of Clock; TT, I and HT
start together at the end of SD; TD starts at the end of HT; HH and TH start
together at the end of TD; Ā starts at the end of TH; CL at the end of Ā; B at
the end of CL.

> moderate deviations from the nominal values have no effect on the operation
> of the circuits to which the pulser outputs are applied.
>
> The termination pulses are not shown. However, these all rise at the
> [p. 87: termination of each pulse and last for approximately .5 µs.]

## Printed p. 87a (md p. 100) — Fig. 20 page (amplifier / discriminator input)

> were chosen so that with 0 input voltage these conditions were met.
>
> The remaining elements are the peaking inductance and the three bypass
> condensers. The plate bypass is as large as can be conveniently
> incorporated in the assembly; the cathode bypass is not critical since the
> low-frequency response of the amplifier is not particularly important; it
> is sufficiently large that any serious reduction in gain due to
> degeneration is avoided for the middle range of the amplifier response and
> beyond. The screen bypass again is not critical.
>
> The measured gain characteristic of the amplifier has half-power
> frequencies at very nearly 100 kcps and 800 kcps.
>
> THE DISCRIMINATOR
>
> The signals obtained from the cathode ray tubes, after having been inverted
> and amplified by the three stage output amplifier are as follows:
>
> [Fig. 20: for a stored 0, a positive hump to about +5 v; for a stored 1, a
> negative swing to about −30 v followed by a positive overshoot.]

## Printed p. 89 (md p. 102) — Fig. 21 page (Discriminator input from R₁)

> regenerate" case this is obviously necessary. In the "write" case it turns
> out that as we have pointed out before, it is desirable to use different
> beam turn on routines according as the restoration or changing of the
> stored information is called for.
>
> Once the Discriminator toggle (T₁) has been set, the circuit uses the
> Discriminator pulse routine pulses to effect when necessary the comparison
> of the contents of T₁ and of the corresponding toggle in R₁, and thus to
> establish the appropriate beam turn on routine. It will be noticed that but
> a single lead is brought to the Discriminator from the R₁ toggle, so that
> the gating arrangement is somewhat different from that used to read out of
> T₁. Furthermore, this lead does not come directly from the R₁ toggle, but
> from the plate of the Resident digit gate in the Adder: See Fig. 21.
>
> [Fig. 21: +110 through 4.7K to the plate ("OUT TO DISCRIMINATOR"); the
> other plate goes to the "SUMMING POINT"; one grid "IN FROM R₁ TOGGLE", the
> other grid at −9; common cathode through 32K to ground.]
>
> Thus, for a R₁ toggle grid voltage of −40v (representing a 1), the left
> section of the Resident digit gate will remain cut off, and the plate
> voltage will be +110v, this voltage being determined by the bus. A grid
> voltage of 0, representing a 0, will cause the left section to conduct, and
> the plate current of approximately 5.5 ma brings the output voltage (T₂) to
> about +84v; [p. 90: actually this voltage can vary as much as 5 volts ...]

## Printed p. 96 (md p. 109) — Fig. 24 page

> and (b) the write case.
>
> [Fig. 24 (a) read-regenerate: SO₁ +10 during I only; SA₁ +10 from end of TD
> for the dash time; SO₂ +120 during Cl T₁, otherwise +75; SA₂ constant
> +120. (b) write: SO₁ +10 during I and again after TD; SA₁ +10 during the
> superdot interval and again after TD; SO₂ +120 during Cl T₁, +75, then
> +100 from TD until the end of the superdash interval, then +75; SA₂ +120
> during I and from TD to the end of superdash, otherwise +100.]
>
> (The time scale in Fig. 24 is such that the duration of "Clear T₁" is very
> nearly 1 µsec.)
>
> One slight change must be made to the pattern we have determined, for
> engineering convenience rather than logical necessity. During the clearing
> of T₁ it is possible that very briefly the grid voltages of the toggle tube
> are such that no current is drawn from the summing bus by either of the
> gates. To guarantee that this will not cause beam turn-on, SO₂ is caused to
> rise to +120v during the clearing operation, thus assuring the drawing of
> current from the summing bus by the SO₂ gate. This is shown on our final
> drawing of the pulse routine voltage waveforms.

## Printed p. 97 (md p. 110) — Fig. 25 page

> Another slight change is made in SO₂. It is clearly unimportant whether
> this voltage remains at +100v or drops to +75v after the completion of the
> writing of the B part of a dash; it is also unimportant which of these
> levels it assumes in the brief interval between the Clock pulse and the
> Strobe pulse, for in both these intervals SO₁ and SA₁ are −10v, so that we
> are certain that current is drawn from the summing bus by one of the gates
> leading out of T₁, and that the CRT electron beam, therefore, is cut off.
> As a matter of convenience SO₂ is dropped to +75v at the beginning of the
> Cl pulse, and kept there until the next Clock pulse, at which time it rises
> to +120v. It then drops to +75v at the expiration of the Clock pulse; this
> is shown in Fig. 24.
>
> [Fig. 25: the measured waveforms, (a) read-regenerate, (b) write.]
>
> (The width of the first SO₁ pulse is approximately one microsecond).

## Printed p. 108 (md p. 121) — labels on Fig. 26 (Wm. Local Control)

Three toggles: SYNCH, ACTION, ROUTINE.
- Synch is set by the gate (Yes · TD_t); cleared by the Action side (BCl_A path).
- Action is set by Ā when Synch is on; cleared by the gate (No · Ā).
- Action-on side emits: BCl_A (with Cl), ACl_A (with Cl T₁), B_A and
  "Acknowledge Yes" (with −B), A_A (with −TD); A_A · Read → "Gate into RIII";
  B_A · Read → "Cl RIII"; B_A · Write sets Routine to Write.
- Action-off side emits: BCl_R (with Cl), ACl_R (with Cl T₁), B_R (with −B),
  A_R (with −TD); "Finish" (with No); B_R (−B) resets Routine.
- Routine outputs to the Routine Generator: one lead +10 v = Write /
  −20 v = Read, the other +10 v = Read / −20 v = Write.

## Printed pp. 111–112 (md pp. 124–125) — Figs. 27, 28 timing charts

Both charts are drawn with "Time scale: ⊢⊣ = 1 µsec" and show the pulse
train (Cl T₁, TT, I, HT, TD, HH, TH, Ā, Cl, B) along the top. Rows: Yes/No,
Read/Write, Synch, Action, BCl_R, B_R, ACl_R, A_R, BCl_A, B_A, ACl_A, A_A,
Clear RIII, Gate into RIII, Acknowledge Yes, Finish, Routine, SO₁, SA₁, SO₂,
SA₂. Fig. 27 sequence: Regenerate, Write, Regenerate, Read, Regenerate.
Fig. 28 sequence: Regenerate, Fetch, Write, Regenerate. (The scans are too
coarse to read individual edge times; the text on md pp. 122–123 gives the
event order.)

## Printed p. 145 (md p. 159) — Fig. I

Text is in the main transcription. Figure labels: (C) into Main Control; (D)
Main Control → Memory Control; (G) Memory Control → Arithmetic Control; (E),
(F) between Memory Control and Memory; (H), (J) between Arithmetic Control and
Arithmetic Unit; (B) Main Control → Memory (fetch); (A) Memory → Main Control
(order digits).

## Printed p. 148 (md p. 162) — Fig. II page

> subsequent activities until this particular phase is reached. The time T
> from I.A or I.B to I.C may encompass several Memory cycles and it is
> therefore imperative that no reference be made to the Memory after the
> initial one. The acknowledgment signal II.10 is thus used to turn off II.D.
> It has certain auxiliary functions that it also performs but which are not
> relevant at this moment. We discuss these later. However, these same
> functions may be needed in case II.D' is emitted instead of II.D. In this
> case a portion of the Control emits II.10' which is the analogue of II.10
> and initiates, in this case, the auxiliary activities. This occurs almost
> immediately after II.D' is emitted since no synchronism is involved.
>
> [Figure II: Main Control → II.D → Williams Control → II.G; Williams
> Control → II.10 → Main Control. Main Control → II.D' → −Williams Control →
> II.G'; −Williams Control → II.10' → Main Control.]
>
> In the case where II.D was stimulated a stimulus II.G appears after the
> Memory phase of the Control activity is completed. In the contrary case,
> i.e. II.D', an analogous signal II.G' is emitted almost immediately after
> II.10'.

## Printed p. 150 (md p. 164) — Fig. III page

> durations of the arithmetic operations. Cf. pp. 126 ff. It has three
> inputs; one of these III.α comes from the Main Control and is initially set
> up by the order; the others are II.G or II.G' and III.13. Its two outputs
> are the input III.H to the Arithmetic Unit and the termination signal
> III.C. We indicate these connections below in Fig. III.
>
> [Figure III: III.α → GATE CLEAR CHAIN; II.G and II.G' (joined) → GATE CLEAR
> CHAIN; GATE CLEAR CHAIN → III.H → ARITHMETIC UNIT; ARITHMETIC UNIT → III.J →
> SHIFT COUNTER; III.12 → SHIFT COUNTER; SHIFT COUNTER → III.13 → GATE CLEAR
> CHAIN; GATE CLEAR CHAIN → III.C.]
>
> We see from the figure and the previous explanation that the Gate Clear
> Unit is initially set up by III.α, i.e. by the order digits, and is then
> turned on when the stimulus II.G or II.G' arrives. It then commands the
> Arithmetic Unit to perform the operation in question and to advance the
> Shift Counter until it reaches the required count, as specified by III.12.
> At this time the Shift Counter emits III.13 which turns off the Gate Clear
> Chain and which is essentially reissued as the completion signal III.C.
>
> It remains to describe in somewhat more detail the functions of I.E and
> I.F above, i.e. the intercommunications between the Memory Control and the
> Memory proper. To describe these we recall to the reader the Dispatch
> Counter previously discussed in pp. 130 ff. above. It contains two
> principal parts, an Address Generator and an Order Counter. The Address
> Generator is that unit which stores temporarily a given 10
> [p. 151: digit address and converts it ...]

## Printed p. 153 (md p. 167) — Fig. V page

> [Figure V: MAIN CONTROL feeds L, R, F(0), F(1) of the three-stage counter
> and the address portion of the order to gate B.3 → ADDRESS GENERATOR → "To
> MEMORY". ADDRESS GENERATOR → ADD → gate → ORDER REGISTER; ORDER REGISTER →
> gate B.0 → ADDRESS GENERATOR. F(0) enables B.3; F(1) enables B.0. Toggle
> T_L; stimulus G passes through gates into R₃ (T_L on) or R³ (T_L off). The
> "M to R₃" gate resets T_L and feeds the ORDER REGISTER gate.]
>
> DETAILS OF TRANSFER OF CONTROL ORDERS
>
> In this sketch we have shown the third stage F or Fetch of the three stage
> counter as a two stage organ connecting to gates B.0 and B.3 and to a
> toggle T_L. The state F(0) is that which obtains when the counter is in
> states L or R. In this case the gate B.3 is enabled. In the contrary case
> it is B.0. This turning on allows the stimulus G to be transmitted in
> several directions. The choice of B.0 or B.3 determines the source of the
> address transmitted to the Memory, i.e. whether from the Order Counter in
> the "fetch case" — or from the Address portion of the order in a half word
> in R₃. We also note that T_L can be turned on directly by the Main Control.
> This is done to [p. 154: effect a transfer of the Control.]

## Printed p. 155 (md p. 169) — labels on Fig. VI (Memory Orders)

- R₃ (four fields: left address, left order, right address, right order)
  read out through gates G.1, G.2, G.3, G.4. L enables G.1, G.2; R enables
  G.3, G.4.
- Address digits (G.1 or G.3) → gate "3" (with UP and F(0)) → ADDRESS
  GENERATOR → MEMORY. ADDRESS GENERATOR → ADD → gate (with M→R₃Gt) → ORDER
  REGISTER → gate (with F.1) → ADDRESS GENERATOR.
- Order digits (G.2 or G.4) → ORDER INTERPRETER. ORDER INTERPRETER → gate
  (with Ûp) → ADDRESS RECOGNITION GATES ← SHIFT COUNTER. ADDRESS RECOGNITION
  GATES → STOP → CLEAR GATE CHAIN, → L (three-stage counter), → T_Y/O (0 side).
- ORDER INTERPRETER → CLEAR GATE CHAIN (set-up); M→R³Gt → START → CLEAR GATE
  CHAIN; CLEAR GATE CHAIN → RI; CLEAR GATE CHAIN → gate (with a line from the
  ORDER INTERPRETER) → RII. RI → STEP → SHIFT COUNTER.
- ORDER INTERPRETER → "YES Wms." → gate (with T_Y/O = 0) → MEMORY CONTROL.
  MEMORY CONTROL → UP (sets T_Y/O to 1) and → I_t.
- I_t → gate (with T_L = 0) → M→R³Gt; I_t → gate (with T_L = 1) → M→R₃Gt.
  M→R₃Gt → δ (delay) → T_L reset to 0. ORDER INTERPRETER → T.C. → gate (with
  UP) → T_L set to 1. F(1) → T_L set.
- Time line at bottom right: YES Wms. … UP … I_t.

## Printed p. 158 (md p. 172) — Fig. VII page

> the contents of the Order Register are permitted to enter the Address
> Generator. We have not yet shown in Figure VI the manner in which the
> Memory Control is stimulated to act. In fact, in this case a false "yes
> Williams" signal is produced and serves to stimulate in the usual way the
> Memory Control. Since no arithmetic activity takes place the process is
> terminated with the help of the M → R₃ Gate. Of course, the contents of the
> Order Register must be modified. This is done as in the case of a transfer
> of the Control.
>
> The situation with regard to those orders which make no reference to the
> Memory, orders 20 - 23, is indicated in Figure VII below. In this case the
> Williams Control is not used but the Not-Williams Control of Figure II is.
>
> [Figure VII NON-MEMORY ORDERS: R₃ → G.1…G.4 → ORDER INTERPRETER and (address
> digits, via a gate enabled by YES Wms.-not) → ADDRESS RECOGNITION GATES ←
> SHIFT COUNTER; ADDRESS RECOGNITION GATES → STOP → CLEAR GATE CHAIN; ORDER
> INTERPRETER → YES ARITH → −WILLIAMS CONTROL → R₂→R³Gt → CLEAR GATE CHAIN;
> CLEAR GATE CHAIN → RI and (gated) RII; RI → SHIFT COUNTER.]
>
> In this case the Order Interpreter issues a "yes Arithmetic" stimulus —
> D' in Figure II — to the Non-Williams Control which emits the so-called
> R₂ → R³ Gate, G¹ in Figure II. The yes Arithmetic
> [p. 159: stimulus also causes the address portion ...]

## Printed p. 160 (md p. 174) — Fig. VIII page

> [Figure VIII (a): UP from t₁ to t₃, then DOWN. (b): UP from t₁ to t₂, then
> DOWN.]
>
> Figure VIII (a) shows certain time relations for non-arithmetically trivial
> orders and VIII (b) shows the comparable relations for the trivial ones.
> The time t₁ defines for Williams orders the start of the Memory phase of the
> Control's activities, and for non-Williams orders the start of the R₂ to R³
> Gate. The time t₂ is defined only for Williams orders. It marks that time
> after which the Memory Control has no further need for the address portion
> of the order being executed. It is indeed at this time always that we turn
> off the address portion, i.e. we disable gate B.1 or G.3. Finally t₃ is
> defined only for non-trivial orders. It marks that time at which the order
> has been completed. For arithmetically trivial orders t₂ is effectively the
> end of the order, even though the Memory may in fact be completing certain
> of its internal activities. The stimulus Up is indicated on the Figure; the
> pulse lasting from t₁ until t₂ for trivial orders and until t₃ for
> non-trivial orders is called the "sync" pulse; the time after t₂ in the
> former case and after t₃ in the latter is called Up or Down.
>
> We now show a detailed diagram of the three stage counter.

## Printed p. 161 (md p. 175) — Fig. IX page

> [Figure IX: toggles T_T (0|1), T_O/1 (0|1), T_F (0|1), T_L (1|0). Gates
> driven by UP and Ûp. T_O/1's 0 side → G.2, its 1 side → G.4. T_L set by
> T.C., reset by M→R₃Gt. T_F's outputs and UP feed the T_T gates; Ûp gates
> transfer T_T back into T_O/1 and into T_F.]
>
> The pair of toggles T_T, T_O/1 are to be regarded as one binary counter
> cell. The former toggle is used primarily as an intermediate storage space
> during the counting process. It is the analogue of the familiar "circuit
> inertia" in more conventional scalars. This is in keeping with the
> registers and other counters in the machine. As has been seen such a
> counter requires two stimuli per count. These stimuli are here Up and Ûp
> (or Down). Thus a complete count is caused by the Up signal followed by the
> Down signal.
>
> As we see from Figure IX the Up signal, when T_F is in the zero state, i.e.
> F(0), transfers the complement of the contents of T_O/1 into T_T. The Down
> signal, under certain conditions, as seen in the figure, transfers its
> contents back into T_O/1. To describe the block
> [p. 162: diagram it is helpful to note the following Table:]

## Printed p. 162 (md p. 176) — Fig. X (Non-Williams Control)

> [Figure X: YES ARITH sets toggle TT₁ (1|0). TT₁ on → gate → UP and "Clear
> R³ to 1". "Clear R³ to 1" sets toggle TT₂ (1|0). TT₂ on, gated with TT₁ →
> "Gate R₂ to R³". "Gate R₂ to R³" feeds back to reset TT₂ and TT₁.]

## Printed p. 163 (md p. 177) — Fig. XI page (RII Load order control)

> From this figure we see how the Up signal is generated. From this together
> with Figures VI, VII we see how the R₂ to R³ Gate plays the role for
> Non-Williams Orders that the M to R³ Gate does for Williams orders.
>
> Note that the reaction times of the prototype toggles TT1, TT2 determine
> the effective durations of Clear and Gate impulses.
>
> There is a separate unit to execute the order for loading RII. This unit
> is similar to that illustrated in Figure X above.
>
> [Figure XI: "RII Load Order" gated with UP → "Clear R₂ to 1" → sets toggle
> "T RII Clear" (1|0); "Gate R³ to R₂" resets it. "M to R³ Gt" gated by T RII
> Clear → sets toggle "T RII Load" (1|0); T RII Load → gate inhibited by "M to
> R³ Gt" → "Gate R³ to R₂".]
>
> Since the RII Load Order, 12, is a Williams Order the Control provides, as
> usual an Up signal and later an M to R³ Gate. The former is used to handle
> the clearing of R₂ and the latter to permit the transfer of information
> from R³ to R₂. The symbol [p. 164: gate symbol ...]

## Printed p. 165 (md p. 179) — Fig. XII (Order Interpretation tree)

Root "ORDER". Circled numbers are order digits (0–9 of the 10-digit operation
field); left branch = digit is 0, right branch = 1; boxed numbers are order
list numbers. "TIME" arrow runs downward (decisions in approximate time order).

- Digit 1: Ext. (0) / Int. (1).
  - Ext. → digit 2: IBM (0) / DRUM (1) → digit 3: to Wms (0) / from Wms (1):
    IBM to Wms = 26, IBM from Wms = 27, Drum to Wms = 28, Drum from Wms = 29.
  - Int. → digit 2: Non Wms (0) / Wms (1). A dashed line labelled
    "digit 8: Preclear R₁ → 0" crosses both branches below digit 2.
    - Non Wms → digit 6: Shift (0) / R₂→R₁ (1, order 23).
      Shift → digit 5: Right (0) / Left (1, order 22).
      Right → digit 7: N.R.O. (0, order 20) / R.O. (1, order 21).
    - Wms → digit 3: AT (0) / NAT (1).
      - AT → digit 6: T.C. (0) / Store (1, orders 13, 14).
        T.C. → digit 5: U.T.C. (0, orders 15, 16) / C.T.C. (1, orders 17, 18).
      - NAT → digit 6: ÷× (0) / Σ, RIIL (1).
        ÷× → digit 5: × (0) / ÷ (1, order 11).
        × → digit 7: N.R.O. (0, order 9) / R.O. (1, order 10).
        Σ, RIIL → digit 7: Σ (0, orders 1–8) / RIIL (1, order 12).

## The order code table (printed p. 41, md p. 51)

Column headings, digit 0 … 9 of the operation field, with the meaning of a 0
and of a 1:

| Digit | 0 means | 1 means |
|---|---|---|
| 0 | No Step | Step |
| 1 | Ext. | Int. |
| 2 | Arith. | Wms. |
| 3 | AT | NAT |
| 4 | # (number) | Abs. |
| 5 | +R | −L |
| 6 | ×/÷ | Σ |
| 7 | No RO | RO |
| 8 | Hold | Clear |
| 9 | Spare | — |

| No. | Order | Address | d0 | d1 | d2 | d3 | d4 | d5 | d6 | d7 | d8 | d9 | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | + clear | 0–1023 | 1/0 | 1 | 1 | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 1 |
| 2 | + hold | 0–1023 | 1/0 | 1 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | |
| 3 | − clear | 0–1023 | 1/0 | 1 | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | |
| 4 | − hold | 0–1023 | 1/0 | 1 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | |
| 5 | + abs. clear | 0–1023 | 1/0 | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 0 | |
| 6 | + abs. hold | 0–1023 | 1/0 | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | |
| 7 | − abs. clear | 0–1023 | 1/0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 0 | |
| 8 | − abs. hold | 0–1023 | 1/0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | |
| 9 | × clear NRO | 0–1023 | 1/0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 1/0 | 0 | 2 |
| 10 | × clear RO | 0–1023 | 1/0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 1/0 | 0 | |
| 11 | ÷ | 0–1023 | 1/0 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | |
| 12 | Load R₂ | 0–1023 | 1/0 | 1 | 1 | 1 | 0 | 0 | 1 | 1 | 0 | 0 | |
| 13 | Store | 0–1023 | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 3 |
| 14 | Store Clear | 0–1023 | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | |
| 15 | Un. T. C. no step | 0–1023 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 4 |
| 16 | Un. T. C. step | 0–1023 | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | |
| 17 | Con. T. C. no step | 0–1023 | 0 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | |
| 18 | Con. T. C. step | 0–1023 | 1 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | |
| 19 | Quick Sum | 0–1023 | 1 | 1 | 1 | 1 | 1/0 | 1/0 | 1 | 0 | 1/0 | 1 | 5 |
| 20 | Sh. Right NRO | 1–47 | 1/0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1/0 | 0 | |
| 21 | Sh. Right RO | 1–47 | 1/0 | 1 | 0 | 1 | 0 | 0 | 0 | 1 | 1/0 | 0 | 6 |
| 22 | Sh. Left | 1–47 | 1/0 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 1/0 | 0 | |
| 23 | R₂ → R₁ | 2 | 1/0 | 1 | 0 | 1 | 1/0 | 1/0 | 1 | 0 | 1/0 | 0 | 7 |
| 24 | IBM priming | 1–127 | 1 | 0 | 1 | 1/0 | 1/0 | 1/0 | 1/0 | 1/0 | 1/0 | 0 | 8 |
| 25 | Drum priming | 0–31; 0–31 | 1 | 0 | 1 | 1/0 | 1/0 | 1/0 | 1/0 | 1/0 | 1/0 | 0 | 9 |
| 26 | IBM Load | 0–1023 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 10 |
| 27 | IBM Punch | 0–1023 | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 1 | 1 | 0 | |
| 28 | Drum → Memory | 0–1023 | 1 | 0 | 1 | 0 | 0 | 1/0 | 1 | 0 | 0 | 0 | 11 |
| 29 | Memory → Drum | 0–1023 | 1 | 0 | 1 | 1 | 0 | 1/0 | 1 | 1 | 1 | 0 | 11 |

Groupings printed in the table: 1–8 "Summation"; 9–12 "Other NAT Orders";
13–18 "Arith. Trivial Orders"; 19 "Special Order"; 20–23 "Non Memory Orders";
24–29 "Input-Output Orders". Address column heading for 1–19: "Memory orders
(address specifies word in memory) 0–1023". Row 23 shows the address "2" (the
worked example in 0.23 uses the shift count n; the text allows 1 ≤ n ≤ 47).
The "Notes" column numbers (1–11) refer to notes that are not on this page.
