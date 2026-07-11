#!/usr/bin/env python3
"""Differential test: our MFL tw engine vs the real tailwindcss standalone binary.

Generates a corpus of classes across the spike's utility families, runs both
engines, normalizes each stylesheet into a set of
(media-conditions, selector, declarations) triples, and diffs them.
"""
import re, subprocess, sys, itertools, pathlib
from families import static_gen, param_corpus

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent

# ---------- corpus ----------
def corpus():
    cls = []
    spacing = "0 px 0.5 1 1.5 2 2.5 3 3.5 4 5 6 7 8 9 10 11 12 14 16 20 24 28 32 36 40 44 48 52 56 60 64 72 80 96".split()
    hues = "slate gray zinc neutral stone red orange amber yellow lime green emerald teal cyan sky blue indigo violet purple fuchsia pink rose".split()
    shades = "50 100 200 300 400 500 600 700 800 900 950".split()

    cls += "block inline-block inline flex inline-flex grid inline-grid hidden".split()
    for h in "p px py pt pr pb pl m mx my mt mr mb ml".split():
        for s in spacing: cls.append(f"{h}-{s}")
    cls += ["m-auto", "mx-auto", "my-auto", "mt-auto", "mb-auto", "ml-auto", "mr-auto"]
    fr_w = "1/2 1/3 2/3 1/4 2/4 3/4 1/5 2/5 3/5 4/5 1/6 2/6 3/6 4/6 5/6 1/12 2/12 3/12 4/12 5/12 6/12 7/12 8/12 9/12 10/12 11/12".split()
    fr_h = "1/2 1/3 2/3 1/4 2/4 3/4 1/5 2/5 3/5 4/5 1/6 2/6 3/6 4/6 5/6".split()
    for s in spacing: cls += [f"w-{s}", f"h-{s}"]
    cls += [f"w-{f}" for f in fr_w] + [f"h-{f}" for f in fr_h]
    cls += "w-auto w-full w-screen w-min w-max w-fit h-auto h-full h-screen h-min h-max h-fit".split()
    # colors: bg gets the full palette; text/border get every hue at 3 shades + specials
    for h in hues:
        for s in shades: cls.append(f"bg-{h}-{s}")
        for s in ("200", "500", "900"): cls += [f"text-{h}-{s}", f"border-{h}-{s}"]
    for p in ("bg", "text", "border"):
        cls += [f"{p}-black", f"{p}-white", f"{p}-transparent", f"{p}-current", f"{p}-inherit"]
    cls += ["border", "border-0", "border-2", "border-4", "border-8"]
    for side in "x y t r b l".split():
        cls += [f"border-{side}"] + [f"border-{side}-{n}" for n in "0 2 4 8".split()]
    cls += [f"rounded{s}" for s in ["-none", "-sm", "", "-md", "-lg", "-xl", "-2xl", "-3xl", "-full"]]
    cls += [f"text-{s}" for s in "xs sm base lg xl 2xl 3xl 4xl 5xl 6xl 7xl 8xl 9xl left center right justify".split()]
    cls += [f"font-{w}" for w in "thin extralight light normal medium semibold bold extrabold black".split()]
    cls += ["italic", "not-italic"]
    cls += [f"tracking-{t}" for t in "tighter tight normal wide wider widest".split()]
    cls += [f"leading-{t}" for t in "none tight snug normal relaxed loose 3 4 5 6 7 8 9 10".split()]
    cls += "flex-row flex-row-reverse flex-col flex-col-reverse flex-wrap flex-wrap-reverse flex-nowrap flex-1 flex-auto flex-initial flex-none grow grow-0 shrink shrink-0".split()
    cls += [f"items-{a}" for a in "start end center baseline stretch".split()]
    cls += [f"justify-{a}" for a in "start end center between around evenly".split()]
    for s in spacing: cls += [f"gap-{s}", f"gap-x-{s}", f"gap-y-{s}"]
    cls += [f"grid-cols-{n}" for n in range(1, 13)] + ["grid-cols-none"]
    cls += [f"col-span-{n}" for n in range(1, 13)] + ["col-span-full", "col-auto"]
    cls += [f"shadow{s}" for s in ["-sm", "", "-md", "-lg", "-xl", "-2xl", "-inner", "-none"]]
    # variants: cross a representative base set with every variant + stacks
    bases = ["bg-stone-700", "px-4", "flex", "text-sm", "shadow-md", "text-red-500",
             "border-stone-200", "rounded-lg", "w-full", "font-medium"]
    variants = ["hover", "focus", "active", "disabled", "visited", "focus-within",
                "focus-visible", "dark", "sm", "md", "lg", "xl", "2xl"]
    for v, b in itertools.product(variants, bases): cls.append(f"{v}:{b}")
    stacks = ["md:hover", "dark:hover", "md:dark", "lg:focus", "2xl:dark:hover", "sm:focus-visible"]
    for st, b in itertools.product(stacks, bases): cls.append(f"{st}:{b}")
    cls += static_gen() + param_corpus()
    return sorted(set(cls))

# ---------- css normalization ----------
def normalize(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    rules, media_stack, out = [], [], set()
    i, n = 0, len(css)
    sel = ""
    buf = ""
    while i < n:
        c = css[i]
        if c == "{":
            head = buf.strip(); buf = ""
            if head.startswith("@media"):
                media_stack.append(head[len("@media"):].strip())
                sel = None
            else:
                sel = head
        elif c == "}":
            if sel is not None and sel != "":
                decls = frozenset(d.strip() for d in buf.split(";") if d.strip())
                out.add((frozenset(media_stack), sel, decls))
                sel = ""
            elif media_stack and not buf.strip() and sel in ("", None):
                media_stack.pop()
            buf = ""
            if sel is None: sel = ""
        else:
            buf += c
        i += 1
    return out

def normalize2(css):
    """proper recursive-descent parse (handles nested @media and @keyframes)."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out = set()
    def parse(s, i, media):
        buf = ""
        while i < len(s):
            c = s[i]
            if c == "{":
                head = buf.strip(); buf = ""
                if head.startswith("@media"):
                    i = parse(s, i + 1, media + [head[len("@media"):].strip()])
                elif head.startswith("@keyframes"):
                    depth, j = 1, i + 1
                    while depth:
                        if s[j] == "{": depth += 1
                        elif s[j] == "}": depth -= 1
                        j += 1
                    body = " ".join(s[i+1:j-1].split())
                    out.add((frozenset(media), head, frozenset([body])))
                    i = j - 1
                else:
                    j = s.index("}", i + 1)
                    decls = frozenset(d.strip() for d in s[i+1:j].split(";") if d.strip())
                    out.add((frozenset(media), head, decls))
                    i = j
            elif c == "}":
                return i
            else:
                buf += c
            i += 1
        return i
    parse(css, 0, [])
    return out

def run_oracle(content_path, config="tailwind.config.js", input_css="input.css", out="oracle.css"):
    subprocess.run([str(ROOT / "bin/tailwindcss"), "-c", config, "-i", input_css, "-o", out],
                   cwd=HERE, check=True, capture_output=True)
    return (HERE / out).read_text()

def show(name, s):
    print(f"\n== {name}: {len(s)} ==")
    for media, sel, decls in sorted(s, key=lambda x: x[1])[:25]:
        m = f" @media[{', '.join(sorted(media))}]" if media else ""
        print(f"  {sel}{m}\n    {'; '.join(sorted(decls))}")

def diff(label, oracle, ours):
    missing, extra = oracle - ours, ours - oracle
    print(f"{label}: oracle rules: {len(oracle)} | ours: {len(ours)}")
    if missing: show(f"{label} ORACLE-ONLY (we're wrong/missing)", missing)
    if extra: show(f"{label} OURS-ONLY (we emit, oracle doesn't)", extra)
    return not missing and not extra

def main():
    binary = ROOT / "machin-web-ui"
    ok = True

    # 1. corpus: explicit class list, every family x variant
    classes = corpus()
    (HERE / "classes.txt").write_text("\n".join(classes) + "\n")
    (HERE / "content.html").write_text('<i class="' + " ".join(classes) + '"></i>')
    oracle = normalize2(run_oracle("content.html"))
    r = subprocess.run([str(binary), "css", "--no-preflight", "-"], input="\n".join(classes),
                       capture_output=True, text=True, check=True)
    (HERE / "ours.css").write_text(r.stdout)
    unknown = re.search(r"/\* tw-unknown:(.*?)\*/", r.stdout, flags=re.S)
    if unknown:
        toks = unknown.group(1).split()
        print(f"our engine flagged {len(toks)} unknown: {' '.join(toks[:20])}{' ...' if len(toks) > 20 else ''}")
    ok &= diff(f"corpus ({len(classes)} classes)", oracle, normalize2(r.stdout))

    # 2. scanner: both engines scan the same MFL fixture file
    (HERE / "tailwind.fixture.config.js").write_text(
        'module.exports = { content: ["./fixture/*.src"], corePlugins: { preflight: false } }\n')
    oracle_scan = normalize2(run_oracle(None, config="tailwind.fixture.config.js", out="oracle_scan.css"))
    r = subprocess.run([str(binary), "css", "--no-preflight", str(HERE / "fixture")],
                       capture_output=True, text=True, check=True)
    ok &= diff("scanner (oracle/fixture)", oracle_scan, normalize2(r.stdout))

    # 3. cascade order: for same-property conflicts, the relative rule order
    #    must match the oracle (set-comparison can't see this)
    pairs = [("border-stone-200", "border-l-green-600"), ("border-x-red-500", "border-t-red-500"),
             ("m-4", "mt-2"), ("px-4", "pl-2"), ("my-2", "mb-8"),
             ("inset-0", "top-4"), ("inset-0", "inset-y-2"), ("gap-2", "gap-x-4"),
             ("overflow-hidden", "overflow-y-scroll")]
    order_ok = True
    for a, b in pairs:
        (HERE / "orderfix.src").write_text(f'func v() (h) {{ h = "{a} {b}" }}\n')
        (HERE / "tailwind.order.config.js").write_text(
            'module.exports = { content: ["./orderfix.src"], corePlugins: { preflight: false } }\n')
        ocss = run_oracle(None, config="tailwind.order.config.js", out="oracle_order.css")
        r = subprocess.run([str(binary), "css", "--no-preflight", str(HERE / "orderfix.src")],
                           capture_output=True, text=True, check=True)
        def pos(css, cls):
            i = css.find("." + cls.replace(":", "\\:") + " ")
            return i if i >= 0 else css.find("." + cls)
        o_first = pos(ocss, a) < pos(ocss, b)
        u_first = pos(r.stdout, a) < pos(r.stdout, b)
        if o_first != u_first:
            print(f"ORDER MISMATCH for ({a}, {b}): oracle {'a<b' if o_first else 'b<a'}, ours {'a<b' if u_first else 'b<a'}")
            order_ok = False
    if order_ok:
        print(f"cascade order: {len(pairs)} conflict pairs match the oracle")
    ok &= order_ok

    # 4. preflight: our embedded @tailwind base == the oracle's, byte-identical
    oracle_base = run_oracle(None, config="tailwind.preflight.config.js", input_css="base.css",
                             out="oracle_base.css")
    r = subprocess.run([str(binary), "css", "-"], input="", capture_output=True, text=True, check=True)
    if r.stdout == oracle_base:
        print("preflight: byte-identical with @tailwind base")
    else:
        print(f"preflight: MISMATCH (ours {len(r.stdout)}B vs oracle {len(oracle_base)}B)")
        ok = False

    if ok:
        print("\nPASS: corpus + scanner + preflight identical with tailwindcss v3.4.17")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())
