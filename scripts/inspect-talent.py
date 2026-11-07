#!/usr/bin/env python3
"""Inspect Forever Talent public HTML markup to build ID-based skill mapping."""
from html.parser import HTMLParser
import urllib.request
import pathlib
u="https://wowforevertalent.com/professions/leatherworking/"
r=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 (compatible; WoWProfessions/0.1)"})
with urllib.request.urlopen(r, timeout=60) as response: html=response.read().decode("utf-8","replace")
print("Page bytes:",len(html))
lines=[]
for needle in ("Spell 1263031","Spell 2149","Learning skill: 140","Learning skill: 300","spell-1263031","data-spell"):
    start=html.find(needle)
    lines.append(f"NEEDLE {needle}: {start}")
    if start>=0:lines.append(html[max(0,start-900):start+900])
pathlib.Path("docs").mkdir(exist_ok=True)
pathlib.Path("docs/talent-markup-probe.txt").write_text("\n".join(lines),encoding="utf-8")
