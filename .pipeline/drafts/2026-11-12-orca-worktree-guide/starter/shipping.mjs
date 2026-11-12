export function shippingFee(orderTotal) {
  return orderTotal > 50_000 ? 0 : 3000;
}
