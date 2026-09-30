/**
 * Bit-exact BigInt port of Uniswap V3 core math (FullMath, TickMath, SqrtPriceMath, SwapMath, TickBitmap)
 * plus a swap simulator that walks initialized ticks exactly like UniswapV3Pool.swap.
 * Applies unchanged to Sushi V3, PancakeSwap V3 and Aerodrome Slipstream pools.
 */

export const Q96 = 1n << 96n;
export const Q128 = 1n << 128n;
export const MAX_UINT256 = (1n << 256n) - 1n;
export const MAX_UINT160 = (1n << 160n) - 1n;
export const MIN_TICK = -887272;
export const MAX_TICK = 887272;
export const MIN_SQRT_RATIO = 4295128739n;
export const MAX_SQRT_RATIO = 1461446703485210103287273052203988822378723970342n;

// ---------- FullMath ----------
export function mulDiv(a: bigint, b: bigint, d: bigint): bigint {
  if (d === 0n) throw new Error("mulDiv: division by zero");
  return (a * b) / d;
}
export function mulDivRoundingUp(a: bigint, b: bigint, d: bigint): bigint {
  const p = a * b;
  let r = p / d;
  if (p % d !== 0n) r += 1n;
  if (r > MAX_UINT256) throw new Error("mulDivRoundingUp overflow");
  return r;
}
function divRoundingUp(a: bigint, b: bigint): bigint {
  return a / b + (a % b === 0n ? 0n : 1n);
}

// ---------- TickMath ----------
export function getSqrtRatioAtTick(tick: number): bigint {
  const absTick = tick < 0 ? -tick : tick;
  if (absTick > MAX_TICK) throw new Error("T");
  let ratio = (absTick & 0x1) !== 0 ? 0xfffcb933bd6fad37aa2d162d1a594001n : 0x100000000000000000000000000000000n;
  if ((absTick & 0x2) !== 0) ratio = (ratio * 0xfff97272373d413259a46990580e213an) >> 128n;
  if ((absTick & 0x4) !== 0) ratio = (ratio * 0xfff2e50f5f656932ef12357cf3c7fdccn) >> 128n;
  if ((absTick & 0x8) !== 0) ratio = (ratio * 0xffe5caca7e10e4e61c3624eaa0941cd0n) >> 128n;
  if ((absTick & 0x10) !== 0) ratio = (ratio * 0xffcb9843d60f6159c9db58835c926644n) >> 128n;
  if ((absTick & 0x20) !== 0) ratio = (ratio * 0xff973b41fa98c081472e6896dfb254c0n) >> 128n;
  if ((absTick & 0x40) !== 0) ratio = (ratio * 0xff2ea16466c96a3843ec78b326b52861n) >> 128n;
  if ((absTick & 0x80) !== 0) ratio = (ratio * 0xfe5dee046a99a2a811c461f1969c3053n) >> 128n;
  if ((absTick & 0x100) !== 0) ratio = (ratio * 0xfcbe86c7900a88aedcffc83b479aa3a4n) >> 128n;
  if ((absTick & 0x200) !== 0) ratio = (ratio * 0xf987a7253ac413176f2b074cf7815e54n) >> 128n;
  if ((absTick & 0x400) !== 0) ratio = (ratio * 0xf3392b0822b70005940c7a398e4b70f3n) >> 128n;
  if ((absTick & 0x800) !== 0) ratio = (ratio * 0xe7159475a2c29b7443b29c7fa6e889d9n) >> 128n;
  if ((absTick & 0x1000) !== 0) ratio = (ratio * 0xd097f3bdfd2022b8845ad8f792aa5825n) >> 128n;
  if ((absTick & 0x2000) !== 0) ratio = (ratio * 0xa9f746462d870fdf8a65dc1f90e061e5n) >> 128n;
  if ((absTick & 0x4000) !== 0) ratio = (ratio * 0x70d869a156d2a1b890bb3df62baf32f7n) >> 128n;
  if ((absTick & 0x8000) !== 0) ratio = (ratio * 0x31be135f97d08fd981231505542fcfa6n) >> 128n;
  if ((absTick & 0x10000) !== 0) ratio = (ratio * 0x9aa508b5b7a84e1c677de54f3e99bc9n) >> 128n;
  if ((absTick & 0x20000) !== 0) ratio = (ratio * 0x5d6af8dedb81196699c329225ee604n) >> 128n;
  if ((absTick & 0x40000) !== 0) ratio = (ratio * 0x2216e584f5fa1ea926041bedfe98n) >> 128n;
  if ((absTick & 0x80000) !== 0) ratio = (ratio * 0x48a170391f7dc42444e8fa2n) >> 128n;
  if (tick > 0) ratio = MAX_UINT256 / ratio;
  // downcast to uint160 rounding up
  return (ratio >> 32n) + (ratio % (1n << 32n) === 0n ? 0n : 1n);
}

const mostSignificantBit = (x: bigint): number => x.toString(2).length - 1;

export function getTickAtSqrtRatio(sqrtPriceX96: bigint): number {
  if (!(sqrtPriceX96 >= MIN_SQRT_RATIO && sqrtPriceX96 < MAX_SQRT_RATIO)) throw new Error("R");
  const ratio = sqrtPriceX96 << 32n;
  const msb = BigInt(mostSignificantBit(ratio));
  let r = msb >= 128n ? ratio >> (msb - 127n) : ratio << (127n - msb);
  let log_2 = (msb - 128n) << 64n;
  for (let i = 63n; i >= 50n; i--) {
    r = (r * r) >> 127n;
    const f = r >> 128n;
    log_2 = log_2 | (f << i);
    r = r >> f;
  }
  const log_sqrt10001 = log_2 * 255738958999603826347141n;
  const tickLow = Number((log_sqrt10001 - 3402992956809132418596140100660247210n) >> 128n);
  const tickHi = Number((log_sqrt10001 + 291339464771989622907027621153398088495n) >> 128n);
  if (tickLow === tickHi) return tickLow;
  return getSqrtRatioAtTick(tickHi) <= sqrtPriceX96 ? tickHi : tickLow;
}

// ---------- SqrtPriceMath ----------
export function getNextSqrtPriceFromAmount0RoundingUp(sqrtPX96: bigint, liquidity: bigint, amount: bigint, add: boolean): bigint {
  if (amount === 0n) return sqrtPX96;
  const numerator1 = liquidity << 96n;
  const product = amount * sqrtPX96;
  if (add) {
    if (product / amount === sqrtPX96 && product <= MAX_UINT256) {
      const denominator = numerator1 + product;
      if (denominator >= numerator1) return mulDivRoundingUp(numerator1, sqrtPX96, denominator);
    }
    return divRoundingUp(numerator1, numerator1 / sqrtPX96 + amount);
  } else {
    if (!(product / amount === sqrtPX96 && numerator1 > product)) throw new Error("price underflow");
    const denominator = numerator1 - product;
    return mulDivRoundingUp(numerator1, sqrtPX96, denominator);
  }
}

export function getNextSqrtPriceFromAmount1RoundingDown(sqrtPX96: bigint, liquidity: bigint, amount: bigint, add: boolean): bigint {
  if (add) {
    const quotient = amount <= MAX_UINT160 ? (amount << 96n) / liquidity : mulDiv(amount, Q96, liquidity);
    return sqrtPX96 + quotient;
  } else {
    const quotient = amount <= MAX_UINT160 ? divRoundingUp(amount << 96n, liquidity) : mulDivRoundingUp(amount, Q96, liquidity);
    if (!(sqrtPX96 > quotient)) throw new Error("price underflow");
    return sqrtPX96 - quotient;
  }
}

export function getNextSqrtPriceFromInput(sqrtPX96: bigint, liquidity: bigint, amountIn: bigint, zeroForOne: boolean): bigint {
  if (sqrtPX96 <= 0n || liquidity <= 0n) throw new Error("bad price/liquidity");
  return zeroForOne
    ? getNextSqrtPriceFromAmount0RoundingUp(sqrtPX96, liquidity, amountIn, true)
    : getNextSqrtPriceFromAmount1RoundingDown(sqrtPX96, liquidity, amountIn, true);
}

export function getNextSqrtPriceFromOutput(sqrtPX96: bigint, liquidity: bigint, amountOut: bigint, zeroForOne: boolean): bigint {
  if (sqrtPX96 <= 0n || liquidity <= 0n) throw new Error("bad price/liquidity");
  return zeroForOne
    ? getNextSqrtPriceFromAmount1RoundingDown(sqrtPX96, liquidity, amountOut, false)
    : getNextSqrtPriceFromAmount0RoundingUp(sqrtPX96, liquidity, amountOut, false);
}

export function getAmount0Delta(sqrtA: bigint, sqrtB: bigint, liquidity: bigint, roundUp: boolean): bigint {
  if (sqrtA > sqrtB) [sqrtA, sqrtB] = [sqrtB, sqrtA];
  const numerator1 = liquidity << 96n;
  const numerator2 = sqrtB - sqrtA;
  if (sqrtA <= 0n) throw new Error("sqrtA<=0");
  return roundUp
    ? divRoundingUp(mulDivRoundingUp(numerator1, numerator2, sqrtB), sqrtA)
    : mulDiv(numerator1, numerator2, sqrtB) / sqrtA;
}

export function getAmount1Delta(sqrtA: bigint, sqrtB: bigint, liquidity: bigint, roundUp: boolean): bigint {
  if (sqrtA > sqrtB) [sqrtA, sqrtB] = [sqrtB, sqrtA];
  return roundUp ? mulDivRoundingUp(liquidity, sqrtB - sqrtA, Q96) : mulDiv(liquidity, sqrtB - sqrtA, Q96);
}

// ---------- SwapMath ----------
export interface SwapStep {
  sqrtRatioNextX96: bigint;
  amountIn: bigint;
  amountOut: bigint;
  feeAmount: bigint;
}

export function computeSwapStep(
  sqrtRatioCurrentX96: bigint,
  sqrtRatioTargetX96: bigint,
  liquidity: bigint,
  amountRemaining: bigint,
  feePips: number,
): SwapStep {
  const fee = BigInt(feePips);
  const zeroForOne = sqrtRatioCurrentX96 >= sqrtRatioTargetX96;
  const exactIn = amountRemaining >= 0n;
  let sqrtRatioNextX96: bigint;
  let amountIn = 0n;
  let amountOut = 0n;
  let feeAmount: bigint;

  if (exactIn) {
    const amountRemainingLessFee = mulDiv(amountRemaining, 1_000_000n - fee, 1_000_000n);
    amountIn = zeroForOne
      ? getAmount0Delta(sqrtRatioTargetX96, sqrtRatioCurrentX96, liquidity, true)
      : getAmount1Delta(sqrtRatioCurrentX96, sqrtRatioTargetX96, liquidity, true);
    if (amountRemainingLessFee >= amountIn) sqrtRatioNextX96 = sqrtRatioTargetX96;
    else sqrtRatioNextX96 = getNextSqrtPriceFromInput(sqrtRatioCurrentX96, liquidity, amountRemainingLessFee, zeroForOne);
  } else {
    amountOut = zeroForOne
      ? getAmount1Delta(sqrtRatioTargetX96, sqrtRatioCurrentX96, liquidity, false)
      : getAmount0Delta(sqrtRatioCurrentX96, sqrtRatioTargetX96, liquidity, false);
    if (-amountRemaining >= amountOut) sqrtRatioNextX96 = sqrtRatioTargetX96;
    else sqrtRatioNextX96 = getNextSqrtPriceFromOutput(sqrtRatioCurrentX96, liquidity, -amountRemaining, zeroForOne);
  }

  const max = sqrtRatioTargetX96 === sqrtRatioNextX96;

  if (zeroForOne) {
    amountIn = max && exactIn ? amountIn : getAmount0Delta(sqrtRatioNextX96, sqrtRatioCurrentX96, liquidity, true);
    amountOut = max && !exactIn ? amountOut : getAmount1Delta(sqrtRatioNextX96, sqrtRatioCurrentX96, liquidity, false);
  } else {
    amountIn = max && exactIn ? amountIn : getAmount1Delta(sqrtRatioCurrentX96, sqrtRatioNextX96, liquidity, true);
    amountOut = max && !exactIn ? amountOut : getAmount0Delta(sqrtRatioCurrentX96, sqrtRatioNextX96, liquidity, false);
  }

  if (!exactIn && amountOut > -amountRemaining) amountOut = -amountRemaining;

  if (exactIn && sqrtRatioNextX96 !== sqrtRatioTargetX96) {
    feeAmount = amountRemaining - amountIn;
  } else {
    feeAmount = mulDivRoundingUp(amountIn, fee, 1_000_000n - fee);
  }
  return { sqrtRatioNextX96, amountIn, amountOut, feeAmount };
}

// ---------- TickBitmap ----------
export function tickPosition(tick: number): { wordPos: number; bitPos: number } {
  // arithmetic shift right of int24 → floor division by 256
  const wordPos = tick >> 8;
  const bitPos = tick & 0xff;
  return { wordPos, bitPos };
}

/** floor division for negative ticks, matching Solidity `tick / tickSpacing` with the V3 adjustment. */
export function compressTick(tick: number, tickSpacing: number): number {
  let compressed = Math.trunc(tick / tickSpacing);
  if (tick < 0 && tick % tickSpacing !== 0) compressed -= 1;
  return compressed;
}

export type TickBitmapWords = Map<number, bigint>; // wordPos -> uint256 word

/** Port of TickBitmap.nextInitializedTickWithinOneWord. Also reports which bitmap word was consulted. */
export function nextInitializedTickWithinOneWord(
  bitmap: TickBitmapWords,
  tick: number,
  tickSpacing: number,
  lte: boolean,
): { next: number; initialized: boolean; wordPos: number } {
  const compressed = compressTick(tick, tickSpacing);
  if (lte) {
    const { wordPos, bitPos } = tickPosition(compressed);
    const mask = (1n << BigInt(bitPos)) - 1n + (1n << BigInt(bitPos));
    const word = bitmap.get(wordPos) ?? 0n;
    const masked = word & mask;
    const initialized = masked !== 0n;
    const next = initialized
      ? (compressed - (bitPos - mostSignificantBit(masked))) * tickSpacing
      : (compressed - bitPos) * tickSpacing;
    return { next, initialized, wordPos };
  } else {
    const { wordPos, bitPos } = tickPosition(compressed + 1);
    const mask = ~((1n << BigInt(bitPos)) - 1n) & MAX_UINT256;
    const word = bitmap.get(wordPos) ?? 0n;
    const masked = word & mask;
    const initialized = masked !== 0n;
    const next = initialized
      ? (compressed + 1 + (leastSignificantBit(masked) - bitPos)) * tickSpacing
      : (compressed + 1 + (255 - bitPos)) * tickSpacing;
    return { next, initialized, wordPos };
  }
}

function leastSignificantBit(x: bigint): number {
  if (x === 0n) throw new Error("lsb(0)");
  let i = 0;
  while ((x & 1n) === 0n) {
    x >>= 1n;
    i++;
  }
  return i;
}

// ---------- Swap simulation ----------
export interface V3PoolState {
  sqrtPriceX96: bigint;
  tick: number;
  liquidity: bigint;
  fee: number; // pips (1e-6)
  tickSpacing: number;
  bitmap: TickBitmapWords;
  /** tick -> liquidityNet for every initialized tick we have fetched. */
  ticks: Map<number, bigint>;
  /** Word range we fetched; a swap that walks outside it is flagged `truncated`. */
  wordRange: { min: number; max: number };
}

export interface SwapResult {
  amountIn: bigint; // gross input consumed (incl. fee)
  amountOut: bigint;
  sqrtPriceX96After: bigint;
  tickAfter: number;
  liquidityAfter: bigint;
  ticksCrossed: number;
  /** true if the simulation ran out of fetched tick data or liquidity before consuming all input. */
  truncated: boolean;
}

/**
 * Exact-input swap simulation. Returns the pool's amountOut for `amountIn` of tokenIn
 * (token0 if zeroForOne). Mirrors UniswapV3Pool.swap without state mutation.
 */
export function simulateExactInput(pool: V3PoolState, zeroForOne: boolean, amountIn: bigint): SwapResult {
  if (amountIn <= 0n) throw new Error("amountIn must be > 0");
  const sqrtPriceLimitX96 = zeroForOne ? MIN_SQRT_RATIO + 1n : MAX_SQRT_RATIO - 1n;
  let amountRemaining = amountIn;
  let amountOut = 0n;
  let sqrtPriceX96 = pool.sqrtPriceX96;
  let tick = pool.tick;
  let liquidity = pool.liquidity;
  let ticksCrossed = 0;
  let truncated = false;
  let guard = 0;

  while (amountRemaining !== 0n && sqrtPriceX96 !== sqrtPriceLimitX96) {
    if (++guard > 1000) {
      truncated = true;
      break;
    }
    const sqrtPriceStartX96 = sqrtPriceX96;
    const { next, initialized, wordPos } = nextInitializedTickWithinOneWord(pool.bitmap, tick, pool.tickSpacing, zeroForOne);
    if (wordPos < pool.wordRange.min || wordPos > pool.wordRange.max) {
      truncated = true;
      break;
    }
    let tickNext = next;
    if (tickNext < MIN_TICK) tickNext = MIN_TICK;
    else if (tickNext > MAX_TICK) tickNext = MAX_TICK;
    const sqrtPriceNextX96 = getSqrtRatioAtTick(tickNext);
    const target = zeroForOne
      ? sqrtPriceNextX96 < sqrtPriceLimitX96
        ? sqrtPriceLimitX96
        : sqrtPriceNextX96
      : sqrtPriceNextX96 > sqrtPriceLimitX96
        ? sqrtPriceLimitX96
        : sqrtPriceNextX96;

    // computeSwapStep handles liquidity == 0 exactly like the pool does (price jumps to target, nothing fills).
    const step = computeSwapStep(sqrtPriceX96, target, liquidity, amountRemaining, pool.fee);
    sqrtPriceX96 = step.sqrtRatioNextX96;
    amountRemaining -= step.amountIn + step.feeAmount;
    amountOut += step.amountOut;

    if (sqrtPriceX96 === sqrtPriceNextX96) {
      if (initialized) {
        const net = pool.ticks.get(tickNext);
        if (net === undefined) {
          truncated = true;
          break;
        }
        liquidity += zeroForOne ? -net : net;
        ticksCrossed++;
      }
      tick = zeroForOne ? tickNext - 1 : tickNext;
    } else if (sqrtPriceX96 !== sqrtPriceStartX96) {
      tick = getTickAtSqrtRatio(sqrtPriceX96);
    }
  }
  if (amountRemaining > 0n) truncated = true; // hit the price limit before consuming all input
  return {
    amountIn: amountIn - amountRemaining,
    amountOut,
    sqrtPriceX96After: sqrtPriceX96,
    tickAfter: tick,
    liquidityAfter: liquidity,
    ticksCrossed,
    truncated,
  };
}

/** Spot price of token1 in token0 terms as a float (for ranking/logging only). */
export function sqrtPriceToPrice(sqrtPriceX96: bigint, dec0: number, dec1: number): number {
  const p = Number(sqrtPriceX96) / Number(Q96);
  return p * p * 10 ** (dec0 - dec1);
}
