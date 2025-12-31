# Movie Recommendation Frontend

A modern Next.js frontend for the AI-powered movie recommendation system with RAG integration.

## Features

- 🎯 **Personalized Recommendations**: Get movie suggestions based on your preferences
- 🎨 **Genre Selection**: Choose your favorite genres with preference weights
- 💬 **Chat Assistant**: Interactive chat for movie questions and recommendations
- 👤 **User Profiles**: Optional user ID support for personalized experiences
- 🎭 **Beautiful UI**: Modern, responsive design with Tailwind CSS
- 🤖 **RAG Integration**: Movie explanations powered by retrieval-augmented generation

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Package Manager**: pnpm

## Getting Started

### Prerequisites

- Node.js 18+ installed
- pnpm installed (`npm install -g pnpm`)
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
cd frontend
pnpm install
```

2. Create environment file (already created):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run the development server:
```bash
pnpm dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Building for Production

```bash
pnpm build
pnpm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js app router pages
│   │   ├── page.tsx           # Home page with recommendations
│   │   ├── chat/
│   │   │   └── page.tsx       # Chat assistant page
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles
│   ├── components/            # React components
│   │   ├── PreferenceForm.tsx # Genre preference selector
│   │   ├── RecommendationCard.tsx # Movie card display
│   │   └── ChatBox.tsx        # Chat interface
│   └── services/
│       └── api.ts             # API client functions
├── public/                    # Static assets
├── package.json
├── next.config.js
├── tailwind.config.js
└── tsconfig.json
```

## Usage

### Browse Recommendations

1. Visit the home page
2. Select your favorite genres (click to set preference level)
3. Click "Get Recommendations" or "Skip" for random suggestions
4. View personalized movie recommendations with genres
5. Enter a User ID (optional) for profile-based recommendations

### Chat Assistant

1. Click "Chat Assistant" button in header
2. Ask questions like:
   - "Recommend me a sci-fi movie"
   - "What's a good comedy?"
   - "Show me action movies similar to Die Hard"
3. Get conversational responses with movie recommendations
4. View recommended movies with explanations (if RAG is enabled)

## API Integration

The frontend connects to these backend endpoints:

- `GET /recommend` - Get recommendations for a user or anonymous
- `POST /recommend/custom` - Get recommendations based on custom preferences
- `POST /chat` - Send chat messages and get AI responses

## Customization

### Change Backend URL

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://your-backend-url:port
```

### Modify Genres

Edit available genres in [`PreferenceForm.tsx`](src/components/PreferenceForm.tsx):
```typescript
const AVAILABLE_GENRES = [
  'Action', 'Comedy', 'Drama', // ... add more
];
```

### Adjust Recommendation Count

Change the `topK` parameter in API calls (default: 10):
```typescript
await getRecommendations(userId, 20); // Get 20 recommendations
```

## Features Explained

### Preference Form
- Click once: Strong preference (❤️)
- Click twice: Moderate preference (👍)
- Click three times: Deselect

### User ID
- Leave empty for anonymous recommendations
- Enter a number for personalized recommendations based on viewing history

### Chat Mode
- Natural language interaction
- Context-aware responses
- Movie recommendations with explanations

## Troubleshooting

**"Failed to fetch recommendations"**
- Ensure backend is running on http://localhost:8000
- Check CORS settings in backend
- Verify API endpoints are accessible

**Styles not loading**
- Run `pnpm install` to ensure Tailwind is installed
- Check `tailwind.config.js` paths configuration

**Type errors**
- Run `pnpm build` to check for TypeScript errors
- Ensure all dependencies are installed

## Contributing

1. Follow TypeScript best practices
2. Use Tailwind CSS for styling
3. Keep components modular and reusable
4. Add prop types for all components

## License

MIT
