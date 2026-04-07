# LogiCraft — User Manual
### Digital Design & Computer Organisation Simulator · v1.0.4

---

## Table of Contents

1. [Overview](#1-overview)
2. [Installation & Launch](#2-installation--launch)
3. [Application Interface](#3-application-interface)
   - 3.1 [Toolbar](#31-toolbar)
   - 3.2 [Sidebar Navigator](#32-sidebar-navigator)
   - 3.3 [Content Area](#33-content-area)
   - 3.4 [Status Bar](#34-status-bar)
4. [Module 1 — ALU Simulator](#4-module-1--alu-simulator)
5. [Module 2 — Number Systems](#5-module-2--number-systems)
6. [Module 3 — Gates & K-Map](#6-module-3--gates--k-map)
7. [Module 4 — Sequential Logic](#7-module-4--sequential-logic)
8. [Module 5 — Adder Types](#8-module-5--adder-types)
9. [Module 6 — Booth's Algorithm](#9-module-6--booths-algorithm)
10. [Module 7 — FSM Designer](#10-module-7--fsm-designer)
11. [Global Features](#11-global-features)
12. [Keyboard & Mouse Reference](#12-keyboard--mouse-reference)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Overview

**LogiCraft** is an interactive desktop simulator for digital logic design and computer organisation concepts. It provides a hands-on, visual environment to explore:

- Arithmetic-Logic Unit (ALU) operations with gate-level carry-chain visualisation
- Number system conversions (Binary, Octal, Decimal, Hex) and IEEE 754 floating-point analysis
- Karnaugh Map (K-Map) minimisation with automatic SOP expression generation
- Flip-flop (D, T, SR, JK) simulation with timing diagrams
- Adder architecture comparison — Ripple-Carry, Carry-Lookahead, and Carry-Select
- Booth's multiplication algorithm with step-by-step register animation
- Finite State Machine (Moore & Mealy) design, simulation, and minimisation

LogiCraft is built with **PyQt6** and **Matplotlib**, making it lightweight and cross-platform (macOS, Linux, Windows).

---

## 2. Installation & Launch

### Prerequisites

| Requirement | Minimum Version |
|---|---|
| Python | 3.10 |
| PyQt6 | 6.6 |
| matplotlib | 3.8 |
| numpy | 1.26 |

### Setup Steps

```bash
# 1. Navigate to the project root
cd "path/to/LogiCraft"

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # macOS / Linux
venv\Scripts\activate.bat         # Windows

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Launch the application
python main.py
```

### First Launch Defaults

| Setting | Default |
|---|---|
| Active Module | ALU Simulator |
| Theme | Light |
| Bit Width | 8-bit |
| Window Size | 1366 × 900 (minimum 1280 × 800) |

---

## 3. Application Interface

LogiCraft's shell consists of four persistent regions that are always visible regardless of the active module.

```
┌─────────────────── TOOLBAR ────────────────────────────────────────┐
│  Digital Design Studio   [4-bit][8-bit][16-bit]             [⚙]   │
├──────────────┬─────────────────────────────────────────────────────┤
│              │                                                      │
│   SIDEBAR    │               CONTENT AREA                          │
│  (Project    │    ┌──────── Left Panel ──┬──── Right Canvas ───┐   │
│  Explorer)   │    │ Controls & Results   │  Visualisation       │   │
│              │    └──────────────────────┴─────────────────────┘   │
├──────────────┴─────────────────────────────────────────────────────┤
│  STATUS BAR: MODE: SIMULATION ACTIVE   CYCLE: 0.004MS     V1.0.4  │
└────────────────────────────────────────────────────────────────────┘
```

### 3.1 Toolbar

| Control | Purpose |
|---|---|
| **"Digital Design Studio"** label | Branding — always visible |
| **4-bit / 8-bit / 16-bit** segment control | Sets the global bit width for ALU, Number Systems, and Adder modules |
| **⚙ button** (top-right, 32×32 px) | Toggles Light ↔ Dark theme |

> **Tip:** Switching bit width while a result is displayed re-renders the module immediately at the new precision.

### 3.2 Sidebar Navigator

The 260 px **Project Explorer** sidebar lists all seven modules. Click any item to navigate:

| Icon | Module | Key Features |
|---|---|---|
| ⚙ | **ALU Simulator** | Bit-toggle inputs, 5 operations, status flags, carry-chain diagram |
| 🔢 | **Number Systems** | Live base conversion, two's complement, IEEE 754, bit-cell canvas |
| 🔲 | **Gates & K-Map** | Editable truth table, Quine-McCluskey SOP, K-Map with groups |
| ≡ | **Sequential Logic** | D/T/SR/JK flip-flop simulation, timing diagram, CSV export |
| ➕ | **Adder Types** | RCA/CLA/CSA comparison, per-bit delay bars, scaling view |
| ✖ | **Booth's Algorithm** | Signed multiplication, step-by-step register animation, CSV export |
| 🔄 | **FSM Designer** | Moore/Mealy builder, simulation trace, state minimisation |

### 3.3 Content Area

Every module uses a **horizontal splitter** dividing the workspace into:

- **Left panel** — scrollable region with input controls, drop-down selectors, and text result panels
- **Right canvas** — a Matplotlib figure that renders diagrams, charts, and diagrams reactively

Drag the **splitter handle** between the two panels to resize. The splitter remembers its position per module.

### 3.4 Status Bar

| Side | Content |
|---|---|
| Left | `MODE: SIMULATION ACTIVE   CYCLE: 0.004MS` |
| Right | `V1.0.4   DOCUMENTATION   READY` |

---

## 4. Module 1 — ALU Simulator

> **Navigate**: Sidebar → ⚙ ALU Simulator

The ALU Simulator models a combinational Arithmetic-Logic Unit. You toggle individual bits for two operands, select an operation, and see the result along with a gate-level carry-chain diagram.

### 4.1 Left Panel Layout

```
[ INPUT A ]   Dec: 0   Hex: 0x0
  [0][0][0][0][0][0][0][0]          ← bit-toggle buttons

[ INPUT B ]   Dec: 0   Hex: 0x0
  [0][0][0][0][0][0][0][0]

OPERATION
  [ ADD (Addition)          ▼ ]

[ COMPUTE ]

STATUS FLAGS
  [ ZERO ] [ CARRY ] [ OVF ] [ SIGN ]

RESULT OUTPUT
  Binary  :  —
  Decimal :  —
  Hex     :  —
  Signed  :  —

────────────────────────
Operation History
  (scrollable list)
```

### 4.2 Setting Inputs via Bit Toggles

Each operand row shows **N toggle buttons** (N = 4, 8, or 16 depending on the toolbar bit-width selector). The **MSB is on the left**.

- **Click a bit button** → toggles between `0` (unpressed) and `1` (pressed/highlighted)
- The **Dec:** and **Hex:** live readouts in the group header update on every toggle

### 4.3 Selecting an Operation

| Drop-down Text | Internal Code | Description |
|---|---|---|
| ADD (Addition) | `ADD` | A + B, unsigned |
| SUB (Subtraction) | `SUB` | A − B via two's complement |
| AND (Bitwise AND) | `AND` | A AND B, bit-by-bit |
| OR (Bitwise OR) | `OR` | A OR B, bit-by-bit |
| XOR (Bitwise XOR) | `XOR` | A XOR B, bit-by-bit |

### 4.4 Computing and Reading Results

Click **COMPUTE**. The **RESULT OUTPUT** box updates with:

| Row | Format | Example |
|---|---|---|
| Binary | `BIN: <bits>` | `BIN: 00101101` |
| Decimal | `DEC: <unsigned>` | `DEC: 45` |
| Hex | `HEX: <hex>` | `HEX: 2D` |
| Signed | `SIGNED: <signed>` | `SIGNED: 45` (red if negative) |

### 4.5 Status Flags Explained

| Flag Pill | Lights Up When… |
|---|---|
| **ZERO** | Result equals 0 |
| **CARRY** | ADD/SUB generates a carry-out from the MSB |
| **OVF** | The signed result overflows the two's complement range |
| **SIGN** | The MSB of the result is `1` (negative value in signed arithmetic) |

Flag pills use a coloured border/text when **active** and a grey appearance when **inactive**.

### 4.6 Gate-Level Carry Chain (Right Canvas)

After computing, the right panel renders one **cell per bit**, from MSB (left) to LSB (right):

```
   Bit 7       Bit 6    ...    Bit 0
  ┌────────┐  ┌────────┐     ┌────────┐
  │ A: 0   │  │ A: 1   │     │ A: 1   │
  │ B: 1   │  │ B: 0   │     │ B: 1   │
  │  ADD   │  │  ADD   │     │  ADD   │
  │ = 1    │  │ = 1    │     │ = 0    │
  └────────┘  └────────┘     └────────┘
     ↑ C1        ↑ C0
```

- **Red carry arrows** appear between cells wherever a carry propagates from the lower bit.
- The chart title reflects the operation: e.g., `8-Bit ADD Chain`.

### 4.7 Operation History

The last **20 computations** are stored and displayed in a scrolling list:

```
A=42 ADD B=27 = 69 [Z=0 C=0 V=0 S=0]
A=200 ADD B=100 = 44 [Z=0 C=1 V=1 S=0]
```

The list auto-scrolls to the most recent entry.

---

## 5. Module 2 — Number Systems

> **Navigate**: Sidebar → 🔢 Number Systems

This module is a comprehensive number-system toolkit: live base conversion, two's complement analysis, step-by-step conversion walkthrough, and IEEE 754 single-precision encoding.

### 5.1 Entering a Value

1. Select the **Base** of your input from the drop-down:
   | Option | Base |
   |---|---|
   | Binary (2) | 2 |
   | Octal (8) | 8 |
   | **Decimal (10)** *(default)* | 10 |
   | Hex (16) | 16 |

2. Type the value in the **text field** below. All conversions refresh **live** on every keystroke.

### 5.2 All-Base Conversion Panel

Five read-only output fields show the same value in every number base simultaneously:

| Field | Description |
|---|---|
| Binary | Base-2 representation, zero-padded to the current bit width |
| Octal | Base-8 representation |
| Decimal | Unsigned base-10 |
| Signed Decimal | Two's complement signed value at the current bit width |
| Hexadecimal | Base-16, uppercase |

> **Note:** The toolbar's **bit-width selector** (4 / 8 / 16) determines how many bits are used
> for the Signed Decimal and Binary interpretations.

### 5.3 Two's Complement Analysis Panel

A read-only text area breaks down the two's complement process step by step:

```
Unsigned:  45
Binary:    00101101
Sign Bit:  0 (positive)
Inverted:  11010010
Add One:   11010011
Signed:    -45
```

| Line | Meaning |
|---|---|
| `Unsigned` | The raw unsigned decimal value |
| `Binary` | Full N-bit binary representation |
| `Sign Bit` | MSB value, with "positive"/"negative" label |
| `Inverted` | All bits flipped (bitwise NOT) |
| `Add One` | Inverted + 1 — this is the two's complement |
| `Signed` | The signed decimal interpretation |

### 5.4 Conversion Steps (Expandable)

Click **📋 Show Conversion Steps** to reveal a step-by-step repeated-division walkthrough showing how the value is converted from the input base to binary. Click again to hide.

Example (Decimal 45 → Binary):
```
45 ÷ 2 = 22 remainder 1
22 ÷ 2 = 11 remainder 0
11 ÷ 2 = 5  remainder 1
...
Read remainders bottom-up: 00101101
```

### 5.5 Bit Cell Visualisation (Right Canvas)

The canvas renders each bit as a coloured square, MSB on the left:

| Cell Colour | Meaning |
|---|---|
| **Red** | Most-significant (sign) bit |
| **Primary (blue/teal)** | Bit is `1` |
| **Neutral (grey)** | Bit is `0` |

- Cells with value `1` show a **power annotation** above: `2^n = <value>`
- Bit position index (n) is shown below each cell
- The chart title: `N-Bit Register Visualization`

### 5.6 IEEE 754 Float Analyser

Located at the bottom of the left panel under the section **"IEEE 754 Float Analyser"**.

**Steps:**
1. Enter any decimal float in the text field (e.g., `3.14`, `-0.001`, `255`, `Inf`).
2. Click **Analyse**.

**Text output format:**
```
Hex: 0x4048f5c3
Sign: 0  Exponent: 10000000 (128, bias=127)
Mantissa: 00010001111010111000011
Formula: (-1)^0 × 1.5707... × 2^1
```
For special values a `Special:` line appears (e.g., `Special: Positive Infinity`).

**Canvas** switches to the IEEE 754 32-bit layout:

```
S  EEEEEEEE  MMMMMMMMMMMMMMMMMMMMMMM
1  8 bits    23 bits
```
- 🔴 **Red** = Sign bit (bit 31)
- 🔵 **Blue (Primary)** = Exponent field (bits 30–23)
- 🟢 **Green (Tertiary)** = Mantissa/Fraction field (bits 22–0)
- The formula string is shown below the bit grid.

---

## 6. Module 3 — Gates & K-Map

> **Navigate**: Sidebar → 🔲 Gates & K-Map

Design a Boolean truth table with up to 4 variables, minimise it using the Quine-McCluskey algorithm, and view the resulting Karnaugh Map with prime implicant groups highlighted.

### 6.1 Selecting Variable Count

Choose **2**, **3**, or **4** variables from the **Count** drop-down. The truth table regenerates immediately — rows = 2^N.

### 6.2 Editing the Truth Table

The table has columns for each input variable (A, B, C, D) and one output column **F**.

- Input columns are **read-only** — they enumerate all minterm combinations automatically.
- Click any cell in the **F** column to **cycle its value**:

  ```
  0  →  1  →  X (don't-care)  →  0  →  ...
  ```

  | Value | Meaning |
  |---|---|
  | `0` | Output is LOW for this minterm |
  | `1` | Output is HIGH — this is a minterm to cover |
  | `X` | Don't-care — may be treated as 0 or 1 by the minimiser |

### 6.3 Solving (K-Map Minimisation)

Click **⚡ Solve**:

1. The Quine-McCluskey algorithm runs on your output vector.
2. The **SOP (Sum of Products)** expression is displayed below the table: e.g., `SOP: AB' + BC + A'C'`
3. The right canvas renders the **Karnaugh Map** with:
   - Cell values (0, 1, or X) displayed in each K-Map cell
   - **Prime implicant groups** drawn as semi-transparent coloured rectangles
   - A **legend** on the right side labelling each group's Boolean expression

> **Tip:** Don't-care cells (`X`) appear in red within the K-Map.

### 6.4 Exporting the Truth Table

Click **📋 Export CSV** to open a file-save dialog. The CSV includes input variable columns and the F column with 0/1/X values.

---

## 7. Module 4 — Sequential Logic

> **Navigate**: Sidebar → ≡ Sequential Logic

Simulate any of the four classic flip-flops cycle-by-cycle and view a professional timing diagram of the clock, inputs, Q, and Q-bar signals.

### 7.1 Supported Flip-Flop Types

| Type | Description | Next-State Equation |
|---|---|---|
| **D** | Data / Delay | Q⁺ = D |
| **T** | Toggle | Q⁺ = Q ⊕ T |
| **SR** | Set-Reset | S=1→Q⁺=1; R=1→Q⁺=0; S=R=1 is **invalid** |
| **JK** | Universal | J=K=0→hold; J=1,K=0→set; J=0,K=1→reset; J=K=1→toggle |

Select the flip-flop type from the **Flip-Flop Type** drop-down. The **Characteristic Table** below updates to show the state-transition truth table for that flip-flop.

> **Warning (SR):** Input combination S=1, R=1 is undefined. Any such cycle
> is highlighted in **red** on the timing diagram.

### 7.2 Configuring the Simulation

**Input sequence field** — Enter space-separated values:

| Flip-Flop | Token Format | Example |
|---|---|---|
| D | Single bit | `0 1 1 0 1 0 1 1` |
| T | Single bit | `1 0 1 1 0` |
| SR | Two-character (S then R) | `00 01 10 00 11` |
| JK | Two-character (J then K) | `10 11 01 00` |

**Initial Q spinner** — Set the starting state of the flip-flop output to `0` or `1`.

### 7.3 Running the Simulation

Click **▶ Run Simulation**. The timing diagram renders on the right canvas with these signals (top to bottom):

| Signal | Colour | Description |
|---|---|---|
| CLK | Grey | Clock waveform |
| D / T / S, R / J, K | Tertiary | Input signal(s) |
| Q | Primary (filled) | Flip-flop output |
| Q̄ | Secondary | Complement of Q |

Each signal is drawn as a **step waveform**. Invalid SR cycles are shaded with a light red background across all waveforms.

### 7.4 Exporting Simulation Data

Click **📋 Export CSV**. Exported columns:

```
Cycle, <Input Name(s)>, Q_before, Q_after, Invalid
```

The file-save dialog defaults to `timing_log.csv`.

---

## 8. Module 5 — Adder Types

> **Navigate**: Sidebar → ➕ Adder Types

Compare the three classic binary adder architectures on any two inputs. Visualise per-bit propagation delay and see how each architecture scales with bit width.

### 8.1 Setting Inputs

Enter two **decimal integers** in the **A** and **B** fields. Negative values and large numbers are accepted — the engine works at the bit width set by the toolbar.

### 8.2 Running the Comparison

Click **⚡ Compare Adders**. Three adder architectures are evaluated:

| Architecture | Delay Class | How It Computes |
|---|---|---|
| **Ripple Carry Adder (RCA)** | O(n) | Carry propagates sequentially, bit by bit |
| **Carry Lookahead Adder (CLA)** | O(log n) | Generate/Propagate signals computed in parallel blocks |
| **Carry Select Adder (CSA)** | O(√n) | Pre-computes both Cin=0 and Cin=1 results, selects when carry arrives |

The **Statistics** panel below shows for each adder:
```
<Name>: Result=<decimal>  |  Gates=<count>  |  Delay=<gate-delays>
```

### 8.3 Per-Bit Delay Chart (Right Canvas)

Three side-by-side **bar charts** appear, one per adder, with:
- X-axis: bit position (0 to N-1)
- Y-axis: delay in gate-delay units for each bit
- **Dashed red line**: critical-path delay (worst-case total, i.e., the MSB delay)

This makes it immediately clear how RCA's delay grows linearly while CLA stays nearly flat.

### 8.4 Scaling View

Click **📊 Show Scaling View** to replace the bar charts with a **line graph**:
- X-axis: bit width (4, 8, 12, 16)
- Y-axis: critical-path delay
- Three lines, one per adder type, with distinct markers

This demonstrates the asymptotic advantage of CLA and CSA architectures at higher bit counts.

---

## 9. Module 6 — Booth's Algorithm

> **Navigate**: Sidebar → ✖ Booth's Algorithm

Booth's algorithm multiplies two signed two's complement integers using a hardware-efficient sequence of add, subtract, and arithmetic right-shift operations. This module runs the full algorithm and lets you inspect every clock cycle.

### 9.1 Inputs

| Field | Spin Range | Description |
|---|---|---|
| **Multiplicand M** | −128 to 127 | Number to be multiplied |
| **Multiplier R** | −128 to 127 | The multiplier |
| **Bit Width** | 4, 6, 8 | Internal register precision |

> **Note:** Negative values are fully supported — Booth's algorithm is designed for
> signed two's complement operands.

### 9.2 Running the Algorithm

Click **▶ Run Booth's**:
1. All cycles are computed and the **Step Table** populates.
2. The **Result** label shows:
   ```
   Product: -15  (expected -15)  ✅ Correct
   Binary: 11110001
   ```
3. The canvas renders **Cycle 0** (initialisation).

### 9.3 Understanding Booth's Operations

At each cycle, the algorithm inspects the two-bit pattern `[Q[0], Q₋₁]`:

| Q[0] | Q₋₁ | Action | Effect |
|---|---|---|---|
| 1 | 0 | **ADD M** | A ← A + M, then arithmetic right shift |
| 0 | 1 | **SUB M** | A ← A − M, then arithmetic right shift |
| 0 | 0 | **NOP** | Arithmetic right shift only |
| 1 | 1 | **NOP** | Arithmetic right shift only |

### 9.4 Step Table

Columns: `Cycle  |  Action  |  A (accumulator bits)  |  Q (multiplier register)  |  Q₋₁`

- Each row is **read-only** and formatted in monospace binary.
- **Click any row** to jump the canvas to that cycle instantly.

### 9.5 Step Navigation

| Control | Action |
|---|---|
| **◀ Prev** button | Move to previous cycle |
| **Next ▶** button | Move to next cycle |
| **Step: X / N** label | Shows current position |
| Click step table row | Jump directly to any cycle |

### 9.6 Register Visualisation (Right Canvas)

The canvas is split into two sub-plots:

**Upper — Register State:**
- **A register** row (primary blue): each bit drawn as a coloured cell
- **Q register** row (tertiary green): each bit drawn as a coloured cell
- **Q₋₁** (secondary): single extra cell to the right of Q
- Large **action label** (e.g., `ADD M`) and the reason string above the registers

**Lower — History Chart:**
- Line plot of signed values of A and Q across all cycles up to the current step
- Useful for seeing convergence toward the final product

### 9.7 Exporting

Click **📋 Export CSV** (defaults to `booth_log.csv`). Columns:
```
Cycle, Action, A_bits, Q_bits, Q-1, A_signed, Q_signed
```

---

## 10. Module 7 — FSM Designer

> **Navigate**: Sidebar → 🔄 FSM Designer

Design Moore or Mealy finite state machines graphically. Add states and transitions interactively, simulate an input string, and minimise redundant states.

### 10.1 Machine Type Selection

| Type | Where Output is Defined |
|---|---|
| **Moore** | On each **state** — output depends only on current state |
| **Mealy** | On each **transition** — output depends on current state and input |

Choose from the **Machine Type** drop-down. Switch at any time; existing states and transitions are preserved.

### 10.2 Using Presets

The **Presets** group provides ready-made example FSMs:
1. Select a preset name from the drop-down.
2. Click **Load**.

The FSM resets to the preset's states, transitions, and start/accept markings. Useful for quick demos or learning.

### 10.3 Adding States

Fill in the **Add State** form:

| Field | Required | Description |
|---|---|---|
| Name | Yes | Unique identifier, e.g., `S0`, `IDLE`, `q_accept` |
| Output | No | Moore output string for this state; blank for Mealy FSMs |
| Start checkbox | — | Check to mark as the **initial state** (only one per FSM) |
| Accept checkbox | — | Check to mark as an **accepting / final state** |

Click **+ Add State**. The state circle appears on the canvas, arranged automatically on a circle.

### 10.4 Adding Transitions

Fill in the **Add Transition** form:

| Field | Required | Description |
|---|---|---|
| From | Yes | Name of the source state |
| To | Yes | Name of the destination state |
| Input | Yes | Input symbol (e.g., `0`, `1`, `a`) |
| Output | No | Mealy output symbol for this transition |

Click **+ Add Transition**. The arrow is drawn on the canvas immediately.

### 10.5 Reading the State Diagram Canvas

| Visual Element | Meaning |
|---|---|
| Plain circle | Regular state |
| Double-ring circle | Accepting / final state |
| Arrow entering from the left | Initial (start) state |
| Curved arrow between two states | Transition |
| Looping arc on a single state | Self-transition |
| Label on arrow | `input` (Moore) or `input/output` (Mealy) |
| Label inside circle | `name` (Moore) or `name\n/output` |
| Gold glow ring | State was visited during last simulation |

#### Dragging States

Click and drag **any state circle** to reposition it. All connected transition arrows redraw in real time.

### 10.6 Simulating an Input String

1. Enter your input string in the **Simulate** text field (e.g., `10110`, `abba`).
2. Click **▶ Run**.

**Verdict banner:**
| Outcome | Display |
|---|---|
| Final state is Accept | ✅ `ACCEPTED — Final state: <name>` (green) |
| Final state is not Accept | ❌ `REJECTED — Final state: <name>` (red) |

**Trace Table** — one row per input symbol consumed:

| Column | Meaning |
|---|---|
| Step | 0-indexed step number |
| State | Current state before consuming the input |
| Input | Input symbol consumed at this step |
| Next | State transitioned to |
| Output | Output produced (Mealy transition output, or Moore state output) |

All states visited during the simulation are highlighted with a **gold glow ring** on the canvas.

### 10.7 State Minimisation

Click **🔧 Minimize States**. The engine applies the **partition (table-filling) algorithm** to merge states that are behaviourally equivalent. The FSM updates in-place and the state diagram redraws with the reduced set of states.

---

## 11. Global Features

### 11.1 Light / Dark Theme

Click the **⚙ gear button** in the top-right toolbar. The entire application — all canvases, flag pills, sidebar, and panels — switches themes simultaneously. All subsequent diagrams will also use the correct palette.

### 11.2 Global Bit Width

The **4-bit / 8-bit / 16-bit** segment control in the toolbar is a global setting that applies to:

| Module | Effect of Changing Bit Width |
|---|---|
| ALU Simulator | Resizes bit-toggle rows; carry chain redraws with N cells |
| Number Systems | Adjusts register size for signed interpretation and bit-cell canvas |
| Adder Types | Changes the N used in the per-bit delay comparison |

> **Note:** **Booth's Algorithm** has its **own** bit-width selector (4/6/8) embedded in its input panel,
> independent of the global toolbar control.

### 11.3 CSV Export

Three modules support data export via a **📋 Export CSV** button:

| Module | Default Filename | Columns |
|---|---|---|
| Gates & K-Map | `truth_table.csv` | A, B, C, D, F |
| Sequential Logic | `timing_log.csv` | Cycle, inputs, Q_before, Q_after, Invalid |
| Booth's Algorithm | `booth_log.csv` | Cycle, Action, A_bits, Q_bits, Q-1, A_signed, Q_signed |

All exports use the native OS file-save dialog.

---

## 12. Keyboard & Mouse Reference

| Action | Method |
|---|---|
| Navigate to a module | Click sidebar item |
| Toggle an ALU bit | Left-click any bit button |
| Cycle a K-Map truth table output | Left-click the `F` cell (0 → 1 → X → 0) |
| Jump to a Booth step | Click the row in the Step Table |
| Drag an FSM state node | Left-click + hold + drag the state circle |
| Resize left / right panels | Drag the vertical splitter handle |
| Run computation / simulation | Click the primary action button in each module |
| Switch Light ↔ Dark theme | Click the ⚙ button in the top-right toolbar |
| Change bit width globally | Click 4-bit / 8-bit / 16-bit in the toolbar |

---

## 13. Troubleshooting

### The application doesn't start

- **Activate your virtual environment** before running `python main.py`.
- Run `pip install -r requirements.txt` to ensure all dependencies are present.
- Confirm Python version: `python --version` — must be **3.10 or higher**.
- Run `python -c "import PyQt6; import matplotlib"` to verify imports.

### The canvas / diagram is blank after I click Compute / Run

- Drag the splitter handle to trigger a canvas resize repaint.
- Confirm you clicked the correct action button — results are **not automatic** in most modules.

### Booth's Algorithm shows ❌ Mismatch

- The selected **Bit Width** is likely too small to represent the full product of M × R. Increase to 6 or 8 bits. For example, 5 × −3 = −15, which needs at least 6 bits for correct representation.

### K-Map SOP shows only "—" or seems incomplete

- At least one output cell must be set to `1`. If every cell is `0` or `X`, no minterms exist to cover.
- Click **⚡ Solve** after placing at least one `1` in the F column.

### FSM simulation gives REJECTED when I expect ACCEPTED

- Verify at least one state has the **Accept checkbox** checked — double rings should appear on the canvas for accepting states.
- Check the **Start** state is marked — an entry arrow should appear to its left on the canvas.
- Ensure a valid transition exists for **every input symbol from every state** — undefined transitions cause early termination.
- The input string must use only symbols that appear in at least one transition label.

### SR Flip-Flop shows red-highlighted cycles

- Red cycles mean your input contained the combination **S=1, R=1** (the undefined state). Remove any `11` tokens from your input sequence.

### High-DPI / blurry display on macOS

- LogiCraft sets `QT_ENABLE_HIGHDPI_SCALING=1` automatically on launch. If the UI still appears blurry, try setting the environment variable manually before launching:
  ```bash
  export QT_ENABLE_HIGHDPI_SCALING=1
  python main.py
  ```

---

*LogiCraft — Digital Design Studio | Karunya University COA Micro-Project | Even Semester*
