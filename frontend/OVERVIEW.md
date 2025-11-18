# Frontend Overview

## Architecture

The frontend is a **React + Vite** single-page application (SPA) that provides a user interface for frog species identification through audio classification. It consists of a client-side React app and a Node.js Express backend server that acts as a proxy and media enrichment layer.

## Technology Stack

### Core Framework
- **React 18.3.1** - UI component library
- **Vite 6.0.3** - Build tool and development server
- **React Router DOM 7.0.2** - Client-side routing

### Backend Server (Express)
- **Express 4.21.1** - Node.js web server framework
- **Multer 1.4.5-lts.1** - Middleware for handling multipart/form-data (file uploads)
- **@supabase/supabase-js 2.47.10** - Supabase client for database and storage access
- **node-fetch 3.3.2** - HTTP client for making requests to FastAPI service
- **form-data 4.0.0** - Library for constructing multipart/form-data payloads
- **dotenv 16.4.7** - Environment variable management
- **cors 2.8.5** - Cross-Origin Resource Sharing middleware

### Development Tools
- **@vitejs/plugin-react 4.3.4** - Vite plugin for React Fast Refresh
- **ESLint 9.17.0** - Code linting and quality checks
- **@eslint/js 9.17.0** - ESLint JavaScript plugin
- **eslint-plugin-react 7.37.2** - React-specific linting rules
- **eslint-plugin-react-hooks 5.0.0** - Hooks-specific linting rules
- **eslint-plugin-react-refresh 0.4.16** - React Fast Refresh linting
- **globals 15.13.0** - Global identifiers for different environments

## Project Structure

```
frontend/
├── index.html              # Entry HTML file
├── package.json            # Client dependencies and scripts
├── vite.config.js          # Vite configuration
├── server/                 # Express backend server
│   ├── index.js           # Server entry point with API routes
│   ├── package.json       # Server dependencies
│   └── .env.example       # Environment variable template
└── src/                   # React application source
    ├── App.jsx            # Main app component with routing
    ├── main.jsx           # React DOM entry point
    ├── api/
    │   └── api.js         # API client functions
    ├── components/
    │   ├── Classifier.jsx           # Audio classification interface
    │   ├── Home.jsx                 # Landing page
    │   └── SpeciesDictionary.jsx    # Species reference browser
    └── styles/
        └── global.css     # Application-wide styles
```

## Component Architecture

### 1. **Home Component** (`src/components/Home.jsx`)
- **Purpose**: Landing page with project overview and feature highlights
- **Features**:
  - Feature cards linking to Classifier and Species Dictionary
  - Statistics bar showing key metrics (14 species, Top 3 predictions)
  - How-it-works section explaining the classification process
  - Best practices tips for recording quality
- **Routing**: Uses React Router `Link` components for navigation

### 2. **Classifier Component** (`src/components/Classifier.jsx`)
- **Purpose**: Main audio classification interface
- **State Management**:
  - `file` - Selected/recorded audio file
  - `loading` - Classification request status
  - `result` - Top 3 predictions with confidence scores
  - `error` - Error messages
  - `audioUrl` - Blob URL for audio playback preview
  - `isRecording` - Recording state flag
  - `recordingMode` - Toggle between 'upload' and 'record'
- **Key Features**:
  - **Upload Mode**: File input accepting audio files (WAV, MP3, FLAC, OGG, M4A, WebM)
  - **Record Mode**: Browser-based audio recording using MediaRecorder API
  - **Audio Preview**: Playback widget for reviewing uploaded/recorded audio
  - **Top-3 Predictions Display**: Visual cards with species images, confidence bars, rank badges
- **APIs Used**:
  - `navigator.mediaDevices.getUserMedia()` - Microphone access
  - `MediaRecorder` - Audio recording with format detection (audio/mp4, audio/mpeg, audio/webm)
  - `URL.createObjectURL()` - Generate blob URLs for audio preview
  - `FormData` - Multipart file upload to Express server

### 3. **Species Dictionary Component** (`src/components/SpeciesDictionary.jsx`)
- **Purpose**: Browsable reference of all 14 Georgia frog species
- **State Management**:
  - `query` - Search input value
  - `results` - Filtered species list (defaults to all species)
  - `loading` - Media fetch status
  - `mediaUrls` - Cached Supabase media URLs
- **Features**:
  - Search by scientific name, common name, or slug
  - Displays all 14 species by default (no empty state)
  - Species cards with thumbnail images and audio players
  - Real-time search filtering
- **Data Flow**:
  1. Fetch media URLs from Supabase via Express server on mount
  2. Build species objects with image/audio URLs
  3. Set as initial results to display all species
  4. Search rebuilds species list with current URLs before filtering

### 4. **API Client** (`src/api/api.js`)
- **Purpose**: Centralized HTTP client for backend communication
- **Base URL**: Configured via `VITE_API_BASE` environment variable (defaults to `http://localhost:8000`)
- **Functions**:
  - `get(endpoint)` - GET requests with JSON response parsing
  - `post(endpoint, body, options)` - POST requests with FormData or JSON support
  - `getSpeciesMediaBatch(slugs)` - Batch fetch media URLs for multiple species

## Backend Server Architecture

### Express Server (`server/index.js`)

**Purpose**: Acts as a unified backend layer between the React frontend and external services (FastAPI, Supabase)

**Key Responsibilities**:
1. **Proxy Classification Requests**: Forwards audio files from frontend to FastAPI service
2. **Media URL Enrichment**: Fetches and caches Supabase Storage public URLs
3. **CORS Management**: Enables cross-origin requests from Vite dev server
4. **File Upload Handling**: Processes multipart/form-data with Multer

**API Endpoints**:

#### `POST /classify`
- **Purpose**: Proxy audio classification to FastAPI service
- **Process**:
  1. Receives audio file via Multer middleware
  2. Constructs FormData with file
  3. Forwards to FastAPI at `${FROG_API_URL}/predict-audio` (port 8001)
  4. Enriches top-3 predictions with Supabase image URLs
  5. Returns predictions with `image_url` field added
- **Request**: `multipart/form-data` with `file` field
- **Response**: 
  ```json
  {
    "top_3": [
      {
        "species": "american_bullfrog",
        "confidence": 0.87,
        "image_url": "https://..."
      }
    ]
  }
  ```

#### `POST /species-media-batch`
- **Purpose**: Batch fetch Supabase media URLs for multiple species
- **Process**:
  1. Receives array of species slugs
  2. For each slug, fetches public URLs from Supabase Storage
  3. Returns map of slug → {image, audio} URLs
- **Request**: 
  ```json
  {
    "slugs": ["american_bullfrog", "green_frog"]
  }
  ```
- **Response**:
  ```json
  {
    "american_bullfrog": {
      "image": "https://...",
      "audio": "https://..."
    }
  }
  ```

**Environment Configuration**:
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous/public API key
- `FROG_API_URL` - FastAPI service URL (default: `http://localhost:8001`)
- `PORT` - Express server port (default: 8000)

## Audio Recording Implementation

### MediaRecorder API
The Classifier component uses the browser's native MediaRecorder API for audio capture:

```javascript
// Format detection with fallback hierarchy
let mimeType = 'audio/webm'
if (MediaRecorder.isTypeSupported('audio/mp4')) {
  mimeType = 'audio/mp4'  // Safari (M4A)
} else if (MediaRecorder.isTypeSupported('audio/mpeg')) {
  mimeType = 'audio/mpeg'  // Rare
} else if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
  mimeType = 'audio/webm;codecs=opus'  // Chrome/Firefox
}
```

**Browser Compatibility**:
- **Safari**: Records as `audio/mp4` (M4A format)
- **Chrome/Firefox**: Records as `audio/webm` (Opus codec)
- **Fallback**: All major browsers support at least WebM

**Recording Flow**:
1. Request microphone permission via `getUserMedia()`
2. Initialize MediaRecorder with supported MIME type
3. Collect audio chunks in `ondataavailable` callback
4. On stop, create Blob and File object
5. Generate object URL for preview playback
6. Clean up media stream tracks

## Styling System

### Design Tokens (`global.css`)
- **Color Palette**: 
  - `--bg`: #f6f8fa (light page background)
  - `--card`: #ffffff (card background)
  - `--muted`: #6b7280 (subtle gray text)
  - `--accent`: #166534 (darker green accent)
- **Typography**: Inter font family with system font fallbacks
- **Spacing**: 12px border radius, 1100px max content width

### CSS Organization
- **Layout**: CSS Grid and Flexbox for responsive layouts
- **Components**: BEM-inspired class naming (.prediction-card, .feature-cards)
- **Interactions**: Hover effects, transitions, and animations
- **Responsive**: Mobile-first with media queries for tablet/desktop

### Key Style Patterns
- **Glassmorphism**: Subtle background gradients with low opacity
- **Card Hover Effects**: `translateY(-4px)` lift with shadow enhancement
- **Confidence Bars**: Gradient fills with smooth width transitions
- **Rank Badges**: Circular badges with distinct colors per rank (#1 green, #2 blue, #3 purple)

## Build & Deployment

### Development Workflow
```bash
# Install client dependencies
npm install

# Install server dependencies
cd server && npm install

# Start Vite dev server (port 5173)
npm run dev

# Start Express server (port 8000)
cd server && node index.js
```

### Production Build
```bash
# Build optimized static assets
npm run build

# Preview production build
npm run preview
```

### Build Output
- **Directory**: `dist/`
- **Assets**: HTML, JS bundles, CSS, source maps
- **Optimization**: Code splitting, tree shaking, minification
- **Deployment**: Static hosting (Vercel, Netlify, Cloudflare Pages)

## Data Flow Architecture

### Classification Flow
1. **User Action**: Upload file or record audio in Classifier component
2. **Client**: Create FormData with audio file
3. **Express Server**: 
   - Receive file via Multer
   - Forward to FastAPI service
   - Enrich response with Supabase image URLs
4. **FastAPI**: 
   - Extract audio features with librosa
   - Run Random Forest classification
   - Return top-3 predictions with confidence scores
5. **Client**: Display prediction cards with images and confidence bars

### Species Dictionary Flow
1. **Component Mount**: Trigger media fetch in useEffect
2. **Client**: POST to `/species-media-batch` with all species slugs
3. **Express Server**: 
   - Query Supabase Storage for each slug
   - Return map of {slug: {image, audio}}
4. **Client**: 
   - Cache URLs in state
   - Build species objects with media
   - Display all species in grid
5. **Search**: Filter cached species without re-fetching

## Environment Configuration

### Client (Vite)
Create `.env` file in `frontend/`:
```env
VITE_API_BASE=http://localhost:8000
```

### Server (Express)
Create `.env` file in `frontend/server/`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
FROG_API_URL=http://localhost:8001
PORT=8000
```

## Integration with Backend Services

### FastAPI Service (Port 8001)
- **Endpoint**: `/predict-audio`
- **Method**: POST with multipart/form-data
- **Purpose**: Audio feature extraction and ML classification
- **Response**: Top-3 species predictions with confidence scores

### Supabase Storage
- **Bucket**: `Species Catalog` (public access)
- **Structure**: 
  - Images: `images/{slug}/{slug}.jpg`
  - Audio: `audio/{slug}/{slug}.mp3`
- **Access**: Public URLs via `getPublicUrl()` method

## Error Handling

### Client-Side
- **Network Errors**: Caught in try-catch blocks, displayed in error state
- **Missing Files**: Button disabled until file selected
- **Recording Failures**: Permission errors shown to user
- **Image Load Failures**: Fallback to emoji placeholder (🐸)

### Server-Side
- **FastAPI Timeout**: 30-second timeout on classification requests
- **Supabase Errors**: Logged to console, continues with fallback paths
- **File Upload Errors**: Multer error middleware with descriptive messages

## Performance Optimizations

### Client
- **Code Splitting**: React.lazy() for route-based splitting (not yet implemented)
- **Asset Optimization**: Vite automatically optimizes images and bundles
- **State Management**: Minimal re-renders with proper state structure

### Server
- **URL Caching**: Media URLs cached in memory during batch requests
- **Stream Handling**: Multer streams files instead of loading into memory
- **CORS Preflight**: Efficient OPTIONS handling

## Future Enhancements

### Potential Improvements
- [ ] Add user authentication for saving classification history
- [ ] Implement Progressive Web App (PWA) for offline capability
- [ ] Add waveform visualization for audio preview
- [ ] Client-side MP3 encoding with lamejs library
- [ ] WebSocket connection for real-time classification updates
- [ ] Audio spectrum analyzer during recording
- [ ] Export classification results as PDF/CSV
- [ ] Species comparison view with side-by-side audio
- [ ] Mobile-optimized recording interface
- [ ] Dark mode toggle

## Troubleshooting

### Common Issues

**Vite dev server won't start**
- Check if port 5173 is already in use
- Verify `package.json` has correct Vite version
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`

**Express server connection refused**
- Ensure server is running: `cd server && node index.js`
- Check `.env` file exists in `server/` directory
- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set

**Classification not working**
- Confirm FastAPI service is running on port 8001
- Check `FROG_API_URL` in server `.env` file
- Verify Express server logs for proxy errors

**Recording not working**
- Browser must support MediaRecorder API (all modern browsers)
- User must grant microphone permission
- Check browser console for getUserMedia errors
- HTTPS required in production (not localhost)

**Species images not loading**
- Verify Supabase bucket is public
- Check bucket structure matches `images/{slug}/{slug}.jpg`
- Inspect network tab for 404s or CORS errors
- Confirm `SUPABASE_URL` and `SUPABASE_ANON_KEY` are correct

## Development Guidelines

### Code Style
- Use functional components with hooks
- Prefer arrow functions for component definitions
- Keep components under 300 lines (split if larger)
- Use meaningful variable names (no single letters except loop indices)
- Add comments for complex logic only

### State Management
- Use `useState` for local component state
- Use `useEffect` for side effects (API calls, subscriptions)
- Use `useRef` for mutable values that don't trigger re-renders
- Avoid prop drilling beyond 2 levels (consider Context API if needed)

### API Integration
- All API calls go through `src/api/api.js` client
- Handle loading and error states in components
- Use try-catch for async operations
- Display user-friendly error messages

### Styling
- Keep CSS in `global.css` (no CSS modules currently)
- Use semantic class names (.classifier-card, not .card1)
- Maintain consistent spacing (8px increments)
- Test responsive layouts at mobile (375px), tablet (768px), desktop (1024px+)
