---
{
  "kind": "post",
  "publishedAt": "2026-11-22T21:00:52+09:00",
  "updatedAt": "2026-11-22T21:00:52+09:00",
  "reviewedAt": "2026-11-22",
  "reviewStatus": "source-audited",
  "reviewScope": "Checked Stripe’s idempotency and webhook guidance and AWS’s transactional outbox guidance. Verified seven sequential state transitions on JDK 21.0.1. Database races, provider integration, and production payments require separate verification.",
  "reviewSources": [
    "https://docs.stripe.com/api/idempotent_requests",
    "https://docs.stripe.com/webhooks#event-delivery-behaviors",
    "https://docs.stripe.com/webhooks#handle-duplicate-events",
    "https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html"
  ],
  "translationKey": "2026-11-22-commerce-system-design-last-unit-of-stock",
  "routeSlug": "2026-11-22-commerce-system-design-last-unit-of-stock",
  "categories": [
    "architecture"
  ],
  "tags": [
    "ecommerce",
    "inventory",
    "payments",
    "transactional-outbox"
  ],
  "language": "en",
  "title": "Commerce System Design: Who Gets the Last Unit of Stock?",
  "description": "Use the last unit of stock to examine SKU reservations, payment reconciliation, and refunds after a reservation is released."
}
---

**When two customers try to check out with the last unit of a product, only one order should be able to reserve it.** If the store reserves the unit and then loses the payment provider's response, the order stays pending while the store verifies the payment. If the store later confirms payment after releasing the reservation, it keeps the order canceled and requests a refund. Following one purchase shows which data the catalog, inventory, orders, and payments each own.

The example follows a single merchant that sells physical goods, takes one payment in Korean won (KRW) per order, and ships from one warehouse. It covers cancellations and refunds for unresolved and late payments. Marketplace settlements, partial shipments, and returns are outside this example's scope.

## Stock shown on the product page and stock held for an order

A **product** is the catalog entry customers see. A **SKU** (stock keeping unit) is what the store tracks for orders and inventory. The white and black versions of the same keyboard have different SKUs. The product page shows availability at the time of lookup. If the inventory module fails to respond, the page still shows the product and marks availability as “Checking stock.” Adding an item to the cart leaves inventory unchanged.

| Responsibility | Data it can change | Example |
| --- | --- | --- |
| Catalog and pricing | Products, SKUs, whether items are for sale, current unit prices | Change the unit price of the black keyboard, `KB-BLK` |
| Inventory | Physical stock by warehouse, reservations, fulfillment allocations | Reserve one `KB-BLK` for a specific order |
| Orders | Buyer, order lines and amounts at the time of purchase, order status | Save quantities, unit prices, discount allocation, and shipping fees for order `O-42` |
| Payments | Payment attempts, provider transaction IDs, payment and refund status | Reconcile the provider result for attempt `P-1` |
| Fulfillment | Fulfillment requests and their progress | Pick an order after payment and inventory allocation |

Just before checkout, the server checks whether the items are still for sale and rechecks their prices. It identifies the buyer from the authenticated session and calculates the total using its own pricing, discounts, and shipping rules. If the black keyboard was KRW 39,000 when the customer added it to the cart and it now costs KRW 42,000, the store shows the new amount and asks the customer to confirm it. During order creation, the server checks that the price version the customer accepted matches the version it applies. The order preserves the SKU, option name, quantity, unit price, discounts, shipping fee, and currency. With the new unit price of KRW 42,000, a KRW 2,000 discount, and KRW 3,000 shipping, the server sends KRW 43,000 to the payment provider. The saved order must still show the approved amount if the product is renamed or its price drops the next day. This is the boundary you add when you extend the [Spring Boot product lookup example](/en/posts/2026-11-22-spring-boot-4-2-restclient-migration/) from displaying a product to placing an order.

## What belongs in a single transaction?

Start with **separate modules in one application** for catalog, inventory, orders, and payment records. The modules share one database, and each module owns the rules for writing to its tables. The order and reservation can then commit in one local transaction. Call the external payment provider after that commit.

1. **Create the order and reserve stock.** Identify retries by buyer and order request key. Treat the same key with different request data as a conflict. The inventory module checks available stock by locking the SKU row or using a conditional update. For an order with multiple SKUs, save the order lines, reservations, and payment attempt together once all items are secured. If any item falls short, roll back the whole transaction and report the stock shortage. Record the work needed to resume the payment request in the same local commit.
2. **Call the payment provider.** Send the payment request with a provider idempotency key tied to the saved payment attempt ID. If the server stops immediately after making the call, it must be able to find the record and reconcile the same attempt. If the response is lost, look up the existing transaction with the provider. Resend the request only as far as the provider's guarantees for the same key and request parameters allow. Keep using the existing attempt while the outcome is unresolved. [Stripe's idempotent requests documentation](https://docs.stripe.com/api/idempotent_requests)
3. **Apply the result.** Verify the webhook signature before recording the event, or look up the transaction from the server. Check that the order, payment attempt, merchant account, amount, and currency match. Lock the order and reservation, read their current states, then save the payment state, inventory transition, and follow-up work in one transaction. Write the fulfillment or refund request to an outbox in the same commit. [Stripe's webhook delivery rules](https://docs.stripe.com/webhooks#event-delivery-behaviors) · [AWS transactional outbox pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

In this example, **available stock = physical stock − active reservations − fulfillment allocations**. When payment confirms a reservation, subtract the reserved quantity and add the same quantity to the fulfillment allocation. At shipment, reduce both physical stock and the allocation. If two orders arrive at the same time with just one unit left, the second order must see zero available after the first reservation commits. Verify this rule by running overlapping transactions against the actual database.

## Handling unresolved and late payments

![The system reads the verified payment result and order state. An unresolved result preserves the reservation state, and a confirmed closure without a charge releases the reservation. A paid result requests fulfillment if stock is held, or a refund if stock was already released. Reapplying a handled result creates no duplicate work.](/assets/img/architecture/2026-11-22-commerce-system-design-last-unit-of-stock-en.svg)

The diagram shows how the store applies payment results after reserving stock. When the saved payment state is already `PAID` or `REFUND_PENDING`, the code preserves that state and creates no follow-up work.

The order, payment, and stock reservation each have their own state. The storefront combines those states into a message the customer can understand. For example, if the provider is slow to respond, the order remains `PENDING_PAYMENT`, the payment is `UNKNOWN`, and the reservation stays `HELD`. Show “Verifying payment” and let the customer check the same order again.

| Situation | Saved state and follow-up |
| --- | --- |
| Payment confirmed, stock held | Order `CONFIRMED`, payment `PAID`, stock `ALLOCATED`. Record a fulfillment request |
| Response lost or provider still processing | Order `PENDING_PAYMENT`, payment `UNKNOWN`, stock `HELD`. Recheck the existing payment |
| Transaction confirmed closed without a charge | Order `CANCELLED`, payment `CLOSED_UNPAID`, reservation `RELEASED` |
| Payment confirmed after an exceptional release | Order `CANCELLED`, payment `REFUND_PENDING`, reservation `RELEASED`. Record a refund request |

If the hold expires while payment is unresolved, check the provider first. If it stays unresolved, record the case for an operator to find and reconcile the transaction. If payment confirmation comes in after an exceptional release, this design requests a refund and leaves the reservation released. Record the refund as successful after the provider confirms it. Decide how long to hold stock and who can authorize an exceptional release based on how quickly the store sells through inventory and the terms of its provider contract.

Deduplicate repeat deliveries by webhook event ID. Also protect each payment against duplicate fulfillment requests even when the event IDs differ. For example, add a unique constraint on `order_id` and job type in the fulfillment outbox, and on `payment_attempt_id` and job type in the refund outbox. Outbox publication can retry, so fulfillment and refund workers use the same job ID to prevent duplicate execution. When retrying a refund with the provider, use a refund-specific idempotency key supported by that provider. An older event reporting that payment is still processing leaves the confirmed payment state unchanged. Send results with mismatched IDs or amounts, or results that conflict with the confirmed history, to reconciliation before applying them. [Stripe's guidance on duplicate webhooks](https://docs.stripe.com/webhooks#handle-duplicate-events) · [AWS transactional outbox pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

## Checking payment transitions in Java

Save the code below as `CheckoutPolicy.java` and run `java CheckoutPolicy.java`. The example takes the **server-verified result of one payment attempt** tied to an order. `CLOSED_UNPAID` means the provider confirmed the transaction ended without a charge. A decline message alone gives insufficient evidence. The code assumes the order and reservation states agree. An order awaiting payment holds a reservation, and a canceled order has already released it. The caller validates IDs and amounts and reconciles conflicting results. The code returns the next state and the follow-up work to record.

```java
public class CheckoutPolicy {
    enum Order { PENDING_PAYMENT, CONFIRMED, CANCELLED }
    enum Payment { PENDING, UNKNOWN, PAID, CLOSED_UNPAID, REFUND_PENDING }
    enum Reservation { HELD, ALLOCATED, RELEASED }
    enum Result { UNRESOLVED, CLOSED_UNPAID, PAID }
    enum Effect { NONE, REQUEST_FULFILLMENT, REQUEST_REFUND }

    record State(Order order, Payment payment, Reservation reservation) {}
    record Decision(State state, Effect effect) {}

    static Decision apply(State current, Result result) {
        if (current.payment() == Payment.PAID
                || current.payment() == Payment.REFUND_PENDING) {
            return new Decision(current, Effect.NONE);
        }

        if (current.order() == Order.CANCELLED) {
            return switch (result) {
                case PAID -> new Decision(
                    new State(Order.CANCELLED, Payment.REFUND_PENDING, Reservation.RELEASED),
                    Effect.REQUEST_REFUND);
                case CLOSED_UNPAID -> new Decision(
                    new State(Order.CANCELLED, Payment.CLOSED_UNPAID, Reservation.RELEASED),
                    Effect.NONE);
                case UNRESOLVED -> new Decision(current, Effect.NONE);
            };
        }

        return switch (result) {
            case PAID -> new Decision(
                new State(Order.CONFIRMED, Payment.PAID, Reservation.ALLOCATED),
                Effect.REQUEST_FULFILLMENT);
            case CLOSED_UNPAID -> new Decision(
                new State(Order.CANCELLED, Payment.CLOSED_UNPAID, Reservation.RELEASED),
                Effect.NONE);
            case UNRESOLVED -> new Decision(
                new State(Order.PENDING_PAYMENT, Payment.UNKNOWN, Reservation.HELD),
                Effect.NONE);
        };
    }

    static void check(String label, Decision expected, Decision actual) {
        if (!expected.equals(actual)) {
            throw new AssertionError(label + ": " + actual);
        }
        System.out.println("PASS " + label);
    }

    public static void main(String[] args) {
        State held = new State(Order.PENDING_PAYMENT, Payment.PENDING, Reservation.HELD);
        State unknown = new State(Order.PENDING_PAYMENT, Payment.UNKNOWN, Reservation.HELD);
        State paid = new State(Order.CONFIRMED, Payment.PAID, Reservation.ALLOCATED);
        State closed = new State(
            Order.CANCELLED, Payment.CLOSED_UNPAID, Reservation.RELEASED);
        State released = new State(Order.CANCELLED, Payment.UNKNOWN, Reservation.RELEASED);
        State refundPending = new State(
            Order.CANCELLED, Payment.REFUND_PENDING, Reservation.RELEASED);

        check("unresolved retains hold", new Decision(unknown, Effect.NONE),
            apply(held, Result.UNRESOLVED));
        check("paid allocates stock", new Decision(paid, Effect.REQUEST_FULFILLMENT),
            apply(unknown, Result.PAID));
        check("duplicate paid has no effect", new Decision(paid, Effect.NONE),
            apply(paid, Result.PAID));
        check("old unresolved does not reopen payment", new Decision(paid, Effect.NONE),
            apply(paid, Result.UNRESOLVED));
        check("closed unpaid releases hold", new Decision(closed, Effect.NONE),
            apply(unknown, Result.CLOSED_UNPAID));
        check("late paid requests refund", new Decision(refundPending, Effect.REQUEST_REFUND),
            apply(released, Result.PAID));
        check("duplicate late paid has no effect", new Decision(refundPending, Effect.NONE),
            apply(refundPending, Result.PAID));
    }
}
```

The following seven checks ran on JDK 21.0.1. Applying payment confirmation twice created no additional work. Payment confirmed after the reservation was released returned a refund request.

```text
PASS unresolved retains hold
PASS paid allocates stock
PASS duplicate paid has no effect
PASS old unresolved does not reopen payment
PASS closed unpaid releases hold
PASS late paid requests refund
PASS duplicate late paid has no effect
```

Two races need their own checks in the implementation. When two orders try to reserve the last unit at once, only one should succeed. When expiration processing and payment confirmation arrive together for the same order, the system should record only one outcome: fulfillment while the order still holds stock, or a refund after release. The sequential Java example leaves the database races, provider integration, and production payments for separate verification.

Consider moving inventory to a separate service when more warehouses need to manage inventory or inventory needs independent deployment or scaling. The order and inventory databases then lose their shared local commit. The inventory service must apply each reservation ID only once, and the order module must be able to look up the outcome or compensate for a failure. The business rules still apply across service boundaries: prevent overselling and apply each payment and fulfillment once.
