# BloodLens 2.0

Production-grade AI blood test interpreter with a Flask backend and React + Tailwind frontend.

Key features:
- Validated inputs (Pydantic) and robust error handling
- Biomarker classification with ranges, units, and descriptions
- Biological age estimation from deviations against optimal ranges
- AI insights via Gemini (structured JSON → sanitized markdown)
- Rate limiting and CORS
- Modern, responsive dashboard UI with loading states and dynamic advice cards

## Updated Structure
```
app.py                         # Thin runner -> backend app factory
backend/
  __init__.py                  # create_app, logging, blueprints
  config.py                    # env + app settings
  extensions.py                # limiter, CORS
  wsgi.py                      # standalone runner
  routes/
    api.py                     # /api/results, /api/advice/<type>
    pages.py                   # serves frontend SPA (/) and /results
  schemas/
    models.py                  # Pydantic models
  services/
    analysis_service.py        # biomarker analysis + biological age
    ai_service.py              # Gemini integration (JSON sections)
  utils/
    biological_age.py          # refined biological age calculation
    reference_data.py          # biomarker ranges/units/desc
frontend/
  package.json                 # vite + react + tailwind
  index.html
  tailwind.config.js
  postcss.config.js
  vite.config.ts
  tsconfig.json
  src/
    main.tsx, App.tsx
    styles/index.css
    api/client.ts
    pages/Home.tsx, Results.tsx
    components/* (AgeGauge, BiomarkerGrid, AdvicePanel)
requirements.v2.txt            # Backend dependencies (safe encoding)
.env.example                   # Copy to .env and fill
```

## Backend Setup
1) Create and fill `.env`:
```
cp .env.example .env
# set GEMINI_API_KEY=...
```

2) Install deps (Windows PowerShell shown):
```
pip install -r requirements.v2.txt
```

3) Run the API:
```
python app.py
# health check → http://localhost:5000/health
```

## Frontend Setup
1) Install deps:
```
cd frontend
npm install
```

2) Start dev server (proxy to Flask /api):
```
npm run dev
```

3) Production build (served by Flask from frontend/dist):
```
npm run build
# restart Flask, then open http://localhost:5000/
```

## API
- POST `/api/results` → full JSON report (biological age, biomarker grid, health score, AI sections)
- POST `/api/advice/<type>` → one section (overall_analysis | meal_plan | exercise_plan | supplement_advice | risk_assessment)

## Notes
- If `GEMINI_API_KEY` is missing, AI sections are disabled (analysis still works).
- The legacy Jinja templates and utils remain unused in v2; React SPA is the default UI.

