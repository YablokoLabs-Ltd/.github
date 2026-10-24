# Agensi listing: QuantumClaw Route Optimizer

Copy-paste values for https://www.agensi.io/dashboard/submit, one section per
form step. Upload `quantumclaw-route-optimizer.zip` in Step 1, and `logo.png`
as the skill logo.

The demo in Step 3 is real output from the São Paulo example bundled in the
skill (seeds 1–5). It was run with the QuantumClaw main branch and the D-Wave
bridge installed from git.

---

## Step 2: Skill details

**Skill name** (34/60)

```
QuantumClaw Delivery Route Optimizer
```

**Summary**

```
Plan and benchmark delivery routes with classical and quantum-inspired solvers, ranked on plans that serve every stop.
```

**Full description**

```markdown
Give your agent a list of stops, vehicles and a depot, and get back optimized delivery routes plus an honest comparison of how different solvers did on *your* data.

Built on [QuantumClaw](https://github.com/yablokolabs/QuantumClaw), an open-source Rust runtime from Yabloko Labs for hybrid classical and quantum-inspired planning.

### What it does

1. **Builds the problem.** Converts a CSV, spreadsheet export or JSON of stops into a validated routing problem with vehicle capacities, time windows, cost per km, fuel and CO2.
2. **Benchmarks solvers side by side.** Runs a classical heuristic, simulated annealing and a quantum annealing emulator, five times each with fixed seeds, so results are reproducible.
3. **Ranks them fairly.** A plan that serves every delivery always beats a cheaper plan that strands one. Ties go to the lower *median* cost, not the luckiest run.
4. **Compares against what you do today.** Give it your current routes and it reports km, cost, fuel and CO2 saved, and flags constraints your current plan breaks (like an overloaded truck).
5. **Writes a Markdown report** with the recommended route for each vehicle.

### Why it's different

- **No hype.** The skill tells your agent exactly what each solver is. Simulated annealing is classical. The quantum annealing emulator runs on your CPU. Nothing claims to have run on a quantum computer unless it really did.
- **Runs offline.** No API keys or cloud accounts for the local solvers. Your delivery data stays on your machine.
- **Scales by decomposition.** Large fleets are split by depot, geography, capacity or time window automatically.
- **Optional real hardware.** If you have a D-Wave Leap token, the same workflow can run on Leap hybrid or a D-Wave QPU.

### Good for

- Last-mile and courier operations checking whether their current routes are wasting km
- Ops and data teams that want a reproducible routing benchmark, not a black box
- Developers exploring quantum-inspired optimization on a real problem

### What's included

- `SKILL.md`: the step-by-step workflow and reporting rules
- `scripts/csv_to_qrouter.py`: CSV to problem-file converter
- `scripts/best_plan.py`: picks the best feasible plan across seeds
- `scripts/report.py`: benchmark JSON to Markdown report
- `references/input-format.md`: full input schema, including real road-distance matrices
- Two example datasets (São Paulo and London)

### Known limits (stated up front)

- Distances default to straight-line estimates unless you provide a road-distance matrix.
- Time windows are scored (late minutes count against a plan) but not enforced while routes are built.
- Pickup-and-delivery pairs, driver breaks and multi-day plans are not modelled yet.
```

---

## Step 3: Demo

**The request (what the buyer types)**

```markdown
I run morning deliveries out of our São Paulo depot with 2 trucks (capacity 12) and 1 van (capacity 8). Here are today's 7 stops and how we currently route them: `examples/sao-paulo-deliveries.json`.

Can you find a better plan? Compare the solvers properly and tell me what we'd save versus our current routes.
```

**The result (what your agent delivers)**

```markdown
## Summary

Your current plan **overloads truck-2** (14 units on a 12-unit truck), so it can't actually be run as written. The best plan that serves all 7 stops within capacity uses the same 3 vehicles and cuts the benchmark median cost by **10.2%** and distance by **12.1%**. The best single seeded plan (below) goes further: 61.6 km and a cost of 226.39, down from 78.0 km and 267.28.

**Recommendation:** use the `dwave-sa` plan below. It was the only solver that served every stop on all 5 runs.

## Solver comparison: `sao-paulo-morning`

| Plan | What it is | Feasible runs | Median cost | Spread (sd) | Distance km | Served | Late | CO2 kg |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | your current plan | no | 267.28 | — | 78.0 | 7/7 | 0 | 48.9 |
| classical | classical greedy heuristic | 0/5 | 234.49 | 0.00 | 63.6 | 6/7 | 0 | 38.7 |
| **dwave-sa** (winner) | classical simulated annealing (D-Wave Ocean, local CPU) | 5/5 | 239.95 | 13.36 | 68.5 | 7/7 | 0 | 37.3 |
| dwave-sqa | quantum annealing emulator (local CPU, not a QPU) | 4/5 | 229.42 | 11.84 | 60.1 | 7/7 | 0 | 35.7 |

Ranking rule: plans that served every delivery on more runs rank first, then lower median cost. Seeds 1–5; re-running with the same seeds reproduces this table exactly.

**How to read this:**
- The **classical** heuristic looks cheap, but it leaves one stop undelivered on every run. Your fleet is at 94% capacity, and greedy packing gets stuck at that level.
- The **quantum annealing emulator** (`dwave-sqa`) found the cheapest plans on average, but missed a stop on 1 of 5 runs, so it ranks second.
- **`dwave-sa`** served every stop on every run. It is classical simulated annealing over a QUBO model, not quantum hardware.

## `dwave-sa` compared with your current plan (benchmark median)

| Metric | Saved | Change |
| --- | --- | --- |
| Distance | 9.4 km | 12.1% |
| Operating cost | 27.33 | 10.2% |
| CO2 | 11.6 kg | |
| Fuel | 4.3 l | |

## Recommended routes

Solved with `dwave-sa`, best feasible plan across seeds 1–5 (seed 1).

| Vehicle | Stops in order |
| --- | --- |
| truck-1 | depot-sp → santana-1 → pinheiros-1 → pinheiros-3 → depot-sp |
| truck-2 | depot-sp → tatuape-1 → tatuape-2 → depot-sp |
| van-1 | depot-sp → santana-2 → pinheiros-2 → depot-sp |

Total **61.6 km**, 115 min driving, cost **226.39**, CO2 **32.9 kg**, 0 late, capacity used 94%.

**Next steps**
- Distances are straight-line estimates. Send me a road-distance matrix (or allow a routing API) and I'll re-run on real roads.
- With capacity this tight, one extra parcel will break any plan. Consider adding a van on heavy days.
- Re-run this benchmark weekly on real stop lists to see which solver wins on your typical day.
```

---

## Step 4: Compatibility note

```
Requires Rust/cargo (one-time ~5 min build of the quantumclaw CLI) and Python 3.9+ for the D-Wave Ocean solvers. Runs fully offline; no API keys for local solvers. Tested on Linux.
```

---

## Step 5: Pricing

**Free** is my recommendation (see the chat for why).

---

## Tags, categories, use cases

- **Tags:** route-optimization, logistics, vrp, delivery, fleet, quantum, qubo, d-wave, optimization, benchmarking, rust
- **Category:** Data & Analytics (or Operations / Logistics if listed)
- **Use cases:** last-mile delivery planning, fleet route audits, solver benchmarking, quantum-inspired optimization experiments

---

## Permissions

**Required tools & software** (one per line)

```
Rust toolchain (cargo)
Python 3.9+
quantumclaw CLI (installed by the skill from github.com/yablokolabs/QuantumClaw)
quantumclaw-dwave Python bridge (optional, for D-Wave solvers)
```

**Tools used:** tick **Terminal / Shell**, **Read Files**, **Write Files**, **Network Access**, **Environment Variables**. Leave **Browser** unticked.

**Needs access to:** leave empty. For "Other tool", optionally add `dwave.com`, used only if the buyer chooses the cloud D-Wave solvers.

**File scopes**

```
*.csv
*.json
route-report.md
.quantumclaw-venv/**
```

**Notes**

```
Shell runs the quantumclaw CLI and the bundled Python scripts. Network access is only needed once, to install the CLI (cargo, from GitHub) and the solver bridge (pip). Routing itself runs offline. Environment variables: QUANTUMCLAW_DWAVE_PYTHON points to the solver bridge; DWAVE_API_TOKEN is only read if the buyer explicitly opts into D-Wave cloud solvers. Delivery data never leaves the machine with the local solvers.
```

---

## FAQ

**Does this run on a quantum computer?**
Not by default. The local solvers are a classical heuristic, classical simulated annealing, and a quantum annealing *emulator* running on your CPU. If you have a D-Wave Leap token, you can opt into D-Wave's hybrid solver or QPU.

**Do I need an API key or account?**
No. Everything runs locally. A D-Wave token is only needed for the optional cloud solvers.

**How big a problem can it handle?**
Small and medium instances solve in one piece. Larger ones are split automatically by depot, geography, capacity or time window, so each piece stays small enough for the solvers.

**Does it use real road distances?**
By default it uses straight-line (haversine) distances with an average speed. Supply your own distance/duration matrix for real roads.

**Why did the "cheaper" solver lose?**
Because it left a delivery unserved or broke a capacity limit. A plan that can't be executed isn't cheaper.

**Is it open source?**
Yes. The engine is MIT-licensed at github.com/yablokolabs/QuantumClaw.

---

## Extra details

- **Documentation URL:** `https://github.com/yablokolabs/QuantumClaw/blob/main/docs/brains/qrouter.md`
- **Website:** `https://yablokolabs.com`
- **Source:** `https://github.com/yablokolabs/QuantumClaw`
- **Screenshots:** `screenshot-report.png` (the rendered demo report)
- **Demo video:** optional. A 30-second screen recording of Claude Code running the skill on `examples/sao-paulo-deliveries.json` would work well.
