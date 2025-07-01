import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent } from '@/components/ui/card.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { Send, Bot, User, Loader2, Copy, Trash2 } from 'lucide-react'
import { useToast } from '@/hooks/use-toast.js'
import axios from 'axios'

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: 'Hello! I\'m your AI financial assistant. I can help you with market analysis, investment strategies, and financial questions. How can I assist you today?',
      timestamp: new Date()
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const scrollAreaRef = useRef(null)
  const { toast } = useToast()

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]')
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight
      }
    }
  }, [messages])

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      // Replace with your actual backend URL
      const response = await axios.post('http://localhost:8000/chat', {
        message: inputMessage.trim()
      })

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.data.response || 'I apologize, but I couldn\'t process your request at the moment.',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'I\'m sorry, I\'m having trouble connecting to the server. Please try again later.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
      
      toast({
        title: "Connection Error",
        description: "Failed to send message. Please check your connection.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const copyMessage = (content) => {
    navigator.clipboard.writeText(content)
    toast({
      title: "Copied!",
      description: "Message copied to clipboard.",
    })
  }

  const clearChat = () => {
    setMessages([
      {
        id: 1,
        type: 'bot',
        content: 'Hello! I\'m your AI financial assistant. I can help you with market analysis, investment strategies, and financial questions. How can I assist you today?',
        timestamp: new Date()
      }
    ])
    toast({
      title: "Chat Cleared",
      description: "Chat history has been cleared.",
    })
  }

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="flex flex-col h-[600px]">
      {/* Chat Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center space-x-2">
          <Bot className="h-5 w-5 text-blue-600" />
          <span className="font-medium">AI Financial Assistant</span>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={clearChat}
          className="flex items-center space-x-1"
        >
          <Trash2 className="h-4 w-4" />
          <span>Clear</span>
        </Button>
      </div>

      {/* Messages Area */}
      <ScrollArea ref={scrollAreaRef} className="flex-1 p-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
                }`}
              >
                <div className="flex items-start space-x-2">
                  {message.type === 'bot' && (
                    <Bot className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  )}
                  {message.type === 'user' && (
                    <User className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  )}
                  <div className="flex-1">
                    <div className="whitespace-pre-wrap">{message.content}</div>
                    <div className="flex items-center justify-between mt-2">
                      <span className={`text-xs ${
                        message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {formatTime(message.timestamp)}
                      </span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyMessage(message.content)}
                        className={`h-6 w-6 p-0 ${
                          message.type === 'user' 
                            ? 'hover:bg-blue-700 text-blue-100' 
                            : 'hover:bg-gray-200 dark:hover:bg-gray-700'
                        }`}
                      >
                        <Copy className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-3 max-w-[80%]">
                <div className="flex items-center space-x-2">
                  <Bot className="h-4 w-4" />
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    AI is thinking...
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="p-4 border-t">
        <div className="flex space-x-2">
          <Input
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about stocks, market trends, investment strategies..."
            className="flex-1"
            disabled={isLoading}
          />
          <Button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="px-4"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}

export default ChatInterface

