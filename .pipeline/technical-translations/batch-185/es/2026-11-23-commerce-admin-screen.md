---
{
  "state": "draft",
  "language": "es",
  "translationKey": "2026-11-23-commerce-admin-screen",
  "title": "Diseño del panel de administración de una tienda: colas de pedidos, pagos y preparación de envíos",
  "description": "Organiza el panel por tareas operativas y usa colas y fichas de pedidos para gestionar pagos sin confirmar, reservas de stock liberadas y solicitudes de reembolso.",
  "sourcePath": "src/content/posts/en/2026-11-23-commerce-admin-screen.md",
  "sourceSha256": "00692a737eb62a4f313f4adb76e503c7796c83e7a788f20151b7f09669719558"
}
---

**El panel de administración de una tienda debe ayudar al personal a localizar los pedidos que necesitan atención y ver los datos necesarios para actuar.** Empieza con colas para comprobar pagos, preparar envíos y seguir los reembolsos. En el detalle del pedido, muestra el resultado del pago junto al stock reservado para ese pedido. Si el pago se confirma después de liberar la reserva, el operador debe poder mantener el envío en pausa y seguir la solicitud de reembolso.

Supongamos un comerciante que vende productos físicos en wones surcoreanos (KRW) y envía desde un almacén. La guía traslada al panel el caso de la última unidad del artículo de diseño de sistemas y el modelo de líneas de pedido, reservas e intentos de pago del artículo de base de datos. Seguimos a un operador que consulta una transacción existente en el proveedor de pagos. [Diseño de sistemas de comercio electrónico](/en/posts/2026-11-22-commerce-system-design-last-unit-of-stock/) · [Diseño de la base de datos de comercio electrónico](/en/posts/2026-11-22-commerce-database-design/)

## Da a cada menú un punto de partida operativo

«Pedidos» es el punto de partida para las tareas diarias. «Pagos y reembolsos» y «Preparación de envíos» llevan al equipo directamente a sus tareas pendientes. Sea cual sea el punto de partida, el mismo número debe llevar al mismo detalle e historial para facilitar los traspasos entre turnos y equipos.

| Menú | Trabajo que empieza aquí | Qué debe ver el operador |
| --- | --- | --- |
| Pedidos | Abrir pedidos con pago sin confirmar, a la espera de preparación o con un reembolso pendiente. | Número de pedido, artículos e importes al comprar y los cuatro campos de estado |
| Catálogo | Modificar la disponibilidad de un SKU para la venta, sus opciones o su precio actual. | Condiciones vigentes por SKU, valores anteriores y posteriores |
| Inventario | Encontrar pedidos con stock reservado o ajustar diferencias del recuento físico. | Stock físico, reservado y asignado por SKU, pedidos vinculados e historial de ajustes |
| Pagos y reembolsos | Conciliar transacciones existentes del proveedor y seguir las solicitudes de reembolso. | Intentos de pago, ID de transacción del proveedor, importe original e historial de consultas y reembolsos |
| Preparación de envíos | Recoger y enviar los artículos asignados a los pedidos. | SKU, cantidad, posibilidad de envío y registros de expedición |
| Roles y permisos | Dar al personal permisos de consulta o ejecución y revisar los cambios. | Permisos por tarea, alcance e historial de concesión y revocación |

Un cambio de precio del catálogo se aplica a las ventas futuras. El detalle del pedido consulta el importe guardado en la línea. Por ejemplo, el pedido `O-42` de un teclado negro suma 43.000 KRW tras aplicar un descuento de 2.000 KRW al precio unitario de 42.000 KRW y añadir 3.000 KRW de envío. El detalle y la revisión del reembolso siguen mostrando el importe de la compra cuando cambia el precio del catálogo.

## Elige una tarea en la cola y revisa los datos en el detalle

**Comprobación de pagos** reúne los pedidos con resultados de pago sin confirmar. **Pendientes de preparación** reúne los pedidos con stock asignado y envío pendiente de procesar. **Seguimiento de reembolsos** reúne los pedidos con una solicitud registrada y sin resultado final. Elige un orden para cada cola. Por ejemplo, los pagos pueden mostrar primero los problemas detectados hace más tiempo, mientras que los envíos se pueden ordenar por la hora límite del almacén.

En la lista, muestra número de pedido, hora, producto, importe y estados actuales. Permite buscar por número, nombre de producto o SKU junto con un filtro por estado del pago. Junto a cada tarea, muestra el total sin filtros y, sobre la lista, el número actual de resultados. En producción, añade filtros de fecha y asignación si hacen falta, y conserva filtros, búsqueda y posición de desplazamiento al cerrar el detalle. Si una actualización quita la fila original, devuelve el foco a la tarea seleccionada para poder pasar al siguiente pedido.

| Estado | Qué mostrar | Por qué importa |
| --- | --- | --- |
| Pedido | Pendiente de pago, confirmado, cancelado | Muestra la fase del pedido. El pago de un pedido cancelado aún puede confirmarse más tarde. |
| Pago | Sin confirmar, pagado, reembolso solicitado, reembolsado | Indica si hay que volver a consultar la misma transacción o esperar el reembolso. |
| Inventario | Reservado, reserva liberada, asignado, enviado | Muestra la cantidad asegurada para el pedido y su estado actual. |
| Envío | Envío en pausa, pendiente de preparación, enviado | Indica si el almacén puede actuar ahora o ya envió el pedido. |

Justo debajo de los estados, muestra el importe de la compra, el SKU y la cantidad, el ID de la reserva vinculada y el ID de transacción del proveedor. Cuando el pago sigue sin confirmar, la cantidad disponible para vender no permite saber si el pedido tiene stock reservado. En el historial, muestra cuándo ocurrió cada cambio, quién lo hizo, su origen y los identificadores pertinentes. Mantén las etiquetas legibles en pantallas estrechas y usa el color para resaltarlas.

## Consulta la transacción existente cuando el pago sigue sin confirmar

La respuesta a la solicitud de pago de `O-42` se perdió. El resultado siguió sin aclararse el tiempo suficiente para que alguien aprobara una excepción, liberara la reserva `R-42` y cancelara el pedido. El operador de pagos abre el pedido y consulta la transacción existente `PG-DEMO-42`. Cuando se confirme el pago, registra una **solicitud de reembolso**. Mantén el pedido cancelado, el envío en pausa y la reserva liberada. Registra el reembolso como completado cuando lo confirme el proveedor.

![Consulta la transacción existente en el proveedor para un pedido cuyo pago sigue sin confirmar. Si no hay respuesta, mantén los estados de pago, inventario y envío. Si se confirma el pago, solicita un reembolso cuando la reserva ya está liberada, o asigna stock y pasa el pedido a pendientes de preparación cuando la reserva sigue activa.](2026-11-23-commerce-admin-screen.svg)

El diagrama muestra las ramas para tres pedidos ficticios. La consulta de `O-43` no recibe respuesta, por lo que **el pago sigue sin confirmar, la reserva sigue activa y el envío queda en pausa**. En `O-44`, el pago se confirma y la reserva está activa, así que **se confirma el pedido, se marca el pago como completado, se asigna stock y se pasa el pedido a pendientes de preparación**. El diagrama cubre la falta de respuesta y los pagos confirmados. En producción, si se confirma un cierre sin cobro, puede liberarse la reserva y cancelarse el pedido. Si los datos de la transacción no coinciden, registra una excepción de conciliación antes de cambiar el estado.

### Ejemplo en JavaScript de las transiciones de estado

El ejemplo aplica los resultados a tres pedidos ficticios con pagos sin confirmar y envíos en pausa. Pega el código en la consola de desarrollo del navegador para ejecutarlo sin instalar nada. La función solo actualiza objetos de pedido en memoria.

```javascript
function applyDemoPaymentResult(order, result) {
  if (order.payment !== 'UNKNOWN' || result !== 'PAID') return 'NO_CHANGE';

  if (order.stock === 'RELEASED') {
    order.payment = 'REFUND_PENDING';
    return 'REFUND_REQUESTED';
  }

  if (order.stock === 'HELD') {
    order.order = 'CONFIRMED';
    order.payment = 'PAID';
    order.stock = 'ALLOCATED';
    order.shipping = 'READY';
    return 'READY_TO_SHIP';
  }

  return 'NO_CHANGE';
}

const examples = [
  ['O-42', 'CANCELLED', 'RELEASED', 'PAID'],
  ['O-43', 'PENDING_PAYMENT', 'HELD', 'UNAVAILABLE'],
  ['O-44', 'PENDING_PAYMENT', 'HELD', 'PAID'],
];

for (const [id, state, stock, result] of examples) {
  const order = { order: state, payment: 'UNKNOWN', stock, shipping: 'BLOCKED' };
  console.log(id, applyDemoPaymentResult(order, result), ...Object.values(order));
}
```

La salida esperada en consola muestra el ID del pedido, el resultado y los estados del pedido, el pago, el inventario y el envío, en ese orden.

```text
O-42 REFUND_REQUESTED CANCELLED REFUND_PENDING RELEASED BLOCKED
O-43 NO_CHANGE PENDING_PAYMENT UNKNOWN HELD BLOCKED
O-44 READY_TO_SHIP CONFIRMED PAID ALLOCATED READY
```

El bloque se ejecutó en Node.js 24.13.0 y produjo las tres líneas esperadas.

## Verifica permisos y estados en el servidor

Da al equipo de pagos acceso a consultas de transacciones existentes, al personal del almacén acceso a los registros de expedición y a responsables designados capacidad para aprobar liberaciones excepcionales de stock o reembolsos. Concede por separado el permiso para modificar precios del catálogo. En el detalle del pedido, devuelve solo los campos y las acciones disponibles para el usuario actual. Ante cada solicitud de acción, la API debe comprobar autenticación, permiso de ejecución, acceso al pedido y su estado actual. La API de consulta localiza en el servidor la transacción existente que ya está vinculada al pedido. Coteja la cuenta del proveedor, el ID de transacción, el importe y la moneda. Al aplicar el resultado, lee la versión más reciente del pedido y de su reserva. Evita duplicar solicitudes de envío o reembolso si un reintento coincide con un webhook. Cuando el almacén pide el envío, el servidor vuelve a comprobar que pedido y pago estén confirmados y que el stock esté asignado.

En acciones como la consulta de una transacción, muestra junto al botón la transacción y el alcance de la acción. La consulta no genera un cargo. Si confirma el pago, el estado de la reserva determina si se solicita un reembolso o si el pedido pasa a pendientes de preparación. Las acciones que afectan directamente al dinero o al stock, como un reembolso manual o una liberación excepcional, requieren confirmación y permiso aparte. Por ejemplo, la confirmación del reembolso manual muestra **el pedido `O-42`, la transacción original `PG-DEMO-42`, el reembolso solicitado de 43.000 KRW y el motivo**. Etiqueta la solicitud aceptada como «Reembolso solicitado» y guarda en el registro de auditoría del servidor quién la aprobó y ejecutó, la hora, los estados anterior y nuevo, la transacción vinculada y el resultado. Si se pierde la respuesta, consulta primero el estado de la misma solicitud.

## Distingue las colas vacías de los resultados sin confirmar

| Situación | Mensaje y acción siguiente |
| --- | --- |
| No hay pedidos en la cola | «No hay pedidos para esta tarea». Deja que el operador abra otra cola. |
| Nada coincide con la búsqueda o los filtros | «No hay pedidos que coincidan con la búsqueda o los filtros». Permite eliminar esos criterios sin salir de la cola. |
| No se pudo cargar la lista | «No se pudieron cargar los pedidos». Conserva la búsqueda y ofrece volver a cargar. Si hay resultados anteriores visibles, indica cuándo se obtuvieron. |
| El pedido está abierto pero el proveedor no ha confirmado el resultado | «La consulta no recibió respuesta. El pago sigue sin confirmar y el envío permanece en pausa». Permite repetir la consulta de la misma transacción. |
| El usuario no tiene permiso para la acción | «El equipo de pagos puede consultar transacciones existentes». Mantén visibles los estados y el historial dentro de los permisos de su rol. |

## Refleja los resultados del ejemplo en las colas

Imagina que abres un pedido en **Comprobación de pagos** y eliges **Consultar el pago existente**. Sin respuesta, `O-43` se queda en «Comprobación de pagos». El historial registra que no hubo respuesta y la reserva siguió activa. Al registrar la solicitud de reembolso para `O-42`, lo encuentras en **Seguimiento de reembolsos**. Tras asignar stock a `O-44`, lo encuentras en **Pendientes de preparación**. El operador de envíos ve los estados y el historial, con un aviso de que el equipo de pagos puede realizar la consulta.

El ejemplo usa pedidos y respuestas de pago preparados. Una implementación en producción aborda por separado el inicio de sesión, los datos de clientes, las consultas y los reembolsos reales al proveedor y la integración con el almacén.
