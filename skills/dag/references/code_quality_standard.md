# Code Quality & Comprehensive Documentation Standards

## 1. Core Principles for Code Authorship

When authoring or modifying code within the `dag` skill, the Maker agent must uphold three non-negotiable standards:

1. **Extensive Documentation**: Every module, class, interface, method, and non-trivial function must have comprehensive, self-describing documentation.
2. **Contractual Pre- and Post-Conditions**: Every public function must specify its required entry state (pre-conditions) and guaranteed exit state (post-conditions).
3. **Deep Knowledge with Inline Explanations**: Code documentation must demonstrate masterful understanding of computer science principles while explaining complex programming terms inline in accessible human language.

---

## 2. Function & Method Documentation Specification

Every function must include a docstring/documentation block structured as follows:

```typescript
/**
 * Validates and decodes an encrypted authentication token.
 *
 * This function is idempotent (an operation that can be executed repeatedly without
 * changing the final result beyond the initial execution). It ensures thread safety
 * through immutability (meaning the data structures cannot be altered once created).
 *
 * @param token - The raw base64-encoded encrypted token string received from the client.
 *                Must not be null, empty, or exceed 4096 bytes.
 * @param secretKey - The 256-bit symmetric cryptographic key used to verify the HMAC signature.
 *                    Must be exactly 32 bytes in length.
 * @param maxClockSkewSeconds - Maximum allowed time drift in seconds between client and server clocks.
 *                              Defaults to 60 seconds to tolerate minor network latency.
 *
 * @precondition `token` is non-empty and well-formed base64.
 * @precondition Cryptographic subsystem has completed initialization.
 *
 * @postcondition Returns a frozen, validated `UserClaims` object if the signature and expiration check pass.
 * @postcondition No state outside this function is mutated (pure function guarantee).
 *
 * @throws {TokenExpiredError} If current system epoch timestamp exceeds the `exp` claim.
 * @throws {CryptographicVerificationError} If the HMAC signature check fails, indicating potential tampering.
 * @throws {IllegalArgumentError} If the token string is malformed or exceeds maximum length.
 *
 * @returns A decoded, immutable `UserClaims` record containing the authenticated user's identity.
 */
export function verifyAuthToken(
  token: string,
  secretKey: Buffer,
  maxClockSkewSeconds: number = 60
): Readonly<UserClaims> {
  // Implementation...
}
```

---

## 3. Explaining Complex Programming Terms Inline

Documentation must be written with the confidence of a principal engineer while explaining nuanced concepts inline for human collaborators.

### Required Inline Explanation Style:
- **Memoization**: `memoization (a performance optimization technique where expensive function results are cached and reused when identical inputs occur again)`.
- **Reentrancy**: `reentrancy (the ability of a routine to be interrupted in the middle of execution and safely called again before its previous executions finish)`.
- **Backpressure**: `backpressure (a flow-control mechanism that signals the producer to slow down when the consumer cannot keep up with the volume of incoming data)`.
- **Idempotency**: `idempotency (a property where performing an action multiple times produces the exact same outcome as performing it once)`.
- **Deadlock**: `deadlock (a frozen state where two processes are permanently stuck because each is waiting for a resource held by the other)`.
- **Invariant**: `invariant (a core rule or condition that must always remain true throughout the entire lifecycle of the program)`.

---

## 4. Module & File-Level Documentation Header

Every newly created or refactored source file must begin with a standardized module docstring:

```typescript
/**
 * @file session_store.ts
 * @module auth/session
 *
 * @description
 * High-performance, distributed session persistence layer utilizing Redis.
 *
 * @architecture
 * Implements the Repository Pattern (a design approach that isolates the data access
 * logic from the business layer). All database operations are wrapped in atomic transactions
 * (operations that succeed completely or fail with zero partial changes).
 *
 * @invariants
 * 1. Session IDs are cryptographically random 128-bit identifiers.
 * 2. Stored session data is serialized as canonical JSON with strict schema validation.
 * 3. Connection pools are gracefully drained during process termination.
 */
```

---

## 5. Final Adversarial Analysis for Code Changes

Before any code is finalized, the **Phase 5 3-Agent Adversarial Panel** conducts a comprehensive side-effect audit:
1. **Regression Scan**: Proves no existing caller interfaces or return types were broken.
2. **Blast Radius Analysis**: Proves no unbudgeted CPU spikes, memory leaks, or file handle leaks were introduced.
3. **Invariant Preservation Check**: Audits that all cataloged system invariants remain strictly intact.
