# Order Database

Stores confirmed orders once the queue processor writes them. Uses a
connection pool shared across the order service, the queue processor, and
the reporting service.

## Common issues

- **Connection pool exhaustion**: if the reporting service runs a long
  query, it can hold connections long enough that the queue processor
  can't get one, which looks like a queue problem but is actually a
  database contention problem.
- **Payment failures are not a database issue**: a failed payment never
  reaches the database at all - it's rejected upstream, in the queue, so
  database health checks will look completely normal even during a wave
  of payment failures.

## Escalation

Slow queries and pool exhaustion should go to the database on-call.
Do not restart the database to "clear" a stuck queue - the queue and
database are separate failure domains, and restarting the database
will not un-stick a queue that's blocked for a non-database reason.
