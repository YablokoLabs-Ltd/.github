# Yabloko Labs

**Infrastructure for verifiable autonomous systems.** — [yablokolabs.com](https://yablokolabs.com)

We build agent infrastructure where the planning, the representation, and the trust layers are separable, inspectable components — not prompt engineering. Two commitments run through everything here: **machine-checked proofs** in Lean 4 for the core algebra of our representation and trust layers, and **deterministic policy** that decides what an agent may execute. The planner proposes. The policy engine decides. A model cannot talk its way past it.

## The Stack

**[QuantumClaw](https://github.com/yablokolabs/QuantumClaw)** — *runtime*
A Rust agent runtime where planning is a first-class, swappable component. Classical solvers today, quantum-inspired now, QPU backends later, with no application rewrite when the backend changes. ShadowCompare runs two planners side by side so you can measure the tradeoff instead of guessing.

**[nexa-core](https://github.com/yablokolabs/nexa-core)** — *representation*
A universal representation runtime. Encode text, JSON, images, audio, or sensor streams into high-dimensional holographic hypervectors and compute directly in encoded space — no tensor pipeline. Corruption-resilient, SIMD-accelerated, 27 Lean 4 theorems on the core algebra.

**[jnaapakam](https://github.com/yablokolabs/jnaapakam)** — *memory*
An open protocol for agent memory persistence. A portable soul schema plus an ingest → consolidate → query server, so an agent's identity and context survive restarts and move between frameworks.

**[truthlens](https://github.com/yablokolabs/truthlens)** — *trust*
Hallucination detection and trust scoring for LLM output. Zero API calls, zero model inference, runs locally in microseconds. Every scoring property — bounds, monotonicity, composition — proven in Lean 4.

**[gridcrawler-agent](https://github.com/yablokolabs/gridcrawler-agent)** · **[hermes-sentinel](https://github.com/yablokolabs/hermes-sentinel)** — *reference agents*
Working systems that show the boundaries in practice. GridCrawler retrieves utility billing data and structurally cannot make a payment. Hermes Sentinel performs Kubernetes root-cause analysis and structurally cannot mutate a workload. Both treat observed content as untrusted input.

**[quantaforge](https://github.com/yablokolabs/quantaforge)** — *quantum*
Simulation-first quantum platform: state-vector and stabilizer simulators, surface-code and LDPC error correction, Lean 4 proofs of the underlying gate algebra. Simulation software, honestly scoped — not hardware control.

## MCP Servers

Three layers ship as Model Context Protocol servers, usable from Claude, Cursor, VS Code, or any MCP client.

| MCP | What it gives your agent |
| --- | --- |
| **[Jñāpakam](https://mcpize.com/mcp/jnaapakam)** | Persistent long-term memory — ingest, consolidate, and query context that survives restarts. |
| **[TruthLens](https://mcpize.com/mcp/truthlens)** | Formally verified trust scoring — analyze claims, detect contradictions, extract entities. No API keys. |
| **[NexaCore](https://mcpize.com/mcp/nexa-core)** | Hyperdimensional computing — encode, compress, forge models, and query in geometric algebraic space. |

## Products

| Brand | |
| --- | --- |
| **[Q-Router™](https://router.yablokolabs.com)** | Quantum-enhanced delivery route optimization with AI traffic prediction. |
| **[Q-AdMix™](https://admix.yablokolabs.com)** | Hybrid quantum-classical optimization for ad spend allocation. |
| **[Q-Porter™](https://porter.yablokolabs.com)** | Quantum-AI scheduling and throughput optimization for ports and airports. |
| **[Q-Consent™](https://consent.yablokolabs.com)** | Quantum-AI consent and compliance management for GDPR and HIPAA workflows. |

---

Yabloko Labs Ltd · London · [ceo@yablokolabs.com](mailto:ceo@yablokolabs.com)
