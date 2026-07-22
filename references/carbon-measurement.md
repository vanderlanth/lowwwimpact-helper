# Carbon Measurement for Sustainable Web Design

## Sustainable Web Manifesto

The 5 principles from the Sustainable Web Manifesto (sustainablewebmanifesto.com) define what sustainable web projects should be:

1. **Clean** — powered by renewable energy
2. **Efficient** — use the least amount of energy and resources possible
3. **Open** — accessible, allow information sharing, open to collaboration
4. **Honest** — do not deceive or exploit users
5. **Regenerative** — support an economy that nourishes people and planet

## Key Statistics

- If the internet were a country, it would be the 6th most polluting in the world, with annual emissions similar to Germany (source: Greenwood, *Sustainable Web Design*, citing 2018 data)
- Communication technology is estimated to use 14% of global electricity by 2040, up from ~4% in 2020 (source: *Journal of Cleaner Production*)
- The median web page weight is approximately 2 MB (desktop) and 1.8 MB (mobile), with roughly half of data transfer being images (source: HTTP Archive)
- From 2017 to 2020, median page weight increased by ~30% (source: HTTP Archive)
- Streaming video from YouTube produces approximately 10 kg of CO2 per hour, or 2.8 grams per second (source: University of Bristol)
- Bots account for approximately 50% of website traffic and consume significant server resources and bandwidth (source: BlogVault/Akshat Choudhary)
- Removing a 20 KB JavaScript dependency from a WordPress plugin installed on 2 million websites would reduce emissions by 708 tons per year (source: Danny van Kooten)
- A basic iPhone 11 (194 grams) has a carbon footprint of 72 kg CO2 over its entire life; 83% of this is embodied carbon from manufacturing (source: Apple environmental reports)

## Carbon Calculation

### The Sustainable Web Design (SWD) Model

The SWD model estimates carbon emissions from data transfer by attributing energy consumption across three system segments:

```
CO2 per visit = Data Transfer × Energy Intensity × Carbon Intensity
```

Where:
- **Data Transfer** = page weight in GB (transferred bytes, not resource size)
- **Energy Intensity** = kWh per GB of data transferred (varies by system segment)
- **Carbon Intensity** = gCO2 per kWh of electricity (varies by region and energy source)

### Energy Intensity by System Segment

The total energy per GB is split across:

| Segment | Share | Energy (kWh/GB) | Description |
|---|---|---|---|
| Data center | ~15% | 0.055 | Servers, storage, cooling |
| Network | ~14% | 0.059 | Telecom infrastructure, routers, cell towers |
| End-user device | ~52% | 0.080 | Phone, laptop, display, CPU |
| Production (embodied) | ~19% | 0.012 | Manufacturing of all infrastructure |
| **Total** | **100%** | **0.206** | **Average energy intensity** |

Note: These values are based on the Sustainable Web Design model used by CO2.js and the Website Carbon Calculator. Actual energy usage depends heavily on context. Network energy use is not directly proportional to data volume (see Schien et al., 2023).

### Carbon Intensity by Region

Carbon intensity varies dramatically by energy source and grid mix:

| Region / Energy Source | Carbon Intensity (gCO2/kWh) |
|---|---|
| Renewable (solar, wind, hydro) | <10 |
| Nuclear | <10 (including construction) |
| France (high nuclear) | ~55 |
| Norway/Sweden (high hydro) | ~20-30 |
| UK | ~230 |
| USA (average) | ~380 |
| Germany | ~350 |
| China | ~550 |
| India | ~700 |
| Coal-heavy grid | 800-1000 |
| **Global average** | **~440** |

Green hosting (100% renewable energy) reduces the data center segment's carbon intensity to near zero, but network and end-user segments still use grid electricity.

### Worked Example

For a 1.5 MB page (0.0015 GB), global average grid, standard hosting:

```
Energy = 0.0015 GB × 0.206 kWh/GB = 0.000309 kWh
CO2    = 0.000309 kWh × 440 gCO2/kWh = 0.136 gCO2
```

For the same page on green hosting (data center at ~0 gCO2/kWh):

```
Data center energy  = 0.0015 × 0.055 = 0.0000825 kWh → ~0 gCO2 (renewable)
Network energy      = 0.0015 × 0.059 = 0.0000885 kWh × 440 = 0.039 gCO2
End-user energy     = 0.0015 × 0.080 = 0.000120 kWh × 440  = 0.053 gCO2
Production energy   = 0.0015 × 0.012 = 0.000018 kWh × 440  = 0.008 gCO2
Total ≈ 0.10 gCO2 per page view (green hosting)
```

### Annual Emissions Scale

| Monthly Visitors | Page Weight | CO2/visit | Annual CO2 |
|---|---|---|---|
| 10,000 | 500 KB | ~0.045g | ~5.4 kg |
| 10,000 | 2 MB | ~0.18g | ~21.6 kg |
| 100,000 | 500 KB | ~0.045g | ~54 kg |
| 100,000 | 2 MB | ~0.18g | ~216 kg |
| 1,000,000 | 500 KB | ~0.045g | ~540 kg |
| 1,000,000 | 2 MB | ~0.18g | ~2,160 kg |

For context: a round-trip flight London to Paris emits ~250 kg CO2; London to San Francisco emits ~2,800 kg CO2.

## Browser Energy and CPU Impact

- More computation in the user's browser = more energy consumed by the user's device
- Applications with heavy CPU load drain batteries faster on mobile, disproportionately affecting users with older devices
- A static HTML file makes ~46 system calls; the equivalent PHP-generated page makes ~888 (nearly 20x more server work)
- Heavy JavaScript frameworks put processing burden on end-user devices rather than servers

### OLED Screen Energy Savings

For devices with OLED displays (most modern smartphones, growing number of laptops):
- Night mode on Google Maps reduced screen power draw by 63%
- Black pixels are off (zero energy); white is the most energy-intensive
- Darker colors generally use less energy than lighter colors
- Blue pixels consume ~25% more energy than green or red

Implication: offering a dark mode reduces energy consumption on OLED devices.

## Embodied Carbon

Embodied carbon is the CO2 emitted during the manufacture, transport, and end-of-life disposal of a product — not just its operational use.

- For an iPhone 11, only 17% of lifetime emissions come from usage; 83% is embodied carbon from manufacturing
- Heavy, CPU-intensive web applications cause users to upgrade devices faster, contributing to embodied carbon and e-waste
- Building efficient websites extends device usable lifetimes, reducing embodied carbon impact

## Measurement Tools

| Tool | Type | What It Measures |
|---|---|---|
| CO2.js | JavaScript library | Calculates CO2 from transfer size using the SWD model |
| Website Carbon Calculator | Online tool | CO2 per page view, green hosting check, percentile ranking |
| Ecograder | Online tool | Sustainability score with category breakdown |
| Beacon (digitalbeacon.co) | Online tool | Sustainability score aligned with WSG guidelines |
| Lighthouse | Browser tool / CI | Performance score, transfer sizes, unused code |
| WebPageTest | Online tool | Waterfall analysis, total transfer size, request count |
| HTTP Archive | Dataset | Industry benchmarks, historical trends, percentile data |
| Chrome DevTools Coverage | Browser tool | Unused CSS and JavaScript bytes |
| Safari Energy Impact | Browser tool | CPU energy impact rating per page load |
| Carbon Footprint (carbonfootprint.com) | Calculator | Non-digital carbon comparisons (flights, commuting) |

## W3C WSG Guideline ID Mapping

Key W3C Web Sustainability Guidelines (WSG) referenced throughout these reference files:

| WSG ID | Guideline Title | Primary Category |
|---|---|---|
| 2.5 | Account for stakeholder issues | UX Design |
| 2.7 | Avoid unnecessary or overabundance of assets | UX Design |
| 2.11 | Avoid manipulative patterns | UX Design |
| 2.15 | Take a more sustainable approach to image assets | Images |
| 2.16 | Take a more sustainable approach to media assets | Video/Audio |
| 2.17 | Take a more sustainable approach to animation | Animation |
| 2.18 | Take a more sustainable approach to typefaces | Fonts |
| 2.19 | Provide suitable alternatives to web assets | Fonts/Media |
| 2.24 | Create a stakeholder-focused testing/prototyping policy | Testing |
| 2.29 | Incorporate compatibility testing into each release cycle | Compatibility |
| 3.1 | Identify relevant technical indicators | Performance |
| 3.2 | Minify your HTML, CSS, and JavaScript | Minification |
| 3.5 | Ensure your solutions are accessible | Accessibility |
| 3.6 | Avoid code duplication | Code Quality |
| 3.7 | Rigorously assess third-party services | Third-Party |
| 3.12 | Use metadata correctly | SEO/HTML |
| 3.22 | Use the latest stable language version | Technology |
| 3.23 | Take advantage of native features | Native APIs |
| 3.24 | Run fewer, simpler queries as possible | Requests |
| 4.1 | Choose a sustainable hosting provider | Hosting |
| 4.2 | Optimize browser caching | Caching |
| 4.3 | Compress your files | Compression |
| 4.6 | Automate to fit the needs | Automation |
| 4.7 | Maintain a relevant refresh frequency | Data Transfer |
| 4.11 | Use the lowest infrastructure tier meeting business requirements | Infrastructure |
| 4.12 | Store data according to visitor needs | Data Storage |

## Reporting Template

When reporting carbon metrics for a page or site, include:

```markdown
## Sustainability Report: [Page/Site Name]

**Date:** YYYY-MM-DD
**URL:** https://example.com/page

### Page Metrics
- Page weight (transferred): X KB
- HTTP requests: X
- Third-party domains: X
- Third-party requests: X

### Carbon Estimate
- CO2 per page view: X.XXg (green hosting) / X.XXg (standard hosting)
- Carbon rating: [A+ / A / B / C / D / F]
- Monthly visitors: X → Annual CO2: X.X kg

### Budget Compliance
| Metric | Budget | Actual | Status |
|---|---|---|---|
| Total page weight | <1.5 MB | X KB | PASS/FAIL |
| Images | <500 KB | X KB | PASS/FAIL |
| JavaScript | <200 KB | X KB | PASS/FAIL |
| CSS | <70 KB | X KB | PASS/FAIL |
| Fonts | <50 KB | X KB | PASS/FAIL |
| HTTP requests | <30 | X | PASS/FAIL |
| Third-party domains | <4 | X | PASS/FAIL |

### Comparison
- Cleaner than X% of pages tested (Website Carbon Calculator)
- Industry median: X MB (HTTP Archive)

### Priority Actions
1. [Action with estimated savings]
2. [Action with estimated savings]
3. [Action with estimated savings]
```
