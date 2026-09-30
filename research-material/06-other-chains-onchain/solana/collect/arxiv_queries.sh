#!/bin/bash
# arXiv API listings (raw Atom XML) used for docs/literature/. Re-run: bash arxiv_queries.sh
cd "$(dirname "$0")/../docs/literature"
curl -sS -m 60 -A "Mozilla/5.0" -o arxiv-query-solana-arbitrage-mev.atom.xml "https://export.arxiv.org/api/query?search_query=abs:solana+AND+(abs:arbitrage+OR+abs:MEV+OR+abs:%22maximal+extractable+value%22+OR+abs:sandwich+OR+abs:jito)&max_results=100&sortBy=submittedDate&sortOrder=descending"
for q in "all:solana+AND+all:arbitrage" "all:solana+AND+all:MEV" "all:solana+AND+all:jito" "all:solana+AND+all:sandwich" "all:solana+AND+all:%22transaction+fees%22"; do
  f="arxiv-query-$(echo $q | tr -c 'A-Za-z0-9' '_' ).atom.xml"
  curl -sS -m 60 -A "Mozilla/5.0" -o "$f" "https://export.arxiv.org/api/query?search_query=$q&max_results=100&sortBy=submittedDate&sortOrder=descending"; sleep 3
done
date -u +%FT%TZ >> arxiv-query-solana-arbitrage-mev.fetched_at_utc.txt
