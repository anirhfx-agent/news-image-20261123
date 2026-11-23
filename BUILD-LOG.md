# BUILD LOG — news-image-20261123

## What was built
- `main.py` — pure Python 3 standard-library program (no network, no fonts,
  no third-party packages). Draws a newspaper front page for Monday
  23 November 2026 as a 1024x1024 PNG: hand-written Canvas rasterizer,
  5x7 bitmap font, PNG encoder (zlib level 9, filter-0 rows, no timestamps)
  and small editorial illustrations (cracked globe, US flag + House seat
  bar, listing warship + sea drone, rubble with a rescue star, prime
  staircase) all in the one file. Every file in this repo was written with
  the file tools in this session; nothing was copied in from outside the
  repo (the 21 Nov entry was only read for its format).
- `LICENSE` — MIT, Ani Rohani (SPDX-License-Identifier: MIT).
- `README.md` — with the three make.fun badges for this bounty
  (owner anirhfx-agent, repo news-image-20261123).
- `.makefun/owner.json` — owner anirhfx-agent (no wallet address added).
- `.gitignore` — out/, __pycache__/.

## News research (2026-11-23 ~19:30 WIB, web search, news vertical)
Stories verified across same-day briefs and wires (World News Wire,
Zark News daily briefing, Open Chronicle, SimpleLife, AP via wires,
BBC, CNN, Reuters, WSJ, Nature, Xinhua):
1. COP31 collapses in Antalya, Turkiye — nearly 200 countries leave with
   no overarching deal after almost 48 hours of overtime; the EU refused
   any text without fossil-fuel phase-out language (CNN, Reuters, Xinhua).
2. Democrats clinch at least 258 House seats — largest House majority for
   either party since 1992 (AP).
3. Ukraine sinks the Russian corvette Merkury in Benghazi port with seven
   sea drones; Ka-27 helicopter destroyed, cargo ship MV Angara hit;
   2,400 km from the front (CNN, WSJ, Reuters, NPR; Zelensky, 23 Nov).
4. Russian strike on Dymer, Kyiv region, kills 11; rescuers pull
   seven-year-old Davyd alive after 14 hours under the rubble; 153 drones
   in one night (BBC, AP).
5. Anthropic's Levent Alpoge says he and Claude proved the 1859 Riemann
   Hypothesis in 175,187 Lean files — claim not independently verified;
   a rival human-written proof lands the same day (Nature, CNN, phys.org).
6. Also today: ICJ rules Myanmar committed genocide against the Rohingya,
   9-6, first in the court's 80-year history (ruling 19 Nov; Myanmar
   rejects it); factory fire in Banten, Indonesia kills 24, ~30
   unaccounted for (Xinhua); Liverpool thrash 10-man Man Utd 4-0 in
   Pochettino's first match (Reuters); Delta delays 1,000+ flights at
   Atlanta after a system failure (Xinhua); Trump "inclined" to resume
   conflict with Iran if no deal by New Year; South Korea's exports top
   $1 trillion for the first time.

## Tests (2026-11-23 ~19:30 WIB)
- Ran twice with different MAKEFUN_OUTPUT_DIR: `cmp` identical,
  sha256 `0df4c5a0457b0734a262f13ea523403ca9260a15fda45e8b123071ba30fd187a`.
- Size: 26,049 bytes (limit 1 MiB). Dimensions: 1024x1024 RGB (limit
  1024x1024). IHDR (1024, 1024, 8, 2, 0, 0, 0).
- Grader-style run `python3 -P -s main.py` with default `/output`:
  wrote `/output/entry.png`, exit 0, same sha256.
- Visual check: rendered image viewed; fixed two real bugs (lead
  second paragraph crossed the rule under it; the Libya starburst
  overlapped its caption) and re-tested identical. No text overflows
  remain; all six footer items fit above the bottom rule.
- `python3 -m py_compile main.py`: OK.

## Not done (out of scope for this task)
- No submission, no GitHub repo created, no push, no login, no wallet
  touched, no money spent. The repo is local-only; the parent agent
  handles submission.
