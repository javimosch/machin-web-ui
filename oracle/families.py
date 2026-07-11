"""Shared class-list definitions: which classes are STATIC (finite set, table
generated from the oracle by gen_static.py) and which corpus entries exercise
the engine's PARAMETRIC code paths (checked by check.py)."""

SPACING = "0 px 0.5 1 1.5 2 2.5 3 3.5 4 5 6 7 8 9 10 11 12 14 16 20 24 28 32 36 40 44 48 52 56 60 64 72 80 96".split()
HUES = "slate gray zinc neutral stone red orange amber yellow lime green emerald teal cyan sky blue indigo violet purple fuchsia pink rose".split()
SHADES = "50 100 200 300 400 500 600 700 800 900 950".split()
INSET_FR = "1/2 1/3 2/3 1/4 2/4 3/4".split()
TRANSLATE_FR = "1/2 1/3 2/3 1/4 2/4 3/4".split()


def static_gen():
    """Finite-set classes whose (selector-suffix, declarations) are generated
    verbatim from the oracle into src/tw_static_gen.src."""
    c = []
    c += "static fixed absolute relative sticky".split()
    c += "visible invisible collapse".split()
    c += [f"z-{z}" for z in "0 10 20 30 40 50 auto".split()] + [f"-z-{z}" for z in "10 20 30 40 50".split()]
    c += [f"order-{o}" for o in list(range(1, 13)) + ["first", "last", "none"]]
    c += [f"overflow-{v}" for v in "auto hidden clip visible scroll".split()]
    c += [f"overflow-{a}-{v}" for a in "xy" for v in "auto hidden clip visible scroll".split()]
    c += [f"overscroll-{v}" for v in "auto contain none".split()]
    c += [f"overscroll-{a}-{v}" for a in "xy" for v in "auto contain none".split()]
    c += "float-right float-left float-none clear-left clear-right clear-both clear-none".split()
    c += "box-border box-content".split()
    c += [f"object-{v}" for v in "contain cover fill none scale-down bottom center left left-bottom left-top right right-bottom right-top top".split()]
    c += [f"aspect-{v}" for v in "auto square video".split()]
    c += [f"min-w-{v}" for v in "0 full min max fit".split()]
    c += [f"max-w-{v}" for v in "0 none xs sm md lg xl 2xl 3xl 4xl 5xl 6xl 7xl full min max fit prose screen-sm screen-md screen-lg screen-xl screen-2xl".split()]
    c += [f"min-h-{v}" for v in "0 full screen min max fit".split()]
    c += [f"max-h-{v}" for v in "none full screen min max fit".split()]
    c += [f"cursor-{v}" for v in ("auto default pointer wait text move help not-allowed none context-menu progress cell "
                                  "crosshair vertical-text alias copy no-drop grab grabbing all-scroll col-resize row-resize "
                                  "n-resize e-resize s-resize w-resize ne-resize nw-resize se-resize sw-resize ew-resize "
                                  "ns-resize nesw-resize nwse-resize zoom-in zoom-out").split()]
    c += [f"select-{v}" for v in "none text all auto".split()]
    c += "pointer-events-none pointer-events-auto".split()
    c += "resize-none resize-y resize-x resize".split()
    c += "scroll-auto scroll-smooth appearance-none sr-only not-sr-only".split()
    c += ["outline-none", "outline", "outline-dashed", "outline-dotted", "outline-double"]
    c += [f"outline-{n}" for n in "0 1 2 4 8".split()]
    c += [f"outline-offset-{n}" for n in "0 1 2 4 8".split()]
    c += ["ring", "ring-inset"] + [f"ring-{n}" for n in "0 1 2 4 8".split()]
    c += [f"ring-offset-{n}" for n in "0 1 2 4 8".split()]
    c += [f"border-{s}" for s in "solid dashed dotted double hidden none".split()]
    c += ["divide-x", "divide-y", "divide-x-reverse", "divide-y-reverse"]
    c += [f"divide-{a}-{n}" for a in "xy" for n in "0 2 4 8".split()]
    c += [f"divide-{s}" for s in "solid dashed dotted double none".split()]
    c += "font-sans font-serif font-mono".split()
    c += "underline overline line-through no-underline".split()
    c += [f"decoration-{v}" for v in "solid double dotted dashed wavy 0 1 2 4 8 auto from-font".split()]
    c += [f"underline-offset-{v}" for v in "auto 0 1 2 4 8".split()]
    c += "uppercase lowercase capitalize normal-case".split()
    c += "truncate text-ellipsis text-clip break-normal break-words break-all".split()
    c += [f"whitespace-{v}" for v in "normal nowrap pre pre-line pre-wrap break-spaces".split()]
    c += [f"list-{v}" for v in "none disc decimal inside outside".split()]
    c += [f"align-{v}" for v in "baseline top middle bottom text-top text-bottom sub super".split()]
    c += [f"opacity-{n}" for n in range(0, 101, 5)]
    c += ["transition"] + [f"transition-{v}" for v in "none all colors opacity shadow transform".split()]
    c += [f"duration-{n}" for n in "75 100 150 200 300 500 700 1000".split()]
    c += [f"ease-{v}" for v in "linear in out in-out".split()]
    c += [f"delay-{n}" for n in "75 100 150 200 300 500 700 1000".split()]
    c += [f"animate-{v}" for v in "none spin ping pulse bounce".split()]
    c += "transform transform-gpu transform-none".split()
    c += [f"origin-{v}" for v in "center top top-right right bottom-right bottom bottom-left left top-left".split()]
    rot = "0 1 2 3 6 12 45 90 180".split()
    c += [f"rotate-{n}" for n in rot] + [f"-rotate-{n}" for n in rot if n != "0"]
    sc = "0 50 75 90 95 100 105 110 125 150".split()
    c += [f"scale-{n}" for n in sc] + [f"scale-x-{n}" for n in sc] + [f"scale-y-{n}" for n in sc]
    sk = "0 1 2 3 6 12".split()
    for a in "xy":
        c += [f"skew-{a}-{n}" for n in sk] + [f"-skew-{a}-{n}" for n in sk if n != "0"]
    c += ["bg-none"] + [f"bg-gradient-to-{d}" for d in "t tr r br b bl l tl".split()]
    c += [f"{p}-{v}" for p in ("from", "via", "to") for v in "transparent current black white inherit".split()]
    c += [f"bg-{v}" for v in "auto cover contain fixed local scroll repeat no-repeat repeat-x repeat-y repeat-round repeat-space".split()]
    c += [f"bg-{v}" for v in "bottom center left left-bottom left-top right right-bottom right-top top".split()]
    c += [f"bg-clip-{v}" for v in "border padding content text".split()]
    c += [f"bg-origin-{v}" for v in "border padding content".split()]
    c += [f"grid-rows-{n}" for n in list(range(1, 7)) + ["none"]]
    c += [f"row-span-{n}" for n in list(range(1, 7)) + ["full"]] + ["row-auto"]
    c += [f"grid-flow-{v}" for v in "row col dense row-dense col-dense".split()]
    c += [f"content-{v}" for v in "normal center start end between around evenly baseline stretch".split()]
    c += [f"self-{v}" for v in "auto start end center stretch baseline".split()]
    c += [f"justify-items-{v}" for v in "start end center stretch".split()]
    c += [f"justify-self-{v}" for v in "auto start end center stretch".split()]
    c += [f"place-content-{v}" for v in "center start end between around evenly baseline stretch".split()]
    c += [f"place-items-{v}" for v in "start end center baseline stretch".split()]
    c += [f"place-self-{v}" for v in "auto start end center stretch".split()]
    return c


def param_corpus():
    """Classes that exercise the engine's parametric code paths."""
    c = []
    # inset family: spacing + auto/full/fractions + negatives
    heads = "inset inset-x inset-y top right bottom left".split()
    for h in heads:
        c += [f"{h}-{s}" for s in SPACING] + [f"{h}-auto", f"{h}-full"]
        c += [f"{h}-{f}" for f in INSET_FR]
        c += [f"-{h}-{s}" for s in SPACING if s != "0"] + [f"-{h}-full"]
        c += [f"-{h}-{f}" for f in INSET_FR]
    # negative margins
    for h in "m mx my mt mr mb ml".split():
        c += [f"-{h}-{s}" for s in SPACING]
    # min/max sizing over spacing (v3.4 addition)
    for h in ("max-h", "min-w", "max-w", "min-h"):
        c += [f"{h}-{s}" for s in SPACING]
    # translate (parametric: spacing + fractions + full + negatives)
    for a in "xy":
        c += [f"translate-{a}-{s}" for s in SPACING] + [f"translate-{a}-full"]
        c += [f"translate-{a}-{f}" for f in TRANSLATE_FR]
        c += [f"-translate-{a}-{s}" for s in SPACING if s != "0"] + [f"-translate-{a}-full"]
        c += [f"-translate-{a}-{f}" for f in TRANSLATE_FR]
    # space between
    for a in "xy":
        c += [f"space-{a}-{s}" for s in SPACING]
        c += [f"-space-{a}-{s}" for s in SPACING if s != "0"]
    # palette-parametric color families (every hue at one shade + a few depth probes)
    probe_colors = [f"{h}-500" for h in HUES] + ["stone-50", "stone-950", "red-900"]
    for col in probe_colors:
        c += [f"ring-{col}", f"ring-offset-{col}", f"outline-{col}", f"divide-{col}",
              f"from-{col}", f"via-{col}", f"to-{col}", f"decoration-{col}"]
    # color opacity modifiers
    for n in ("0", "5", "10", "25", "40", "50", "75", "90", "95", "100"):
        c += [f"bg-red-500/{n}", f"text-stone-900/{n}", f"border-blue-500/{n}"]
    c += ["bg-white/50", "bg-black/5", "text-white/75"]
    c += ["ring-stone-950/10", "ring-red-500/50", "divide-stone-200/50", "divide-blue-500/5"]
    # per-side border colors
    for side in "t r b l x y".split():
        c += [f"border-{side}-green-600", f"border-{side}-stone-200/50", f"border-{side}-transparent"]
    c += [f"border-l-{h}-500" for h in HUES]
    # arbitrary values
    c += ["w-[13px]", "h-[45%]", "min-w-[13px]", "max-w-[65ch]", "min-h-[7rem]", "max-h-[13px]",
          "p-[2.5rem]", "px-[3px]", "mt-[7px]", "m-[1.25em]", "gap-[7px]", "gap-x-[3px]", "gap-y-[9px]",
          "top-[117px]", "inset-[4px]", "inset-x-[2px]", "left-[5%]", "z-[99]", "rounded-[11px]",
          "tracking-[0.2em]", "leading-[3.2]", "text-[14px]", "text-[2.75rem]",
          "w-[calc(100%_-_2rem)]", "h-[calc(100vh_-_4rem)]",
          "bg-[#0af]", "bg-[#bada55]", "text-[#0af]", "border-[#12345f]",
          "bg-[rgb(1,2,3)]", "text-[rgb(250,250,249)]",
          "border-[3px]", "border-[0.5px]"]
    # group/peer variants
    for b in ("flex", "bg-stone-700", "underline", "opacity-50"):
        c += [f"group-hover:{b}", f"group-focus:{b}",
              f"peer-hover:{b}", f"peer-focus:{b}", f"peer-checked:{b}", f"peer-disabled:{b}"]
    # stacking with the new variants
    c += ["md:group-hover:bg-stone-700", "dark:peer-checked:underline",
          "hover:ring-2", "focus:ring-blue-500", "md:divide-y", "dark:divide-stone-700",
          "hover:-translate-y-1", "md:opacity-75", "hover:bg-red-500/90", "md:w-[13px]",
          "dark:bg-[#0af]", "lg:-mt-8", "sm:transition", "md:animate-spin"]
    return c
