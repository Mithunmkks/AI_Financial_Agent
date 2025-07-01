import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { MessageCircle, TrendingUp, Briefcase, Bot } from 'lucide-react'
import ChatInterface from './components/ChatInterface'
import SentimentAnalyzer from './components/SentimentAnalyzer'
import PortfolioManager from './components/PortfolioManager'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('chat')

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2 rounded-lg">
                <Bot className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  Agentic AI Financial Assistant
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Your intelligent financial companion
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-8">
            <TabsTrigger value="chat" className="flex items-center space-x-2">
              <MessageCircle className="h-4 w-4" />
              <span>AI Chat</span>
            </TabsTrigger>
            <TabsTrigger value="sentiment" className="flex items-center space-x-2">
              <TrendingUp className="h-4 w-4" />
              <span>Market Sentiment</span>
            </TabsTrigger>
            <TabsTrigger value="portfolio" className="flex items-center space-x-2">
              <Briefcase className="h-4 w-4" />
              <span>Portfolio</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="chat" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <MessageCircle className="h-5 w-5" />
                  <span>Chat with AI Agent</span>
                </CardTitle>
                <CardDescription>
                  Get intelligent insights and answers about financial markets, stocks, and investment strategies.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ChatInterface />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="sentiment" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5" />
                  <span>Market Sentiment Analysis</span>
                </CardTitle>
                <CardDescription>
                  Analyze market sentiment for individual stocks and get AI-powered insights.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <SentimentAnalyzer />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="portfolio" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Briefcase className="h-5 w-5" />
                  <span>Portfolio Management</span>
                </CardTitle>
                <CardDescription>
                  Create and manage your stock portfolio, get AI recommendations for your holdings.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <PortfolioManager />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

export default App

