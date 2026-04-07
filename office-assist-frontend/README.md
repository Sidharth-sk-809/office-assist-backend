# Office Assist Frontend

A modern React frontend for the HR Training Bot, designed for new joiners to interact with AI-powered HR assistance.

## 🚀 Features

### 1. **User Session Management**
- Login system for new joiners with persistent sessions
- Session data stored in localStorage
- Unique conversation IDs for tracking interactions

### 2. **Policy Chat Bot** 💬
- Real-time chat interface with company policy assistant
- RAG-powered responses using Vertex AI
- Conversation history maintained per session
- Source citations for answers

### 3. **Task Submission & Grading** 📝
- Submit training tasks as text or file
- AI-powered grading using Gemini 1.5 Pro
- Detailed feedback and scoring (0-100)
- Task history saved to Firestore

### 4. **Resume Analysis** 📄
- Upload resume in PDF format
- AI classification (Junior/Mid/Senior)
- Confidence scores and detailed reasoning
- Drag-and-drop file upload

## 📋 Prerequisites

- Node.js 16+ and npm
- Backend API running on port 8000
- Modern web browser

## 🛠️ Installation

### 1. Install Dependencies

```bash
cd office-assist-frontend
npm install
```

### 2. Environment Configuration (Optional)

Create a `.env` file if you need custom API URL:

```bash
VITE_API_URL=http://localhost:8000
```

By default, the app uses `/api` proxy which forwards to `http://localhost:8000`.

### 3. Start Development Server

```bash
npm run dev
```

The app will be available at: **http://localhost:3000**

## 🏗️ Project Structure

```
office-assist-frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Header.jsx       # Navigation header
│   │   └── Header.css
│   ├── pages/               # Page components
│   │   ├── Login.jsx        # Login page with session creation
│   │   ├── Dashboard.jsx    # Main dashboard
│   │   ├── Chat.jsx         # Policy chat interface
│   │   ├── TaskSubmission.jsx  # Task submission form
│   │   ├── ResumeUpload.jsx    # Resume upload & analysis
│   │   └── *.css            # Page-specific styles
│   ├── services/            # API integration
│   │   └── api.js           # Axios service for backend calls
│   ├── App.jsx              # Main app with routing
│   ├── main.jsx             # Entry point
│   └── index.css            # Global styles
├── index.html               # HTML template
├── vite.config.js           # Vite configuration
└── package.json             # Dependencies
```

## 🔌 API Integration

The frontend communicates with the FastAPI backend through these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/chat` | POST | Send chat messages |
| `/classify` | POST | Upload resume for classification |
| `/submit-task` | POST | Submit task for grading |

## 🎨 Features in Detail

### Session Management
- **Persistent Sessions**: User data saved to localStorage
- **Automatic Login**: Users stay logged in across page refreshes
- **Unique IDs**: Each session gets a unique conversation ID
- **Session Data**: Includes name, email, role, login time, and conversation ID

### Dashboard
- API health status indicator
- Session information display
- Quick navigation to all features
- Real-time backend connectivity check

### Policy Chat
- Message history with user/bot distinction
- Typing indicators while processing
- Source citations for transparency
- Suggested questions for new users
- Auto-scroll to latest message

### Task Submission
- Text input or file upload
- Real-time grading with visual feedback
- Score display with color-coded results
- Detailed feedback from AI
- Task ID and timestamp tracking

### Resume Upload
- Drag-and-drop file upload
- PDF validation
- Visual upload status
- Classification results with confidence scores
- Detailed reasoning for classification

## 🚀 Running in Production

### Build for Production

```bash
npm run build
```

This creates an optimized build in the `dist` folder.

### Preview Production Build

```bash
npm run preview
```

### Deploy

The `dist` folder can be deployed to any static hosting service:
- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages
- Any web server

## 🔧 Troubleshooting

### Issue 1: Backend Not Connected

**Symptoms:**
- Red "API: Disconnected" status on dashboard
- Error messages in chat/task submission
- Network errors in browser console

**Solutions:**

1. **Check if backend is running:**
```bash
cd office-assist-backend
python main.py
```

2. **Verify backend is accessible:**
```bash
curl http://localhost:8000
# Should return: {"status":"healthy","service":"Office Assist API"}
```

3. **Check proxy configuration:**
   - Ensure `vite.config.js` has correct proxy settings
   - Default: proxies `/api` to `http://localhost:8000`

4. **CORS Issues:**
   Add CORS middleware to backend `main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 2: AI Features Not Working

**Symptoms:**
- Chat returns errors
- Resume classification fails
- Task grading fails

**Solutions:**

1. **Verify Google Cloud credentials:**
```bash
echo $GOOGLE_APPLICATION_CREDENTIALS
# Should point to valid service account key
```

2. **Check required environment variables:**
```bash
cd office-assist-backend
cat .env

# Required variables:
# GCP_PROJECT_ID=your-project-id
# GCP_LOCATION=us-central1
# VERTEX_SEARCH_DATA_STORE_ID=your-data-store-id
```

3. **Test backend endpoints directly:**
```bash
# Test chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_input":"What is the vacation policy?"}'

# Test health
curl http://localhost:8000
```

4. **Check backend logs:**
```bash
cd office-assist-backend
python main.py
# Watch for errors in console output
```

5. **Verify GCP APIs are enabled:**
   - Vertex AI API
   - Discovery Engine API
   - Firestore API

### Issue 3: File Upload Failures

**Symptoms:**
- Resume upload fails
- Task file upload fails
- "File is empty" errors

**Solutions:**

1. **Check file size limits:**
   - FastAPI default: 16MB
   - Increase if needed in backend

2. **Verify file format:**
   - Resume: Only PDF accepted
   - Tasks: .txt, .doc, .docx, .pdf

3. **Check browser console:**
   - Look for CORS errors
   - Check network tab for failed requests

4. **Test with curl:**
```bash
curl -X POST http://localhost:8000/classify \
  -F "file=@/path/to/resume.pdf"
```

### Issue 4: Session Lost After Refresh

**Solutions:**

1. **Check localStorage:**
   - Open browser DevTools → Application → Local Storage
   - Look for `userSession` key

2. **Clear and re-login:**
```javascript
// In browser console:
localStorage.clear()
// Then refresh and login again
```

### Issue 5: Build Failures

**Symptoms:**
- `npm run build` fails
- Missing dependencies

**Solutions:**

1. **Clear node_modules and reinstall:**
```bash
rm -rf node_modules package-lock.json
npm install
```

2. **Check Node.js version:**
```bash
node --version
# Should be 16.0.0 or higher
```

3. **Update dependencies:**
```bash
npm update
```

## 🔐 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `/api` | Backend API base URL |

## 📱 Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🎨 Customization

### Changing Colors

Edit `src/index.css` CSS variables:

```css
:root {
  --primary-color: #6366f1;     /* Main brand color */
  --secondary-color: #10b981;   /* Success/accent color */
  --danger-color: #ef4444;      /* Error color */
}
```

### Adding New Features

1. Create component in `src/pages/`
2. Add route in `src/App.jsx`
3. Add navigation link in `src/components/Header.jsx`
4. Add API method in `src/services/api.js`

## 🐛 Common Issues & Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Port 3000 in use | Change port in `vite.config.js` |
| API 404 errors | Check backend is running on port 8000 |
| Session not persisting | Check browser localStorage is enabled |
| Styles not loading | Clear browser cache, rebuild |
| Build size too large | Enable tree-shaking, lazy loading |

## 📝 Development Commands

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## 📄 License

MIT License

## 🆘 Need Help?

1. Check this README first
2. Review backend documentation
3. Check browser console for errors
4. Verify all environment variables
5. Test backend endpoints with curl

---

Built with ❤️ using React + Vite for seamless HR training experiences!
