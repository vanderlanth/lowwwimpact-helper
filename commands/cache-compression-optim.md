# Gzip, Caching & Hashed Filenames — Apache .htaccess

Enable Gzip compression, extend browser cache TTL, and use hashed filenames for CSS/JS versioning. All server-side rules go in the project's `.htaccess` file. Apply every rule below. Report what was changed and what needs manual action.

---

## 1. Hashed Filenames for CSS & JS

Content-hashed filenames let you set aggressive cache TTLs without stale-content risk — when the file content changes, the filename changes, so browsers fetch the new version automatically.

**Rule:** CSS and JS files output by the build tool must include a content hash in their filename (e.g. `style-a8f3c1.css`, `app-b7d2e4.js`). HTML and PHP files must never be hashed.

### 1.1 Vite (default for SvelteKit, Nuxt, etc.)

Vite hashes by default. Verify the output pattern is locked:

```js
// vite.config.js
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]',
      },
    },
  },
});
```

### 1.2 webpack

```js
// webpack.config.js
module.exports = {
  output: {
    filename:      'assets/[name].[contenthash:8].js',
    chunkFilename: 'assets/[name].[contenthash:8].chunk.js',
    assetModuleFilename: 'assets/[name].[contenthash:8][ext]',
  },
};
```

### 1.3 No Build Tool

If the project has no bundler (plain PHP/HTML site), skip this section. Filenames are managed manually — append a query string version parameter to `<link>` and `<script>` tags instead:

```html
<link rel="stylesheet" href="/css/style.css?v=1.2.0">
<script src="/js/app.js?v=1.2.0"></script>
```

Note to the agent: detect whether the project uses a build tool. If it does, configure hashed output. If it does not, add or update `?v=` query strings on CSS/JS references in templates.

---

## 2. Gzip Compression via `mod_deflate`

Add the following block to the project's `.htaccess`. It compresses all text-based responses (HTML, CSS, JS, JSON, fonts) on the fly. Binary formats (JPEG, PNG, WOFF2, MP4) are already compressed and must be skipped.

```apache
# Gzip compression
<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/plain
AddOutputFilterByType DEFLATE text/html
AddOutputFilterByType DEFLATE text/css
AddOutputFilterByType DEFLATE text/javascript
AddOutputFilterByType DEFLATE application/json
AddOutputFilterByType DEFLATE application/javascript
AddOutputFilterByType DEFLATE application/x-javascript
AddOutputFilterByType DEFLATE font/ttf font/otf font/woff font/woff2
</IfModule>
```

---

## 3. Expire Headers via `mod_expires`

Set long TTLs for static assets and short TTLs for HTML. Images, CSS, JS, and fonts get 30 days. HTML/XHTML gets 2 hours so content updates propagate quickly.

```apache
# Expire headers
<IfModule mod_expires.c>
ExpiresActive On

ExpiresDefault "access plus 7200 seconds"
ExpiresByType image/jpg "access plus 2592000 seconds"
ExpiresByType image/jpeg "access plus 2592000 seconds"
ExpiresByType image/png "access plus 2592000 seconds"
ExpiresByType image/webp "access plus 2592000 seconds"
ExpiresByType image/avif "access plus 2592000 seconds"
ExpiresByType image/gif "access plus 2592000 seconds"
AddType image/x-icon .ico
ExpiresByType image/ico "access plus 2592000 seconds"
ExpiresByType image/icon "access plus 2592000 seconds"
ExpiresByType image/x-icon "access plus 2592000 seconds"
ExpiresByType text/css "access plus 2592000 seconds"
ExpiresByType text/javascript "access plus 2592000 seconds"
ExpiresByType text/html "access plus 7200 seconds"
ExpiresByType application/xhtml+xml "access plus 7200 seconds"
ExpiresByType application/javascript "access plus 2592000 seconds"
ExpiresByType application/x-javascript "access plus 2592000 seconds"
ExpiresByType application/x-shockwave-flash "access plus 2592000 seconds"
ExpiresByType application/vnd.ms-fontobject "access plus 1 year"

ExpiresByType font/ttf "access plus 1 year"
ExpiresByType font/otf "access plus 1 year"
ExpiresByType font/woff "access plus 1 year"
ExpiresByType font/woff2 "access plus 1 year"
ExpiresByType image/svg+xml "access plus 1 year"

</IfModule>
```

---

## 4. Cache-Control Headers via `mod_headers`

Reinforce the expire headers with explicit `Cache-Control` values. Images, CSS, and compressed assets get 30 days public cache. JS gets 30 days private cache. HTML gets 2 hours. Dynamic scripts (PHP, CGI) are excluded.

```apache
# Cache-Control headers
<IfModule mod_headers.c>
 <FilesMatch "\.(ico|jpe?g|png|webp|avif|gif|swf|css|gz)$">
 Header set Cache-Control "max-age=2592000, public"
 </FilesMatch>
 <FilesMatch "\.(js)$">
 Header set Cache-Control "max-age=2592000, private"
 </FilesMatch>
<filesMatch "\.(html|htm)$">
Header set Cache-Control "max-age=7200, public"
</filesMatch>
# Disable caching for scripts and other dynamic files
<FilesMatch "\.(pl|php|cgi|spl|scgi|fcgi)$">
Header unset Cache-Control
</FilesMatch>
</IfModule>
```

---

## How to Apply

1. Find or create the `.htaccess` file at the project web root.
2. If any of the blocks above already exist (look for `mod_deflate`, `mod_expires`, `mod_headers`), replace them with the versions above.
3. If they do not exist, append them at the end of the file.
4. Do not duplicate blocks — each module section should appear exactly once.
5. Preserve any other existing rules in the `.htaccess` (rewrites, redirects, auth, etc.).

---

## Deliverables

After applying, output a report with:

### Changes Applied

- List every file modified (`.htaccess`, build config, templates).
- Note which blocks were added vs replaced.

### Manual Actions Required

- Flag if `mod_deflate`, `mod_expires`, or `mod_headers` might not be enabled on the server (they must be activated in the Apache config by the hosting provider).
- Flag if the project has no build tool and query-string versioning was used instead of hashed filenames.
