---
{
  "state": "draft",
  "language": "es",
  "translationKey": "2026-11-22-commerce-system-design-last-unit-of-stock",
  "title": "Diseño de sistemas de comercio electrónico: ¿quién se queda con la última unidad?",
  "description": "Usa la última unidad en stock para analizar las reservas por SKU, la conciliación de pagos y los reembolsos tras liberar una reserva.",
  "sourcePath": "src/content/posts/en/2026-11-22-commerce-system-design-last-unit-of-stock.md",
  "sourceSha256": "63b33b1222e2cc6c885b4f2d63fb1a3f2727041b8710e7bf8ed7b335b6f8b9d6"
}
---

**Si dos clientes intentan comprar la última unidad de un producto, solo uno de los pedidos debe poder reservarla.** Si la tienda reserva la unidad y pierde la respuesta del proveedor de pagos, el pedido sigue pendiente mientras se verifica el pago. Si el pago se confirma después de liberar la reserva, el pedido se mantiene cancelado y se solicita un reembolso. Seguir una compra permite ver de qué datos se encargan el catálogo, el inventario, los pedidos y los pagos.

El ejemplo sigue a un comerciante que vende productos físicos, acepta un pago en wones surcoreanos (KRW) por pedido y envía desde un único almacén. Cubre cancelaciones y reembolsos para pagos sin confirmar y pagos confirmados tarde. Quedan fuera la liquidación de un marketplace, los envíos parciales y las devoluciones de productos.

## Stock que muestra la ficha y stock reservado para un pedido

Un **producto** es la ficha del catálogo que ve el cliente. Un **SKU** (unidad de mantenimiento de inventario) es la unidad que la tienda sigue en los pedidos y el inventario. Las versiones blanca y negra del mismo teclado tienen SKU distintos. La ficha muestra la disponibilidad en el momento de la consulta. Si el módulo de inventario no responde, la página sigue mostrando el producto e indica «Comprobando stock». Agregar un artículo al carrito no cambia el inventario.

| Responsabilidad | Datos que puede cambiar | Ejemplo |
| --- | --- | --- |
| Catálogo y precios | Productos, SKU, disponibilidad a la venta y precios unitarios vigentes | Cambiar el precio unitario del teclado negro `KB-BLK` |
| Inventario | Stock físico por almacén, reservas y asignaciones para envío | Reservar una unidad de `KB-BLK` para un pedido concreto |
| Pedidos | Comprador, líneas e importes en el momento de la compra y estado del pedido | Guardar cantidades, precios unitarios, reparto del descuento y coste de envío de `O-42` |
| Pagos | Intentos de pago, ID de transacción del proveedor y estados de pago y reembolso | Conciliar el resultado del proveedor para el intento `P-1` |
| Preparación de envíos | Solicitudes de preparación y su progreso | Recoger los artículos del pedido después del pago y la asignación de stock |

Justo antes de finalizar la compra, el servidor verifica si los artículos siguen a la venta y comprueba sus precios. Identifica al comprador con la sesión autenticada y calcula el total con sus propias reglas de precios, descuentos y envío. Si el teclado negro costaba 39.000 KRW al agregarlo al carrito y ahora cuesta 42.000 KRW, la tienda muestra el nuevo importe y pide al comprador que lo confirme. Al crear el pedido, el servidor verifica que la versión del precio aceptada coincide con la que aplica. El pedido conserva el SKU, el nombre de la opción, la cantidad, el precio unitario, los descuentos, el coste de envío y la moneda. Con el nuevo precio unitario de 42.000 KRW, un descuento de 2.000 KRW y 3.000 KRW de envío, el servidor envía 43.000 KRW al proveedor de pagos. El pedido guardado debe seguir mostrando el importe aceptado si cambia el nombre del producto o baja su precio al día siguiente. Ese es el límite que incorporas al extender el [ejemplo de consulta de productos con Spring Boot](/en/posts/2026-11-22-spring-boot-4-2-restclient-migration/) de mostrar un producto a realizar un pedido.

## ¿Qué debe quedar en una sola transacción?

Empieza con **módulos separados en una aplicación** para el catálogo, el inventario, los pedidos y los registros de pago. Comparten una base de datos y cada módulo define las reglas de escritura de sus tablas. Así, el pedido y la reserva se pueden confirmar en una sola transacción local. Llama al proveedor de pagos externo después de confirmarla.

1. **Crea el pedido y reserva el stock.** Identifica los reintentos por comprador y clave de solicitud del pedido. Si los datos cambian con la misma clave, trátalo como un conflicto. El módulo de inventario comprueba el stock disponible bloqueando la fila del SKU o con una actualización condicional. Con varios SKU, guarda las líneas del pedido, las reservas y el intento de pago juntos cuando estén asegurados todos los artículos. Si falta stock de alguno, revierte toda la transacción e informa de la falta de stock. En el mismo commit local, registra el trabajo necesario para reanudar la solicitud de pago.
2. **Llama al proveedor de pagos.** Envía la solicitud de pago con una clave de idempotencia del proveedor ligada al ID del intento guardado. Si el servidor se detiene justo después de la llamada, debe poder encontrar el registro y conciliar el mismo intento. Si se pierde la respuesta, consulta la transacción existente en el proveedor. Reenvía la solicitud solo dentro de las garantías del proveedor para la misma clave y los mismos parámetros. Sigue usando el intento existente mientras el resultado siga sin confirmar. [Documentación de Stripe sobre solicitudes idempotentes](https://docs.stripe.com/api/idempotent_requests)
3. **Aplica el resultado.** Antes de registrar el evento, verifica la firma del webhook o consulta la transacción desde el servidor. Comprueba que coincidan el pedido, el intento de pago, la cuenta del comerciante, el importe y la moneda. Bloquea el pedido y la reserva, lee sus estados actuales y guarda el estado del pago, la transición del inventario y el trabajo posterior en una transacción. Escribe la solicitud de envío o reembolso en un outbox en el mismo commit. [Reglas de Stripe para la entrega de webhooks](https://docs.stripe.com/webhooks#event-delivery-behaviors) · [Patrón de outbox transaccional de AWS](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

En este ejemplo, **stock disponible = stock físico − reservas activas − asignaciones para envío**. Al confirmar el pago de una reserva, resta la cantidad reservada y añade la misma cantidad a la asignada para el envío. Al enviar, reduce tanto el stock físico como la asignación. Si llegan dos pedidos al mismo tiempo y queda una sola unidad, el segundo debe ver cero unidades disponibles tras confirmar la primera reserva. Comprueba esta regla ejecutando transacciones superpuestas en la base de datos real.

## Cómo gestionar pagos sin confirmar o tardíos

![El sistema lee el resultado de pago verificado y el estado del pedido. Un resultado sin confirmar mantiene la reserva y un cierre confirmado sin cobro la libera. Si se confirma el pago, se solicita el envío cuando el stock sigue reservado y un reembolso cuando ya se liberó. Volver a aplicar un resultado procesado no duplica el trabajo.](2026-11-22-commerce-system-design-last-unit-of-stock.svg)

El diagrama muestra cómo aplica la tienda el resultado del pago después de reservar el stock. Si el estado guardado ya es `PAID` o `REFUND_PENDING`, el código lo conserva y no genera trabajo de seguimiento.

El pedido, el pago y la reserva de stock tienen sus propios estados. La tienda combina esos estados en un mensaje comprensible. Por ejemplo, si el proveedor tarda en responder, el pedido sigue en `PENDING_PAYMENT`, el pago en `UNKNOWN` y la reserva en `HELD`. Muestra «Verificando el pago» y permite consultar el mismo pedido otra vez.

| Situación | Estado guardado y acción posterior |
| --- | --- |
| Pago confirmado, stock reservado | Pedido `CONFIRMED`, pago `PAID`, stock `ALLOCATED`. Registrar una solicitud de preparación de envío |
| Respuesta perdida o proveedor aún procesando el pago | Pedido `PENDING_PAYMENT`, pago `UNKNOWN`, stock `HELD`. Volver a comprobar el pago existente |
| Se confirma que la transacción se cerró sin cobro | Pedido `CANCELLED`, pago `CLOSED_UNPAID`, reserva `RELEASED` |
| Pago confirmado después de una liberación excepcional | Pedido `CANCELLED`, pago `REFUND_PENDING`, reserva `RELEASED`. Registrar una solicitud de reembolso |

Si vence la reserva con el pago aún sin confirmar, consulta primero al proveedor. Si el resultado sigue sin aclararse, registra el caso para que un operador encuentre y concilie la operación. Si se confirma el pago después de una liberación excepcional, el diseño solicita un reembolso y mantiene liberada la reserva. Registra el reembolso como completado cuando lo confirme el proveedor. Decide cuánto tiempo reservar el stock y quién puede autorizar una liberación excepcional en función de la velocidad de venta y las condiciones del contrato con el proveedor.

Elimina entregas repetidas por ID de evento del webhook. Protege cada pago contra solicitudes de envío duplicadas incluso cuando difieran los ID de evento. Por ejemplo, agrega una restricción de unicidad sobre `order_id` y tipo de tarea en el outbox de envíos, y sobre `payment_attempt_id` y tipo de tarea en el outbox de reembolsos. La publicación del outbox se puede repetir, por lo que los procesos de envío y reembolso usan el mismo ID de tarea para evitar la doble ejecución. Si reintentas un reembolso con el proveedor, usa una clave de idempotencia específica para reembolsos que este admita. Un evento más antiguo que indique que el pago sigue en curso deja intacto el estado confirmado. Envía a conciliación los resultados con identificadores o importes distintos y los que contradigan el historial confirmado antes de aplicarlos. [Guía de Stripe sobre webhooks duplicados](https://docs.stripe.com/webhooks#handle-duplicate-events) · [Patrón de outbox transaccional de AWS](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

## Cómo comprobar las transiciones de pago en Java

Guarda el código como `CheckoutPolicy.java` y ejecuta `java CheckoutPolicy.java`. El ejemplo toma **el resultado de un intento de pago verificado por el servidor** y vinculado a un pedido. `CLOSED_UNPAID` significa que el proveedor confirmó que la transacción terminó sin cobro. Un mensaje de rechazo por sí solo no basta. El código presupone estados coherentes para el pedido y la reserva. Un pedido pendiente de pago retiene una reserva y, si está cancelado, ya la ha liberado. Quien llama valida los identificadores y los importes y concilia los resultados contradictorios. El código devuelve el siguiente estado y el trabajo de seguimiento que hay que registrar.

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

Las siete comprobaciones siguientes se ejecutaron con JDK 21.0.1. Aplicar dos veces la confirmación de pago no generó trabajo adicional. Confirmar el pago después de liberar la reserva devolvió una solicitud de reembolso.

```text
PASS unresolved retains hold
PASS paid allocates stock
PASS duplicate paid has no effect
PASS old unresolved does not reopen payment
PASS closed unpaid releases hold
PASS late paid requests refund
PASS duplicate late paid has no effect
```

Dos carreras requieren comprobaciones propias en la implementación. Si dos pedidos intentan reservar la última unidad a la vez, solo uno debe conseguirlo. Cuando el vencimiento y la confirmación del pago coinciden para el mismo pedido, el sistema debe registrar un único resultado: preparación del envío si retiene el stock o reembolso tras liberarlo. Las carreras entre transacciones, la integración con el proveedor y los pagos en producción se verifican aparte del ejemplo secuencial de Java.

Considera separar el inventario en un servicio si más almacenes deben gestionarlo o si necesita desplegarse o escalar de forma independiente. En ese caso las bases de datos de pedidos e inventario pierden el commit local compartido. El servicio de inventario debe aplicar una sola vez cada ID de reserva, y el módulo de pedidos debe poder consultar el resultado o compensar un fallo. Las reglas de negocio siguen vigentes entre servicios: evita vender por encima del stock y aplica cada pago y cada envío una sola vez.
