# Sustainability Report Template

Use this exact structure for the final synthesized report. Fill every section.

---

```markdown
# Sustainability Report: [Application Name]

**Date**: [Date]
**URL**: [Target URL]
**Reviewed by**: AI Sustainability Audit Team (6 specialist agents)

---

## Executive Summary

[3-5 sentences: What is the overall sustainability posture of this site? What are the biggest
wins already in place? What are the most impactful problems? What is the estimated carbon
per pageview and how does it compare to the budget?]

---

## Sustainability Grade: [A+ / A / B / C / D / F]

**Carbon per pageview**: [X.XX g CO2]
**Annual estimate**: [X.X kg CO2] (at [N] pageviews/month)

| Rating | Threshold | Status |
|--------|-----------|--------|
| A+ | < 0.02 g | |
| A | < 0.06 g | |
| B | < 0.12 g | |
| C | < 0.25 g | |
| D | < 0.50 g | |
| F | > 0.50 g | |

---

## Page Weight Breakdown

| Asset Type | Current | Budget | Status | Savings Potential |
|------------|---------|--------|--------|-------------------|
| Images | X KB | < 500 KB | PASS/OVER | ~X KB |
| JavaScript | X KB | < 200 KB | PASS/OVER | ~X KB |
| CSS | X KB | < 70 KB | PASS/OVER | ~X KB |
| Fonts | X KB | < 50 KB | PASS/OVER | ~X KB |
| HTML | X KB | < 50 KB | PASS/OVER | ~X KB |
| Other | X KB | — | — | ~X KB |
| **Total** | **X KB** | **< 1.5 MB** | **PASS/OVER** | **~X KB** |

**HTTP Requests**: [N] (budget: < 30)
**Third-party domains**: [N] (budget: < 4)

---

## Scores by Domain

| Domain | Score (1-10) | Summary |
|--------|:---:|---------|
| Images | X | [One sentence] |
| Media & Fonts | X | [One sentence] |
| JavaScript | X | [One sentence] |
| CSS & HTML | X | [One sentence] |
| Network & Infrastructure | X | [One sentence] |
| Carbon & Performance | X | [One sentence] |
| **Overall** | **X** | **[One sentence]** |

---

## Top 5 Critical Issues

### 1. [Issue Title]
**Impact**: [Estimated KB savings and/or CO2 reduction]
**Evidence**: [What was observed — reference specific resources/pages]
**Fix**: Run `/xyz-optim` — [brief description of what the command will do]
**Effort**: [Quick fix / Small task / Medium task / Large task]

### 2. [Issue Title]
...

[Repeat for top 5]

---

## Quick Wins (< 30 minutes each)

These high-impact, low-effort fixes should be tackled first:

| # | Fix | Location | Est. Savings | Fix Command | Est. Time |
|---|-----|----------|-------------|-------------|-----------|
| 1 | [Specific change] | [Page/Resource] | ~X KB | `/xyz-optim` | [Minutes] |
| 2 | ... | ... | ... | ... | ... |

---

## Fix Command Summary

Grouped by which `/xyz-optim` command to run, ordered by total impact:

| Order | Command | Findings Covered | Est. Total Savings | Priority |
|-------|---------|-----------------|-------------------|----------|
| 1 | `/image-optim` | [N] findings | ~X KB | High |
| 2 | `/typo-optim` | [N] findings | ~X KB | High |
| 3 | ... | ... | ... | ... |

---

## Sprint Plan

### Sprint 1: Quick Wins (< 1 day total)
High-impact, low-effort optimizations.

- [ ] [Task 1 — specific, actionable, with KB savings estimate]
- [ ] [Task 2]
- [ ] ...

**Estimated savings**: ~X KB (~X% of current page weight)

### Sprint 2: Core Optimizations (2-3 days)
Major asset and infrastructure improvements.

- [ ] [Task 1]
- [ ] [Task 2]
- [ ] ...

**Estimated savings**: ~X KB (~X% of current page weight)

### Sprint 3: Deep Optimization (1 week)
Structural changes, code splitting, caching strategy.

- [ ] [Task 1]
- [ ] [Task 2]
- [ ] ...

**Estimated savings**: ~X KB (~X% of current page weight)

### Sprint 4: Maintenance (ongoing)
Monitoring, CI enforcement, lower-priority improvements.

- [ ] [Task 1]
- [ ] [Task 2]
- [ ] ...

---

## Detailed Findings

### Images
[Consolidated findings from the images audit agent]

### Media & Fonts
[Consolidated findings from the media & fonts audit agent]

### JavaScript
[Consolidated findings from the JavaScript audit agent]

### CSS & HTML
[Consolidated findings from the CSS & HTML audit agent]

### Network & Infrastructure
[Consolidated findings from the network & infrastructure audit agent]

### Carbon & Performance
[Consolidated findings from the carbon & performance audit agent]

---

## Strengths (Keep These)

Things that are already efficient — don't regress on these while optimizing:

- [Strength 1]
- [Strength 2]
- [Strength 3]

---

## Methodology

This review was conducted by 6 specialized AI agents, each using Playwright CLI to browse
the live application and inspect its resources, network behavior, and code patterns.

**Scoring model**: Sustainable Web Design (SWD) model
- Data transfer × Energy intensity (0.206 kWh/GB) × Carbon intensity (442 gCO2/kWh global avg)
- Green hosting adjustment applied when detected

**Budgets**: Based on W3C Web Sustainability Guidelines (WSG)
- Page weight: < 1.5 MB total (stretch: < 500 KB)
- Images: < 500 KB | JS: < 200 KB | CSS: < 70 KB | Fonts: < 50 KB | HTML: < 50 KB
- HTTP requests: < 30 | Third-party domains: < 4

**Limitations**:
- Transfer sizes from Performance API may differ from server-reported sizes
- Carbon calculations use global average grid intensity unless hosting region is known
- Compression savings are estimates based on typical ratios
- Dynamic/authenticated content may not be fully audited without credentials
- This is an automated heuristic audit, not a lab-grade performance test
```
