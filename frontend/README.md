# Banana Blitz frontend

React + TypeScript + Vite client for Banana Blitz.

Look at the project root [README](../README.md) for setup and architecture.

## Commands

```bash
npm install
npm run dev      # http://localhost:5173, proxies /api to Django on :8000
npm run lint     # Oxlint
npm run build    # TypeScript + Vite production build
npm run preview  # serve the production build
```

The API base is `/api` by default. Set `VITE_API_URL` when the frontend is deployed on another origin.
