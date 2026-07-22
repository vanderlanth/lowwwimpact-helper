# Web Assets Management in the CMS

Audit and enforce media constraints at the CMS level to prevent content editors from degrading page performance. Apply every rule below to the CMS configuration, upload pipeline, and editorial interface. Report what was changed, what needs manual action, and why.

---

## 1. Set Content Limits Per Page

Define hard upper bounds in the CMS schema/blueprint to prevent unbounded content growth.

### Block / Section Limits
Enforce a maximum number of content blocks per page. Flag any page type with no block cap:

**Kirby (blueprints/pages/article.yml):**
```yaml
fields:
  content:
    type: blocks
    max: 20
```

**Craft CMS (Matrix field):**
```php
// In field settings or via config
'maxBlocks' => 20,
```

**WordPress (ACF flexible content):**
```php
'max' => 20,
```

**Recommended limits by page type:**

| Page type | Max blocks | Max galleries | Max embeds |
|---|---|---|---|
| Article / Post | 20 | 1 | 3 |
| Landing page | 30 | 2 | 4 |
| Homepage | 15 | 1 | 2 |
| Product page | 25 | 1 | 2 |

### Gallery Image Limits
Cap the number of images allowed in any gallery or image list field:

**Kirby:**
```yaml
fields:
  gallery:
    type: files
    max: 12
    accepts:
      - image
```

**Craft CMS (Assets field):**
```php
'limit' => 12,
```

**WordPress (ACF gallery):**
```php
'max' => 12,
```

### Embed Limits
Limit the number of iframe / video embeds per page. Audit all rich-text fields and block builders for uncapped embed blocks and add a maximum.

### File Upload Size Limits
Set a hard maximum upload size at the CMS application level, independent of the server's `upload_max_filesize`:

**Kirby (config/config.php):**
```php
return [
    'thumbs' => [
        'quality' => 80,
    ],
    'files' => [
        'maxSize' => 5 * 1024 * 1024, // 5 MB hard limit
    ],
];
```

**WordPress (functions.php or plugin):**
```php
add_filter('upload_size_limit', function () {
    return 5 * 1024 * 1024; // 5 MB
});
```

**Craft CMS (config/general.php):**
```php
'maxUploadFileSize' => 5 * 1024 * 1024, // 5 MB
```

**Recommended upload size limits by file type:**

| File type | Max upload size |
|---|---|
| Image (raster) | 5 MB |
| Image (vector SVG) | 500 KB |
| PDF | 10 MB |
| Video | 50 MB (prefer external hosting) |
| Audio | 20 MB |
| Document | 10 MB |

---

## 2. Automatic Processing on Upload

Every image uploaded through the CMS must be automatically resized, compressed, converted, and stripped of metadata before storage.

### Resize on Ingest
Never store the raw uploaded file as the canonical asset. Resize to a maximum display resolution immediately on upload:

**Kirby (using Kirby's built-in thumb API in a hook):**
```php
// site/config/config.php
return [
    'hooks' => [
        'file.create:after' => function ($file) {
            if ($file->type() === 'image') {
                // Force max dimension on storage
                $file->thumb([
                    'width'   => 2400,
                    'height'  => 2400,
                    'quality' => 80,
                ]);
            }
        },
    ],
];
```

**WordPress (using `wp_handle_upload_prefilter` or Imagify/ShortPixel plugin):**
```php
add_filter('wp_handle_upload_prefilter', function ($file) {
    // Delegate to a server-side resize before saving
    // Use Imagick or GD to cap dimensions at 2400px
    return $file;
});
```

**Sharp (Node.js — for custom CMS pipelines or headless setups):**
```js
import sharp from 'sharp';

async function processUpload(inputPath, outputPath) {
  await sharp(inputPath)
    .resize(2400, 2400, { fit: 'inside', withoutEnlargement: true })
    .toFile(outputPath);
}
```

**Maximum storage dimensions by intended use:**

| Use case | Max width | Max height |
|---|---|---|
| Hero / full-width | 2400 px | 1600 px |
| Article inline image | 1600 px | 1200 px |
| Thumbnail / card | 800 px | 800 px |
| Avatar / profile | 400 px | 400 px |

### Compress on Ingest
Target **80% perceptual quality** for all raster images. Flag any pipeline storing uncompressed originals as the served asset.

```bash
# Sharp (Node.js)
sharp(input).resize(2400).webp({ quality: 80 }).toFile(output);

# cwebp
cwebp -q 80 input.png -o output.webp

# Squoosh CLI
squoosh-cli --webp '{"quality":80}' input.jpg

# ImageMagick
convert input.jpg -resize 2400x2400\> -quality 80 -strip output.jpg
```

### Convert to AVIF / WebP
Store all raster uploads as **AVIF** (primary) with a **WebP** fallback. Never store or serve JPEG/PNG as the primary format for new uploads:

**Sharp pipeline (Node.js — recommended for custom or headless CMS):**
```js
import sharp from 'sharp';
import path from 'path';

async function convertUpload(inputPath, baseName, outputDir) {
  // AVIF — best compression, modern browsers
  await sharp(inputPath)
    .resize(2400, 2400, { fit: 'inside', withoutEnlargement: true })
    .avif({ quality: 60, effort: 6 })
    .toFile(path.join(outputDir, `${baseName}.avif`));

  // WebP — fallback for broader support
  await sharp(inputPath)
    .resize(2400, 2400, { fit: 'inside', withoutEnlargement: true })
    .webp({ quality: 80 })
    .toFile(path.join(outputDir, `${baseName}.webp`));

  // JPEG — legacy fallback only
  await sharp(inputPath)
    .resize(2400, 2400, { fit: 'inside', withoutEnlargement: true })
    .jpeg({ quality: 80, progressive: true })
    .toFile(path.join(outputDir, `${baseName}.jpg`));
}
```

**Kirby (thumbs config with AVIF + WebP):**
```php
return [
    'thumbs' => [
        'format'  => 'avif', // primary
        'quality' => 60,
        'driver'  => 'im', // ImageMagick required for AVIF
    ],
];
```

**WordPress:** Use Imagify, ShortPixel, or EWWW Image Optimizer configured to auto-convert on upload and serve via `<picture>` with AVIF + WebP sources.

### Strip EXIF / Metadata
Remove all EXIF, IPTC, XMP, and GPS metadata from every uploaded image before storage:

```bash
# ImageMagick — strip all metadata
convert input.jpg -strip output.jpg

# ExifTool — remove all tags
exiftool -all= -overwrite_original input.jpg

# Sharp — strips metadata by default; confirm with:
sharp(input).withMetadata(false).toFile(output);
```

- Flag any storage pipeline that preserves GPS coordinates — this is a privacy risk as well as a weight issue.
- The only metadata that may be intentionally retained: copyright strings where legally required.

---

## 3. Reject Oversized Uploads

Validate uploads **before** storage and return a clear error to the editor if constraints are violated.

### Image Resolution Rejection
Reject images whose pixel dimensions exceed the maximum useful display size. There is no valid reason to store a 8000×6000 px photo on a website:

**Kirby (file upload hook with validation):**
```php
return [
    'hooks' => [
        'file.create:before' => function ($file, $upload) {
            if ($file->type() === 'image') {
                $dimensions = $upload->dimensions();
                if ($dimensions->width() > 5000 || $dimensions->height() > 5000) {
                    throw new \Exception(
                        'Image exceeds maximum resolution (5000×5000 px). Please resize before uploading.'
                    );
                }
            }
        },
    ],
];
```

**WordPress:**
```php
add_filter('wp_handle_upload_prefilter', function ($file) {
    if (str_starts_with($file['type'], 'image/')) {
        [$width, $height] = getimagesize($file['tmp_name']);
        if ($width > 5000 || $height > 5000) {
            $file['error'] = 'Image exceeds 5000×5000 px. Please resize before uploading.';
        }
    }
    return $file;
});
```

**Rejection thresholds:**

| Type | Max pixel dimensions | Max file size |
|---|---|---|
| General image | 5000 × 5000 px | 5 MB |
| Hero image | 5000 × 3000 px | 5 MB |
| Thumbnail | 1600 × 1600 px | 2 MB |

### Video Size Rejection
Reject video uploads above a defined threshold and direct editors to an external video host (YouTube, Vimeo, self-hosted stream):

**Kirby:**
```php
return [
    'hooks' => [
        'file.create:before' => function ($file, $upload) {
            if ($file->type() === 'video') {
                if ($upload->size() > 50 * 1024 * 1024) { // 50 MB
                    throw new \Exception(
                        'Videos must be under 50 MB. Upload to Vimeo or YouTube and embed the URL instead.'
                    );
                }
            }
        },
    ],
];
```

**WordPress:**
```php
add_filter('wp_handle_upload_prefilter', function ($file) {
    $videoTypes = ['video/mp4', 'video/webm', 'video/ogg'];
    if (in_array($file['type'], $videoTypes) && $file['size'] > 50 * 1024 * 1024) {
        $file['error'] = 'Videos over 50 MB are not allowed. Use an external video host and embed the URL.';
    }
    return $file;
});
```

---

## 4. File Size Warnings for Editors

Surface file size information in the CMS editorial interface so non-technical editors understand the cost of their choices.

### Show File Size in File/Asset Lists
Ensure the CMS panel always displays file size alongside filename, dimensions, and format. Flag any asset list view that omits file size.

**Kirby (custom panel view snippet):**
Display size in the files section by configuring the `info` property in the blueprint:
```yaml
# blueprints/files/image.yml
title: Image
accept:
  mime: image/*
fields:
  alt:
    type: text
    label: Alt text
    required: true
info: "{{ file.niceSize }} — {{ file.dimensions }}"
```

**WordPress (custom admin column):**
```php
add_filter('manage_media_columns', function ($cols) {
    $cols['file_size'] = 'File Size';
    return $cols;
});
add_action('manage_media_custom_column', function ($col, $postId) {
    if ($col === 'file_size') {
        $bytes = filesize(get_attached_file($postId));
        echo size_format($bytes);
    }
}, 10, 2);
```

### Inline Warnings at Upload Time
Display a visible warning banner when an uploaded file is large but within the accepted limit:

```php
// Kirby hook — add a warning notification for files between 2 MB and the 5 MB limit
return [
    'hooks' => [
        'file.create:after' => function ($file) {
            if ($file->type() === 'image' && $file->size() > 2 * 1024 * 1024) {
                // Surface a panel notification
                \Kirby\Panel\Panel::notify([
                    'message' => 'This image is ' . $file->niceSize() . '. Consider compressing it before publishing.',
                    'type'    => 'warning',
                ]);
            }
        },
    ],
];
```

**Warning thresholds:**

| File type | Warning threshold | Block threshold |
|---|---|---|
| Image | > 500 KB | > 5 MB |
| Video | > 10 MB | > 50 MB |
| PDF | > 3 MB | > 10 MB |
| Audio | > 5 MB | > 20 MB |

---

## 5. Sustainability Indicator — Estimated Page Weight

Show content editors a real-time or on-save estimate of total page weight, so they understand the environmental and performance cost of the content they are building.

### Page Weight Calculation
Estimate total page transfer size by summing:
- Image files linked from the page (use stored file sizes)
- Video embeds (estimate 500 KB overhead per external embed; 0 for facade-loaded)
- Document / PDF downloads linked
- Approximate HTML + CSS + JS bundle size (use a static baseline from the last build)

**Kirby (custom panel section plugin):**
```php
// site/plugins/page-weight/index.php
Kirby::plugin('studio/page-weight', [
    'sections' => [
        'pageWeight' => [
            'props' => [
                'headline' => fn ($headline = 'Page Weight Estimate') => $headline,
            ],
            'computed' => [
                'weight' => function () {
                    $page   = kirby()->page($this->model()->id());
                    $bytes  = 0;

                    // Sum all linked file sizes
                    foreach ($page->files() as $file) {
                        $bytes += $file->size();
                    }

                    // Static baseline for HTML/CSS/JS
                    $bytes += 200 * 1024; // 200 KB baseline

                    return [
                        'total'  => round($bytes / 1024) . ' KB',
                        'rating' => $bytes < 500 * 1024 ? 'green'
                                  : ($bytes < 1500 * 1024 ? 'amber' : 'red'),
                    ];
                },
            ],
        ],
    ],
]);
```

Add to any page blueprint:
```yaml
sections:
  pageWeight:
    type: pageWeight
    headline: "Estimated Page Weight"
```

**WordPress (meta box):**
```php
add_action('add_meta_boxes', function () {
    add_meta_box('page_weight', 'Page Weight Estimate', function ($post) {
        $bytes = 200 * 1024; // HTML/CSS/JS baseline
        $attachments = get_attached_media('', $post->ID);
        foreach ($attachments as $a) {
            $bytes += filesize(get_attached_file($a->ID));
        }
        $kb     = round($bytes / 1024);
        $rating = $kb < 500 ? '🟢 Lightweight' : ($kb < 1500 ? '🟡 Moderate' : '🔴 Heavy');
        echo "<p><strong>{$kb} KB</strong> estimated transfer — {$rating}</p>";
        echo "<p style='color:#888;font-size:12px'>Includes images attached to this post + 200 KB baseline for HTML/CSS/JS.</p>";
    }, ['post', 'page'], 'side');
});
```

### Sustainability Rating Scale

| Total page weight | Rating | Guidance |
|---|---|---|
| < 500 KB | Green — Lightweight | Excellent. Low carbon, fast on mobile. |
| 500 KB – 1.5 MB | Amber — Moderate | Acceptable. Review largest assets. |
| 1.5 MB – 3 MB | Red — Heavy | Action required. Compress or remove assets. |
| > 3 MB | Critical | Publish blocked or strong warning shown. |

### Optional: Block Publishing Above a Weight Threshold
For strict enforcement, prevent saving/publishing a page that exceeds the critical threshold:

**Kirby (page.update:before hook):**
```php
return [
    'hooks' => [
        'page.update:before' => function ($page, $values, $strings) {
            $bytes = 0;
            foreach ($page->files() as $file) {
                $bytes += $file->size();
            }
            if ($bytes > 3 * 1024 * 1024) {
                throw new \Exception(
                    'This page exceeds the 3 MB weight limit (' . round($bytes / 1024 / 1024, 1) . ' MB). Remove or compress assets before publishing.'
                );
            }
        },
    ],
];
```

---

## Deliverables

After auditing the project, output a structured report with these sections:

### ✅ Changes Applied
List every CMS config file, blueprint, hook, or plugin modified — what limit was added, what validation was introduced, what auto-processing pipeline was configured.

### ⚠️ Manual Actions Required
List items requiring human action — installing image processing dependencies (Sharp, ImageMagick), configuring server upload limits (`upload_max_filesize`, `post_max_size`), building a custom panel plugin for page weight. Include exact file paths and setup steps.

### Server Configuration Checklist
Provide copy-paste server-level settings to align with CMS limits:

**PHP (php.ini or .htaccess):**
```ini
upload_max_filesize = 5M
post_max_size = 6M
max_execution_time = 60
```
```apache
# .htaccess
php_value upload_max_filesize 5M
php_value post_max_size 6M
```

**Nginx:**
```nginx
client_max_body_size 5M;
```

### 📊 Estimated Impact
Provide a rough before/after summary of:
- Maximum possible page weight before and after limits
- Number of upload constraints introduced
- Auto-processing steps added (resize, compress, convert, strip)
- Whether a page weight indicator was added and at what thresholds
