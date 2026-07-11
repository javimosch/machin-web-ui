#!/usr/bin/env python3
"""Differential test: our MFL tw engine vs the real tailwindcss standalone binary.

Generates a corpus of classes across the spike's utility families, runs both
engines, normalizes each stylesheet into a set of
(media-conditions, selector, declarations) triples, and diffs them.
"""
import re, subprocess, sys, itertools, pathlib

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
    """proper recursive-descent parse (handles nested @media)."""
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

def main():
    classes = corpus()
    (HERE / "classes.txt").write_text("\n".join(classes) + "\n")
    # oracle
    (HERE / "content.html").write_text('<i class="' + " ".join(classes) + '"></i>')
    subprocess.run([str(ROOT / "bin/tailwindcss"), "-c", str(HERE / "tailwind.config.js"),
                    "-i", str(HERE / "input.css"), "-o", str(HERE / "oracle.css")],
                   cwd=HERE, check=True, capture_output=True)
    oracle = normalize2((HERE / "oracle.css").read_text())
    # ours
    r = subprocess.run([str(ROOT / "twgen")], input="\n".join(classes),
                       capture_output=True, text=True, check=True)
    (HERE / "ours.css").write_text(r.stdout)
    unknown = re.search(r"/\* tw-unknown:(.*?)\*/", r.stdout, flags=re.S)
    ours = normalize2(r.stdout)

    missing = oracle - ours     # oracle emits, we don't (or differ)
    extra = ours - oracle       # we emit, oracle doesn't (or differ)
    print(f"corpus: {len(classes)} classes | oracle rules: {len(oracle)} | ours: {len(ours)}")
    if unknown:
        toks = unknown.group(1).split()
        print(f"our engine flagged {len(toks)} unknown: {' '.join(toks[:20])}{' ...' if len(toks) > 20 else ''}")
    def show(name, s):
        print(f"\n== {name}: {len(s)} ==")
        for media, sel, decls in sorted(s, key=lambda x: x[1])[:25]:
            m = f" @media[{', '.join(sorted(media))}]" if media else ""
            print(f"  {sel}{m}\n    {'; '.join(sorted(decls))}")
    if missing: show("ORACLE-ONLY (we're wrong/missing)", missing)
    if extra: show("OURS-ONLY (we emit, oracle doesn't)", extra)
    if not missing and not extra:
        print("\nPASS: rule-for-rule identical with tailwindcss v3.4.17")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())
