> For the complete documentation index, see [llms.txt](https://docs.flap.sh/flap/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.flap.sh/flap/developers/basic-and-mechanism/bonding-curve.md).

# Bonding Curve

{% hint style="info" %}
Since v2.4.0, Flap supports multiple bonding curves, but only one is active for a quote token.
{% endhint %}

### What is a Bonding Curve

Before migrating to DEX, each token launched on flap is bonded to a bonding curve. When you buy tokens from the bonding curve, you send your ETH ( or other quote token: BNB, USDT etc) to the bonding curve as a reserve, and the bonding curve mints tokens to your address. Or if you sell your tokens to the bonding curve, the bonding curve will burn your selling tokens and send the ETH back to you.

{% hint style="info" %}
Under the hood, we don't implement it as burn & mint. Initially, all the tokens are in our bonding curve contract until the user buys 80% of the total supply and the remaining token will be added to DEX as liquidity.
{% endhint %}

<figure><img src="https://2671086575-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F5KujUBwRoHVjn8OZEgtZ%2Fuploads%2FxYdFM0ADkLAeAIJo56Kh%2Fimage.png?alt=media&amp;token=a0bf6998-b2e0-4a40-9c4d-bc568f96cfa7" alt=""><figcaption></figcaption></figure>

A bonding curve defines the relationship between the trading token's supply and the reserve (i.e. Quote tokens like ETH or BNB). The change of the reserve respect to the supply is the price. Our bonding curve is based on a constant product equation. You may have heard about this equation, which Uniswap popularized.

You may even wonder what is the difference between a bonding curve token launching platform like flap and Unsiwap? The answer is the liquidity. The liquidity does not change on the bonding curve. However, anyone can add liquidity to the Uniswap pools.

### Flap's Bonding Curve V2

The token created on our platform has the same max supply of $$10^9$$ , with 18 decimals. For each token, the amounts of token and the Quote (ETH, BNB or USD\*) follow the following constant product equation:

$$
(x+ h)(y + r) = K
$$

$$r$$ ,$$h$$ and $$K$$ are constant parameters dependent on the target chain ( check [#bonding-curves-on-different-chains](#bonding-curves-on-different-chains "mention") for more details).

$$
(x+ h)(y + r) = K
$$

* $$x$$ is the amount of token in the bonding curve (i.e: token reserve), initially, it is $$10^9$$, which means all the tokens are in the bonding curve in the beginning.
* $$y$$ is the amount of quote token (i.e: quote reserve) , it is 0 in the beginning.
* Our curve have 3 constant parameters:
  * $$r$$ can be interpreted as the virtual reserve of quote token in the bonding curve
  * $$h$$ can be interpreted as the virtual reserve of the launched token in the bonding curve
  * $$K$$ is the square of the virtual liquidity

### Bonding Curves On Different Chains

{% hint style="danger" %}
The following table may be out of date.\
\
We don't recommend that you hardcode the bonding curve parameters in your application. Instead, you should use `getTokenV5` method from the Portal contract to get the parameters for each token. The parameters are immutable for each token, so you only need to fetch them once and cache them in your application.
{% endhint %}

For different and different quote token , the constants are different:

<table><thead><tr><th width="317.43804931640625">Chain</th><th width="126.9757080078125">r</th><th>h</th><th>K</th></tr></thead><tbody><tr><td>BSC (Legacy before block #42042177 )</td><td>15</td><td>0</td><td><span class="math">15 \cdot 10^{9}</span></td></tr><tr><td>BSC (Legacy since block 42042177 and before 47855189 )</td><td>4</td><td>0</td><td><span class="math">4 \cdot 10^{9}</span></td></tr><tr><td>BSC (Legacy since block 47855189 and before <a href="https://bscscan.com/block/51314696">51314696</a>)</td><td>2</td><td>0</td><td><span class="math">2 \cdot 10^{9}</span></td></tr><tr><td>BSC(before 61837444, BNB as payment Token)</td><td>4</td><td>0</td><td><span class="math">4 \cdot 10^{9}</span></td></tr><tr><td>BSC(before 61837444, USD1/lisUSD as payment token)</td><td>2500</td><td>0</td><td><span class="math">2500 \cdot 10^{9}</span></td></tr><tr><td>BSC(lastest, BNB as payment Token)</td><td>6.14</td><td>107036752</td><td>6797205657.28</td></tr><tr><td>BSC(latest, USD1/lisUSD as payment token)</td><td>3837</td><td>107036752</td><td>4247700017424</td></tr><tr><td>ToshiMart</td><td>0.5</td><td>0</td><td><span class="math">0.5 \cdot 10^{9}</span></td></tr><tr><td>XLayer (Before block 31564005)</td><td>28</td><td>0</td><td><span class="math">28 \cdot 10^{9}</span></td></tr><tr><td>XLayer (Before block 32470187)</td><td>21.25</td><td>0</td><td><span class="math">21.25 \cdot 10^{9}</span></td></tr><tr><td>XLayer(Since block 32470187)</td><td>28.25</td><td>108002126</td><td>31301060059</td></tr><tr><td>Monad (mainnet)</td><td>50000</td><td>107036752</td><td>55351837600000</td></tr></tbody></table>

### Example Curve BNB

{% embed url="<https://www.desmos.com/calculator/qu77rif6q0>" %}
