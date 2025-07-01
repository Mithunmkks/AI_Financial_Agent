import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Search, TrendingUp, TrendingDown, Minus, Loader2, BarChart3, AlertCircle } from 'lucide-react'
import { useToast } from '@/hooks/use-toast.js'
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'
import axios from 'axios'

const SentimentAnalyzer = () => {
  const [ticker, setTicker] = useState('')
  const [sentimentData, setSentimentData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [history, setHistory] = useState([])
  const { toast } = useToast()

  const analyzeSentiment = async () => {
    if (!ticker.trim()) {
      toast({
        title: "Invalid Input",
        description: "Please enter a stock ticker symbol.",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)
    
    try {
      // Replace with your actual backend URL
      const response = await axios.post('http://localhost:8000/sentiment', {
        ticker: ticker.trim().toUpperCase()
      })
      console.log('Sentiment analysis response:', response.data)
      const data = response.data
      setSentimentData({
        ...data,
        ticker: ticker.trim().toUpperCase(),
        timestamp: new Date()
      })

      // Add to history
      setHistory(prev => [
        {
          ticker: ticker.trim().toUpperCase(),
          sentiment: data.sentiment,
          sentiment_score: data.sentiment_score,
          timestamp: new Date()
        },
        ...prev.slice(0, 4) // Keep only last 5 entries
      ])

      toast({
        title: "Analysis Complete",
        description: `Sentiment analysis for ${ticker.toUpperCase()} completed successfully.`,
      })

    } catch (error) {
      console.error('Sentiment analysis error:', error)
      toast({
        title: "Analysis Failed",
        description: "Failed to analyze sentiment. Please check the ticker symbol and try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      analyzeSentiment()
    }
  }

  const getSentimentIcon = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return <TrendingUp className="h-4 w-4 text-green-600" />
      case 'negative':
        return <TrendingDown className="h-4 w-4 text-red-600" />
      default:
        return <Minus className="h-4 w-4 text-yellow-600" />
    }
  }

  const getSentimentColor = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'negative':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    }
  }

  const getScoreColor = (score) => {
    if (score > 0.6) return 'text-green-600'
    if (score < -0.6) return 'text-red-600'
    return 'text-yellow-600'
  }

  // Prepare chart data
  const pieData = sentimentData ? [
    { name: 'Positive', value: Math.max(0, sentimentData.sentiment_score * 100), color: '#10b981' },
    { name: 'Negative', value: Math.max(0, -sentimentData.sentiment_score * 100), color: '#ef4444' },
    { name: 'Neutral', value: 100 - Math.abs(sentimentData.sentiment_score * 100), color: '#f59e0b' }
  ] : []

  const barData = history.map(item => ({
    ticker: item.ticker,
    score: item.sentiment_score,
    sentiment: item.sentiment
  }))

  return (
    <div className="space-y-6">
      {/* Search Section */}
      <div className="flex space-x-2">
        <Input
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter stock ticker (e.g., AAPL, TSLA, GOOGL)"
          className="flex-1"
          disabled={isLoading}
        />
        <Button
          onClick={analyzeSentiment}
          disabled={!ticker.trim() || isLoading}
          className="px-6"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Search className="h-4 w-4" />
          )}
          <span className="ml-2">Analyze</span>
        </Button>
      </div>

      {/* Results Section */}
      {sentimentData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Sentiment Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                {getSentimentIcon(sentimentData.sentiment)}
                <span>Sentiment Analysis: {sentimentData.ticker}</span>
              </CardTitle>
              <CardDescription>
                Analysis completed at {sentimentData.timestamp.toLocaleString()}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Overall Sentiment:</span>
                <Badge className={getSentimentColor(sentimentData.sentiment)}>
                  {sentimentData.sentiment}
                </Badge>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Sentiment Score:</span>
                  <span className={`font-bold ${getScoreColor(sentimentData.sentiment_score)}`}>
                    {sentimentData.sentiment_score?.toFixed(3)}
                  </span>
                </div>
                <Progress 
                  value={Math.abs(sentimentData.sentiment_score) * 100} 
                  className="h-2"
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Impact Score:</span>
                  <span className="font-bold">
                    {sentimentData.impact_score?.toFixed(3)}
                  </span>
                </div>
                <Progress 
                  value={sentimentData.impact_score * 100} 
                  className="h-2"
                />
              </div>

              {sentimentData.reasoning && (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    <strong>AI Reasoning:</strong> {sentimentData.reasoning}
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Sentiment Visualization */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5" />
                <span>Sentiment Breakdown</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value.toFixed(1)}%`, 'Percentage']} />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex justify-center space-x-4 mt-4">
                {pieData.map((entry, index) => (
                  <div key={index} className="flex items-center space-x-1">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: entry.color }}
                    />
                    <span className="text-sm">{entry.name}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* History Section */}
      {history.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Analysis History</CardTitle>
            <CardDescription>
              Your recent sentiment analyses
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {history.map((item, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="flex items-center space-x-3">
                    {getSentimentIcon(item.sentiment)}
                    <div>
                      <span className="font-medium">{item.ticker}</span>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {item.timestamp.toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge className={getSentimentColor(item.sentiment)}>
                      {item.sentiment}
                    </Badge>
                    <p className={`text-sm font-medium ${getScoreColor(item.sentiment_score)}`}>
                      Score: {item.sentiment_score?.toFixed(3)}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* History Chart */}
            {barData.length > 1 && (
              <div className="mt-6">
                <h4 className="text-sm font-medium mb-3">Sentiment Score Comparison</h4>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={barData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="ticker" />
                    <YAxis domain={[-1, 1]} />
                    <Tooltip 
                      formatter={(value) => [value.toFixed(3), 'Sentiment Score']}
                      labelFormatter={(label) => `Ticker: ${label}`}
                    />
                    <Bar 
                      dataKey="score" 
                      fill={(entry) => entry > 0 ? '#10b981' : '#ef4444'}
                      radius={[2, 2, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {!sentimentData && !isLoading && (
        <Card>
          <CardContent className="text-center py-12">
            <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              No Analysis Yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Enter a stock ticker symbol above to get started with sentiment analysis.
            </p>
            <p className="text-sm text-gray-500">
              Try popular tickers like AAPL, TSLA, GOOGL, MSFT, or AMZN
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default SentimentAnalyzer

