# Frontend — Mind Map Generator

React 18 SPA (Create React App) that lets the user submit a PDF, audio file, or text prompt, displays the PDF inline, renders the LLM-generated mind map with [Markmap](https://markmap.js.org/), and exports it as PNG.

---

## Run

```bash
npm install
npm start        # http://localhost:3000
```

Assumes the backend is running at `http://localhost:8000`. The URL is hard-coded in `src/App.js` — see [Configuration](#configuration) below.

---

## Scripts

| Command | Effect |
| --- | --- |
| `npm start` | Dev server with hot reload |
| `npm run build` | Optimized bundle in `build/` |
| `npm test` | Jest runner (`*.test.js` files) |
| `npm run eject` | Irreversible CRA operation (avoid) |

---

## Structure

```
frontend/
├── public/
├── src/
│   ├── App.js         # Main app: layout, state, /process-file fetch
│   ├── App.css
│   ├── index.js       # Entry point
│   └── index.css
└── package.json
```

For now the whole UI lives in `App.js` (~390 lines). Splitting it into components (e.g. `PromptBar`, `ModelSelector`, `MindMapView`) is planned in `TODO.md` Phase 3.

---

## Key dependencies

| Package | Purpose |
| --- | --- |
| `@mui/material` v6, `@mui/icons-material` | UI (buttons, tabs, inputs, tooltips) |
| `markmap-lib`, `markmap-view` | Turn markdown into an SVG mind map |
| `@react-pdf-viewer/*` | Embedded PDF viewer (toolbar, thumbnails, search, zoom) |
| `axios` | HTTP calls to the backend |
| `html2canvas` | Export the mind map as PNG |

---

## Configuration

The backend endpoint is currently hard-coded in `src/App.js`:

```js
await axios.post("http://localhost:8000/process-file", formData);
```

For production, switch to a `REACT_APP_API_URL` env var (CRA only injects variables with that prefix). Migration tracked in `TODO.md` Phase 1.

---

## Flow

1. User picks a model and submits a PDF, audio, or prompt.
2. `handleSubmit` (in `App.js`) builds a `FormData` and calls `POST /process-file`.
3. Backend returns `{ markdown }`.
4. A `useEffect` converts the markdown with `markmap-lib` and renders the SVG into `svgRef`.
5. The download button uses `html2canvas` to export the SVG + metadata (model, date/time) as PNG.

---

## Known limitations

- No visible error feedback (only `console.error`) — see `TODO.md` Phase 3.
- No client-side validation of file size/type before submitting.
- The "Model Summary" tab receives the field but the backend doesn't populate it yet.
- No tests beyond the empty CRA-generated `App.test.js`.
- No mobile/responsive support — the PDF viewer and mind map assume a wide screen.

---

## Accessibility

Known gaps: icon-only buttons without `aria-label`, contrast on active tabs, keyboard navigation across tabs. Tracked in `TODO.md` Phase 3.
