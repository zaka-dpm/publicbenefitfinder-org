PUBLIC BENEFIT FINDER SITE PAGES

Run python3 scripts/preview.py, then open http://127.0.0.1:8093/.
Clean URLs need the preview server locally and Apache mod_rewrite on the server.
Every page shares the same stylesheets and scripts.

index.html          Homepage
find.html           Public benefits wizard; state, need, urgency, household and optional income
programs.html       Program guides index, grouped by type of help, with search
guide-snap.html     Program guide template (SNAP shown)
states.html         Browse by state (A to Z list plus a state picker)
state-*.html        Generated directories for all 50 states and D.C.
about.html          About, how we write guides, contact

css/tokens.css          Brand colors, spacing and fonts (light and dark mode)
css/pbf-components.css  Design system components
css/site.css            Page layouts
js/pbf.js, js/site.js   ZIP validation and the mobile menu
fonts/                  Public Sans, self-hosted

Content marked with [brackets] or a "Sample content" comment must be checked or filled in from
the official agency before publishing: income limits, benefit amounts, agency names and links.
Public URLs are listed in data/routes.json. The HTML files remain the page sources.
.htaccess serves the clean URLs and redirects old .html URLs permanently.
Keep data/routes.json, .htaccess, canonical URLs and sitemap.xml in sync when adding pages.

Source content audit: data/source-inventory.json lists the 596 local source program guides
and 54 help pages. Content still requires agency verification before migration.

Rebuild directories and routing: python3 scripts/build_directory.py
Arizona guide content: data/arizona-snap-content.html
Wizard behavior: js/finder.js; catalog: data/finder-programs.json
Guide expansion: python3 scripts/expand_program_guides.py, then python3 scripts/build_directory.py
594 in-scope program pages are available locally. Current checkpoint: 581 reviewed
program guides and 13 individually rewritten guides awaiting specific primary-source checks.
No source-adapted starter drafts remain.
These counts include Arizona SNAP's separate fragment. See data/content-progress.json
for state-by-state remaining slugs and blockers; refresh with scripts/content_progress.py.
Pending guides retain noindex metadata and are excluded from the sitemap.
Do not deploy the full collection as finished content.

Authored copy: data/guide-content/*.json; Arizona uses its separate HTML fragment.
Editorial status: data/program-details.json. Agency link replacements retain provenance
in data/agency-link-overrides.json. A reachable site is not a factual verification.
Raw source collection is ignored in .content-review/source-guides.json.
962 historical screenshot files are saved under images/programs (about 97 MB).
Ten source guides did not provide screenshots. Ohio WIC now points to the USDA state
contact page. Some current agency information remains inaccessible or contradictory;
precise unresolved details are recorded in the authored guide provenance.
The national SNAP guide is rewritten and links to the state SNAP application guides.
All changes remain local pending approval to push.

Parallel work resumed October 1, 2026 after the user refreshed the allowance.
Completed JSON batches are integrated into local pages. No commit or push.
Remaining verification is listed by exact slug in data/content-progress.json. Resume manual
program-specific research and rewriting; do not replace these articles with bulk profiles.
