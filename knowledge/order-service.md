# Order Service

The order service accepts incoming orders from the storefront and pushes
them onto the order queue for processing. It does not talk to the database
directly - all persistence happens further down the pipeline, once the
queue processor picks an order up.

## Common failure modes

- If the order queue is blocked or its depth is growing, orders will
  appear "stuck" even though the order service itself reports healthy.
- If authentication is failing upstream, orders never reach the service at
  all - this looks like *no* new orders, not stuck ones.
- The order service retries a failed queue push up to 3 times before
  giving up and logging an error.

## Escalation

Order service issues that are actually queue or database problems should
be routed to the on-call queue/database owner, not the order service team.
