# 03-v2-older-pairs: V2-style pools the section 2.6 run did not enumerate, and 24 h of V2-style activity on Base

Raw material only. This file maps the data, says how it was produced, and lists what is missing. It contains no findings,
rankings or conclusions. Every value below that is not a copy of an RPC response is marked **derived**, and each derivation
is deterministic and lossless (a decoded ABI field, a flag computed from an index, or a sum or count of raw event fields).

**Status: COMPLETE** (set 2026-10-01 after re-verification). In `/home/user/dapparb/research-material/.sentinels/`:
`V2OLD_SNAPSHOT.DONE` (22:17:38Z, `rows=125197 parts=1 snapshot_gaps=0`), `V2OLD_CENSUS.DONE` (22:18:46Z, `log_rows=304359
activity_rows=30921 emitters=4385 window=51965201-52008400`), `V2OLD_TOKENS.DONE` (22:23:43Z) and `V2OLD.DONE` (22:24:35Z,
`gaps=0 too_big=[]`), all 2026-09-30; no `V2OLD*.FAILED` sentinel exists. `gaps.csv` does not exist (0 unrecoverable batches or
ranges). Every file in the directory was re-read on 2026-10-01 (see "Verified inventory (2026-10-01)"); no committed file is over
90 MB. All collectors of this directory finished at 22:24:35Z on 2026-09-30, before the container restart at ~23:00Z, and none was
re-run. The coverage limits that are part of the design (Uniswap V2 sampled, one pinned block, four event topics) are in section 7.

The block below was written by `collect/finalize.py` at the end of the run (re-running `finalize.py` rewrites only this block,
`file-index.csv` and the `V2OLD` sentinel). Its row counts, byte sizes and sha256 prefixes were re-checked on 2026-10-01 and all
match the files.

<!-- AUTO-STATUS-BEGIN -->

**Status: COMPLETE** (filled by `collect/finalize.py` at 2026-09-30T22:24:35Z).

| Component sentinel | State |
|---|---|
| `.sentinels/V2OLD_SNAPSHOT` | DONE |
| `.sentinels/V2OLD_CENSUS` | DONE |
| `.sentinels/V2OLD_TOKENS` | DONE |

Rows in gaps.csv (unrecoverable batches/ranges): 0. Files over 90 MB: none.

| File | Data rows (excl. header) | Bytes | sha256 |
|---|---:|---:|---|
| `activity-pool-hour.csv.gz` | 30921 | 1270678 | `0d5245559cf5e02e…` |
| `buckets.csv` | 24 | 5391 | `cea2da263c7c7424…` |
| `census-chunks.csv` | 87 | 9377 | `32c149c18327c2b8…` |
| `census-crosscheck.csv` | 3 | 309 | `ca0069d5d0985c7e…` |
| `census-logs-part-0001.csv.gz` | 304359 | 29589834 | `6485a7a9fa71a982…` |
| `census-meta.json` |  | 1339 | `e7455c7de4088612…` |
| `emitters.csv.gz` | 4385 | 375763 | `5b4200c6c01c10f8…` |
| `factories.csv` | 8 | 2514 | `5724ffc98b437801…` |
| `factory-length-history.csv` | 840 | 81802 | `757aa59cceec45fa…` |
| `getreserves-abi.csv` | 5 | 2642 | `b31d0d24588d5c2b…` |
| `pools-part-0001.csv.gz` | 125197 | 9340614 | `887bbcf42c613eca…` |
| `price-reference-weth-pools.csv.gz` | 7640 | 583851 | `313adafa3a4f51e0…` |
| `snapshot-meta.json` |  | 962 | `320e66f35a648f1d…` |
| `tokens-meta.json` |  | 287 | `782192e8dc99dafe…` |
| `tokens.csv.gz` | 111983 | 4793479 | `d78f917a5f2af35d…` |
| `topics.csv` | 4 | 2196 | `0326e19622995abc…` |
| `uniswapv2-sample-indices.csv.gz` | 66000 | 222474 | `0eb7a12b2bd99a51…` |

Snapshot rows by factory/sample group: `{"Aerodrome/all_indices": 29601, "BaseSwap/all_indices": 8258, "PancakeV2/all_indices": 15243, "SushiV2/all_indices": 6095, "UniswapV2/newest_6000_at_snapshot": 6000, "UniswapV2/random_sample_older": 60000}`

Census: window 51965201-52008400, log rows 304359 by event `{"sync_uint112": 82788, "swap_univ2": 84002, "sync_uint256": 71714, "swap_aero_v2": 65855}`, activity rows 30921, distinct emitters 4385, missing chunks [].

Tokens: 111983 tokens with metadata; WETH-route set 6862 tokens, 247032 lookups, 7640 pool rows.

Full per-file list with complete sha256: `file-index.csv`.

<!-- AUTO-STATUS-END -->

## Verified inventory (2026-10-01)

Every file under this directory, recursively: 125 files. 29 are committed (this manifest, 18 data/metadata files at the top level,
10 scripts and logs in `collect/`). 96 are local-only: everything under `collect/state/` is git-ignored
(`research-material/**/collect/state/` in the repository `.gitignore`) and will **not** be in the repository.
The largest committed file is `census-logs-part-0001.csv.gz` (29,589,834 bytes); no committed file is over 90 MB.

How each file was checked (streamed, at most ~22 MB RSS): bytes from the file system; sha256 of the file as stored;
`gzip -t` for every `.gz`; for CSV, the number of records read with Python's `csv` module (equal to the number of newline
characters in every CSV here, so no field contains a line break) and the set of column counts per record; every `.json` file and
every line of every `.jsonl.gz` file parsed with Python's `json`. "Rows / lines" for CSV = data records (header excluded);
the `collect/state/census/chunks/*.csv.gz` files have no header. Every count that the auto-status block, `file-index.csv`, the
`*-meta.json` files or the sentinels state matches the verified count, and the sha256 values equal those in `file-index.csv`. In addition, each `collect/state/census/chunks/<a>_<b>.csv.gz`
decompresses to exactly the same bytes as the rows of `census-logs-part-0001.csv.gz` with `block_number` in [a, b]
(checked by sha256 for all 87 chunks; the row counts per chunk also equal `census-chunks.csv` `log_rows`), and the 87 lines
of `collect/state/census/chunks.jsonl.gz` hold the same values as `census-chunks.csv` (fields `a`, `b`, `n`, `endpoints`,
`secs`, `utc` = `chunk_start`, `chunk_end`, `log_rows`, `endpoints_used`, `fetch_secs`, `fetched_utc`).

| File | Bytes | Rows / lines | Check | sha256 | Git |
|---|---:|---|---|---|---|
| `MANIFEST.md` | (this file) | | | (not hashed: changes with every edit) | committed |
| `activity-pool-hour.csv.gz` | 1,270,678 | 30,921 data rows + header | gzip -t ok; 18 columns in every row | `0d5245559cf5e02eba3251dc38a295617b8f30afeeb16f34411c066118c770dd` | committed |
| `buckets.csv` | 5,391 | 24 data rows + header | 9 columns in every row | `cea2da263c7c7424eb3333d0b6a658c55818d565d664e5d9cd952fd115862585` | committed |
| `census-chunks.csv` | 9,377 | 87 data rows + header | 7 columns in every row | `32c149c18327c2b82731909370e0d4fb9c9b3eb0e4567c29132c9edd0e967395` | committed |
| `census-crosscheck.csv` | 309 | 3 data rows + header | 9 columns in every row | `ca0069d5d0985c7eb13e55f6e9571dcb8e64bad983485006084a10e1111c41c0` | committed |
| `census-logs-part-0001.csv.gz` | 29,589,834 | 304,359 data rows + header | gzip -t ok; 23 columns in every row | `6485a7a9fa71a982d6ee5565026810d650307a368ec29e4c4bfe49586c1dfb91` | committed |
| `census-meta.json` | 1,339 | 47 lines | parses as JSON | `e7455c7de408861217ab53cef517c6d40a954949811b384e5277e2e03c34d047` | committed |
| `emitters.csv.gz` | 375,763 | 4,385 data rows + header | gzip -t ok; 19 columns in every row | `5b4200c6c01c10f882e5c52a19ed5eaf8166b3e66821959e59cdbb07d5842e37` | committed |
| `factories.csv` | 2,514 | 8 data rows + header | 23 columns in every row | `5724ffc98b437801059c7c97bde4fbfeb24c83ab319dabc01c8a045c8c1f7670` | committed |
| `factory-length-history.csv` | 81,802 | 840 data rows + header | 7 columns in every row | `757aa59cceec45fa3e7db6957bf6faeb3faf1bbd996954df5c5c06a7c617b7eb` | committed |
| `file-index.csv` | 1,747 | 17 data rows + header | 5 columns in every row | `cfaeda2c559201bdbf8804026d445a94cc1158360d4a99bef4973f41db747805` | committed |
| `getreserves-abi.csv` | 2,642 | 5 data rows + header | 9 columns in every row | `b31d0d24588d5c2b4c0bd13210e71523f2497f0f9b7c47531c0e67637937b6d1` | committed |
| `pools-part-0001.csv.gz` | 9,340,614 | 125,197 data rows + header | gzip -t ok; 26 columns in every row | `887bbcf42c613eca2c9f810740e1e05dde12a3666d302b141fdd85834a2b92d4` | committed |
| `price-reference-weth-pools.csv.gz` | 583,851 | 7,640 data rows + header | gzip -t ok; 25 columns in every row | `313adafa3a4f51e0d19b63f00134b6cae55aaad7890492c3de6bcdaa37792ade` | committed |
| `snapshot-meta.json` | 962 | 35 lines | parses as JSON | `320e66f35a648f1d5b936f308a18eeba2805a2143cc8e529ffc5d1dd4843d5ba` | committed |
| `tokens-meta.json` | 287 | 16 lines | parses as JSON | `782192e8dc99dafe890f75803fac00ff7c6ae59037771bcb10582e005cd12dc6` | committed |
| `tokens.csv.gz` | 4,793,479 | 111,983 data rows + header | gzip -t ok; 16 columns in every row | `d78f917a5f2af35d383bb7ec0aeca7ddeecb93648ad01a6fad8c388d8d0593c3` | committed |
| `topics.csv` | 2,196 | 4 data rows + header | 13 columns in every row | `0326e19622995abc3d732ab13632bc7af3e1c381be02cb3f7e64fef3ab06c064` | committed |
| `uniswapv2-sample-indices.csv.gz` | 222,474 | 66,000 data rows + header | gzip -t ok; 6 columns in every row | `0eb7a12b2bd99a518222784781e5f2acbe22bf2d29fa91b5c44c2e4e658acf5d` | committed |
| `collect/abi_shapes.log` | 2,637 | 7 lines |  | `a631a3ce2acee2388361d9c046e3844afcaaa9d8e410619e71027c02f7b89d12` | committed |
| `collect/abi_shapes.py` | 2,443 | 41 lines |  | `c2fecf8b517481940826108dda8cec658f5b5bfad26c8027d8d2ebd3aece2c97` | committed |
| `collect/census.log` | 2,293 | 15 lines |  | `992ea711f69dd1893efe8175f1477e9e78d586d3abcb3743bbb188ba0e5777bd` | committed |
| `collect/census.py` | 23,143 | 441 lines |  | `f09364255bfc8009de73efcf803247f084d7d2cad4c47a5224b3d7d8312105a6` | committed |
| `collect/finalize.py` | 4,773 | 90 lines |  | `e154f1b28ab34ce39663a9d026c3771e2b56c279bb24458ef59d5f26784ee2ee` | committed |
| `collect/rpclib.py` | 13,091 | 350 lines |  | `78e50b08b7fd78dae30e0405d56d0407aae7dddffeb0530f20dc76d0e9bf539b` | committed |
| `collect/snapshot.log` | 3,677 | 42 lines |  | `1b2325f01fec095c29525505b4f1ff868cc4f52b3ddf7aaf4530f1848f0e77e8` | committed |
| `collect/snapshot.py` | 18,544 | 345 lines |  | `df2da2089ad53b01b4ae5da358729c509ce3dc35c66386d5afc68412757f4c52` | committed |
| `collect/tokens.log` | 1,614 | 26 lines |  | `977acce25d8089b9fbb4bc8b394888d2c7ed4b9434202ebf5448b4d14beab9ff` | committed |
| `collect/tokens.py` | 14,888 | 261 lines |  | `1efcd0672aa44b04b41555408e348f25da315756c575bcbd10bac14402db905d` | committed |
| `collect/state/aerofee.jsonl.gz` | 10,154 | 60 lines (one batch each) | gzip -t ok; every line parses as JSON | `08bb430c43dc5ee6dc01df89247b99bd02bbece222536862e9b2f6dc7c0dad39` | local-only (R1) |
| `collect/state/census/chunks.jsonl.gz` | 1,427 | 87 lines (one per census chunk) | gzip -t ok; every line parses as JSON | `47577f3dac524303ce38a9a3379c11a63bc87d7208ec03a6d224666549fbb25d` | local-only (R2) |
| `collect/state/census/chunks/051965201_051965700.csv.gz` | 277,370 | 2,767 rows (no header) | gzip -t ok; 23 columns in every row | `24597d1aee8c16eecc642cf3eff77cdd6c36aa8eb5a972ea4cbef4d1c334a0a7` | local-only (R2) |
| `collect/state/census/chunks/051965701_051966200.csv.gz` | 300,885 | 3,050 rows (no header) | gzip -t ok; 23 columns in every row | `8383eaec7e2cb6ba0364e609ea6eaf9f3040e529ba4d9deeaea2bf43c9a67d6c` | local-only (R2) |
| `collect/state/census/chunks/051966201_051966700.csv.gz` | 282,945 | 2,802 rows (no header) | gzip -t ok; 23 columns in every row | `b1b9eb168bcab3d2117b9269cb9c1d5347f2f94b5a65f9759f26d2cf2c5b28e0` | local-only (R2) |
| `collect/state/census/chunks/051966701_051967200.csv.gz` | 289,634 | 2,900 rows (no header) | gzip -t ok; 23 columns in every row | `67fcd3b9a11e30bc0b30b5aecbaf1f7639b70b239890c98b88b5e22ae5b5b2d8` | local-only (R2) |
| `collect/state/census/chunks/051967201_051967700.csv.gz` | 348,093 | 3,541 rows (no header) | gzip -t ok; 23 columns in every row | `d9a02902ee9a9745ccf3308eeadd45926d6bb5bb4c69b6a85bd79f2b36f2ab32` | local-only (R2) |
| `collect/state/census/chunks/051967701_051968200.csv.gz` | 389,763 | 4,080 rows (no header) | gzip -t ok; 23 columns in every row | `444acb2aa86a969509f6f3cdd2a3a60c2abef2a7fa4501d72c4019e06719e7a7` | local-only (R2) |
| `collect/state/census/chunks/051968201_051968700.csv.gz` | 375,630 | 3,837 rows (no header) | gzip -t ok; 23 columns in every row | `c806bc6284103ed1d1d55c54c945e1d0af0c92d6b69a87e12e60105d6c62c820` | local-only (R2) |
| `collect/state/census/chunks/051968701_051969200.csv.gz` | 395,780 | 4,083 rows (no header) | gzip -t ok; 23 columns in every row | `0cdc86c42073285cee483400b53a64f026137efd64257d6bd581eee3e2fb59cb` | local-only (R2) |
| `collect/state/census/chunks/051969201_051969700.csv.gz` | 376,751 | 3,785 rows (no header) | gzip -t ok; 23 columns in every row | `2665058b188a8f711652df3298a6eb707cae2e2529c00d5ee097fafcadd2a722` | local-only (R2) |
| `collect/state/census/chunks/051969701_051970200.csv.gz` | 320,531 | 3,278 rows (no header) | gzip -t ok; 23 columns in every row | `8047f390fb9c49ad597cce8c0407554001ff4af041ef8cd4c1ac1457cf37913f` | local-only (R2) |
| `collect/state/census/chunks/051970201_051970700.csv.gz` | 326,728 | 3,230 rows (no header) | gzip -t ok; 23 columns in every row | `a18a647a79a491dad41c538797434d9de936e6d5b0ed300a89075f38a3bf05e9` | local-only (R2) |
| `collect/state/census/chunks/051970701_051971200.csv.gz` | 347,412 | 3,481 rows (no header) | gzip -t ok; 23 columns in every row | `ee90f63485704490bd345e2c7441daea0ccde0c08b37bd0b2ec1a00dc46ea68b` | local-only (R2) |
| `collect/state/census/chunks/051971201_051971700.csv.gz` | 280,622 | 2,805 rows (no header) | gzip -t ok; 23 columns in every row | `d3fdddbd91210c98d150c2d856a2ad3f1faef3389e683b6427e9211df1b49d37` | local-only (R2) |
| `collect/state/census/chunks/051971701_051972200.csv.gz` | 301,023 | 3,003 rows (no header) | gzip -t ok; 23 columns in every row | `a4a22c6378942068bc2a4e069c73eaedad7062f0f41882f31cbd6f0ebd0583fa` | local-only (R2) |
| `collect/state/census/chunks/051972201_051972700.csv.gz` | 281,183 | 2,792 rows (no header) | gzip -t ok; 23 columns in every row | `b7d3f678223fbaa0fb51f627edbe45578bfde763bef50a9d83e94fec9170251a` | local-only (R2) |
| `collect/state/census/chunks/051972701_051973200.csv.gz` | 282,300 | 2,804 rows (no header) | gzip -t ok; 23 columns in every row | `4fecc68fb9d51714ab99d3dd93f283c94ff88d3d5265fc98fed7af562c60f5e8` | local-only (R2) |
| `collect/state/census/chunks/051973201_051973700.csv.gz` | 300,405 | 3,138 rows (no header) | gzip -t ok; 23 columns in every row | `d0778ddf5424efc0f141cdedd91b0df8fbc0f2e2cec24773e39f47916d728650` | local-only (R2) |
| `collect/state/census/chunks/051973701_051974200.csv.gz` | 297,570 | 3,021 rows (no header) | gzip -t ok; 23 columns in every row | `1e87a8b39f52558f990cc76f71a7c61554ae5946acef6fcce0930c9f5647064d` | local-only (R2) |
| `collect/state/census/chunks/051974201_051974700.csv.gz` | 294,129 | 2,925 rows (no header) | gzip -t ok; 23 columns in every row | `9847826a280fe7c82ad867009a3a6278ba6f8738e7a6f4324c0bd257058aae99` | local-only (R2) |
| `collect/state/census/chunks/051974701_051975200.csv.gz` | 292,534 | 2,986 rows (no header) | gzip -t ok; 23 columns in every row | `23a055a5068929e86b79752bf22f0049b094014a9ea2595adbf0785cc414c994` | local-only (R2) |
| `collect/state/census/chunks/051975201_051975700.csv.gz` | 271,832 | 2,747 rows (no header) | gzip -t ok; 23 columns in every row | `c97878756722ac8d40a74258b7f9906342f2ba5ec582e5d4db3ae0f101975276` | local-only (R2) |
| `collect/state/census/chunks/051975701_051976200.csv.gz` | 269,044 | 2,724 rows (no header) | gzip -t ok; 23 columns in every row | `77197a730a893ee210f0133147da32f0a6624082488a0af0c7e9a5c855b79370` | local-only (R2) |
| `collect/state/census/chunks/051976201_051976700.csv.gz` | 272,338 | 2,701 rows (no header) | gzip -t ok; 23 columns in every row | `018843b7846fa3c30a6c4b4a751838672a59b2e5ee3f236c0cbb58c0a870db61` | local-only (R2) |
| `collect/state/census/chunks/051976701_051977200.csv.gz` | 317,425 | 3,172 rows (no header) | gzip -t ok; 23 columns in every row | `79953d34c1c8f73d9a2c6602cd6ead1a757504059ba21a144fd7abf48b539c1d` | local-only (R2) |
| `collect/state/census/chunks/051977201_051977700.csv.gz` | 320,947 | 3,331 rows (no header) | gzip -t ok; 23 columns in every row | `db9bcdbe8027b41af707658742fc89c041780715ad5bd2df89fb2f8e1594e34b` | local-only (R2) |
| `collect/state/census/chunks/051977701_051978200.csv.gz` | 284,251 | 2,839 rows (no header) | gzip -t ok; 23 columns in every row | `4c30b7890e7066b02a93ff0c00dd89f5d59758e1a84313072554047641f89dfd` | local-only (R2) |
| `collect/state/census/chunks/051978201_051978700.csv.gz` | 310,250 | 3,088 rows (no header) | gzip -t ok; 23 columns in every row | `82ef5c38d73ccd5f4654a28aeb830800a7942bfe6afff3bcf0c91871b2552234` | local-only (R2) |
| `collect/state/census/chunks/051978701_051979200.csv.gz` | 287,803 | 2,870 rows (no header) | gzip -t ok; 23 columns in every row | `54c26fb1115ce2a25e62e670afebb7b87de228c2bde77f341de629eb4bf5aec1` | local-only (R2) |
| `collect/state/census/chunks/051979201_051979700.csv.gz` | 311,015 | 3,126 rows (no header) | gzip -t ok; 23 columns in every row | `7d3d016b862de906dc4a84e4e90ecca53a2e550cf8d58deec52baec0190d8be2` | local-only (R2) |
| `collect/state/census/chunks/051979701_051980200.csv.gz` | 378,031 | 3,760 rows (no header) | gzip -t ok; 23 columns in every row | `93840d740c614831b8b915e1ab378ce173a1049ac54c66382ef5a0274262bc06` | local-only (R2) |
| `collect/state/census/chunks/051980201_051980700.csv.gz` | 299,963 | 3,037 rows (no header) | gzip -t ok; 23 columns in every row | `7fd3af697f1fdf9bd19867cb6a2014b0f310fa69689f1fd009d9626fb889d17a` | local-only (R2) |
| `collect/state/census/chunks/051980701_051981200.csv.gz` | 360,468 | 3,596 rows (no header) | gzip -t ok; 23 columns in every row | `1474dfb00bb3da853b61700441ac3b023c949ca231648c7756c879f274283fb6` | local-only (R2) |
| `collect/state/census/chunks/051981201_051981700.csv.gz` | 341,858 | 3,549 rows (no header) | gzip -t ok; 23 columns in every row | `717b704fe49852f59bc12170f6fa81b5e5e290343023364cd77435230f343107` | local-only (R2) |
| `collect/state/census/chunks/051981701_051982200.csv.gz` | 401,886 | 4,246 rows (no header) | gzip -t ok; 23 columns in every row | `101008b7f50242a3df84118bd38d9e65ceff40f98df355438e29bf79a2a4f279` | local-only (R2) |
| `collect/state/census/chunks/051982201_051982700.csv.gz` | 337,956 | 3,469 rows (no header) | gzip -t ok; 23 columns in every row | `06cbf61ce9e92000a518b94d2c752ca5b4c07775502b14b32987f4602a01de63` | local-only (R2) |
| `collect/state/census/chunks/051982701_051983200.csv.gz` | 326,651 | 3,414 rows (no header) | gzip -t ok; 23 columns in every row | `26b8dbbc015ec9e5d267ef11fda7ade794672ad4eb831d6e72cc013d47926000` | local-only (R2) |
| `collect/state/census/chunks/051983201_051983700.csv.gz` | 330,689 | 3,484 rows (no header) | gzip -t ok; 23 columns in every row | `e25a99fc2219dadf76a49b12f42a164bf4a8f6019dd8e7f8758a0b9c6f50005e` | local-only (R2) |
| `collect/state/census/chunks/051983701_051984200.csv.gz` | 303,336 | 3,145 rows (no header) | gzip -t ok; 23 columns in every row | `df7bb28b69c5b736774b1a9979ff20932447664745473c7712c4dbbafa7d5dc1` | local-only (R2) |
| `collect/state/census/chunks/051984201_051984700.csv.gz` | 320,592 | 3,278 rows (no header) | gzip -t ok; 23 columns in every row | `ed914354a6082f8e1800d8c67cc84487020c5cf62fc42a56f70feb423b8041f3` | local-only (R2) |
| `collect/state/census/chunks/051984701_051985200.csv.gz` | 312,187 | 3,215 rows (no header) | gzip -t ok; 23 columns in every row | `20830b79620b67120e1b959da755fadcec96dc8090944d01657cec8b47c6d8df` | local-only (R2) |
| `collect/state/census/chunks/051985201_051985700.csv.gz` | 403,735 | 4,641 rows (no header) | gzip -t ok; 23 columns in every row | `44933bec4fe4e66026ba80be418e2b2e3da544df1f106b4ec43840f7528cabfd` | local-only (R2) |
| `collect/state/census/chunks/051985701_051986200.csv.gz` | 339,733 | 3,434 rows (no header) | gzip -t ok; 23 columns in every row | `18ec614cf1d3487bc0f3206b17f90a050c603392af016bb75ce63ea691977f07` | local-only (R2) |
| `collect/state/census/chunks/051986201_051986700.csv.gz` | 334,629 | 3,442 rows (no header) | gzip -t ok; 23 columns in every row | `bdb1d5934675c138cd9025a44c889ba5b15891cde915a2f70867608275fd7774` | local-only (R2) |
| `collect/state/census/chunks/051986701_051987200.csv.gz` | 354,318 | 3,606 rows (no header) | gzip -t ok; 23 columns in every row | `46539d0e29394b3ad80682210f869ce27256ed24ea776cb21ecec3514e58046e` | local-only (R2) |
| `collect/state/census/chunks/051987201_051987700.csv.gz` | 328,304 | 3,317 rows (no header) | gzip -t ok; 23 columns in every row | `760b098a4c08649f3621fb7de342739d1ba21c8533e4635a7b17d8e0f352bff5` | local-only (R2) |
| `collect/state/census/chunks/051987701_051988200.csv.gz` | 315,761 | 3,192 rows (no header) | gzip -t ok; 23 columns in every row | `2ffa2e75e87d1f0971af331090ca191dc775f230fa7939a814f9eb290bd27c7e` | local-only (R2) |
| `collect/state/census/chunks/051988201_051988700.csv.gz` | 351,564 | 3,645 rows (no header) | gzip -t ok; 23 columns in every row | `617d1d256b34c755252ddc27a9aa808fb9fc6828ff4c818cea101bbb968e0e43` | local-only (R2) |
| `collect/state/census/chunks/051988701_051989200.csv.gz` | 408,894 | 4,420 rows (no header) | gzip -t ok; 23 columns in every row | `7e77f4deccdd288b5962bc9e73c95dbf1ca1c3f6878be8b6c986f3e448733b43` | local-only (R2) |
| `collect/state/census/chunks/051989201_051989700.csv.gz` | 329,769 | 3,319 rows (no header) | gzip -t ok; 23 columns in every row | `9d94d87fa9fabcbfc6d74e1433bf5ccf554bb3001ab29425a9138b28bfa3d7fa` | local-only (R2) |
| `collect/state/census/chunks/051989701_051990200.csv.gz` | 320,770 | 3,259 rows (no header) | gzip -t ok; 23 columns in every row | `bbed8aa35a9edf502d647a465534e4961b9d17f37ccc27291051be7e40fd36c2` | local-only (R2) |
| `collect/state/census/chunks/051990201_051990700.csv.gz` | 326,156 | 3,388 rows (no header) | gzip -t ok; 23 columns in every row | `f6a8e7d9d3efdc439322dc51b801f61d4fd869acb06af0cc455bbc6c6ca0770d` | local-only (R2) |
| `collect/state/census/chunks/051990701_051991200.csv.gz` | 593,947 | 6,306 rows (no header) | gzip -t ok; 23 columns in every row | `cff06bac8e8846d7d4c962032d607d591147368ee92b70d5fc3e9bb4ab035234` | local-only (R2) |
| `collect/state/census/chunks/051991201_051991700.csv.gz` | 441,533 | 4,600 rows (no header) | gzip -t ok; 23 columns in every row | `c92c41f770050ad1ee03f23826e9693cecc4c18526ed44a3177b39bc5b099c80` | local-only (R2) |
| `collect/state/census/chunks/051991701_051992200.csv.gz` | 410,850 | 4,363 rows (no header) | gzip -t ok; 23 columns in every row | `2b95b45375254a80d745296d5105b8286776364375701f060beda09734654e3f` | local-only (R2) |
| `collect/state/census/chunks/051992201_051992700.csv.gz` | 258,495 | 2,728 rows (no header) | gzip -t ok; 23 columns in every row | `db1b7957d34a3ae9b4b7a9ff40e7ee3032f8272187ef1c9bcb90c69b7176dbbf` | local-only (R2) |
| `collect/state/census/chunks/051992701_051993200.csv.gz` | 353,562 | 3,710 rows (no header) | gzip -t ok; 23 columns in every row | `9b9763deaf9a80a5f031313c72d78b86d464327c875b6d67a33815f18c0fb00a` | local-only (R2) |
| `collect/state/census/chunks/051993201_051993700.csv.gz` | 457,415 | 4,913 rows (no header) | gzip -t ok; 23 columns in every row | `83caff5bc8367f781b208e7c9e47849c6fdaae1d182f5557605819f916388a22` | local-only (R2) |
| `collect/state/census/chunks/051993701_051994200.csv.gz` | 459,236 | 4,840 rows (no header) | gzip -t ok; 23 columns in every row | `d5b9fe817cc1017016c8f9ab1d5b9b17c83deef37556d01d055ed0c887601916` | local-only (R2) |
| `collect/state/census/chunks/051994201_051994700.csv.gz` | 565,715 | 5,855 rows (no header) | gzip -t ok; 23 columns in every row | `cc67af8989352d3946c304a0ffa55451ccdfa76a7812299095edb43132e3a1d3` | local-only (R2) |
| `collect/state/census/chunks/051994701_051995200.csv.gz` | 530,407 | 5,513 rows (no header) | gzip -t ok; 23 columns in every row | `a180c74dc37fca772f9e144fc52ed960ab3146f963e190b65b2be2f8cf9ed689` | local-only (R2) |
| `collect/state/census/chunks/051995201_051995700.csv.gz` | 408,052 | 4,320 rows (no header) | gzip -t ok; 23 columns in every row | `ad1ba50bb4e230ff9f7bd428581d96ef658036e6a2dcfecac6788ce08d0005b9` | local-only (R2) |
| `collect/state/census/chunks/051995701_051996200.csv.gz` | 380,887 | 3,918 rows (no header) | gzip -t ok; 23 columns in every row | `07d88898e33fa98d9bd3ca9420060950fb7dc35c012992eca5bf89cdbc981811` | local-only (R2) |
| `collect/state/census/chunks/051996201_051996700.csv.gz` | 407,488 | 4,188 rows (no header) | gzip -t ok; 23 columns in every row | `efea96de2ec69558b96094de82837f0e77d7439ed0626618e049700cce73e28d` | local-only (R2) |
| `collect/state/census/chunks/051996701_051997200.csv.gz` | 377,954 | 3,910 rows (no header) | gzip -t ok; 23 columns in every row | `4fa164d5dce2af579c69be0b757cdb6e6b0510667a6064319c6e4b04bfb8c376` | local-only (R2) |
| `collect/state/census/chunks/051997201_051997700.csv.gz` | 473,153 | 4,921 rows (no header) | gzip -t ok; 23 columns in every row | `e692da160187874b5b67e5859f2cb64865291c385574260a94f0f6d19805da95` | local-only (R2) |
| `collect/state/census/chunks/051997701_051998200.csv.gz` | 376,908 | 3,763 rows (no header) | gzip -t ok; 23 columns in every row | `5f308687a6892b5d175ab62f100033bd0f491fd63520784f418cc657dfd526ca` | local-only (R2) |
| `collect/state/census/chunks/051998201_051998700.csv.gz` | 336,281 | 3,421 rows (no header) | gzip -t ok; 23 columns in every row | `4a8852a8426a41d4b0deadd5cd29129c575fe3873e68158551ca47c801810c8c` | local-only (R2) |
| `collect/state/census/chunks/051998701_051999200.csv.gz` | 368,490 | 3,795 rows (no header) | gzip -t ok; 23 columns in every row | `6931e7a2fb1b05b75e1cfe6dea8d03a553a98464a2adb9320e59d81a10908824` | local-only (R2) |
| `collect/state/census/chunks/051999201_051999700.csv.gz` | 390,936 | 4,071 rows (no header) | gzip -t ok; 23 columns in every row | `da5e92998fef66f2a679f46f9082a545c4a41b1e48123964b29151959eef87a8` | local-only (R2) |
| `collect/state/census/chunks/051999701_052000200.csv.gz` | 327,336 | 3,395 rows (no header) | gzip -t ok; 23 columns in every row | `5036640f1bdd562541b658736386eb54df5b7bdfef98da62da1416bc1f07dae1` | local-only (R2) |
| `collect/state/census/chunks/052000201_052000700.csv.gz` | 334,810 | 3,404 rows (no header) | gzip -t ok; 23 columns in every row | `255e063e975b792b08b9f2d2f0463c3d98c7943a701f0f7ae6253112dec56fa6` | local-only (R2) |
| `collect/state/census/chunks/052000701_052001200.csv.gz` | 349,651 | 3,606 rows (no header) | gzip -t ok; 23 columns in every row | `4affc50ecb1b7b2192f21a11f6a35eb05a00f6f61a34b1f2ef79487f13814fcd` | local-only (R2) |
| `collect/state/census/chunks/052001201_052001700.csv.gz` | 289,283 | 2,944 rows (no header) | gzip -t ok; 23 columns in every row | `ea0a723cfde9b0dc334b2faad5d83caa7c526d74a70b42870c5285fb221f9c07` | local-only (R2) |
| `collect/state/census/chunks/052001701_052002200.csv.gz` | 387,266 | 4,083 rows (no header) | gzip -t ok; 23 columns in every row | `d98f59b01889520bacf9e75d670efddd8274a1b7efa135c464555a1807cd6009` | local-only (R2) |
| `collect/state/census/chunks/052002201_052002700.csv.gz` | 332,197 | 3,446 rows (no header) | gzip -t ok; 23 columns in every row | `793ce96db840e2869793f3db08eaf34be32aefaee36d419015c1272c4337a069` | local-only (R2) |
| `collect/state/census/chunks/052002701_052003200.csv.gz` | 333,497 | 3,479 rows (no header) | gzip -t ok; 23 columns in every row | `a05dee4e4ea134f29abab13bcadb9f4b0005fe3de4e12be902a1d701f58dbc73` | local-only (R2) |
| `collect/state/census/chunks/052003201_052003700.csv.gz` | 306,849 | 3,105 rows (no header) | gzip -t ok; 23 columns in every row | `bf9bf1aa3f06b27592f1b5a3c21625a6f74b282fa1abbc3c20ad6bf3f5b2aabf` | local-only (R2) |
| `collect/state/census/chunks/052003701_052004200.csv.gz` | 282,167 | 2,844 rows (no header) | gzip -t ok; 23 columns in every row | `2b2baf749a2e002783dd03fe400574eab366f412dbee969a9b1b7bded742455c` | local-only (R2) |
| `collect/state/census/chunks/052004201_052004700.csv.gz` | 345,678 | 3,563 rows (no header) | gzip -t ok; 23 columns in every row | `2171824039ca7f1707ddf6081e09545d210e975fe55cae168bc3096100897217` | local-only (R2) |
| `collect/state/census/chunks/052004701_052005200.csv.gz` | 312,170 | 3,174 rows (no header) | gzip -t ok; 23 columns in every row | `805818ffad2e1829ae63be86be4e61d2d82457a38885647c3ee228acfa7b5228` | local-only (R2) |
| `collect/state/census/chunks/052005201_052005700.csv.gz` | 330,009 | 3,328 rows (no header) | gzip -t ok; 23 columns in every row | `cc0f752281bc9c85630ed7d9d059c8b4a08a04c92f983236770b34e8193e3aaf` | local-only (R2) |
| `collect/state/census/chunks/052005701_052006200.csv.gz` | 290,320 | 2,916 rows (no header) | gzip -t ok; 23 columns in every row | `95430bedc85465f13b8196c6948fb6e72d6a7f957cb756a6f8528ff0fcbb43ed` | local-only (R2) |
| `collect/state/census/chunks/052006201_052006700.csv.gz` | 296,091 | 2,995 rows (no header) | gzip -t ok; 23 columns in every row | `36dd989ccbe41e406c6ea90b34d78d2fc508c06385bd5f26b68257e3489b5bd7` | local-only (R2) |
| `collect/state/census/chunks/052006701_052007200.csv.gz` | 273,301 | 2,711 rows (no header) | gzip -t ok; 23 columns in every row | `332608b31957eb2461d7ad65fff6f7978116bcd8d2fe9369a8b95b8d68eeb87d` | local-only (R2) |
| `collect/state/census/chunks/052007201_052007700.csv.gz` | 279,881 | 2,835 rows (no header) | gzip -t ok; 23 columns in every row | `7eb0de7d60e5546277da183ea0c7ae3e902202ec6ac29d6e530ef92f0bf7b153` | local-only (R2) |
| `collect/state/census/chunks/052007701_052008200.csv.gz` | 300,433 | 3,132 rows (no header) | gzip -t ok; 23 columns in every row | `382a379382d811935948eb821db674bab08f5e9233273f73e1074e71cc478648` | local-only (R2) |
| `collect/state/census/chunks/052008201_052008400.csv.gz` | 145,233 | 1,502 rows (no header) | gzip -t ok; 23 columns in every row | `3834cd26274669e7473c6098c6f4fd6c33163a33dd95aa7de5e6dad54b2567d7` | local-only (R2) |
| `collect/state/census/emitters.jsonl.gz` | 272,263 | 44 lines (one batch each) | gzip -t ok; every line parses as JSON | `7803754f8bfc4ee8dee2e66ba0b32b7307e1c682e924e7d416977f8b6f5c2624` | local-only (R1) |
| `collect/state/lenhist.jsonl.gz` | 2,394 | 105 lines (one batch each) | gzip -t ok; every line parses as JSON | `6805011b2d4234a7e62ccf89fd5e210e8dc861a3cd7eedc483d86979559b6046` | local-only (R1) |
| `collect/state/pairs.jsonl.gz` | 3,198,554 | 126 lines (one batch each) | gzip -t ok; every line parses as JSON | `897c4c0ea9a3750d6b00b6d46a381902064af717bb0f84c339b43d8bca2bd4e8` | local-only (R1) |
| `collect/state/poolfields.jsonl.gz` | 5,791,611 | 1,252 lines (one batch each) | gzip -t ok; every line parses as JSON | `b87c200eaf5755d20c8e5b83bb9e8d5680dc3ee3484a12c651ca2dc7f85fe7a2` | local-only (R1) |
| `collect/state/tokens/lookups.jsonl.gz` | 293,306 | 572 lines (one batch each) | gzip -t ok; every line parses as JSON | `5b0f49060a95ad1e29c50f5aaf9975b082d658ab714cd0c5b3814a20c92b9496` | local-only (R1) |
| `collect/state/tokens/meta.jsonl.gz` | 3,216,242 | 1,120 lines (one batch each) | gzip -t ok; every line parses as JSON | `80d75483e16a4de1fc59d04289388fcb6eb3164562c6109d7fee72453111ea3f` | local-only (R1) |
| `collect/state/tokens/routestate.jsonl.gz` | 316,832 | 96 lines (one batch each) | gzip -t ok; every line parses as JSON | `0dbab543cd3eeab166a9a897c25dd7388273eff248e4620bea528e030ea123e5` | local-only (R1) |

### Regenerating the local-only files

- **R2** (`collect/state/census/chunks/*.csv.gz`, `collect/state/census/chunks.jsonl.gz`): rebuild from committed files, no RPC
  needed. Tested on 2026-10-01 in a scratch copy: all 87 chunk files decompress to exactly the original bytes, and `chunks.jsonl`
  has the same 87 lines, in block order (the original lists them in the order the chunks finished). The `.gz` bytes (and so the
  sha256 above) can differ because of the gzip header.

  ```bash
  cd /home/user/dapparb/research-material/03-v2-older-pairs
  python3 - <<'PY'
  import csv, gzip, json, os
  os.makedirs('collect/state/census/chunks', exist_ok=True)
  chunks = [(int(r['chunk_start']), int(r['chunk_end'])) for r in csv.DictReader(open('census-chunks.csv'))]
  src = gzip.open('census-logs-part-0001.csv.gz', 'rb'); src.readline()        # drop the header
  line = src.readline()
  for a, b in chunks:
      with gzip.open('collect/state/census/chunks/%09d_%09d.csv.gz' % (a, b), 'wb') as out:
          while line and int(line.split(b',', 1)[0]) <= b:
              out.write(line); line = src.readline()
  with open('collect/state/census/chunks.jsonl', 'w') as f:
      for r in csv.DictReader(open('census-chunks.csv')):
          f.write(json.dumps({'a': int(r['chunk_start']), 'b': int(r['chunk_end']), 'n': int(r['log_rows']),
                              'endpoints': json.loads(r['endpoints_used']), 'secs': float(r['fetch_secs']),
                              'utc': r['fetched_utc']}) + '\n')
  PY
  gzip collect/state/census/chunks.jsonl
  ```

- **R1** (`collect/state/{aerofee,lenhist,pairs,poolfields}.jsonl.gz`, `collect/state/census/emitters.jsonl.gz`,
  `collect/state/tokens/{meta,lookups,routestate}.jsonl.gz`): the undecoded Multicall3 batch results (format in section 4).
  They cannot be rebuilt from the committed files; they are re-fetched by the committed collectors, which needs an archive
  `eth_call` endpoint for block 52008400 (and, for `census.py`, an endpoint that accepts address-less `eth_getLogs`). Write to a
  scratch directory so the committed outputs, the manifest and the shared sentinels are not touched:

  ```bash
  cd /home/user/dapparb/research-material/03-v2-older-pairs/collect
  X=/path/to/scratch
  python3 snapshot.py --pin 52008400 --out $X/out --state $X/state --sentinel none --smoke 0   # --smoke 0 = full run; it only stops a crash from writing .sentinels/V2OLD_SNAPSHOT.FAILED
  python3 census.py --pin 52008400 --out $X/out --state $X/state/census --sentinel none
  python3 tokens.py --out $X/out --state $X/state/tokens --sentinel none --no-wait --no-finalize
  gzip $X/state/*.jsonl $X/state/census/*.jsonl $X/state/tokens/*.jsonl
  # then copy $X/state/ to collect/state/ if the checkpoints are wanted here
  ```

  The scripts write the checkpoints as plain `.jsonl`; the `.gz` copies listed above were made with `gzip` after the 2026-09-30
  run. A re-fetch reproduces the original bytes only if the RPC returns the same data for the pinned block. `tokens.py` reads
  `snapshot-meta.json`, `pools-part-*.csv.gz` and `emitters.csv.gz` from `--out`, so the snapshot and census steps must run first
  with the same `--out`. (`census.py --state $X/state/census` also re-creates the R2 files.)

## Collectors and sentinels

| Collector | Script | Log | Sentinel (in `/home/user/dapparb/research-material/.sentinels/`) |
|---|---|---|---|
| Factory counts + pool snapshot | `collect/snapshot.py` | `collect/snapshot.log` | `V2OLD_SNAPSHOT.DONE` / `.FAILED` |
| 24 h V2-style event census | `collect/census.py` | `collect/census.log` | `V2OLD_CENSUS.DONE` / `.FAILED` |
| Token metadata + WETH-route reference | `collect/tokens.py` (waits for the two above, then runs `finalize.py`) | `collect/tokens.log` | `V2OLD_TOKENS.DONE` / `.FAILED` |
| Overall | `collect/finalize.py` | (stdout in `collect/tokens.log`) | `V2OLD.DONE` / `.FAILED` (DONE only if all three components are DONE, every file reads back and none is over 90 MB) |
| Declared getReserves ABI (one-off) | `collect/abi_shapes.py` | `collect/abi_shapes.log` | none (small, finished) |

Shared code: `collect/rpclib.py` (JSON-RPC client with a per-endpoint in-flight cap, retries, a hand-written Multicall3
`aggregate3` encoder and decoder, lossless return-data decoders, and a resumable batch store).

## 1. Question lines served

Mapping only. Numbers are the question lines 1–8 as given on 2026-10-01. (Corrected 2026-10-01: the earlier version of this
section numbered the question text Q1–Q10, counting two headings; old Q2→1, Q3→2, Q4→3, Q5→4, Q7→5, Q8→6, Q9→7, Q10→8.)

| Line | Question line (first words) | Files in this directory |
|---|---|---|
| 1 | "Uniswap V4 on Base. This is the biggest gap. …" | none |
| 2 | "Older V2 pairs. I took the newest 6,000 of about 3 million Uniswap V2 pairs. …" | `factories.csv`, `factory-length-history.csv`, `uniswapv2-sample-indices.csv.gz`, `pools-part-0001.csv.gz`, `tokens.csv.gz`, `price-reference-weth-pools.csv.gz`, `census-logs-part-0001.csv.gz`, `activity-pool-hour.csv.gz`, `emitters.csv.gz`, `buckets.csv` |
| 3 | "Pools under 0.1 ETH of liquidity. …" | `pools-part-0001.csv.gz`, `tokens.csv.gz`, `price-reference-weth-pools.csv.gz`, `census-logs-part-0001.csv.gz`, `activity-pool-hour.csv.gz`, `emitters.csv.gz`, `buckets.csv` |
| 4 | "Other chains, live. …" | none |
| 5 | "V4 launches are the one place a bigger number could appear. …" | none |
| 6 | "BSC has the same ordering problem. …" | none |
| 7 | "Chain-wide studies already count every pool. …" | `census-logs-part-0001.csv.gz`, `activity-pool-hour.csv.gz`, `emitters.csv.gz`, `buckets.csv` |
| 8 | "So the search went far beyond selected pairs, but it did not cover everything. …" | `factories.csv`, `pools-part-0001.csv.gz`, `census-logs-part-0001.csv.gz` |

Method, verification and coverage metadata for the files of lines 2, 3, 7 and 8: `snapshot-meta.json`, `census-meta.json`,
`tokens-meta.json`, `topics.csv`, `census-chunks.csv`, `census-crosscheck.csv`, `getreserves-abi.csv`, `file-index.csv`,
`collect/*.py`, `collect/*.log`.

## 2. Sources and endpoints

All data is from Base mainnet (chain id 8453) through public JSON-RPC, requested with a browser-like User-Agent.

| Use | Endpoint | Notes |
|---|---|---|
| `eth_call` at the pinned block (Multicall3 `aggregate3`) and archive `eth_call` at older blocks | `https://base-mainnet.public.blastapi.io` (primary, ≤ 2 in flight per collector) | Every snapshot and token call in this run was served here. The `endpoint_stats` in `*-meta.json` record 0 requests to `base.drpc.org`, the fallback. |
| same, fallback | `https://base.drpc.org` (1 in flight) | |
| `eth_getLogs`, topic-only filter (no address) | `https://gateway.tenderly.co/public/base` (≤ 1,000 blocks per request; 500 used; 2 in flight) | This endpoint served all 87 chunks (`census-chunks.csv`). |
| same, fallback and cross-check | `https://mainnet.base.org` (≤ 2,000 blocks; 1 in flight, ≥ 1 s spacing) | Used for the 3-chunk cross-check. |
| same, last-resort fallback | `https://base.drpc.org` (only 10 blocks for address-less filters, probed 22:10Z) | Not used |
| not used for logs | `https://base-rpc.publicnode.com` | Rejects address-less `eth_getLogs` with "Please specify an address in your request", probed 22:10Z |
| Block headers for bucket bounds | tenderly, then mainnet.base.org, then drpc | |
| Verified ABIs | `https://base.blockscout.com/api/v2/smart-contracts/<addr>` and `/api/v2/addresses/<addr>` | `getreserves-abi.csv` only |
| Section 2.6 enumeration counts | `research-material/00-prior-runs/engine-runs/dry-all.log.gz` (§2.6 run) and `dry-all-v0.log.gz` (v0 run), lines `factory enumerated` | Copied into `factories.csv` (`s26_*`, `v0_*` columns) |

Contracts: factories exactly as in `bot/src/config/chains.ts` (BASE):
Aerodrome V2 PoolFactory `0x420dd381b31aef6683db6b902084cb0ffece40da`, UniswapV2 `0x8909dc15e40173ff4699343b6eb8132c65e18ec6`,
SushiV2 `0x71524b4f93c58fcbf659783284e38825f0622859`, PancakeV2 `0x02a84c1b3bbd7401a5f7fa98a384ebc70bb5749e`,
BaseSwap `0xfda619b6d20975be80a10332cd39b9a4b0faa8bb`. The Slipstream factories AerodromeCL `0x5e7bb104…809a`, CL3 `0xf8f2eb49…61ef`
and CL2 `0xade65c38…716a` are listed in `factories.csv` for reference only. The V3-style factories are used only for the WETH-route lookups.
Multicall3 `0xca11bde05977b3631167028862be2a173976ca11`, WETH `0x4200000000000000000000000000000000000006`.

## 3. Time window, blocks, pinned snapshot

| Item | Value |
|---|---|
| Pinned snapshot block (all `eth_call` data: factories, pools, emitters, tokens, WETH-route) | **52008400**, hash `0x116f70d59e1c4a45476bc1e787fedab83c0e83f8896e9006610f979f3ef206d5`, timestamp 1790806147 = 2026-09-30T22:09:07Z |
| Census window (`eth_getLogs`) | blocks **51965201 – 52008400** inclusive (43,200 blocks), 2026-09-29T22:09:09Z – 2026-09-30T22:09:07Z |
| Hour buckets | 24 buckets of 1,800 blocks: bucket k = blocks [51965201 + 1800k, 51965201 + 1800k + 1799] (`buckets.csv` has header hashes and timestamps) |
| Base block time | block n has timestamp 1686789347 + 2n. Every census log's `blockTimestamp` agrees with this (`census-meta.json` `log_timestamp_formula_mismatches` = 0). `factories.csv` uses it to turn the §2.6 log times into blocks. |
| Section 2.6 enumeration | log times 16:55:48–16:55:56Z → blocks 51999000–51999004. The v0 run's times 16:37:12–16:37:20Z → blocks 51998442–51998446 |
| Collection run | snapshot 22:15–22:17Z, census 22:17–22:18Z, tokens 22:21–22:24Z (UTC, 2026-09-30) |

## 4. Reproduce

```bash
cd /home/user/dapparb/research-material/03-v2-older-pairs/collect
# snapshot (resumable: state/*.jsonl hold finished batches; rerun the same command to resume)
setsid nohup python3 -u snapshot.py --pin 52008400 > snapshot.log 2>&1 < /dev/null &
# census (resumable: state/census/chunks/<a>_<b>.csv.gz per finished 500-block chunk)
setsid nohup python3 -u census.py --pin 52008400 > census.log 2>&1 < /dev/null &
# tokens + WETH-route (waits for both sentinels, then runs finalize.py)
setsid nohup python3 -u tokens.py > tokens.log 2>&1 < /dev/null &
# one-off: declared getReserves ABI per DEX
python3 abi_shapes.py > abi_shapes.log 2>&1
# only re-fill counts/sha256 in this manifest and the V2OLD sentinel
python3 finalize.py
```

Checkpoints: `collect/state/*.jsonl.gz`, `collect/state/tokens/*.jsonl.gz` and `collect/state/census/*.jsonl.gz` were gzipped after
all collectors finished. Each line is one finished batch `{"b": batch_id, "rows": [[status, returnData_hex, rpc_error], ...]}`,
and the calls are in the order the scripts build them. These are the undecoded Multicall3 results behind every decoded column.
(`collect/state/census/chunks.jsonl.gz` is different: one line per finished census chunk, `{"a", "b", "n", "endpoints", "secs", "utc"}`.)
`collect/state/census/chunks/<a>_<b>.csv.gz` are the per-chunk raw log rows (no header, columns as `census-logs-part-*`). To resume
or re-derive from them, gunzip the `.jsonl.gz` files in place first. Without them, the scripts fetch the same pinned block again.
Note (added 2026-10-01): everything under `collect/state/` is git-ignored and local-only; it will not be in the repository.
How to rebuild it is in "Verified inventory (2026-10-01)" → "Regenerating the local-only files". The commands above write
into this directory and the shared `.sentinels/` (they overwrite the committed outputs).

Smoke tests used before the full runs (they write only to scratch, not here):
`snapshot.py --pin 52008400 --smoke 30 --out <scratch> --state <scratch>/state --sentinel none` (300 pools),
`census.py --pin 52008400 --window 3700 --out <scratch> --state <scratch>/state --sentinel none` (8 chunks, cross-check identical),
`tokens.py --out <scratch> --state <scratch>/state --limit 400 --sentinel none --no-wait --no-finalize`.
Requirements: python3 with `requests` and `eth_hash`/pycryptodome (only for the keccak cross-check in `topics.csv`), and
`/root/.foundry/bin/cast` for the second keccak computation. A different pinned block needs an archive `eth_call` endpoint.
`eth_getLogs` needs an endpoint that accepts address-less filters.
To rebuild the Uniswap V2 sample without Python's `random`, use `uniswapv2-sample-indices.csv.gz`.

## 5. Methods

### 5.1 snapshot.py

1. **Factory counts**: `allPoolsLength()` (Aerodrome, Slipstream) or `allPairsLength()` (V2 forks), read with `eth_call` at the
   pinned block. They are also read at the block matching each factory's `factory enumerated` log line of the §2.6 run and of
   the v0 run, and on a grid of every 500,000 blocks from 500,000 to the pinned block (`factory-length-history.csv`).
2. **Index selection** (column `sample_group`):
   - Aerodrome V2, PancakeV2, BaseSwap, SushiV2: `all_indices`, meaning every index in [0, N at the pinned block). This covers
     the indices §2.6 did not enumerate (below its range, and above it for pools created since), and also the §2.6 range itself.
     The derived column `index_vs_s26_range` tells them apart.
   - UniswapV2: `random_sample_older` is 60,000 indices drawn uniformly without replacement from [0, 3,057,605), where
     3,057,605 = 3,063,605 − 6,000 and 3,063,605 is the total the §2.6 run logged. The draw is Python 3.11
     `random.Random(20260930).sample(range(3057605), 60000)`, then sorted. `newest_6000_at_snapshot` is [3,057,708, 3,063,708)
     at the pinned block. It overlaps the §2.6 range [3,057,605, 3,063,605) and also holds the 103 pairs created after §2.6.
3. **Pair addresses**: `allPools(i)` / `allPairs(i)` at the pinned block, 1,000 calls per `aggregate3`.
4. **Pool fields** (100 pools per `aggregate3`): `token0()`, `token1()`, `getReserves()`, `totalSupply()` of the pool's LP
   token, and `stable()` for Aerodrome.
5. **Aerodrome fee**: PoolFactory `getFee(pool, stable)`, called with the pool's own `stable()` result.
6. Every call uses `aggregate3` with `allowFailure = true`. If a whole `aggregate3` reverts, runs out of gas or times out,
   the batch is split in half recursively down to single calls, so every sub-call ends with its own status. HTTP 429, 5xx and
   network errors are retried with exponential backoff and jitter, alternating blastapi and drpc. A batch that still fails goes to `gaps.csv`.

### 5.2 census.py

- Topic-only `eth_getLogs` (no address) with `topics: [[t1, t2, t3, t4]]` in 500-block chunks over the window. The four topic0 values:

  | event label | signature | topic0 |
  |---|---|---|
  | `sync_uint112` | `Sync(uint112,uint112)` (Uniswap V2 style) | `0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1` |
  | `sync_uint256` | `Sync(uint256,uint256)` (Aerodrome/Solidly style) | `0xcf2aa50876cdfbb541206f89af0ee78d44a2abf8d328e37fa4917f982149848a` |
  | `swap_univ2` | `Swap(address,uint256,uint256,uint256,uint256,address)` | `0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822` |
  | `swap_aero_v2` | `Swap(address,address,uint256,uint256,uint256,uint256)` | `0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b` |

  Each topic was computed twice, with `cast keccak "<signature>"` and with Python `eth_hash`. Both are in `topics.csv`, which
  also records a real example log per topic from a pool of the expected factory. For the Sync topics, the example's decoded
  (reserve0, reserve1) was compared with `getReserves()` at the end of that block. For the Swap topics, the check is the topic
  count and data length (`check_result`).
- Validation of every response: each log's block is inside the requested range, its topic0 is one of the four, `removed` is
  false, and no (block, logIndex) repeats. A range error, a size error or a response of 10,000 or more logs (a possible silent
  cap) makes the chunk split in half recursively. Transient errors are retried with backoff and rotated across
  tenderly and mainnet.base.org; drpc is used only for ranges of 10 blocks or fewer.
- Cross-check: the first, middle and last chunks were fetched again from `mainnet.base.org` and compared as sets of
  (block, tx hash, log index, address, topic0, data) (`census-crosscheck.csv`).
- Emitters: every distinct emitting address gets `factory()`, `token0()`, `token1()` and `getReserves()` at the pinned block,
  plus `stable()` for addresses that emitted a Solidly-style topic. All through `aggregate3` with allowFailure.

### 5.3 tokens.py

- Token set: every `token0`/`token1` with status ok in `pools-part-*.csv.gz` and `emitters.csv.gz`, plus WETH and the four
  stablecoins below. Calls: `symbol()`, `name()`, `decimals()`, `totalSupply()` at the pinned block.
- WETH-route set: every token of a pool (snapshot or emitter) whose two sides include neither WETH nor one of
  USDC `0x833589fc…2913`, USDbC `0xd9aaec86…b6ca`, DAI `0x50c57259…b0cb` or USDT `0xfde4c96c…bb2`, plus those four
  stablecoins. For each token, a lookup against WETH on every DEX factory in `bot/src/config/chains.ts`, 36 lookups per token:
  UniswapV2/SushiV2/PancakeV2/BaseSwap `getPair`; Aerodrome `getPool(t, WETH, false|true)`; UniswapV3/SushiV3
  `getPool(t, WETH, 100|500|3000|10000)`; PancakeV3 `getPool(t, WETH, 100|500|2500|10000)`; AerodromeCL/CL2/CL3
  `getPool(t, WETH, 1|10|50|100|200|2000)`. For each non-zero result: V2-style `token0()`, `getReserves()`; V3-style
  `token0()`, `slot0()`, `liquidity()`, `WETH.balanceOf(pool)`, `token.balanceOf(pool)`. Uniswap V4 pools are not looked up.
- Reference for method comparison only (not used by the collectors): the engine's depth filter is `poolDepthEth` in
  `bot/src/arb/depth.ts`, which takes the smaller of the two sides' ETH values using the anchored price map from
  `bot/src/arb/pricing.ts`. The §2.6 run used `--min-depth-eth 0.1`.

## 6. File schemas

General: gzip CSV with a header row, UTF-8, RFC 4180 quoting (the csv module). Addresses and hashes are lowercase 0x-hex.
Integers are base-10 strings. `*_status` values from the Multicall3 decoders:
`ok` (success, decoded); `ok_extra_bytes` (success, more bytes returned than decoded; decoded prefix given);
`empty` (success with 0 bytes returned, e.g. no code at the target); `revert` (the sub-call reverted; revert data is in `failures`);
`baddata` (success but not decodable as the expected type); `batch_error` (even a one-call `aggregate3` failed at RPC level);
`rpc_failed` (batch not collected, listed in `gaps.csv`); `zero_address` (index returned 0x0); `not_called…` (the call did not apply).
A `failures` column holds `fn=status:0x<returned data>[:rpc message]` entries separated by `|`, for every call that was not `ok`.

### factories.csv (one row per factory, 5 V2-style + 3 Slipstream)
`factory_name`, `dex_kind` (from chains.ts), `factory`, `v2_style`, `length_fn`, `snapshot_block`, `n_at_snapshot` (length at
the pinned block), `s26_log_time_utc` (time of the §2.6 `factory enumerated` line), `s26_block_at_log_time` (**derived** from
that time: (ts − 1686789347) / 2), `s26_total_logged` (the `total` in the §2.6 log), `n_onchain_at_s26_block` (length read on
chain at that block), `s26_enumerated_logged`, `s26_enum_index_start` / `s26_enum_index_end_excl` (**derived**: the newest-first
range [total − enumerated, total) that `bot/src/pools/enumerate.ts` reads), the same five `v0_*` columns for the earlier v0
run (16:37Z, dry-all-v0.log.gz), `docs_analysis_text_total` (the number quoted in docs/ANALYSIS.md §2.6, where there is one),
`n_growth_since_s26_derived` (= n_at_snapshot − s26_total_logged), `this_snapshot_index_selection` (text).

### factory-length-history.csv
`block`, `block_timestamp_formula` (**derived**, 1686789347 + 2·block), `factory_name`, `factory`, `length_fn`, `status`
(`empty` = no code yet at that block), `length`. Grid: 500,000, 1,000,000, …, 52,000,000, and 52,008,400.

### uniswapv2-sample-indices.csv.gz
`index`, `group` (`random_sample_older` | `newest_6000_at_snapshot`), `population_start`, `population_end_excl`, `seed`, `method`.

### pools-part-0001.csv.gz (one row per selected factory index)
`snapshot_block`; `factory_name`; `factory`; `dex_kind`; `index` (factory array index); `sample_group` (see 5.1);
`index_vs_s26_range` (**derived**: `below_s26_range` | `in_s26_range` | `above_s26_range`, relative to the §2.6 range in
factories.csv); `pair` + `pair_status`; `token0`, `token1` (+ status); `reserves_status`, `reserves_ret_bytes` (bytes returned
by `getReserves()`); `reserve0`, `reserve1`, `block_timestamp_last` (the three returned 32-byte words as integers, raw units:
token base units and unix seconds); `reserves_extra_hex` (bytes beyond 96, if any); `lp_total_supply` (+ status; pool LP
token `totalSupply()`); `stable` (+ status; Aerodrome only, `true`/`false`); `factory_fee` (+ status; Aerodrome only, raw
`getFee(pool, stable)` return value, in Aerodrome's fee units of 1/10,000); `failures`.
Declared `getReserves()` shapes (`getreserves-abi.csv`, Blockscout-verified ABIs): UniswapV2Pair, SushiSwap UniswapV2Pair,
PancakePair (PancakeV2) and PancakePair (BaseSwap) return `(uint112 _reserve0, uint112 _reserve1, uint32 _blockTimestampLast)`.
The Aerodrome Pool implementation `0xa4e46b4f…6d7` (pools are clones) returns
`(uint256 _reserve0, uint256 _reserve1, uint256 _blockTimestampLast)`. All are ABI-encoded as three 32-byte words (96 bytes).

### tokens.csv.gz (one row per token)
`token`, `snapshot_block`, `in_snapshot_pools` / `in_census_emitters` / `in_weth_route_set` (**derived** membership flags),
`symbol`, `symbol_encoding`, `symbol_raw`, `name`, `name_encoding`, `name_raw`, `decimals` (+ `decimals_status`), `total_supply`
(+ status; raw base units), `failures`. `*_encoding`: `string` (standard ABI string, valid printable UTF-8; `*_raw` empty),
`bytes32` (32-byte right-zero-padded text; `*_raw` holds the 32 bytes), `undecodable` (not an ABI string or bytes32 of printable UTF-8, e.g. text containing newlines or other control
characters; text empty, `*_raw` holds the full return data), or a call status (`revert`, `empty`, …) with any revert data in `*_raw`.

### price-reference-weth-pools.csv.gz (one row per non-zero lookup result, or per failed lookup)
`token`, `snapshot_block`, `venue`, `venue_kind`, `factory`, `lookup_param` (fee / tick spacing / Aerodrome stable flag;
empty for V2 `getPair`), `pool`, `lookup_status`, `pool_token0` (+ status; says which side WETH is on), `reserves_status`, `reserve0`,
`reserve1`, `block_timestamp_last` (V2-style only), `slot0_status`, `slot0_ret_bytes`, `sqrt_price_x96` (slot0 word 0),
`tick` (slot0 word 1 as signed int), `liquidity` (+ status), `weth_balance_of_pool` (+ status), `token_balance_of_pool`
(+ status) (V3-style only; raw base units), `failures`. A (token, venue, param) with no row means the factory returned the zero address.

### census-logs-part-0001.csv.gz (one row per log, sorted by block, log index)
`block_number`, `block_timestamp` (from the RPC's `blockTimestamp` field), `block_hash`, `tx_index`, `tx_hash`, `log_index`,
`address` (emitter), `event` (label from the table in 5.2), `topic0`–`topic3`, `n_topics`, `data` (raw hex), `decode_status`
(`ok` | `layout_mismatch`: topic count or data length differs from the expected layout, so the derived fields stay empty),
**derived** decoded fields: `d_sender`, `d_to` (Swap topics 1 and 2), `d_reserve0`, `d_reserve1` (Sync data words), `d_amount0_in`,
`d_amount1_in`, `d_amount0_out`, `d_amount1_out` (Swap data words, raw token base units).

### activity-pool-hour.csv.gz (**derived** from the census logs, one row per (pool, topic, hour bucket) with ≥ 1 log)
`pool_address`, `event`, `topic0`, `hour_bucket_index` (0–23), `hour_bucket_start_block`, `hour_bucket_end_block`, `count` (logs),
`distinct_tx_count`, `first_block`, `last_block`, `last_log_index`, `last_sync_reserve0` / `last_sync_reserve1` (Sync rows: the
decoded reserves of the last log in the bucket), `sum_amount0_in`, `sum_amount1_in`, `sum_amount0_out`, `sum_amount1_out`
(Swap rows: sums of the decoded amounts over the bucket, raw base units), `layout_mismatch_count`.

### emitters.csv.gz (one row per distinct emitting address in the census)
`address`, `snapshot_block`, `events_seen` (`;`-joined labels), `factory` (+ `factory_status`), `known_factory_name_derived`
(the name if `factory()` equals one of the five V2-style factories above, else empty), `token0`, `token1` (+ status),
`reserves_status`, `reserves_ret_bytes`, `reserve0`, `reserve1`, `block_timestamp_last`, `reserves_extra_hex`, `stable`
(+ status; called only for addresses that emitted `sync_uint256` or `swap_aero_v2`), `failures`.

### buckets.csv
`hour_bucket_index`, `start_block`, `end_block`, `start_timestamp`, `end_timestamp`, `start_utc`, `end_utc`, `start_block_hash`, `end_block_hash`.

### topics.csv
`event`, `signature`, `topic0`, `topic0_cast_keccak`, `topic0_python_keccak`, `example_block`, `example_tx`, `example_log_index`,
`example_emitter`, `emitter_factory_name_derived`, `check` (text), `check_result`, `rows_in_window`.

### census-chunks.csv / census-crosscheck.csv
Chunks: `chunk_start`, `chunk_end`, `log_rows`, `endpoints_used` (JSON: endpoint → logs), `fetch_secs`, `fetched_utc`, `status`.
Cross-check: `chunk_start`, `chunk_end`, `primary_rows`, `check_endpoint`, `check_rows`, `identical_log_sets`, `only_in_primary`, `only_in_check`, `error`.

### getreserves-abi.csv
`factory_name`, `example_pool`, `abi_source_address`, `abi_via`, `contract_name`, `compiler_version`, `getReserves_outputs_json`, `status`, `blockscout_url`.

### snapshot-meta.json, census-meta.json, tokens-meta.json, file-index.csv, gaps.csv
Run metadata (pinned block and hash, seeds, row counts by group, endpoint ok/error counters, start/finish times); per-file
rows, bytes and sha256 (written by finalize.py; covers the top-level files except `MANIFEST.md` and itself); unrecoverable batches
or ranges (`gaps.csv` exists only if there was at least one; it does not exist in this directory).

## 7. Coverage limits and gaps

- **Uniswap V2 is sampled, not complete**: 60,000 of the 3,057,605 indices below the §2.6 range (about 1.96 %), plus the newest 6,000
  at the pinned block. The ~103 indices [3,057,605, 3,057,708) belong to the §2.6 range but fall in neither group, so they were not read.
  All other factories are complete at the pinned block.
- **One pinned block**: reserves, fees, LP supply, token metadata and WETH-route state are single reads at block 52008400. There is no
  time series apart from `block_timestamp_last` (the pool's last reserve update) and the 24 h census.
- **Census scope**: only the four V2-style topics above. Uniswap V3, Slipstream, PancakeV3 and Uniswap V4 events were not collected here
  (V4 is in `../01-v4-pools`). The window is 24 h (43,200 blocks); anything older shows only through `block_timestamp_last`. Topic-only
  filters also catch any contract that emits the same topic; `emitters.csv.gz` records `factory()` for every emitter (row counts
  verified 2026-10-01: 4,385 rows, of which 42 have `factory_status` = `revert` and 416 have `factory_status` = `ok` with an empty
  `known_factory_name_derived`). In `census-logs-part-0001.csv.gz`, 31 rows with event `swap_aero_v2` have 1 topic and 192 data
  bytes, a different layout from the one decoded; they carry `decode_status` = `layout_mismatch`, and their raw topics and data are kept.
  (Reworded 2026-10-01 as row counts by column value; the numbers are unchanged.)
- **Transfer behaviour** (whether a token blocks or taxes transfers, question line 3) was **not** collected in this directory. Only ERC-20
  metadata was read; no transfer or swap simulation was made. A separate transfer probe is in `../04-shallow-pools/transfer-probe/`
  (sentinel `TRANSFER_PROBE.DONE`, 2026-10-01T02:19:45Z). (Corrected 2026-10-01: this line previously said that
  `../04-shallow-pools` records the probe as `TRANSFER_PROBE.FAILED`; that sentinel no longer exists.)
- **Pricing**: no token prices or USD/ETH conversions are computed here. Pools with a WETH side carry the WETH reserve in their own row.
  The Aerodrome WETH/USDC pools are in `pools-part-0001.csv.gz` (for example vAMM `0xcdac0d6c…5c43`). For tokens in pools with neither
  a WETH nor a stablecoin side, `price-reference-weth-pools.csv.gz` holds only direct token/WETH pools on the 11 configured factories:
  no multi-hop routes, no other DEXes, no Uniswap V4. `../04-shallow-pools/prices.csv.gz` holds the engine's own anchored price map at block 52008246, 154 blocks earlier.
- **Section 2.6 range reconstruction**: the §2.6 index ranges come from the run's log totals and the newest-first rule in
  `bot/src/pools/enumerate.ts`. The on-chain lengths at the matching blocks equal the logged totals (`factories.csv`). The exact block of
  each enumeration `eth_call` was not logged, so the block is derived from the log time (±1–2 blocks).
- **Endpoints**: every `eth_call` was served by blastapi and every log chunk by tenderly. Only three chunks were independently cross-checked
  against a second provider.
- **Not collected**: pair creation blocks or times (no `PairCreated` scan; `factory-length-history.csv` is the only index-to-time material),
  per-pool bytecode, and LP-holder or liquidity-lock data.
- Unrecoverable batches or ranges would be in `gaps.csv`. That file does not exist: 0 unrecoverable batches or ranges (auto-status
  block, `V2OLD.DONE` `gaps=0`; checked again 2026-10-01).

## 8. Related material elsewhere in research-material/ (pointers only)

- `../00-prior-runs/engine-runs/dry-all.log.gz`, `dry-all-v0.log.gz`: source of the §2.6 enumeration counts.
- `../04-shallow-pools/`: pools under 0.1 ETH as seen by the engine (`factory-enumeration.csv.gz` there is the engine's own newest-6,000 enumeration).
- `../05-base-onchain/`: full-block census (all transactions and receipts of swap-bearing transactions) for 51995609 onward. It overlaps the last ~12,800 blocks of this census window.
