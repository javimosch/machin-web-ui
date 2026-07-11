# machin-web-ui starter

An **isomorphic machin app**: one native binary that is a CLI, an HTTP server,
a JSON API, and serves its own reactive WebAssembly UI — styled by
machin-web-ui's built-in Tailwind engine. No Node, no bundler, no
`node_modules`.

## Layout

```
src/models.src    the SHARED isomorphic view (app_view) — server + client
src/server.src    CLI flags, SSR page, /app.wasm, /api/* routes
src/client.src    reactive wasm client: signals, hydration, exports
components/       machin-web-ui components you OWN (added via `add`, edit freely)
web/host.js       generic JS host (~30 lines, app-agnostic)
build.sh          css scan -> embed assets -> wasm client -> native server
```

## Build & run

```sh
./build.sh        # needs machin v0.107+, zig, machin-web-ui
./app             # http://localhost:48100
```

## How it works

- **One view, both sides.** `app_view()` in `models.src` renders the page.
  The server calls it with plain SSR fragments (`<span data-s="count">0</span>`);
  the client calls it with `slot("count", ...)` which emits the identical span
  and queues its reactive binding. `hydrate()` then attaches bindings to the
  server's DOM — no re-render, no flash.
- **Clicks.** `<button data-action="bump">` → the host calls the wasm export
  `bump`. Add behavior by adding an `export func` and a `data-action`.
- **Styling.** Write Tailwind classes in any `.src`; `build.sh` regenerates
  `web/tw.css` via `machin-web-ui css`. Check a class with
  `machin-web-ui check <class>`; see the implemented surface with
  `machin-web-ui coverage`.
- **More components.** `machin-web-ui list` shows the registry;
  `machin-web-ui add dialog table tabs` vendors their source into
  `components/` — you own it, edit it.
