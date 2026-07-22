# SEO — Metadata Discoverability Audit

Audit, enforce, and automate SEO metadata across this project. Ensure every page has unique titles, accurate descriptions, canonical URLs, complete Open Graph tags, appropriate structured data, and no redundant or harmful meta declarations. Apply every rule below. Report what was changed, what needs manual action, and why.

---

## 1. Unique Titles and Meta Descriptions Per Page

Every page must have a distinct `<title>` (50–60 characters) and `<meta name="description">` (120–160 characters). Duplicate or missing tags cause search engines to either rewrite the titles themselves or suppress the page entirely.

### 1.1 Framework Patterns

**SvelteKit (`<svelte:head>`):**

```svelte
<svelte:head>
  <title>Page Title — Site Name</title>
  <meta name="description" content="120–160 character description unique to this page." />
</svelte:head>
```

**Next.js (App Router):**

```js
// app/page.js
export const metadata = {
  title: 'Page Title — Site Name',
  description: '120–160 character description unique to this page.',
};
```

**Next.js (Pages Router):**

```jsx
import Head from 'next/head';

export default function Page() {
  return (
    <>
      <Head>
        <title>Page Title — Site Name</title>
        <meta name="description" content="120–160 character description unique to this page." />
      </Head>
    </>
  );
}
```

**Static HTML:**

```html
<head>
  <title>Page Title — Site Name</title>
  <meta name="description" content="120–160 character description unique to this page." />
</head>
```

### 1.2 Resolution Table

| Pattern | Resolution |
|---|---|
| Missing `<title>` | Add a unique, descriptive title to every page template |
| Missing `<meta name="description">` | Add a description summarising the page's specific content |
| Title < 50 chars | Expand with more descriptive terms or include brand name |
| Title > 60 chars | Trim to the most important keywords; move brand to end |
| Description < 120 chars | Expand with a second sentence about page value or content |
| Description > 160 chars | Cut to the first 155 characters at a natural break |
| Duplicate title | Add page-specific differentiator (product name, category, location) |
| Duplicate description | Rewrite each to reflect that specific page's unique content |

---

## 2. Canonical URLs

Every page must declare `<link rel="canonical">` pointing to the single preferred URL.

**SvelteKit:**

```svelte
<script>
  import { page } from '$app/stores';
</script>

<svelte:head>
  <link rel="canonical" href="https://example.com{$page.url.pathname}" />
</svelte:head>
```

**Next.js (App Router):**

```js
export async function generateMetadata({ params }) {
  return {
    alternates: {
      canonical: `https://example.com/${params.slug}`,
    },
  };
}
```

### Canonical Edge Cases

| Scenario | Rule |
|---|---|
| Paginated page (`/blog?page=2`) | Each paginated page uses its own canonical |
| URL parameters for filtering/sorting | Canonical points to the clean URL without parameters |
| HTTP page exists alongside HTTPS | Canonical always points to HTTPS |
| Trailing slash inconsistency | Pick one convention and enforce it site-wide via redirect |

---

## 3. Open Graph Tags

Every public page must include all five required OG tags plus Twitter/X card tags:

```html
<!-- Open Graph -->
<meta property="og:title"       content="Page Title — Site Name" />
<meta property="og:description" content="150-character description written for social sharing context." />
<meta property="og:url"         content="https://example.com/page-path/" />
<meta property="og:image"       content="https://example.com/og/page-image.jpg" />
<meta property="og:type"        content="website" />

<!-- Twitter/X Card -->
<meta name="twitter:card"        content="summary_large_image" />
<meta name="twitter:title"       content="Page Title — Site Name" />
<meta name="twitter:description" content="150-character description written for social sharing context." />
<meta name="twitter:image"       content="https://example.com/og/page-image.jpg" />
```

Use `og:type="article"` for blog posts and editorial content. Use `og:type="website"` for all other pages.

### OG Image Specification

| Property | Requirement |
|---|---|
| Dimensions | 1200 × 630 px |
| File size | < 300 KB (aim for < 150 KB with AVIF/WebP) |
| Format | JPEG or PNG for maximum compatibility |
| Per-page | Unique image per page (not one global fallback for all pages) |

---

## 4. Structured Data (JSON-LD) — When Relevant

Add JSON-LD only when a page genuinely qualifies for a schema type. Never force schema onto pages that do not match.

### Decision Table

| Page type | Schema type |
|---|---|
| Homepage | `Organization` + `WebSite` |
| Blog post / article | `Article` or `BlogPosting` |
| Product page | `Product` with `Offer` |
| Page with real Q&A | `FAQPage` |
| Breadcrumb trail | `BreadcrumbList` |
| Local business | `LocalBusiness` |
| Any other page | None |

**Do not apply schema when:**
- The content described in the schema is not visible on the page
- The page is a login, 404, search results, or utility page

---

## 5. Avoiding Overloaded and Duplicate Meta Tags

### Tags to Remove Unconditionally

| Tag | Why |
|---|---|
| `<meta name="keywords" content="...">` | Ignored by Google since 2009 |
| `<meta http-equiv="X-UA-Compatible" content="IE=edge">` | IE is end-of-life |
| `<meta name="robots" content="index,follow">` | Default behaviour — redundant |
| Duplicate `<meta charset>` declarations | Only one charset declaration per document |
| Duplicate `<meta name="viewport">` | Only one viewport declaration per document |

### robots Meta Tag Rules

| Use case | Correct directive |
|---|---|
| Normal public page | Omit the tag entirely (default is index, follow) |
| Staging / preview environment | `<meta name="robots" content="noindex">` |
| Thin or duplicate content page | `<meta name="robots" content="noindex, follow">` |
| Internal search results | `<meta name="robots" content="noindex, nofollow">` |

---

## 6. Pre-Deployment Audit & CI

### package.json Scripts

```json
{
  "scripts": {
    "audit:seo": "npm run audit:seo:titles && npm run audit:seo:canonical && npm run audit:seo:og && npm run audit:seo:meta",
    "postbuild": "npm run audit:seo"
  }
}
```

### Lighthouse SEO Score

Target a Lighthouse SEO score of 100. Add SEO assertions to your existing Lighthouse CI config:

```js
// lighthouserc.js (add to existing config)
export default {
  ci: {
    assert: {
      assertions: {
        'categories:seo':   ['error', { minScore: 1.0 }],
        'meta-description': ['error', { minScore: 1 }],
        'document-title':   ['error', { minScore: 1 }],
        'canonical':        ['error', { minScore: 1 }],
        'is-crawlable':     ['error', { minScore: 1 }],
      },
    },
  },
};
```

---

## Deliverables

After auditing the project, output a structured report with these sections:

### ✅ Changes Applied

List every file created or modified — meta tags added or corrected, canonical links added, OG tags added, JSON-LD blocks inserted, deprecated tags removed.

### ⚠️ Manual Actions Required

List items requiring human review — OG images that need to be created or resized to 1200 × 630 px, JSON-LD schema decisions pending content review, robots meta directives to confirm as intentional.

### Current SEO Status

| Check | Status | Details |
|---|---|---|
| Unique `<title>` per page | Pass / Fail | X pages, X duplicates |
| Unique `<meta description>` per page | Pass / Fail | X pages, X duplicates |
| `<link rel="canonical">` present | Pass / Fail | X pages missing |
| OG tags complete | Pass / Fail | X pages missing |
| Twitter card tags complete | Pass / Fail | X pages missing |
| Deprecated tags removed | Pass / Fail | X instances found |

### Estimated Impact

- Pages with corrected titles: X
- Pages with new or fixed descriptions: X
- Pages with canonical tags added: X
- Pages with OG/Twitter tags added: X
- Deprecated or harmful tags removed: X
