#!/usr/bin/env python3
"""Generate the static error pages into public/. Run `python3 build.py` after editing and commit the output."""
import html
import pathlib

PAGES = {
    "400": ("Bad request", "The request could not be understood.", "Something about the request was malformed. Check the address and try again."),
    "401": ("Sign-in required", "You need to sign in to see this.", "Authentication is required for this page. Sign in and try again."),
    "403": ("Forbidden", "You don't have access to this.", "The server understood the request but refuses to allow it."),
    "404": ("Page not found", "There is nothing at this address.", "The page may have moved, or the link may be wrong."),
    "408": ("Request timeout", "The request took too long.", "The connection was idle for too long. Try again."),
    "413": ("Payload too large", "That upload is too big.", "The request body exceeds what this server accepts."),
    "429": ("Too many requests", "Slow down a little.", "You have sent too many requests in a short time. Wait a moment and try again."),
    "500": ("Server error", "Something broke on our side.", "The service hit an unexpected error. It is not you; try again shortly."),
    "502": ("Bad gateway", "The service did not answer properly.", "The edge could not get a valid response from the service behind it. It may be restarting."),
    "503": ("Service unavailable", "The service is not available right now.", "It may be restarting or under maintenance. Try again in a minute."),
    "504": ("Gateway timeout", "The service took too long to answer.", "The edge gave up waiting for the service behind it. Try again shortly."),
}
# Served with a 404 status to requests that hit an edge node by bare IP or unknown host.
SPECIAL = {
    "direct-ip": ("Direct IP access forbidden", "This server is not reachable by IP address.",
                  "You reached an edge node without a valid hostname. Use the site's domain name instead.", "403"),
}

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{code_label}{title}</title>
<style>
:root{{--bg:#f6f6f4;--fg:#1b1b1a;--muted:#62625e;--accent:#b4442a;--line:#dcdcd6}}
@media (prefers-color-scheme:dark){{:root{{--bg:#141413;--fg:#ececea;--muted:#9a9a94;--accent:#e8825f;--line:#2e2e2b}}}}
*{{box-sizing:border-box}}
html,body{{margin:0}}
body{{background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:24px 16px}}
main{{max-width:34rem;width:100%}}
.code{{font:700 clamp(4rem,18vw,7.5rem)/1 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--accent);letter-spacing:-.04em;margin:0}}
.code.sm{{font-size:clamp(1.6rem,8vw,2.4rem);letter-spacing:-.02em}}
h1{{font-size:1.5rem;margin:.5rem 0 .25rem}}
p{{margin:.25rem 0;color:var(--muted)}}
p.lead{{color:var(--fg);font-size:1.1rem}}
.actions{{margin-top:1.5rem;display:flex;gap:.75rem;flex-wrap:wrap}}
a.btn{{display:inline-block;padding:.5rem 1rem;border:1px solid var(--line);border-radius:6px;color:var(--fg);text-decoration:none;font-size:.95rem}}
a.btn:hover,a.btn:focus-visible{{border-color:var(--accent);color:var(--accent)}}
footer{{margin-top:2.5rem;padding-top:1rem;border-top:1px solid var(--line);font-size:.8rem;color:var(--muted)}}
/* below: used by the connection trace page only (kept here so the stylesheet is identical everywhere) */
h2{{font-size:.75rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:1.5rem 0 .25rem}}
dl.kv{{margin:0;border-top:1px solid var(--line)}}
dl.kv div{{display:flex;gap:1rem;padding:.45rem 0;border-bottom:1px solid var(--line)}}
dl.kv dt{{flex:0 0 7.5rem;color:var(--muted)}}
dl.kv dd{{margin:0;min-width:0;overflow-wrap:anywhere;font:.9rem/1.5 ui-monospace,SFMono-Regular,Menlo,monospace}}
.map{{width:100%;height:auto;display:block;margin:.75rem 0 .25rem}}
.map .land{{fill:none;stroke:var(--muted);stroke-opacity:.5;stroke-width:.72;stroke-linecap:round;stroke-dasharray:0 1}}
.map .arc{{fill:none;stroke:var(--accent);stroke-width:.45;stroke-linecap:round;stroke-dasharray:1.2 1.2;animation:flow 1.4s linear infinite}}
@keyframes flow{{to{{stroke-dashoffset:-2.4}}}}
@media (prefers-reduced-motion:reduce){{.map .arc{{animation:none}}}}
.map .you{{fill:var(--bg);stroke:var(--fg);stroke-width:.5}}
.map .edge{{fill:var(--accent)}}
.map .ring{{fill:none;stroke:var(--accent);stroke-width:.3;stroke-opacity:.55}}
.map text{{font:2.5px ui-monospace,SFMono-Regular,Menlo,monospace;fill:var(--fg)}}
.map text.dim{{fill:var(--muted)}}
</style>
</head>
<body>
<main>
<p class="code" aria-hidden="true">{code_big}</p>
<h1>{title}</h1>
<p class="lead">{lead}</p>
<p>{detail}</p>
{actions}
<footer>vmd1 edge &middot; {code_label}{title}</footer>
</main>
</body>
</html>
"""

RETRY = '<div class="actions"><a class="btn" href="">Try again</a></div>'
NONE = ""


def render(code_big, code_label, title, lead, detail, actions):
    e = html.escape
    return TEMPLATE.format(code_big=e(code_big), code_label=e(code_label), title=e(title),
                           lead=e(lead), detail=e(detail), actions=actions)


def main():
    out = pathlib.Path(__file__).parent / "public"
    out.mkdir(exist_ok=True)
    for code, (title, lead, detail) in PAGES.items():
        actions = RETRY if code in {"408", "429", "500", "502", "503", "504"} else NONE
        (out / f"{code}.html").write_text(render(code, f"{code} ", title, lead, detail, actions), encoding="utf-8")
    for name, (title, lead, detail, big) in SPECIAL.items():
        (out / f"{name}.html").write_text(render(big, "", title, lead, detail, NONE), encoding="utf-8")
    (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")


if __name__ == "__main__":
    main()
