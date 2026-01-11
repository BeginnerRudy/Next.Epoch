# Next.Epoch Web UI

Modern web interface for the Next.Epoch AI Frontier Intelligence Platform.

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **React Query** - Data fetching and caching
- **Lucide React** - Icon library

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running (optional - demo mode available)

### Installation

```bash
cd web
npm install
```

### Development

```bash
npm run dev
```

The app will be available at http://localhost:3000

### Production Build

```bash
npm run build
npm start
```

## Features

### Dashboard
- Overview stats (papers today, trending repos, high impact items)
- Top content list sorted by frontier score
- Quick refresh functionality

### Search
- Full-text search across papers and repositories
- Filter by source (arXiv, GitHub)
- Filter by type (papers, repositories)
- Real-time search with debouncing

### Content Detail
- Full item information with score breakdown
- AI-generated summary
- Evidence signals explaining the score
- Links to source and PDF (for papers)

### Digests
- List of daily/weekly/field digests
- Digest detail with sections
- Summarized highlights

## Project Structure

```
web/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── page.tsx           # Dashboard
│   │   ├── search/            # Search page
│   │   ├── content/           # Content pages
│   │   │   ├── page.tsx       # Content list
│   │   │   └── [id]/          # Content detail
│   │   └── digests/           # Digest pages
│   │       ├── page.tsx       # Digest list
│   │       └── [id]/          # Digest detail
│   ├── components/
│   │   ├── layout/            # Header, Sidebar
│   │   ├── content/           # ContentCard, ContentList
│   │   └── ui/                # Buttons, Badges
│   ├── lib/
│   │   ├── api.ts             # API client
│   │   └── utils.ts           # Utility functions
│   └── types/
│       └── index.ts           # TypeScript types
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── next.config.js
```

## API Integration

The web UI connects to the backend API via a proxy configured in `next.config.js`. The API client in `src/lib/api.ts` handles all requests.

When the backend is unavailable, the app shows demo data to allow UI development and testing.

## Demo Mode

If the backend API is not running, the app will display mock data and show a notice. This allows you to explore the UI without the full backend setup.

To run with the backend:

```bash
# Terminal 1 - Start backend
cd ..
uvicorn next_epoch.api.main:app --reload

# Terminal 2 - Start frontend
cd web
npm run dev
```
