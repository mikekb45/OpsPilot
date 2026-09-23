# Authentication Service

Verifies the customer session before an order is accepted by the order
service. Unrelated to payment processing - authentication happens before
an order exists at all, payment happens after.

## Common failure modes

- An authentication outage prevents *new* orders from being submitted in
  the first place - existing orders already in the queue are unaffected
  and continue processing normally.
- Symptom to watch for: a sudden drop in new order volume with no
  corresponding queue or database errors usually points here, not to the
  order pipeline itself.

## Escalation

Authentication issues are owned by the identity team, not the order
pipeline team - a queue or database investigation will not find an
authentication problem, since auth happens upstream of both.
