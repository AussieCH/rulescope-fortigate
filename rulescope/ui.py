"""Shared look for every page rulescope writes: color tokens (light + dark), palettes, components, controls.

Pages stay self-contained (no fonts, scripts or styles from the network) because reports are
opened offline at client sites. Area colors identify audit areas everywhere (nav, bars, cards);
severity uses a separate fixed status scale and is always paired with a text label.

Five palettes, each with a light and a dark variant. Every area set was validated for color-vision
deficiency separation, lightness band and contrast against its surface, in this adjacency order:
exposure, rules, device, monitoring, vpn (objects is a neutral gray). Dark tokens apply on screen
only, so printing always uses the light variant of the chosen palette.
"""
from html import escape as _esc
from typing import Dict

AREA_VAR = {"exposure": "--a-exposure", "rules": "--a-rules", "device": "--a-device", "admin": "--a-device",
            "monitoring": "--a-monitoring", "vpn": "--a-vpn", "objects": "--a-objects"}

_LIGHT = """
  color-scheme: light;
  --bg:#eef1f5; --surface:#ffffff; --surface-2:#f6f8fa; --surface-3:#eceff3;
  --ink:#121826; --ink-2:#4a5466; --ink-3:#6f7889; --line:#e1e5eb; --line-2:#cdd3dc;
  --link:#1d5fb8; --focus:#1d5fb8; --brand:#13304f; --brand-2:#1d4a75; --on-brand:#ffffff; --topbar-line:transparent;
  --sev-high:#d03b3b; --sev-medium:#ec835a; --sev-low:#fab219; --sev-info:#8a919c; --good:#0ca30c;
  --sev-high-bg:#fbeaea; --sev-medium-bg:#fdefe8; --sev-low-bg:#fff5dc; --sev-info-bg:#eef0f3; --good-bg:#e7f6e7;
  --good-ink:#006300; --bad-ink:#b42318;
  --a-exposure:#d55181; --a-rules:#2a78d6; --a-device:#1baf7a; --a-monitoring:#6250d6; --a-vpn:#008300; --a-objects:#7c8596;
  --code-bg:#0f1720; --code-ink:#dbe4ee; --tip-bg:#121826; --tip-ink:#ffffff;
"""
_DARK = """
  color-scheme: dark;
  --bg:#0c1016; --surface:#141a22; --surface-2:#19202a; --surface-3:#212a35;
  --ink:#e6ebf2; --ink-2:#aeb7c5; --ink-3:#8a95a7; --line:#252d38; --line-2:#323c49;
  --link:#7fb2f0; --focus:#7fb2f0; --brand:#0f2338; --brand-2:#17375a; --on-brand:#e6ebf2; --topbar-line:transparent;
  --sev-high-bg:rgba(208,59,59,.20); --sev-medium-bg:rgba(236,131,90,.20); --sev-low-bg:rgba(250,178,25,.18);
  --sev-info-bg:rgba(138,145,156,.18); --good-bg:rgba(12,163,12,.18); --good-ink:#3fc93f; --bad-ink:#ff8a80;
  --a-exposure:#d55181; --a-rules:#3987e5; --a-device:#199e70; --a-monitoring:#9085e9; --a-vpn:#008300; --a-objects:#8590a2;
  --code-bg:#0a0e13; --code-ink:#d5dee9; --tip-bg:#e6ebf2; --tip-ink:#121826;
"""

_AREA_ORDER = ("exposure", "rules", "device", "monitoring", "vpn", "objects")


def _areas(*colors: str) -> Dict[str, str]:
    return {f"a-{a}": c for a, c in zip(_AREA_ORDER, colors)}


# id: (label, light overrides, dark overrides). Harbor is the base above.
PALETTES: Dict[str, tuple] = {
    "harbor": ("Harbor", {}, {}),
    "forest": ("Forest", {
        "bg": "#edf2ee", "surface-2": "#f5f8f5", "surface-3": "#e8eee9", "line": "#dde5df", "line-2": "#c9d4cc",
        "link": "#1b6b4a", "focus": "#1b6b4a", "brand": "#163a2c", "brand-2": "#24563f",
        **_areas("#ae4976", "#3275b4", "#158561", "#8a57ae", "#4e822c", "#7d8a80")}, {
        "bg": "#0b120e", "surface": "#121a15", "surface-2": "#17211b", "surface-3": "#1f2b24", "line": "#233029",
        "line-2": "#2f3e35", "link": "#7cc9a3", "focus": "#7cc9a3", "brand": "#0e231b", "brand-2": "#1a3d2e",
        **_areas("#cc6490", "#4e90d2", "#3ca17b", "#a672cb", "#689d48", "#8b9a8f")}),
    "ocean": ("Ocean", {
        "bg": "#ecf3f5", "surface-2": "#f4f8fa", "surface-3": "#e6eef1", "line": "#dbe6ea", "line-2": "#c6d5db",
        "link": "#0b6e8a", "focus": "#0b6e8a", "brand": "#0b3a4a", "brand-2": "#0f5466",
        **_areas("#b4446e", "#0068ad", "#18a07e", "#6363c6", "#3b8841", "#758a93")}, {
        "bg": "#091216", "surface": "#10191e", "surface-2": "#152027", "surface-3": "#1c2a32", "line": "#22313a",
        "line-2": "#2e3f49", "link": "#6fc6dd", "focus": "#6fc6dd", "brand": "#08222c", "brand-2": "#0d3a47",
        **_areas("#cc5a82", "#1380c7", "#2cab88", "#797ce1", "#4e9a52", "#86a0aa")}),
    "graphite": ("Graphite", {
        "bg": "#f0f0f1", "surface-2": "#f7f7f8", "surface-3": "#ebebed", "line": "#e0e0e3", "line-2": "#cacace",
        "link": "#2b5f9e", "focus": "#2b5f9e", "brand": "#24272c", "brand-2": "#3a3f47",
        **_areas("#a74d65", "#1a609e", "#269c79", "#7466b5", "#518133", "#80848c")}, {
        "bg": "#0e0f11", "surface": "#17181b", "surface-2": "#1c1e21", "surface-3": "#24262a", "line": "#2a2c30",
        "line-2": "#36393e", "link": "#8fb4e3", "focus": "#8fb4e3", "brand": "#16181b", "brand-2": "#2a2d33",
        **_areas("#c1657c", "#3c7ebe", "#39aa86", "#897bcc", "#669649", "#8e939b")}),
    "contrast": ("High contrast", {
        "bg": "#ffffff", "surface": "#ffffff", "surface-2": "#f2f2f2", "surface-3": "#e3e3e3", "ink": "#000000",
        "ink-2": "#1a1a1a", "ink-3": "#3d3d3d", "line": "#8a8a8a", "line-2": "#4d4d4d", "link": "#0039a6",
        "focus": "#0039a6", "brand": "#000000", "brand-2": "#1a1a1a", "topbar-line": "#000000",
        **_areas("#a0005d", "#004ead", "#007950", "#5f3bbb", "#006d09", "#5c5c5c")}, {
        "bg": "#000000", "surface": "#000000", "surface-2": "#0d0d0d", "surface-3": "#1f1f1f", "ink": "#ffffff",
        "ink-2": "#f0f0f0", "ink-3": "#c8c8c8", "line": "#7a7a7a", "line-2": "#b0b0b0", "link": "#8ab4ff",
        "focus": "#ffd400", "brand": "#000000", "brand-2": "#1f1f1f", "topbar-line": "#ffffff",
        **_areas("#e8579a", "#3186e9", "#26ac80", "#8e71f5", "#399e43", "#a6a6a6")}),
}
DEFAULT_PALETTE = "harbor"


def _decl(d: Dict[str, str]) -> str:
    return "".join(f"--{k}:{v};" for k, v in d.items())


def _palette_css() -> str:
    light = "".join(f':root[data-palette="{p}"]{{{_decl(lt)}}}' for p, (_, lt, _) in PALETTES.items() if lt)
    dark_auto = "".join(f':root[data-palette="{p}"]:not([data-theme="light"]){{{_decl(dk)}}}'
                        for p, (_, _, dk) in PALETTES.items() if dk)
    dark_set = "".join(f':root[data-palette="{p}"][data-theme="dark"]{{{_decl(dk)}}}' for p, (_, _, dk) in PALETTES.items() if dk)
    return (":root{" + _LIGHT + "}" + light
            + "@media screen and (prefers-color-scheme: dark){:root:not([data-theme=\"light\"]){" + _DARK + "}" + dark_auto + "}"
            + "@media screen{:root[data-theme=\"dark\"]{" + _DARK + "}" + dark_set + "}")


CSS = (_palette_css() + """
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
body{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.55 "Segoe UI Variable Text","Segoe UI",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif}
a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}
:focus-visible{outline:2px solid var(--focus);outline-offset:2px;border-radius:4px}
h1,h2,h3{font-family:"Segoe UI Variable Display","Segoe UI",system-ui,-apple-system,Arial,sans-serif;letter-spacing:-.015em}
h1{font-size:34px;line-height:1.15;margin:0;font-weight:750}
h2{font-size:22px;line-height:1.25;margin:0;font-weight:700}
h3{font-size:16px;margin:0;font-weight:650}
p{margin:0 0 10px}
.mono,code,pre{font-family:ui-monospace,"Cascadia Mono",Consolas,Menlo,monospace}
.dim{color:var(--ink-3)}
.num{text-align:right;font-variant-numeric:tabular-nums}

/* ---------- top bar & shell */
.topbar{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:14px;padding:10px 24px;
  background:var(--brand);color:var(--on-brand);box-shadow:0 1px 0 var(--topbar-line)}
.topbar .mark{display:flex;align-items:center;gap:8px;font-weight:700;letter-spacing:-.01em}
.topbar .mark svg{display:block}
.topbar .who{opacity:.85;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.topbar .spacer{flex:1}
.tbtn{appearance:none;border:1px solid rgba(255,255,255,.28);background:transparent;color:var(--on-brand);
  font:inherit;font-size:13px;padding:5px 12px;border-radius:8px;cursor:pointer;display:inline-flex;gap:6px;align-items:center}
.tbtn:hover{background:rgba(255,255,255,.10)}
.gchip{white-space:nowrap;display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:650;padding:3px 10px;border-radius:999px;
  background:rgba(255,255,255,.12)}
.shell{display:grid;grid-template-columns:232px minmax(0,1fr);gap:32px;max-width:1360px;margin:0 auto;padding:0 24px}
nav.side{position:sticky;top:58px;align-self:start;max-height:calc(100vh - 70px);overflow:auto;padding:28px 0 24px}
nav.side ol{list-style:none;margin:0;padding:0}
nav.side a{display:flex;align-items:center;gap:9px;padding:6px 10px;border-radius:8px;color:var(--ink-2);font-size:14px}
nav.side a:hover{background:var(--surface-3);text-decoration:none;color:var(--ink)}
nav.side a[aria-current="true"]{background:var(--surface);color:var(--ink);font-weight:600;box-shadow:inset 3px 0 0 var(--c,var(--brand-2))}
nav.side .sub a{padding-left:26px;font-size:13px}
nav.side .cnt{margin-left:auto;font-size:12px;color:var(--ink-3);font-variant-numeric:tabular-nums}
nav.side .grp{margin:18px 10px 6px;font-size:12px;color:var(--ink-3)}
.dot{width:9px;height:9px;border-radius:50%;background:var(--c,var(--ink-3));flex:none}
main{min-width:0;padding:28px 0 64px}
main>section{margin:0 0 36px;scroll-margin-top:72px}
.sec-h{display:flex;align-items:baseline;gap:12px;margin:0 0 14px;padding-left:14px;border-left:4px solid var(--c,var(--brand-2))}
.sec-h .aside{margin-left:auto;font-size:13px;color:var(--ink-3)}
.lede{color:var(--ink-2);margin:-6px 0 14px;max-width:78ch}

/* ---------- hero */
.hero{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:20px;margin-bottom:18px}
.hero .sub{color:var(--ink-2);margin-top:6px}
.facts{display:flex;flex-wrap:wrap;gap:6px 22px;margin:0;font-size:13px}
.facts div{display:flex;flex-direction:column}
.facts dt{color:var(--ink-3)}.facts dd{margin:0;font-weight:600}
.keyrow{display:grid;grid-template-columns:1.25fr 1fr 1fr 1fr;gap:14px}
.key{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px 18px;
  border-top:4px solid var(--c,var(--line-2));display:flex;flex-direction:column;gap:6px;min-width:0}
.key .lbl{font-size:13px;color:var(--ink-2)}
.key .big{font-size:40px;font-weight:750;line-height:1;letter-spacing:-.02em}
.key ul{margin:4px 0 0;padding:0;list-style:none;font-size:13px;color:var(--ink-2)}
.key li{margin:2px 0;line-height:1.4}
.key.grade{flex-direction:row;align-items:center;gap:18px;background:linear-gradient(135deg,var(--surface) 55%,var(--g-bg) 100%)}
.key.grade .letter{font-size:96px;font-weight:800;line-height:.85;color:var(--g);letter-spacing:-.04em}
.key.grade .score{font-size:26px;font-weight:700}.key.grade .score small{font-size:15px;color:var(--ink-3);font-weight:500}
.row2{display:grid;grid-template-columns:1.25fr 1fr;gap:14px;margin-top:14px}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px 18px;min-width:0}
.panel>h3{margin-bottom:12px}

/* area bars */
.row2 .panel{display:flex;flex-direction:column}
.bars{display:flex;flex-direction:column;gap:9px;flex:1;justify-content:space-around}
.bar{display:grid;grid-template-columns:172px minmax(0,1fr) 34px 74px;gap:10px;align-items:center;font-size:14px;
  color:var(--ink);border-radius:6px;position:relative}
a.bar:hover{text-decoration:none;background:var(--surface-2)}
.bar .name{display:flex;align-items:center;gap:8px}
.track{height:10px;background:var(--surface-3);border-radius:10px;overflow:hidden}
.track i{display:block;height:100%;border-radius:10px;background:var(--c)}
.bar b{text-align:right;font-variant-numeric:tabular-nums}
.bar .n{font-size:12px;color:var(--ink-3);text-align:right}

/* severity mix */
.stack{display:flex;gap:2px;height:22px;margin:4px 0 12px}
.stack span{display:block;height:100%;border-radius:4px;position:relative;min-width:6px}
.legend{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 16px;margin:0;padding:0;list-style:none;font-size:14px}
.legend li{display:flex;align-items:center;gap:8px}.legend b{margin-left:auto;font-variant-numeric:tabular-nums}
.sq{width:11px;height:11px;border-radius:3px;background:var(--c);flex:none}
[data-tip]:hover::after,[data-tip]:focus-visible::after{content:attr(data-tip);position:absolute;left:50%;bottom:calc(100% + 8px);
  transform:translateX(-50%);background:var(--tip-bg);color:var(--tip-ink);font-size:12px;padding:6px 9px;border-radius:7px;
  white-space:nowrap;z-index:5;pointer-events:none}

.groups{list-style:none;margin:14px 0 0;padding:12px 0 0;border-top:1px solid var(--line);display:flex;flex-direction:column;gap:7px;font-size:13.5px}
.groups li{display:flex;align-items:center;gap:8px}.groups a{flex:1;min-width:0}.groups b{font-variant-numeric:tabular-nums;color:var(--ink-2)}
details.whywan{margin:-6px 0 14px;font-size:13.5px;color:var(--ink-2)}
details.whywan summary{cursor:pointer;color:var(--ink-2)}details.whywan ul{margin:6px 0 0;padding-left:20px}
details.whywan li{margin:2px 0}
.summary{font-size:16px;line-height:1.65;max-width:76ch}
.note{display:flex;gap:10px;margin-top:12px;padding:10px 14px;border-radius:10px;background:var(--surface-2);
  border:1px solid var(--line);font-size:13.5px;color:var(--ink-2)}
.note p{margin:2px 0}

/* ---------- pills & chips */
.pill{display:inline-flex;align-items:center;gap:6px;padding:1px 9px 1px 7px;border-radius:999px;font-size:12px;
  font-weight:600;white-space:nowrap;color:var(--ink);background:var(--sev-info-bg);line-height:20px}
.pill::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--pc,var(--sev-info))}
.pill.high{background:var(--sev-high-bg);--pc:var(--sev-high)}
.pill.medium{background:var(--sev-medium-bg);--pc:var(--sev-medium)}
.pill.low{background:var(--sev-low-bg);--pc:var(--sev-low)}
.pill.info{background:var(--sev-info-bg);--pc:var(--sev-info)}
.pill.ok{background:var(--good-bg);--pc:var(--good)}
.achip{display:inline-flex;align-items:center;gap:6px;font-size:12px;color:var(--ink-2);white-space:nowrap}
.tag{display:inline-block;margin:1px 3px 1px 0;padding:0 6px;border-radius:5px;font-size:11px;background:var(--surface-3);color:var(--ink-2)}
.svc{display:inline-block;margin:2px 3px 0 0;padding:0 7px;border-radius:999px;font-size:11.5px;font-weight:600;
  color:var(--ink);border:1.5px solid var(--a-exposure)}

/* ---------- priority actions (ranked = numbered) */
ol.actions{list-style:none;margin:0;padding:0;counter-reset:a;display:flex;flex-direction:column;gap:10px}
ol.actions li{counter-increment:a;display:grid;grid-template-columns:38px minmax(0,1fr) auto;gap:4px 14px;align-items:start;
  background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--c);border-radius:10px;padding:12px 16px}
ol.actions li::before{content:counter(a);grid-row:span 3;width:30px;height:30px;border-radius:50%;background:var(--surface-3);
  color:var(--ink);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px}
ol.actions .t{font-weight:650}ol.actions .rec{color:var(--ink-2);font-size:14px}ol.actions .tg{font-size:12.5px;color:var(--ink-3)}
ol.actions .go{grid-row:span 3;align-self:center;font-size:13px;white-space:nowrap}

/* ---------- tables */
.tw{overflow-x:auto;background:var(--surface);border:1px solid var(--line);border-radius:12px}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th{text-align:left;font-weight:600;color:var(--ink-2);font-size:12.5px;background:var(--surface-2);
  border-bottom:1px solid var(--line);padding:9px 10px;white-space:nowrap}
td{border-bottom:1px solid var(--line);padding:8px 10px;vertical-align:top}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover td{background:var(--surface-2)}
.exp td,.inv td{font-size:12.5px}
.act-accept,.act-ipsec{color:var(--good-ink);font-weight:600}.act-deny{color:var(--bad-ink);font-weight:600}
tr.off td{color:var(--ink-3)}

/* ---------- findings */
.filters{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:0 0 16px;padding:12px 14px;background:var(--surface);
  border:1px solid var(--line);border-radius:12px}
.filters .lbl{font-size:12.5px;color:var(--ink-3);margin-right:2px}
.chip{appearance:none;font:inherit;font-size:13px;display:inline-flex;align-items:center;gap:7px;padding:4px 11px;border-radius:999px;
  border:1px solid var(--line-2);background:var(--surface);color:var(--ink-2);cursor:pointer}
.chip[aria-pressed="true"]{background:var(--surface-3);color:var(--ink);border-color:var(--ink-3);font-weight:600}
.chip[aria-pressed="false"]{opacity:.55}
.chip .n{font-variant-numeric:tabular-nums;color:var(--ink-3)}
.search{flex:1;min-width:180px;font:inherit;font-size:14px;padding:6px 12px;border-radius:9px;border:1px solid var(--line-2);
  background:var(--surface-2);color:var(--ink)}
.vsep{width:1px;height:22px;background:var(--line);margin:0 4px}
.shown{font-size:13px;color:var(--ink-3);margin-left:auto}
.area-group{margin:0 0 22px}
.area-h{display:flex;align-items:center;gap:10px;margin:0 0 10px;padding:8px 12px;border-radius:10px;
  background:linear-gradient(90deg,color-mix(in srgb,var(--c) 16%,transparent),transparent 70%)}
.area-h h3{font-size:17px}.area-h .meta2{margin-left:auto;font-size:13px;color:var(--ink-2)}
details.fcard{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--c);border-radius:10px;margin:0 0 8px}
details.fcard>summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:10px;padding:11px 14px}
details.fcard>summary::-webkit-details-marker{display:none}
details.fcard>summary::after{content:"";width:8px;height:8px;border-right:2px solid var(--ink-3);border-bottom:2px solid var(--ink-3);
  transform:rotate(-45deg);margin-left:6px;flex:none}
details.fcard[open]>summary::after{transform:rotate(45deg)}
details.fcard>summary{flex-wrap:wrap}
details.fcard .ttl{font-weight:650;min-width:0;flex:0 1 auto}details.fcard .cnt{margin-left:auto;font-size:13px;color:var(--ink-3);white-space:nowrap}
details.fcard .body{padding:0 14px 14px}
.why{color:var(--ink-2);margin:0 0 6px}.rec{margin:0 0 6px}.ctl{font-size:12px;color:var(--ink-3);margin:0 0 10px}
.rows td.id{white-space:nowrap;font-weight:600;width:160px}
.empty{padding:18px;text-align:center;color:var(--ink-3);background:var(--surface);border:1px dashed var(--line-2);border-radius:12px}

/* ---------- tabs, code, misc */
.tabs{display:flex;gap:4px;margin:0 0 12px;flex-wrap:wrap}
.tab{appearance:none;font:inherit;font-size:14px;padding:6px 14px;border-radius:9px;border:1px solid var(--line-2);
  background:var(--surface);color:var(--ink-2);cursor:pointer}
.tab[aria-selected="true"]{background:var(--brand-2);border-color:var(--brand-2);color:#fff;font-weight:600}
.codebox{position:relative}
pre{background:var(--code-bg);color:var(--code-ink);border-radius:12px;padding:18px;overflow:auto;font-size:12.5px;line-height:1.55;margin:0;max-height:620px}
.copy{position:absolute;top:10px;right:10px;appearance:none;font:inherit;font-size:12.5px;padding:4px 11px;border-radius:7px;
  border:1px solid rgba(255,255,255,.25);background:rgba(255,255,255,.08);color:#fff;cursor:pointer}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.delta-up{color:var(--good-ink);font-weight:650}.delta-down{color:var(--bad-ink);font-weight:650}
.toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:0 0 10px}
.toolbar label{font-size:13.5px;color:var(--ink-2);display:flex;gap:6px;align-items:center}
footer.foot{border-top:1px solid var(--line);padding-top:14px;color:var(--ink-3);font-size:12.5px;max-width:90ch}
footer.foot p{margin:4px 0}

/* ---------- simple pages (fleet dashboard, change report) */
.wrap{max-width:1200px;margin:0 auto;padding:28px 24px 64px}
header.top{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;padding-bottom:16px;margin-bottom:18px;
  border-bottom:1px solid var(--line)}
.kicker{font-size:13px;color:var(--ink-3);font-weight:600}
.meta{color:var(--ink-2);font-size:13.5px;margin-top:4px}
.wrap h2{margin:32px 0 12px}
.wrap>table,.wrap .two table{background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.kpis{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px;margin-top:14px}
.kpis>div{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 14px;border-top:4px solid var(--c,var(--line-2))}
.kpis .n{font-size:24px;font-weight:750}.kpis .l{font-size:12.5px;color:var(--ink-2)}
footer{color:var(--ink-3);font-size:12.5px}
.page-tools{display:flex;gap:8px}
.page-tools .tbtn{color:var(--ink-2);border-color:var(--line-2)}
.page-tools .tbtn:hover{background:var(--surface-3)}

/* ---------- palette picker */
.tsel{display:inline-flex;align-items:center;gap:7px;font-size:13px;color:var(--on-brand)}
.tsel .sw{display:inline-flex;gap:2px}.tsel .sw i{width:6px;height:14px;border-radius:2px;display:block}
.tsel select{appearance:none;-webkit-appearance:none;font:inherit;font-size:13px;color:inherit;background-color:transparent;
  border:1px solid rgba(255,255,255,.28);border-radius:8px;padding:5px 26px 5px 10px;cursor:pointer;
  background-image:linear-gradient(45deg,transparent 50%,currentColor 50%),linear-gradient(135deg,currentColor 50%,transparent 50%);
  background-position:calc(100% - 14px) 55%,calc(100% - 10px) 55%;background-size:4px 4px;background-repeat:no-repeat}
.tsel select:hover{background-color:rgba(255,255,255,.10)}
.tsel select option{color:#121826;background:#ffffff}
.page-tools .tsel{color:var(--ink-2)}.page-tools .tsel select{border-color:var(--line-2)}
.page-tools .tsel select:hover{background-color:var(--surface-3)}

/* ---------- key tiles (bento) */
.keygrid{display:grid;grid-template-columns:minmax(0,1.2fr) repeat(3,minmax(0,1fr));gap:14px}
.keygrid .key.grade{grid-row:span 2;flex-direction:column;align-items:stretch;justify-content:flex-start;gap:14px}
.key.grade .gtop{display:flex;align-items:center;gap:18px}
.key.grade .bars{gap:6px;flex:1;justify-content:space-evenly;border-top:1px solid var(--line);padding-top:10px}
.key.grade .bar{grid-template-columns:minmax(0,142px) minmax(0,1fr) 26px;font-size:13px;gap:8px}
.bar.dom{grid-template-columns:minmax(0,150px) minmax(0,1fr) 40px}.bar.dom .meter{margin:0}
.lcl{grid-template-columns:1fr;gap:4px;font-size:13px;margin:0 0 10px}
.key .big.sm{font-size:30px;letter-spacing:-.01em}
.key .row{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.key a.more{font-size:13px;margin-top:auto}
.meter{display:flex;height:9px;border-radius:9px;overflow:hidden;background:var(--surface-3);gap:2px;margin:4px 0 2px}
.meter span{display:block;height:100%}
.weak{font-size:13px;color:var(--ink-2)}

/* ---------- status pills (best-practice baseline) */
.pill.pass{background:var(--good-bg);--pc:var(--good)}
.pill.fail{background:var(--sev-high-bg);--pc:var(--sev-high)}
.pill.partial{background:var(--sev-medium-bg);--pc:var(--sev-medium)}
.pill.manual{background:color-mix(in srgb,var(--link) 14%,transparent);--pc:var(--link)}
.pill.na{background:var(--sev-info-bg);--pc:var(--sev-info);color:var(--ink-2)}
.pill.unknown{background:transparent;box-shadow:inset 0 0 0 1px var(--line-2);--pc:transparent;color:var(--ink-2)}
.pill.unknown::before{box-shadow:inset 0 0 0 1.5px var(--ink-3)}
table.bp td.st{white-space:nowrap;width:128px}
table.bp td.pr{font-weight:600;min-width:220px}
table.bp td.pr .src{display:block;font-weight:400;font-size:12px;color:var(--ink-3);margin-top:2px}
table.bp td.ev{color:var(--ink-2)}
table.bp tr.dom td{background:var(--surface-2);font-weight:650;color:var(--ink);font-size:12.5px;padding:7px 10px}
table.bp tr.dom td span{float:right;font-weight:500;color:var(--ink-3)}
table.bp td.lk a{display:inline-block;margin:0 6px 2px 0;font-size:12.5px}
.bpbar{display:flex;flex-wrap:wrap;align-items:center;gap:10px 18px;margin:0 0 14px;padding:12px 14px;background:var(--surface);
  border:1px solid var(--line);border-radius:12px}
.bpbar .meter{flex:1 1 260px;height:12px;margin:0}

/* ---------- effort tags, quick wins */
.eff{display:inline-block;font-size:11px;line-height:18px;padding:0 7px;border-radius:999px;border:1px solid var(--line-2);
  color:var(--ink-2);white-space:nowrap}
.eff.quick{border-color:var(--good);color:var(--good-ink)}
.eff.project{border-color:var(--sev-medium)}
ul.qw{list-style:none;margin:0 0 14px;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
ul.qw li{display:flex;align-items:center;gap:10px;background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--c);
  border-radius:10px;padding:9px 12px;font-size:14px;min-width:0}
ul.qw li .t{flex:1;min-width:0}ul.qw li .tg{font-size:12.5px;color:var(--ink-3);display:block}

/* ---------- firmware */
.fwgrid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px;margin-bottom:14px}
.lc{position:relative;margin:30px 6px 30px}
.lc .rail{display:flex;height:12px;border-radius:12px;overflow:hidden;background:var(--surface-3)}
.lc .rail span{display:block;height:100%}
.lc .tick{position:absolute;top:18px;transform:translateX(-50%);font-size:11.5px;color:var(--ink-3);white-space:nowrap;text-align:center;line-height:1.3}
.lc .tick.l{transform:none}.lc .tick.r{transform:translateX(-100%)}
.lc .today{position:absolute;top:-8px;width:3px;height:28px;border-radius:2px;background:var(--ink);transform:translateX(-1px)}
.lc .today b{position:absolute;bottom:30px;left:50%;transform:translateX(-50%);font-size:12px;white-space:nowrap;color:var(--ink)}
.kvs{display:grid;grid-template-columns:auto 1fr;gap:4px 14px;margin:0;font-size:14px}
.kvs dt{color:var(--ink-3)}.kvs dd{margin:0;font-weight:600}
tr.cur td{background:color-mix(in srgb,var(--link) 9%,transparent)}

/* ---------- responsive */
@media (max-width:1080px){
  .shell{grid-template-columns:minmax(0,1fr);gap:0;padding:0 16px}
  nav.side{position:sticky;top:50px;z-index:15;max-height:none;overflow-x:auto;padding:8px 0;margin:0 -16px;background:var(--bg);
    border-bottom:1px solid var(--line)}
  nav.side ol{display:flex;gap:4px;padding:0 16px;width:max-content}
  nav.side .sub,nav.side .grp{display:none}
  nav.side a{white-space:nowrap}
  nav.side a[aria-current="true"]{box-shadow:inset 0 -3px 0 var(--c,var(--brand-2))}
  .keyrow{grid-template-columns:1fr 1fr}.row2{grid-template-columns:1fr}
  .keygrid{grid-template-columns:1fr 1fr}.keygrid .key.grade{grid-row:auto;grid-column:1 / -1;flex-direction:row;align-items:center}
  .key.grade .bars{border-top:0;border-left:1px solid var(--line);padding:0 0 0 16px}
  .fwgrid{grid-template-columns:1fr}ul.qw{grid-template-columns:1fr}
  .wrap table{display:block;overflow-x:auto}
  .kpis{grid-template-columns:repeat(3,minmax(0,1fr))}
}
@media (max-width:640px){
  .topbar{padding:10px 16px;gap:10px}.topbar .who,.topbar .mark span,.topbar .tbtn span{display:none}
  .keyrow{grid-template-columns:1fr}.two{grid-template-columns:1fr}.keygrid{grid-template-columns:1fr}
  .topbar .gchip{display:none}.keygrid .key.grade{flex-direction:column;align-items:stretch}
  .key.grade .bars{border-left:0;border-top:1px solid var(--line);padding:10px 0 0}
  .keygrid .key.grade .letter{font-size:76px}.tsel .sw{display:none}
  .bar{grid-template-columns:110px minmax(0,1fr) 30px}.bar .n{display:none}
  .key.grade .letter{font-size:76px}
  .kpis{grid-template-columns:repeat(2,minmax(0,1fr))}
  ol.actions li{grid-template-columns:34px minmax(0,1fr)}ol.actions li>*{grid-column:2}
  ol.actions li::before{grid-row:span 4}ol.actions .go{grid-row:auto}
  header.top{flex-direction:column;align-items:flex-start}
  h1{font-size:28px}
}
@media print{
  body{background:#fff;font-size:12.5px}
  .topbar,nav.side,.filters,.copy,.tabs,.toolbar,.page-tools,.no-print{display:none!important}
  .shell{display:block;padding:0}main{padding:0}
  .tab-panel{display:block!important}
  details.fcard,.key,.panel,ol.actions li,.tw,ul.qw li,.lc{break-inside:avoid}
  .keygrid{grid-template-columns:repeat(3,minmax(0,1fr))}.keygrid .key.grade{grid-row:auto}
  pre{white-space:pre-wrap;max-height:none}
  a{color:inherit}
}
""")

# Applied before first paint so a saved theme or palette never flashes.
THEME_HEAD = ("<script>try{var d=document.documentElement,t=localStorage.getItem('rulescope-theme'),"
              "p=localStorage.getItem('rulescope-palette');if(t==='dark'||t==='light')d.setAttribute('data-theme',t);"
              "if(p&&/^[a-z]+$/.test(p))d.setAttribute('data-palette',p)}catch(e){}</script>")

THEME_BUTTON = ('<button class="tbtn" type="button" data-theme-toggle aria-label="Switch between light and dark theme">'
                '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                'aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>'
                '<span>Theme</span></button>')


def palette_select() -> str:
    opts = "".join(f'<option value="{k}">{_esc(v[0])}</option>' for k, v in PALETTES.items())
    swatch = "".join(f'<i style="background:var(--a-{a})"></i>' for a in _AREA_ORDER[:5])
    return (f'<label class="tsel" title="Color palette"><span class="sw" aria-hidden="true">{swatch}</span>'
            f'<select data-palette-select aria-label="Color palette">{opts}</select></label>')


CONTROLS = palette_select() + THEME_BUTTON


def html_open(palette: str = DEFAULT_PALETTE) -> str:
    """<html> start tag carrying the default palette chosen with --palette."""
    p = palette if palette in PALETTES else DEFAULT_PALETTE
    return f'<!doctype html><html lang="en" data-palette="{p}">'


THEME_JS = """<script>(function(){
var root=document.documentElement;
function isDark(){var t=root.getAttribute('data-theme');if(t)return t==='dark';
  return window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches}
document.querySelectorAll('[data-theme-toggle]').forEach(function(b){b.addEventListener('click',function(){
  var next=isDark()?'light':'dark';root.setAttribute('data-theme',next);
  try{localStorage.setItem('rulescope-theme',next)}catch(e){}})});
var sels=[].slice.call(document.querySelectorAll('[data-palette-select]'));
sels.forEach(function(s){s.value=root.getAttribute('data-palette')||'harbor';if(!s.value)s.value='harbor';
  s.addEventListener('change',function(){var v=s.value;root.setAttribute('data-palette',v);
    try{localStorage.setItem('rulescope-palette',v)}catch(e){}sels.forEach(function(o){o.value=v})})});
})();</script>"""

LOGO = ('<svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2 3.5 5.5v6.2c0 5 3.6 9.3 8.5 10.3 '
        '4.9-1 8.5-5.3 8.5-10.3V5.5z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>'
        '<path d="M7.5 12h9M7.5 8.5h9M7.5 15.5h5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>')
