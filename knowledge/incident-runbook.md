# Incident Response Runbook

General process for investigating "orders have stopped/slowed" reports.

## Investigation order

1. Check queue depth and status first - it's the most common bottleneck
   and the fastest thing to check.
2. If the queue shows a specific recurring error (e.g. repeated failures
   for the same service), investigate that service directly rather than
   the queue itself - the queue is usually a symptom, not the cause.
3. Only escalate to the database team if there's evidence of pool
   exhaustion or slow queries, not just because the queue is backed up -
   most queue backups are not database problems.
4. Only escalate to the identity team if new order *volume* has dropped,
   not if orders are stuck partway through processing - those are
   different failure modes with different owners.

## Confidence guidance

Report a diagnosis as confident only when the evidence directly matches a
known failure mode above. If the evidence is ambiguous or doesn't clearly
match one pattern, say so explicitly rather than guessing - a wrong
confident diagnosis sends the wrong team chasing the wrong problem.
