# Resume & JD Matcher – React UI

React + **Tailwind** + **shadcn-style** components (Button, Card, Input) and **Lucide** icons.

## JD upload

- **Paste** job description in the textarea, or  
- **Upload JD (PDF or .txt)** via the “Upload JD (PDF or .txt)” button, or  
- **Choose a saved JD** from the dropdown.

## Run

1. **Backend** (from project root):  
   `uvicorn app.main:app --reload`

2. **Frontend** (from this folder):  
   `npm install && npm run dev`

3. Open **http://localhost:5173**. The Vite dev server proxies `/api` to the backend (see `vite.config.ts`).

## Build

- `npm run build` → output in `dist/`.  
- To serve the built app from FastAPI, set Vite `base: '/app'`, build, then mount `frontend/dist` at `/app` in the FastAPI app.
