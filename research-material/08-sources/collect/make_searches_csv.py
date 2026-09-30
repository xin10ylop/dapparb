#!/usr/bin/env python3
"""Write ../searches.csv from searches.jsonl (query, date, tool, top result URLs as returned, space-separated)."""
import csv, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(l) for l in open(os.path.join(HERE, 'searches.jsonl')) if l.strip()]
with open(os.path.join(os.path.dirname(HERE), 'searches.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['query', 'date', 'tool', 'top_result_urls'])
    for r in rows:
        w.writerow([r['query'], r['date'], r['tool'], ' '.join(r['top_urls'])])
print(len(rows), 'rows')
