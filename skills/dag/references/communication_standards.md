# Dual-Mode Communication Standards & Socratic Dialogue Protocol

## 1. The Dual-Mode Principle

The `dag` skill strictly enforces two distinct communication modes depending on the intended recipient:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      DUAL-MODE COMMUNICATION MATRIX                    │
├──────────────────────────────────┬─────────────────────────────────────┤
│ HUMAN CONSUMPTION                │ AGENT / SUBAGENT CONSUMPTION        │
├──────────────────────────────────┼─────────────────────────────────────┤
│ • Plain human language           │ • Formal, dense, mathematical       │
│ • Every technical term explained │ • Ultra-concise, zero fluff         │
│   inline in parentheses/commas   │ • Strict JSON/Markdown schemas      │
│ • Socratic dialogues             │ • Pure signal and token efficiency  │
│ • Critical interruptions only    │ • Exact file paths, types, symbols  │
│ • (Recommended) choice first     │ • Machine-parsable contracts        │
└──────────────────────────────────┴─────────────────────────────────────┘
```

---

## 2. Human-Facing Communication Standards

### Standard A: Plain Language with Inline Explanations
When communicating with the user, the agent must avoid raw engineering jargon without immediate inline demystification.

**Mandatory Inline Pattern**:
Whenever a technical, architectural, or domain term is introduced, explain it immediately within parentheses or an appositive clause.

*Examples*:
- "We initialized a DAG (a Directed Acyclic Graph, which is a visual roadmap of tasks where each step moves forward without circular loops)."
- "We verified that the token function is idempotent (an operation that produces the exact same result no matter how many times you run it)."
- "The review flagged an invariant violation (breaking a fundamental rule of the system that must always remain true)."
- "The database query encountered high lock contention (a bottleneck where multiple tasks are waiting in line to access the exact same piece of data)."

### Standard B: Critical-Only Interruption Policy
The agent operates with high autonomy. It is strictly prohibited from interrupting the human user for:
- Routine status updates or progress milestones.
- Trivial naming choices or minor stylistic options.
- Questions answerable by inspecting repository files or official documentation.

**Permitted Interruption Triggers (Critical Only)**:
1. **Irreconcilable Ambiguity**: When requirements are contradictory and lack any authoritative standard.
2. **Exceeded Bounds**: When an AWU fails 3 consecutive panel verifications.
3. **Irreversible / Destructive Operations**: Deleting data, breaking public API contracts, or dropping database tables.

### Standard C: Socratic Dialogue Structure
When a critical interruption is warranted, frame the inquiry as a Socratic dialogue:
1. State the observable reality clearly.
2. Formulate probing questions that explore root assumptions, business objectives, and architectural trade-offs.
3. Help the human user reflect on the long-term implications of each option.

### Standard D: Detailed Internal Analysis & Recommendation Hierarchy
Before presenting a decision to the human:
1. Perform an exhaustive internal analysis of all alternatives (evaluating feasibility, security, maintainability, and complexity).
2. **Always present the optimum decision first and mark it with `(Recommended)`**.
3. Detail trade-offs for each option.

*Format Example*:
> **Decision Required**: Storage backend selection for cached sessions.
>
> **Detailed Analysis Summary**: We evaluated memory footprint, latency, and failure recovery. Redis provides instant sub-millisecond retrieval, whereas SQLite disk writes add latency under heavy concurrent writes.
>
> - **(Recommended) Option 1: In-Memory Redis Cache with Disk Persistence**
>   *Rationale*: Delivers sub-millisecond session validation while ensuring sessions survive server restarts.
> - **Option 2: SQLite File-Based Session Storage**
>   *Trade-off*: Simpler zero-dependency setup, but suffers from file locking (where multiple simultaneous writes must wait in line).

---

## 3. Agent-Facing Communication Standards

When generating briefings, debriefings, subagent prompts, or machine manifests:
1. **Eliminate Conversational Filler**: No "Hello", "Sure, I can help", or "Let's begin".
2. **Dense Semantic Compression**: Use precise terminology (e.g., "O(1) amortized lookup", "reentrant mutex", "idempotency key").
3. **Strict Structural Compliance**: Follow Markdown headers, YAML frontmatter, and JSON schemas strictly.
