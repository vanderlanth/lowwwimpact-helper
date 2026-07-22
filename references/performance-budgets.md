# Performance Budgets for Sustainable Web Design

## Page Weight Budget

Performance budgets are upper limits, not targets. The goal is to come in under budget.

| Asset Type | Target | Stretch Goal |
|---|---|---|
| **Total page weight** | <1.5 MB | <500 KB |
| Images (all) | <500 KB | <200 KB |
| JavaScript (compressed) | <200 KB | <100 KB |
| CSS (compressed) | <70 KB | <30 KB |
| Fonts (all) | <50 KB | <20 KB |
| HTML document | <50 KB | <20 KB |
| Other (data, media) | <100 KB | <50 KB |

## Per-Asset Budgets

| Asset | Target | Stretch Goal |
|---|---|---|
| Single hero image | <150 KB | <80 KB |
| Thumbnail image | <30 KB | <15 KB |
| Icon/logo (SVG) | <5 KB | <2 KB |
| Single font weight (subsetted WOFF2) | <25 KB | <10 KB |
| Analytics script | <5 KB | <2 KB |
| Single JS module (compressed) | <50 KB | <20 KB |
| Single CSS file (compressed) | <30 KB | <15 KB |

## Request Budgets

| Metric | Target | Stretch Goal |
|---|---|---|
| Total HTTP requests | <30 | <15 |
| Third-party domains | <4 | <2 |
| Third-party requests | <10 | <5 |
| Font file requests | <3 | <1 |
| Image requests (above fold) | <6 | <3 |

## 4-Step Budget Methodology

From Tom Greenwood's *Sustainable Web Design* (A Book Apart No. 34):

### Step 1: Benchmark
Measure equivalent web pages: the current version (if redesigning), competitor pages, and industry averages from HTTP Archive. This establishes baseline performance for your sector.

### Step 2: Estimate what's possible
Determine the theoretical minimum. Calculate the lightest possible page weight using your CMS with written content only — no images, custom fonts, or tracking scripts. This is the floor.

### Step 3: Set your budget
Set a budget that is at least as good as the current best in your industry, and ideally stretch to improve on it. The budget should be achievable — something you are confident you will not exceed.

### Step 4: Set a stretch goal
Set an ambitious but theoretically possible stretch goal for each metric. This pushes toward higher efficiency and provides an aspirational target beyond the achievable budget.

## Carbon Budget Ratings

Based on the Sustainable Web Design model (CO2 per page view, green hosting):

| Rating | CO2/pageview | Description |
|---|---|---|
| **A+** | <0.02g | Exceptional — minimal footprint |
| **A** | <0.06g | Very low carbon — well optimized |
| **B** | <0.12g | Low carbon — good practices |
| **C** | <0.25g | Average — room for improvement |
| **D** | <0.50g | Above average — significant optimization needed |
| **F** | >0.50g | High carbon — major intervention required |

## Testing Methodology

### Network Throttling
- Test on simulated 3G connection (1.6 Mbps down, 750 Kbps up, 300ms RTT)
- Test on simulated 4G connection (9 Mbps down, 1.5 Mbps up, 170ms RTT)
- Always test with cache disabled for first-visit metrics

### CPU Throttling
- Apply 4x CPU slowdown in DevTools to simulate mid-range mobile devices
- Monitor CPU usage during page load and interaction (carousel, animation, scroll)

### Device Testing
- Test on devices 5+ years old to ensure performance equity
- Test on both desktop and mobile viewports
- Verify functionality with JavaScript disabled where possible

### What to Measure
- **Page weight** (transferred bytes, not resource size)
- **Number of HTTP requests**
- **Time to Interactive (TTI)**
- **Largest Contentful Paint (LCP)**
- **Cumulative Layout Shift (CLS)**
- **Total Blocking Time (TBT)**
- **CPU usage during load** (via Safari Energy Impact or Chrome Performance tab)

## Tools

| Tool | Purpose |
|---|---|
| HTTP Archive (httparchive.org) | Industry benchmarking and historical page weight trends |
| WebPageTest (webpagetest.org) | Detailed waterfall analysis with throttling |
| Google Lighthouse | Performance, accessibility, and best practices auditing |
| Chrome DevTools Network tab | Per-request size analysis (transferred vs resource) |
| Safari Energy Impact monitor | CPU energy impact measurement |
| CO2.js (thegreenwebfoundation.org) | Programmatic carbon calculation from transfer size |
| Website Carbon Calculator (websitecarbon.com) | Quick per-page carbon estimate |
| Ecograder (ecograder.com) | Sustainability-focused site audit |
| DebugBear | Page weight monitoring over time |
| Beacon (digitalbeacon.co) | Sustainability score with WSG alignment |
