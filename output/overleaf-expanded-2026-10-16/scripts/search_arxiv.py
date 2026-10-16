#!/usr/bin/env python3
"""Reproduce the bounded 2026 arXiv metadata search for this presentation.

This retrieves metadata, not full papers. Inclusion in these results is not
evidence that a paper was read, verified, or selected for the presentation.
"""
import csv
import json
from pathlib import Path
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

CUTOFF = "202609162359"
QUERIES = {
    "self_evolution": '(ti:"self-evolving" OR ti:"self-improving" OR ti:"self-evolution" OR ti:"recursive self-improvement" OR ti:"agent memory" OR ti:"agent skill")',
    "scientific_agents": 'all:agent AND (ti:biology OR ti:biomedical OR ti:bioinformatics OR ti:scientific OR ti:"single-cell" OR ti:"virtual cell")',
    "benchmarks": '(ti:benchmark OR ti:evaluation) AND (all:"self-evolving" OR all:"scientific agents" OR all:bioinformatics OR all:perturbation)',
    "virtual_cell": '(ti:"virtual cell" OR ti:"perturbation prediction" OR ti:"perturbation response")',
}
NS = {"a": "http://www.w3.org/2005/Atom", "o": "http://a9.com/-/spec/opensearch/1.1/"}
OUT = Path(__file__).resolve().parents[1] / "research"
OUT.mkdir(exist_ok=True)
records = {}
log = []
for group, query in QUERIES.items():
    complete_query = f"submittedDate:[202601010000 TO {CUTOFF}] AND ({query})"
    start = 0
    retrieved = 0
    while True:
        params = {"search_query": complete_query, "start": start, "max_results": 500,
                  "sortBy": "submittedDate", "sortOrder": "descending"}
        url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(url, headers={"User-Agent": "literature-review/1.0"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    payload = response.read()
                root = ET.fromstring(payload)
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(5)
        entries = root.findall("a:entry", NS)
        total = int(root.findtext("o:totalResults", default="0", namespaces=NS))
        for entry in entries:
            def val(tag):
                return " ".join(entry.findtext("a:" + tag, default="", namespaces=NS).split())
            versioned_id = val("id").rsplit("/", 1)[-1]
            paper_id = versioned_id.split("v")[0]
            item = records.setdefault(paper_id, {
                "id": paper_id, "version": versioned_id, "title": val("title"),
                "published": val("published"), "updated": val("updated"),
                "url": "https://arxiv.org/abs/" + paper_id,
                "authors": [a.findtext("a:name", namespaces=NS) for a in entry.findall("a:author", NS)],
                "query_groups": [],
            })
            if group not in item["query_groups"]:
                item["query_groups"].append(group)
        retrieved += len(entries)
        print(f"{group}: {retrieved}/{total}", flush=True)
        time.sleep(3.2)
        if retrieved >= total or not entries:
            log.append({"group": group, "query": complete_query, "reported_total": total,
                        "retrieved": retrieved, "complete_for_query": retrieved >= total})
            break
        start += len(entries)

ordered = sorted(records.values(), key=lambda r: r["published"], reverse=True)
(OUT / "arxiv-2026.json").write_text(json.dumps({"cutoff": "2026-09-16", "queries": log, "papers": ordered},
                                                  ensure_ascii=False, indent=2) + "\n")
with (OUT / "arxiv-2026.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["id", "published", "title", "url", "query_groups"], lineterminator="\n")
    writer.writeheader()
    for item in ordered:
        row = {k: item[k] for k in writer.fieldnames}
        row["query_groups"] = ";".join(row["query_groups"])
        writer.writerow(row)
print(f"Unique records: {len(ordered)}", flush=True)
