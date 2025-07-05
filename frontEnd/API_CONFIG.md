# pnpm install

# pnpm run dev

# API Configuration Guide

## Backend API Endpoints

To connect your frontend to your backend, update the API endpoints in the following files:

### 1. Chat Interface (`src/components/ChatInterface.jsx`)

```javascript
// Line 44: Update the backend URL
const response = await axios.post("http://localhost:8000/chat", {
  message: inputMessage.trim(),
});
```

### 2. Sentiment Analyzer (`src/components/SentimentAnalyzer.jsx`)

```javascript
// Line 32: Update the backend URL
const response = await axios.post("http://localhost:8000/sentiment", {
  ticker: ticker.trim().toUpperCase(),
});
```

### 3. Portfolio Manager (`src/components/PortfolioManager.jsx`)

```javascript
// Line 78: Update the backend URL
const response = await axios.post(
  "http://localhost:8000/portfolio/recommendation",
  {
    portfolio: portfolio,
  }
);
```

## API Request/Response Format

### Chat API

- **Endpoint**: `POST /chat`
- **Request**: `{ "message": "string" }`
- **Response**: `"string"` (AI response)

### Sentiment API

- **Endpoint**: `POST /sentiment`
- **Request**: `{ "ticker": "AAPL" }`
- **Response**:

```json
{
  "sentiment": "positive|negative|neutral",
  "sentiment_score": 0.75,
  "impact_score": 0.85,
  "reasoning": "AI reasoning explanation"
}
```

### Portfolio Recommendation API

- **Endpoint**: `POST /portfolio/recommendation`
- **Request**:

```json
{
  "portfolio": [
    { "ticker": "AAPL", "buy_price": 175.5, "quantity": 30 },
    { "ticker": "TSLA", "buy_price": 205.8, "quantity": 12 }
  ]
}
```

- **Response**: Array of recommendations with BUY/HOLD/SELL decisions

## Environment Configuration

Create a `.env` file in the project root to configure your backend URL:

```
VITE_API_BASE_URL=http://localhost:8000
```

Then update the API calls to use:

```javascript
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
```

## CORS Configuration

Make sure your backend allows CORS requests from your frontend domain. In your backend, add CORS headers or use a CORS middleware.

## Running the Application

1. Start your backend server on port 8000
2. Start the frontend development server: `npm run dev --host`
3. Access the application at `http://localhost:5173`
