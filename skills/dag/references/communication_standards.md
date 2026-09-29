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
1. **Phase 1.5 Layered Socratic Input Clarification Gate**: Resolving unstated boundary conditions, contractual ambiguities, or timeout semantics identified post-cartography.
2. **Execution-Phase Assumption Invalidation Human Gate**: When active execution or testing unearths empirical evidence contradicting an earlier assumption.
3. **Exceeded Iteration Bounds**: When an AWU reaches 3 consecutive panel rejections without passing.
4. **Irreversible / Destructive Operations**: Deleting production data, dropping database tables, or breaking public API contracts.

### Standard C: Formal Socratic Dialogue Protocol
Whenever human clarification or sign-off is required, the inquiry MUST strictly adhere to the **Formal Socratic Dialogue Protocol**:

1. **Strictly ONE Question Per Dialogue Turn (Single-Question Discipline)**:
   - Batching or prompt-stuffing multiple questions into a single message is **strictly prohibited**.
   - If multiple ambiguities exist, conduct a sequential series of single-question dialogues ($Q_1 \to A_1 \to Q_2 \to A_2 \to \dots$).
   - The question must be crisp, targeted, and conclude with a question mark.

2. **Observable Reality & Context First**:
   - Begin by presenting the concrete, observable facts: repository file paths, test results, error traces, or unstated specifications.
   - Clearly state why this decision is critical to preventing hallucinations or architectural regressions.

3. **Thorough Evaluation of All Viable Options**:
   - Must present at least 2 distinct, realistic options.
   - For each option, provide:
     - A plain-language summary of what the option entails.
     - Explicit positive benefits (**Pros**).
     - Explicit trade-offs, limitations, or downsides (**Cons**).
     - A deep architectural **Trade-off Analysis** detailing long-term maintainability, security, and performance impact.

4. **Recommendation Hierarchy (Best Option First)**:
   - The optimal, safest, and most maintainable choice MUST always be presented as **Option 1**.
   - Option 1 MUST be explicitly marked with the `(Recommended)` prefix.
   - Subsequent options follow in descending order of desirability.

5. **Plain Human Language & Inline Demystification**:
   - All dialogues must be accessible to human stakeholders without engineering ambiguity.
   - Whenever a technical term is introduced (e.g., *idempotency*, *concurrency*, *pessimistic lock*, *SMT solver*, *AST mod*), explain it immediately inline within parentheses or commas:
     - *Compliant*: "We will enforce idempotency (a safety mechanism ensuring that if an action runs twice due to network retries, the result is identical)."
     - *Non-compliant*: "We will enforce an idempotent deduplication key with a distributed lease."

### Standard D: Canonical Socratic Dialogue Template

```markdown
### [Socratic Clarification: <Inquiry Moniker>]
**Context & Observable Reality**:
During our codebase mapping (Cartography), we observed that the session token handler in `src/auth/token.ts` issues authentication tokens without an explicit expiration window or database revocation table. If left unspecified, the agent would be forced to guess a timeout, creating an unverified assumption.

**Target Question**:
Which session expiration and token revocation strategy should we formally enforce to protect user sessions?

**Evaluated Alternatives**:

#### (Recommended) Option 1: Bounded JWT with Cryptographic TTL and Redis Revocation Denylist
- **Explanation**: We set a 15-minute expiration deadline on tokens (TTL, or Time-To-Live) and store revoked tokens in an in-memory database (Redis) so stolen tokens can be cancelled instantly.
- **Pros**:
  + Delivers immediate revocation capability if a user logs out or changes passwords.
  + Extremely fast sub-millisecond token verification.
- **Cons**:
  - Requires a running Redis cache instance.
- **Trade-off Analysis**: Balances low latency with instant security revocation. Best for production systems where compromised sessions must be invalidated immediately.

#### Option 2: Stateless Self-Contained JWT Tokens with Long Expiration
- **Explanation**: We issue digital tokens that remain valid for 24 hours without checking any database or cache.
- **Pros**:
  + Zero external database dependencies; token verifies purely by math.
- **Cons**:
  - Cannot cancel or revoke a stolen token until the full 24 hours have elapsed.
- **Trade-off Analysis**: Easy to build initially, but introduces a major security risk because revoked or stolen tokens cannot be blocked.
```

## 3. Agent-Facing Communication Standards

When generating briefings, debriefings, subagent prompts, or machine manifests:
1. **Eliminate Conversational Filler**: No "Hello", "Sure, I can help", or "Let's begin".
2. **Dense Semantic Compression**: Use precise terminology (e.g., "O(1) amortized lookup", "reentrant mutex", "idempotency key").
3. **Strict Structural Compliance**: Follow Markdown headers, YAML frontmatter, and JSON schemas strictly.
