import { test } from "node:test";
import assert from "node:assert/strict";
import { isqrt, optimalV2Cycle, univ2GetAmountOut } from "./v2.js";

test("isqrt is exact and fast for huge values", () => {
  const cases = [0n, 1n, 2n, 3n, 4n, 15n, 16n, 17n, 10n ** 18n, 10n ** 36n + 12345n, (1n << 255n) - 1n, 10n ** 112n + 7n, 3n * 10n ** 130n];
  for (const n of cases) {
    const t0 = Date.now();
    const r = isqrt(n);
    assert.ok(r * r <= n && (r + 1n) * (r + 1n) > n, `isqrt(${n}) = ${r}`);
    assert.ok(Date.now() - t0 < 50, "must be fast");
  }
  // random fuzz
  for (let i = 0; i < 2000; i++) {
    const bits = 1 + Math.floor(Math.random() * 400);
    let n = 0n;
    for (let b = 0; b < bits; b += 30) n = (n << 30n) | BigInt(Math.floor(Math.random() * 2 ** 30));
    const r = isqrt(n);
    assert.ok(r * r <= n && (r + 1n) * (r + 1n) > n);
  }
});

test("optimalV2Cycle maximises the two-pool cycle profit", () => {
  // pool1: 100 WETH / 300k USDC (0.3%), pool2: 310k USDC / 100 WETH (0.3%) → ETH cheaper on pool1
  const a1 = 100n * 10n ** 18n, b1 = 300_000n * 10n ** 6n, b2 = 310_000n * 10n ** 6n, a2 = 100n * 10n ** 18n;
  // sell USDC into pool1 (reserves: in=b1, out=a1) then WETH into pool2 (in=a2, out=b2)
  const x = optimalV2Cycle(b1, a1, 30, a2, b2, 30);
  assert.ok(x > 0n);
  const profit = (amt: bigint) => univ2GetAmountOut(univ2GetAmountOut(amt, b1, a1, 30), a2, b2, 30) - amt;
  const p = profit(x);
  assert.ok(p > 0n, `profit ${p}`);
  // neighbours must not be better (unimodal optimum)
  assert.ok(profit((x * 99n) / 100n) <= p);
  assert.ok(profit((x * 101n) / 100n) <= p);
  // huge reserves (the case that used to hang): 18-decimal tokens with 1e27 reserves
  const t0 = Date.now();
  const y = optimalV2Cycle(10n ** 27n, 10n ** 27n, 30, 10n ** 27n, 11n * 10n ** 26n, 25);
  assert.ok(Date.now() - t0 < 100);
  assert.ok(y > 0n);
});
