# Contributing

Thanks for considering contributing! This project welcomes fixes, improvements, and new features.

## How to contribute
1. Fork the repository and create a branch for your change.
2. Make focused, well-scoped edits.
3. Add or update tests if behavior changes.
4. Ensure lint/build passes (see checks below).
5. Open a pull request with a clear description and screenshots if UI changes.

## Development setup

### Backend (FastAPI)
1. Create and activate a Python virtual environment (name it however you like).
2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Run the API:

```bash
python -m uvicorn backend.app:app --reload --port 8000
```

### Frontend (Next.js)
1. Install dependencies:

```bash
cd frontend
pnpm install
```

2. Start the dev server:

```bash
pnpm dev
```

## Environment variables
- Root .env: copy .env.example to .env and set GEMINI_API_KEY.
- frontend/.env.local: set NEXT_PUBLIC_API_URL (default http://localhost:8000).

## Checks

### Backend
- Run unit or script-level checks as needed (see scripts/).

### Frontend
- Lint:

```bash
cd frontend
pnpm lint
```

- Build:

```bash
cd frontend
pnpm build
```

## Code style
- Keep functions small and focused.
- Prefer clear names and explicit logic over clever shortcuts.
- Avoid large refactors in a single PR.

## Reporting issues
Please include:
- Steps to reproduce
- Expected vs actual behavior
- Logs or screenshots
- Environment details (OS, Python, Node versions)
