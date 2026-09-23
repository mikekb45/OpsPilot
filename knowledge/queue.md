# Order Queue

The order queue holds orders between submission and database write. A
healthy queue processes orders within a few seconds of arrival; a growing
queue depth means orders are arriving faster than they're being drained.

## Common causes of a blocked or growing queue

- **Payment failures**: an order that fails payment processing is retried
  automatically, which can back up the queue if failures are frequent.
- **Downstream database issues**: if the database is slow or unreachable,
  the queue processor can't drain orders, and depth climbs even though the
  queue itself is "up."
- **Low stock holds**: an order for an out-of-stock item is held rather
  than failed outright, which also increases depth without an outright
  error.

## What healthy looks like

Queue depth fluctuating in a normal range with status "Processing" is
expected. A depth that's high *and* growing over repeated checks, combined
with a specific recurring error (e.g. repeated payment failures for the
same order), points to a real underlying issue rather than normal load.
