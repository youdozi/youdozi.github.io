export function shippingFee(orderTotal) {
  if (!Number.isSafeInteger(orderTotal) || orderTotal < 0) {
    throw new RangeError('orderTotal must be a nonnegative safe integer');
  }
  return orderTotal >= 50_000 ? 0 : 3000;
}
