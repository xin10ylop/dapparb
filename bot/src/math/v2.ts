/**
 * Constant-product AMM math. Exact integer replicas of the on-chain formulas so that
 * locally-computed outputs match the pool byte-for-byte.
 */

export const BPS = 10_000n;

/** Uniswap V2 / Sushi V2 / Pancake V2 / BaseSwap: `amountIn*(10000-fee)*rOut / (rIn*10000 + amountIn*(10000-fee))`. */
export function univ2GetAmountOut(amountIn: bigint, reserveIn: bigint, reserveOut: bigint, feeBps: number): bigint {
  if (amountIn <= 0n || reserveIn <= 0n || reserveOut <= 0n) return 0n;
  const amountInWithFee = amountIn * (BPS - BigInt(feeBps));
  const numerator = amountInWithFee * reserveOut;
  const denominator = reserveIn * BPS + amountInWithFee;
  return numerator / denominator;
}

/** Uniswap V2 exact-output helper (amount that must be paid to receive `amountOut`). */
export function univ2GetAmountIn(amountOut: bigint, reserveIn: bigint, reserveOut: bigint, feeBps: number): bigint {
  if (amountOut <= 0n || reserveIn <= 0n || reserveOut <= amountOut) return 0n;
  const numerator = reserveIn * amountOut * BPS;
  const denominator = (reserveOut - amountOut) * (BPS - BigInt(feeBps));
  return numerator / denominator + 1n;
}

/** Aerodrome/Velodrome volatile pool: fee is subtracted from amountIn first (integer division), then x*y=k. */
export function aeroVolatileGetAmountOut(amountIn: bigint, reserveIn: bigint, reserveOut: bigint, feeBps: number): bigint {
  if (amountIn <= 0n || reserveIn <= 0n || reserveOut <= 0n) return 0n;
  const netIn = amountIn - (amountIn * BigInt(feeBps)) / BPS;
  return (netIn * reserveOut) / (reserveIn + netIn);
}

const E18 = 10n ** 18n;

function aeroK(x: bigint, y: bigint): bigint {
  // x, y already scaled to 1e18
  const a = (x * y) / E18;
  const b = (x * x) / E18 + (y * y) / E18;
  return (a * b) / E18;
}

function aeroF(x0: bigint, y: bigint): bigint {
  const a = (x0 * y) / E18;
  const b = (x0 * x0) / E18 + (y * y) / E18;
  return (a * b) / E18;
}

function aeroD(x0: bigint, y: bigint): bigint {
  return (3n * x0 * ((y * y) / E18)) / E18 + (((x0 * x0) / E18) * x0) / E18;
}

/** Port of Aerodrome Pool._get_y (Newton's method on the stable curve). */
function aeroGetY(x0: bigint, xy: bigint, yInit: bigint): bigint {
  let y = yInit;
  for (let i = 0; i < 255; i++) {
    const k = aeroF(x0, y);
    if (k < xy) {
      let dy = ((xy - k) * E18) / aeroD(x0, y);
      if (dy === 0n) {
        if (k === xy) return y;
        if (aeroK(x0, y + 1n) > xy) return y + 1n;
        dy = 1n;
      }
      y = y + dy;
    } else {
      let dy = ((k - xy) * E18) / aeroD(x0, y);
      if (dy === 0n) {
        if (k === xy || aeroF(x0, y - 1n) < xy) return y;
        dy = 1n;
      }
      y = y - dy;
    }
  }
  throw new Error("aeroGetY: did not converge");
}

/**
 * Aerodrome stable pool (x^3*y + x*y^3 = k). `decimalsIn/Out` are 10**decimals of the respective tokens.
 * Mirrors Pool._getAmountOut for `stable == true` after the fee has been deducted from amountIn.
 */
export function aeroStableGetAmountOut(
  amountIn: bigint,
  reserveIn: bigint,
  reserveOut: bigint,
  decIn: bigint,
  decOut: bigint,
  feeBps: number,
): bigint {
  if (amountIn <= 0n || reserveIn <= 0n || reserveOut <= 0n) return 0n;
  const netIn = amountIn - (amountIn * BigInt(feeBps)) / BPS;
  const rA = (reserveIn * E18) / decIn;
  const rB = (reserveOut * E18) / decOut;
  const xy = aeroK(rA, rB);
  const aIn = (netIn * E18) / decIn;
  const y = rB - aeroGetY(aIn + rA, xy, rB);
  return (y * decOut) / E18;
}

/**
 * Closed-form optimal input for a two-pool constant-product cycle:
 *   pool1: sell x of A for B (reserves a1 of A, b1 of B, fee f1)
 *   pool2: sell B for A (reserves b2 of B, a2 of A, fee f2)
 * out(x) = A*x / (B + C*x) with A = g1*g2*a2*b1, B = a1*b2, C = g1*(b2 + g2*b1), g = 1-fee.
 * x* = (sqrt(A*B) - B) / C. Returns 0n when no profitable amount exists.
 * Computed in scaled integer arithmetic (fees in bps) to avoid float precision loss on 18-decimal reserves.
 */
export function optimalV2Cycle(a1: bigint, b1: bigint, f1Bps: number, b2: bigint, a2: bigint, f2Bps: number): bigint {
  const g1 = BPS - BigInt(f1Bps);
  const g2 = BPS - BigInt(f2Bps);
  // Work in units scaled by BPS^2 to keep integers.
  const A = g1 * g2 * a2 * b1; // scaled BPS^2
  const B = a1 * b2 * BPS * BPS; // scaled BPS^2
  const C = g1 * (b2 * BPS + g2 * b1); // scaled BPS^2
  if (A <= B) return 0n;
  const root = isqrt(A * B); // scaled BPS^2
  const x = (root - B) / C;
  return x > 0n ? x : 0n;
}

/** Floor integer square root. Newton's method from an initial guess that is provably >= sqrt(n), so the
 *  iteration is monotone decreasing and converges in O(log n) steps for any size of n. */
export function isqrt(n: bigint): bigint {
  if (n < 0n) throw new Error("isqrt of negative");
  if (n < 2n) return n;
  const bits = n.toString(2).length;
  let x0 = 1n << BigInt((bits + 1) >> 1); // 2^ceil(bits/2) >= sqrt(n)
  for (;;) {
    const x1 = (x0 + n / x0) >> 1n;
    if (x1 >= x0) return x0;
    x0 = x1;
  }
}
