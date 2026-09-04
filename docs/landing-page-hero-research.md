# Landing Page Hero — Research & Recommendation

**Date:** 2026-09-04
**Scope:** How to add a hero photo/video to a new arrival screen for Goal Kick (currently there is no dedicated landing page — anonymous and logged-in visitors both land on the matches dashboard at `/`; the only existing hero-style visual is the background photo on the login screen).

## Recommendation (short version)

Ship a high-quality **responsive photo** hero by default. Treat a looping background **video as an optional upgrade**, added later only if the photo version already performs well and the team is willing to do the compression/fallback work properly. Whichever is used, the visual should support a **specific, concrete message** (a real stat, a real preview of today's matches) rather than being purely decorative — a 2026 study of 2,000 landing pages found generic "smiling crowd" stock-photo heroes were the single worst-performing hero pattern tested (~‑11% vs. a plain control), and unoptimized autoplay video heroes also underperformed (~‑7%), mainly because they slow the page down, not because motion itself is bad.

## 1. Photo vs. video — decision table

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| Static photo | Small payload, fast, predictable, accessible by default | Less "alive" feeling | **Default choice** |
| Muted looping video | Strong atmosphere/energy | Heavier, battery/data cost, autoplay quirks, must be built carefully or it hurts conversion | Progressive enhancement only, gated behind a fast-connection + no-reduced-motion check |
| Click-to-play video | User controlled | Adds a step before payoff | Better suited below the hero (e.g. an "about the app" clip) than as the background |
| Animated illustration / mini "live scoreboard" widget | Feels alive, very light | Needs its own small design effort | Good alternative to video that avoids all the performance risk |

**Rule of thumb for turning video on:** only if the photo version is already strong, a poster image is always shown first, mobile page-load stays under ~2.5s, motion-reduction and pause preferences are respected, and hosting/bandwidth cost has been checked.

## 2. Implementation guidance (for this codebase: Create React App, no Next.js image pipeline)

- Don't use a CSS `background-image` for the hero photo — browsers discover a plain `<img>` far earlier during page load, which matters for load-speed scoring. This is the single highest-impact fix.
- Generate the photo at a few widths (roughly 640/960/1280/1920px) and in three formats: AVIF (smallest, serve first), WebP (fallback), JPEG (final fallback) — the `<picture>` element handles serving whichever format/size a browser supports automatically.
- The hero image must load immediately and at high priority: no lazy-loading, and mark it as high-priority so it isn't stuck behind lower-priority requests. Reserve its space on the page up front so nothing shifts around while it loads.
- Target well under 250KB for the hero image itself after compression.
- If/when video is added: keep the clip silent, looping, 4–8 seconds, encoded small (roughly under 2MB for mobile, 4MB for desktop), always show a poster image immediately, don't start loading the video file until the page is otherwise ready, and swap it out entirely for the poster when the visitor's device has "reduce motion" turned on. A single short clip doesn't need a paid video-hosting platform — it can be served as a normal file from the same hosting as the rest of the site.

## 3. Where to get safe, free visuals

Use generic football/stadium/crowd imagery — never real match broadcast footage, club badges, league logos, sponsor marks, or recognizable players, all of which are rights-protected.

- **Pexels** — large free library of football/stadium/crowd photos.
- **Pixabay** and **Mixkit** — free short stadium/football video clips.
- **Coverr**, **Vecteezy** — more footage, but confirm each individual clip is actually free (not a "Pro"/paid item) before using it.
- Lowest-risk option: an empty pitch, grass, ball, floodlights, or a phone-shot clip of a local match — no identifiable people, no logos.

Keep a simple record per asset used: source URL, creator, license type, and download date, in case it's ever questioned later.

## 4. Real-world reference points

- **The Athletic** — minimizes distraction (no autoplay video, no clutter); content and typography carry the page. Relevant since Goal Kick is a news app first.
- **ESPN** — hero ties directly into live utility (scores/standings) rather than pure decoration.
- **Nike sports pages** — one full-bleed image, one message, one button; restraint outperforms busy layouts.
- **Wolves Academy** — video hero works because it shows something specific and real (the training campus), not generic stock motion.

## 5. Suggested next step for Goal Kick

Build the hero around: a football-specific (not generic-crowd) photo background, a short honest headline about what the app does, one clear call-to-action button, and optionally a small "live-feeling" element (e.g. a mini scoreboard tile) to add energy without the cost/risk of video. Mockup concepts for this direction were generated separately via Magic Patterns — see the shared link provided alongside this report.

## Sources

- [Landing Page Conversion: 2,000 Pages Tested in 2026](https://www.digitalapplied.com/blog/landing-page-conversion-study-2000-pages-tested-2026)
- [Cinematic Landing Pages with Video Backgrounds — 2026 Guide](https://sitesplaced.com/blog/cinematic-landing-pages-with-video-backgrounds)
- [Optimize Largest Contentful Paint — web.dev](https://web.dev/articles/optimize-lcp)
- [Optimize the LCP Resource Load Delay](https://www.corewebvitals.io/core-web-vitals/largest-contentful-paint/resource-load-delay)
- [HTML `picture` element — MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/picture)
- [Optimize resource loading with the Fetch Priority API — web.dev](https://web.dev/articles/fetch-priority)
- [How To Optimize LCP For Video Elements — DebugBear](https://www.debugbear.com/blog/optimize-video-lcp)
- [Autoplay guide for media — MDN](https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Autoplay)
- [Can Auto-Playing Videos be Accessible? — Thoughtbot](https://thoughtbot.com/blog/can-auto-playing-videos-be-accessible)
- [Best Video CDN Providers in 2026 — Swarmify](https://swarmify.com/blog/best-video-cdn-providers/)
- [Free football crowd photos — Pexels](https://www.pexels.com/search/football%20crowd/)
- [Free stadium/football video — Pixabay](https://pixabay.com/videos/stadium-football-soccer-arena-350248/)
