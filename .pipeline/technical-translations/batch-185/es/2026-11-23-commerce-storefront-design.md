---
{
  "state": "draft",
  "language": "es",
  "translationKey": "2026-11-23-commerce-storefront-design",
  "title": "Diseño de una tienda en línea: de la selección de productos a la confirmación del pago",
  "description": "Define qué puede ver y hacer el comprador desde el catálogo hasta el detalle del pedido, y oriéntalo al volver del pago según los estados del pedido y del pago en el servidor.",
  "sourcePath": "src/content/posts/en/2026-11-23-commerce-storefront-design.md",
  "sourceSha256": "fde9deae56ab163d6fad0ea42a0136927d901a84ecd0111e5006b0eb21aa00ce"
}
---

**Si un comprador vuelve del pago y se encuentra con una pantalla en blanco, lo primero que quiere saber es si se le cobró.** Muéstrale una pantalla donde pueda comprobar qué ocurrió con el pedido existente. Desde la ficha del producto hasta el historial de pedidos, acompaña los hechos que cada pantalla puede confirmar con una acción que el comprador pueda realizar.

La [guía del panel de administración de una tienda](/en/posts/2026-11-23-commerce-admin-screen/) sigue a un operador que consulta un pedido cuyo pago está sin confirmar. Aquí vemos la misma situación desde el lado del comprador. Supongamos una tienda de un único comerciante que vende en wones surcoreanos bienes físicos que luego envía a sus compradores. Los compradores hacen pedidos con una cuenta. Las reglas de descuentos y envío son ilustrativas.

## ¿Qué decide el comprador en cada pantalla?

| Pantalla | Qué mostrar primero | Qué puede hacer el comprador después |
| --- | --- | --- |
| Catálogo y búsqueda | Nombres y fotos de productos, precios que se puedan comparar y filtros activos | Acotar los resultados o abrir la ficha de un producto |
| Ficha del producto | Precio y disponibilidad de la variante seleccionada, más las condiciones de envío | Elegir una variante y cantidad, y agregarla al carrito |
| Carrito | Variante, cantidad e importe de cada artículo, total estimado y artículos que impiden continuar con la compra | Cambiar cantidades y artículos, y pasar a finalizar la compra |
| Finalizar la compra | Dirección y coste de envío, descuentos, importe final y opciones para hacer cambios | Revisar las condiciones y solicitar el pago |
| Detalle del pedido | Número de pedido, estados del pago, envío y reembolso e historial de cambios | Consultar el resultado o seguir el envío según el estado actual |

Si el catálogo indica «Desde 39.000 ₩», muestra el precio real en cuanto el comprador elija una variante en la ficha. Identifica con texto las variantes agotadas. Si una búsqueda no devuelve resultados, muestra los filtros activos y deja que el comprador los borre. Si la búsqueda no se carga, ofrece volver a intentarlo.

Aplica la misma regla que en la [guía de reservas de stock en comercio electrónico](/en/posts/2026-11-22-commerce-system-design-last-unit-of-stock/). La ficha muestra el stock en el momento de la consulta. El carrito guarda la selección del comprador. El servidor reserva stock al crear el pedido. Si otra persona reserva primero la última unidad, señala en el carrito el artículo y la variante afectados, y conserva los demás artículos y la dirección que introdujo el comprador.

## Permite revisar y hacer cambios antes de pagar

Junto al importe final, permite revisar y modificar las variantes, cantidades y la dirección de envío. Indica en el botón la acción real, por ejemplo **«Pagar 43.000 ₩»**. La guía de WCAG sobre la prevención de errores en transacciones financieras describe cómo permitir que los usuarios revisen y corrijan los datos antes de enviarlos. [Guía de W3C sobre prevención de errores en transacciones financieras](https://www.w3.org/WAI/WCAG22/Understanding/error-prevention-legal-financial-data.html)

Si un teclado costaba 39.000 ₩ al agregarlo al carrito y cuesta 42.000 ₩ al finalizar la compra, identifica el artículo afectado. Por ejemplo, «El precio del teclado negro cambió de 39.000 ₩ a 42.000 ₩». Vuelve a calcular los descuentos y el envío, muestra el nuevo total y deja que el comprador lo confirme antes de solicitar el pago. Al crear el pedido, el servidor coteja el importe que aceptó el comprador con el que cobrará y registra las condiciones de la transacción. [Cómo conserva los importes de los pedidos la base de datos de la tienda](/en/posts/2026-11-22-commerce-database-design/)

En el móvil, coloca los enlaces para cambiar la dirección de envío y los artículos junto a los datos correspondientes, y el importe final cerca del botón de pago. Si el botón está fijo abajo, asegúrate de que el comprador pueda desplazarse lo suficiente para leer el último campo y los mensajes de error. Las tecnologías de asistencia también pueden anunciar cambios que no requieren mover el foco, como un nuevo total del carrito o el resultado de una comprobación de pago. Por ejemplo, agrega `role="status"` a la región que contiene el texto del resultado. [Guía de W3C sobre mensajes de estado](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html)

## Comprueba el resultado del pago en el servidor

![Consulta el pedido existente cuando el comprador vuelve del pago. Distingue la carga de un fallo de consulta y usa los resultados del pago y del pedido para ofrecer la actualización del estado, el seguimiento del envío, el catálogo o información del reembolso.](2026-11-23-commerce-storefront-design.svg)

Cuando el comprador vuelva de la página de pago, consulta el pedido existente en el servidor. Si se pierde la respuesta a la creación del pedido tras pulsar Pagar, usa la misma clave de solicitud de pedido para comprobar si ya se aceptó. Desactivar el botón un momento puede reducir las pulsaciones repetidas. La clave de solicitud y una comprobación de unicidad en el servidor impiden pedidos duplicados. Las API de detalle y estado del pedido comprueban también si el comprador actual tiene permiso para acceder a él.

| Estado verificado por el servidor | Mensaje y acción para el comprador |
| --- | --- |
| Falló la consulta del estado del pedido | «No pudimos cargar el estado de tu pedido.» → **Volver a cargar el estado del pedido** |
| El pedido existe y el resultado del pago sigue sin confirmar | «Estamos comprobando el resultado del pago.» → **Actualizar estado del pedido** |
| Pago completado, pedido en revisión | «Tu pago se completó. Estamos revisando tu pedido.» → **Actualizar estado del pedido** |
| Pago y pedido confirmados | «Hemos recibido tu pedido.» → **Seguir el envío** |
| Cancelación confirmada sin cobro | «Tu pedido se canceló. No se te cobró.» → **Explorar productos** |
| Pago confirmado tras la cancelación, reembolso pendiente | «Estamos procesando tu reembolso.» → **Actualizar estado del reembolso** |
| Reembolso confirmado | «Tu reembolso se ha completado.» → **Ver detalles del reembolso** |

Indica si el pedido se está preparando, está en tránsito o se ha entregado, según el estado real del envío. Muestra un botón para cancelar o devolver solo después de comprobar que el estado actual admite la solicitud y que el usuario tiene permiso. Muestra el progreso una vez aceptada la solicitud. Indica que el reembolso se completó cuando el servidor confirme el resultado.

## Asocia los estados del servidor con mensajes y acciones

El ejemplo toma los estados del pedido y del pago ya consultados en el servidor y les asigna un título y una acción siguiente. Un error de red y un resultado de pago sin confirmar son entradas distintas. Las combinaciones de estados indefinidas nunca muestran un resultado satisfactorio. El ejemplo utiliza textos de interfaz en coreano. La tabla anterior da sus equivalentes en español. Guarda el código como `order-view.mjs` y ejecuta `node order-view.mjs`.

```javascript
const labels = {
  loading: ["주문 상태를 불러오는 중입니다.", null],
  unavailable: ["주문 상태를 불러오지 못했습니다.", "주문 상태 다시 불러오기"],
  pending: ["결제 결과를 확인 중입니다.", "주문 상태 새로고침"],
  paidReview: ["결제는 완료됐고 주문을 확인 중입니다.", "주문 상태 새로고침"],
  confirmed: ["주문이 접수됐습니다.", "배송 상태 보기"],
  closed: ["주문이 취소됐으며 결제된 금액이 없습니다.", "상품 다시 보기"],
  refundPending: ["환불을 처리 중입니다.", "환불 상태 새로고침"],
  refunded: ["환불이 완료됐습니다.", "환불 내역 보기"]
};

function orderView(snapshot) {
  if (snapshot.kind === "loading") return labels.loading;
  if (snapshot.kind === "unavailable") return labels.unavailable;

  const { order, payment } = snapshot;
  if (order === "CANCELLED" && payment === "REFUND_PENDING") {
    return labels.refundPending;
  }
  if (order === "CANCELLED" && payment === "REFUNDED") {
    return labels.refunded;
  }
  if (order === "CANCELLED" && payment === "CLOSED_UNPAID") {
    return labels.closed;
  }
  if (order === "CONFIRMED" && payment === "PAID") {
    return labels.confirmed;
  }
  if (order === "PENDING_PAYMENT" && payment === "PAID") {
    return labels.paidReview;
  }
  if (order === "PENDING_PAYMENT" &&
      (payment === "PENDING" || payment === "UNKNOWN")) {
    return labels.pending;
  }
  return labels.unavailable;
}

const verified = (order, payment) => ({ kind: "loaded", order, payment });
const cases = [
  [{ kind: "loading" }, "loading"],
  [{ kind: "unavailable" }, "unavailable"],
  [verified("PENDING_PAYMENT", "UNKNOWN"), "pending"],
  [verified("PENDING_PAYMENT", "PAID"), "paidReview"],
  [verified("CONFIRMED", "PAID"), "confirmed"],
  [verified("CANCELLED", "CLOSED_UNPAID"), "closed"],
  [verified("CANCELLED", "REFUND_PENDING"), "refundPending"],
  [verified("CANCELLED", "REFUNDED"), "refunded"],
  [verified("CONFIRMED", "UNKNOWN"), "unavailable"]
];

for (const [input, key] of cases) {
  if (orderView(input) !== labels[key]) throw new Error(key);
  console.log("PASS", key);
}
```

Las nueve entradas pasaron las pruebas en Node.js 22.17.0. Una consulta fallida, un resultado de pago sin confirmar, una cancelación sin cobro y un reembolso pendiente devolvieron el mensaje y la acción esperados. La ejecución cubrió la función que asigna a los estados mensajes y acciones de interfaz. La usabilidad en móviles, el comportamiento de las tecnologías de asistencia y la integración real con el sistema de pagos se comprueban en las pantallas implementadas.
