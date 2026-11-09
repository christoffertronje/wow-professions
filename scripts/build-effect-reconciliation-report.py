#!/usr/bin/env python3
"""Summarize source differences without confusing text or unresolved templates with verified errors."""
import json,pathlib,re
root=pathlib.Path(".")
data=json.loads((root/"data/item-stats.json").read_text(encoding="utf-8"))["byItemId"]
reports=["docs/common-item-second-source-audit.json","docs/uncommon-stats-second-source-audit.json","docs/rare-stats-second-source-audit.json","docs/epic-stats-second-source-audit.json"]
sources={p:json.loads((root/p).read_text(encoding="utf-8")) for p in reports}
# These older comparison snapshots may be stale after reviewed corrections.
# Keep their original text and compare it with the CURRENT published record.
classifications={
 "2304":"cooldown-and-format","2313":"cooldown-and-format","18662":"cooldown-and-format",
 "279941":"newer-client-content","279945":"newer-client-content","279978":"newer-client-content",
 "7284":"conflicting-proc-metadata","7375":"redundant-proc-annotation",
 "7348":"gameplay-source-conflict","8197":"gameplay-source-conflict",
 "12641":"wording-only","18251":"gameplay-source-conflict",
 "279258":"source-template-unresolved","252603":"gameplay-source-conflict",
}
unresolved_template_ids={"4265","8173","15564","252452","252453","252462","252463","252487","252488","18251","279258"}
for iid in unresolved_template_ids:
 if iid not in classifications:classifications[iid]="source-template-unresolved"
results=[]
for path,report in sources.items():
 for item in report["results"]:
  if item["status"]=="match":continue
  iid=str(item["itemId"]);current=data.get(iid)
  if current is None:raise RuntimeError("Missing item "+iid)
  kind=classifications.get(iid)
  if kind is None:raise RuntimeError("Unreviewed discrepancy "+iid+" in "+path)
  # A second source may expose raw 0cN spell placeholders while the item
  # itself has a reviewed, properly resolved enchant from other sources.
  # Preserve the historical comparison uncertainty without classifying
  # those already-corrected items as missing gameplay values.
  if kind=="source-template-unresolved" and current.get("reviewedCorrection",{}).get("source"):
   kind="source-template-undecoded-reviewed"
  result={"itemId":int(iid),"name":current["name"],"quality":current["quality"],
     "historicalStatus":item["status"],"classification":kind,
     "currentEffect":current["effects"],"currentStats":current["stats"],
     "sourceItemUrl":item["url"],"currentHasWarning":bool(current.get("statReviewWarning")),
     "notes":current.get("reviewedCorrection",{}).get("reason"),
     "sourceValues":item.get("source",{}).get("effects",[])}
  results.append(result)
counts={}
for item in results:
 kind=item["classification"];counts[kind]=counts.get(kind,0)+1
payload={"meta":{"title":"Legacy cross-source effect reconciliation","scope":"Differences visible in retained second-source audit snapshots, not fresh live item inspection",
 "warning":"Historical audit reports compare earlier versions and are not automatically rewritten after corrections. Template placeholders are undecodable, not zero.",
 "itemRecords":len(data),"checkedSnapshots":reports},"summary":{"historicalFlaggedItems":len(results),
   "classifications":dict(sorted(counts.items())),"currentlyWarnedRecords":sum(bool(x.get("statReviewWarning")) for x in data.values()),
   "templateUnresolvedFromSnapshots":sum(x["classification"].startswith("source-template-") for x in results),
   "templateUnresolvedWithoutReviewedCorrection":sum(x["classification"]=="source-template-unresolved" for x in results)},
 "items":sorted(results,key=lambda x:x["itemId"])}
assert payload["summary"]["templateUnresolvedFromSnapshots"] in (10,11)
assert payload["summary"]["templateUnresolvedWithoutReviewedCorrection"]==0, "Source template still lacks a reviewed effect"
(root/"docs/effect-reconciliation-report.json").write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(payload["summary"])
