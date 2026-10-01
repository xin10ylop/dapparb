import { test } from "node:test";
import assert from "node:assert/strict";
import type { Address } from "viem";
import type { V2Pool } from "../pools/types.js";
import { CycleIndex } from "./incremental.js";
import { findTriangles } from "./triangles.js";

const WETH = "0x4200000000000000000000000000000000000006" as Address;
const USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913" as Address;
const TOK = "0x1111111111111111111111111111111111111111" as Address;
const E18 = 10n ** 18n, E6 = 10n ** 6n;

let n = 0;
function v2(a: Address, b: Address, ra: bigint, rb: bigint, decA: number, decB: number): V2Pool {
  const [token0, token1, r0, r1, dec0, dec1] = a.toLowerCase() < b.toLowerCase() ? [a, b, ra, rb, decA, decB] : [b, a, rb, ra, decB, decA];
  n++;
  return { address: `0x${n.toString(16).padStart(40, "0")}` as Address, dex: "UniswapV2", kind: "univ2", feeBps: 30, stable: false, token0, token1, dec0, dec1, reserve0: r0, reserve1: r1, block: 0n };
}

test("triangle through a touched pool matches the full triangle search and starts in WETH", () => {
  // WETH = 3000 USDC; TOK = 1 USDC on its USDC pool but 1/2500 WETH (= 1.2 USDC) on its WETH pool: a ~20% triangle
  const wethUsdc = v2(WETH, USDC, 100n * E18, 300_000n * E6, 18, 6);
  const tokUsdc = v2(TOK, USDC, 200_000n * E18, 200_000n * E6, 18, 6);
  const tokWeth = v2(TOK, WETH, 250_000n * E18, 100n * E18, 18, 18);
  const pools = [wethUsdc, tokUsdc, tokWeth];
  const idx = new CycleIndex(pools, [WETH, USDC]);
  const inc = idx.searchTriangles([tokUsdc.address], 1000);
  assert.ok(inc.length > 0, "found the triangle");
  assert.equal(inc[0]!.token.toLowerCase(), WETH.toLowerCase(), "rotated to start in WETH");
  assert.equal(inc[0]!.hops.length, 3);
  const full = findTriangles(pools, { startTokens: new Set([WETH.toLowerCase()]) });
  assert.ok(full.length > 0);
  // same best profit as the full search (same pools, same sizing)
  assert.equal(inc[0]!.profit, full[0]!.profit);
  // a pool not on the triangle finds nothing
  assert.equal(idx.searchTriangles(["0x00000000000000000000000000000000000000ff"], 100).length, 0);
});

test("pools added later join both the two-pool and triangle indexes", () => {
  const wethUsdc = v2(WETH, USDC, 100n * E18, 300_000n * E6, 18, 6);
  const tokUsdc = v2(TOK, USDC, 200_000n * E18, 200_000n * E6, 18, 6);
  const idx = new CycleIndex([wethUsdc, tokUsdc], [WETH, USDC]);
  assert.equal(idx.searchTriangles([tokUsdc.address], 100).length, 0);
  const tokWeth = v2(TOK, WETH, 250_000n * E18, 100n * E18, 18, 18);
  idx.add(tokWeth);
  assert.ok(idx.searchTriangles([tokWeth.address], 1000).length > 0, "triangle via the new pool");
  // a second WETH/USDC pool 2% off gives a two-pool cycle
  const wethUsdc2 = v2(WETH, USDC, 100n * E18, 306_000n * E6, 18, 6);
  idx.add(wethUsdc2);
  assert.equal(idx.pools, 4);
  assert.ok(idx.search([wethUsdc2.address], 1000).length > 0, "two-pool cycle via the new pool");
  idx.add(wethUsdc2); // idempotent
  assert.equal(idx.pools, 4);
});
