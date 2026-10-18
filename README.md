# error-pages

Static error pages for the vmd1 Traefik edge. Served as an EdgeSite (see the `homelab` repo) and used by Traefik's `errors` middleware.

- `build.py` generates `public/` (`python3 build.py`); the generated files are committed because the EdgeSite serves `public/` as-is (no build step).
- `public/<status>.html`: 400, 401, 403, 404, 408, 413, 429, 500, 502, 503, 504.
- `public/direct-ip.html`: shown (with HTTP status 404) for requests that reach an edge node by bare IP or an unknown host.
- The footer has a "Click to view IP" toggle (`<details>`, no JavaScript). The IP is filled in by nginx SSI (`<!--# echo var="client_ip" -->`, from the first `X-Forwarded-For` entry, IP characters only) in the homelab `error-pages` DaemonSet; opened as a plain file it shows nothing.
- Pages are fully self-contained (inline CSS, no JavaScript, no external requests), support light/dark, and are `noindex`.

## Shared look

The stylesheet in `build.py` is the single design for all vmd1 infrastructure pages. The Traefik connection trace page (`/.vmd1/trace`, plugin source in the homelab repo, `crds-and-operators/traefik/manifest.yaml`) embeds a copy of the same CSS, so change both together.
