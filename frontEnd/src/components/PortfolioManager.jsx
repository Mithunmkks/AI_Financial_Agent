import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table.jsx'
import {
  Plus,
  Trash2,
  TrendingUp,
  TrendingDown,
  Minus,
  DollarSign,
  Briefcase,
  Target,
  Loader2,
  AlertCircle,
  CheckCircle,
  XCircle,
  Edit
} from 'lucide-react'
import { useToast } from '@/hooks/use-toast.js'
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, LineChart, Line } from 'recharts'
import axios from 'axios'

const PortfolioManager = () => {
  const [portfolio, setPortfolio] = useState([])
  const [recommendations, setRecommendations] = useState([]) 
  const [isLoading, setIsLoading] = useState(false)
  const [isAddingStock, setIsAddingStock] = useState(false)
  const [newStock, setNewStock] = useState({
    ticker: '',
    buy_price: '',
    quantity: ''
  })
  const { toast } = useToast()

  // Sample portfolio data for demonstration
  useEffect(() => {
    const samplePortfolio = [
      { ticker: "AAPL", buy_price: 175.50, quantity: 30 },
      { ticker: "TSLA", buy_price: 205.80, quantity: 12 },
      { ticker: "JPM", buy_price: 155.30, quantity: 16 }
    ]
    setPortfolio(samplePortfolio)
  }, [])

  const addStock = () => {
    if (!newStock.ticker || !newStock.buy_price || !newStock.quantity) {
      toast({
        title: "Invalid Input",
        description: "Please fill in all fields.",
        variant: "destructive",
      })
      return
    }

    const stock = {
      ticker: newStock.ticker.toUpperCase(),
      buy_price: parseFloat(newStock.buy_price),
      quantity: parseInt(newStock.quantity)
    }

    // Check if stock already exists
    const existingIndex = portfolio.findIndex(s => s.ticker === stock.ticker)
    if (existingIndex >= 0) {
      // Update existing stock
      const updatedPortfolio = [...portfolio]
      updatedPortfolio[existingIndex] = {
        ...updatedPortfolio[existingIndex],
        buy_price: ((updatedPortfolio[existingIndex].buy_price * updatedPortfolio[existingIndex].quantity) +
                   (stock.buy_price * stock.quantity)) / (updatedPortfolio[existingIndex].quantity + stock.quantity),
        quantity: updatedPortfolio[existingIndex].quantity + stock.quantity
      }
      setPortfolio(updatedPortfolio)
    } else {
      setPortfolio([...portfolio, stock])
    }

    setNewStock({ ticker: '', buy_price: '', quantity: '' })
    setIsAddingStock(false)
    
    toast({
      title: "Stock Added",
      description: `${stock.ticker} has been added to your portfolio.`,
    })
  }

  const removeStock = (ticker) => {
    setPortfolio(portfolio.filter(stock => stock.ticker !== ticker))
    toast({
      title: "Stock Removed",
      description: `${ticker} has been removed from your portfolio.`,
    })
  }

  const getRecommendations = async () => {
    if (portfolio.length === 0) {
      toast({
        title: "Empty Portfolio",
        description: "Please add stocks to your portfolio first.",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)
    let allRecommendations = []
    
    try {
      for (const stock of portfolio) {
        const response = await axios.post('http://localhost:8000/portfolio/recommendation', {
          portfolio: [stock] // Send one stock at a time
        })
        if (response.data && response.data.recommendation) {
          allRecommendations = [...allRecommendations, ...response.data.recommendation]
        }
      }

      setRecommendations(allRecommendations)
      
      toast({
        title: "Recommendations Generated",
        description: "AI recommendations have been generated for your portfolio.",
      })

    } catch (error) {
      console.error('Portfolio recommendation error:', error)
      toast({
        title: "Recommendation Failed",
        description: "Failed to get portfolio recommendations. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const getRecommendationIcon = (recommendation) => {
    switch (recommendation?.toLowerCase()) {
      case 'buy':
        return <TrendingUp className="h-4 w-4 text-green-600" />
      case 'sell':
        return <TrendingDown className="h-4 w-4 text-red-600" />
      default:
        return <Minus className="h-4 w-4 text-yellow-600" />
    }
  }

  const getRecommendationColor = (recommendation) => {
    switch (recommendation?.toLowerCase()) {
      case 'buy':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'sell':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    }
  }

  // Calculate portfolio metrics
  const totalValue = portfolio.reduce((sum, stock) => sum + (stock.buy_price * stock.quantity), 0)
  const portfolioData = portfolio.map(stock => ({
    name: stock.ticker,
    value: stock.buy_price * stock.quantity,
    percentage: ((stock.buy_price * stock.quantity) / totalValue * 100).toFixed(1)
  }))

  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#84cc16', '#f97316']

  return (
    <div className="space-y-6">
      {/* Portfolio Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Briefcase className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Holdings</p>
                <p className="text-2xl font-bold">{portfolio.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <DollarSign className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Value</p>
                <p className="text-2xl font-bold">${totalValue.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Target className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Avg. Position</p>
                <p className="text-2xl font-bold">
                  ${portfolio.length > 0 ? (totalValue / portfolio.length).toLocaleString() : '0'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Portfolio Management */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Portfolio Holdings */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Portfolio Holdings</CardTitle>
                <CardDescription>
                  Manage your stock positions
                </CardDescription>
              </div>
              <Dialog open={isAddingStock} onOpenChange={setIsAddingStock}>
                <DialogTrigger asChild>
                  <Button size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Stock
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Add Stock to Portfolio</DialogTitle>
                    <DialogDescription>
                      Enter the stock details to add to your portfolio.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="ticker">Stock Ticker</Label>
                      <Input
                        id="ticker"
                        name="ticker"
                        value={newStock.ticker}
                        onChange={(e) => setNewStock({...newStock, ticker: e.target.value})}
                        placeholder="e.g., AAPL"
                        className="uppercase"
                      />
                    </div>
                    <div>
                      <Label htmlFor="buy_price">Buy Price ($)</Label>
                      <Input
                        id="buy_price"
                        name="buy_price"
                        type="number"
                        step="0.01"
                        value={newStock.buy_price}
                        onChange={(e) => setNewStock({...newStock, buy_price: e.target.value})}
                        placeholder="175.50"
                      />
                    </div>
                    <div>
                      <Label htmlFor="quantity">Quantity</Label>
                      <Input
                        id="quantity"
                        name="quantity"
                        type="number"
                        value={newStock.quantity}
                        onChange={(e) => setNewStock({...newStock, quantity: e.target.value})}
                        placeholder="10"
                      />
                    </div>
                    <div className="flex space-x-2">
                      <Button onClick={addStock} className="flex-1">
                        Add Stock
                      </Button>
                      <Button variant="outline" onClick={() => setIsAddingStock(false)} className="flex-1">
                        Cancel
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </CardHeader>
          <CardContent>
            {portfolio.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Ticker</TableHead>
                    <TableHead>Qty</TableHead>
                    <TableHead>Buy Price</TableHead>
                    <TableHead>Value</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {portfolio.map((stock, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">{stock.ticker}</TableCell>
                      <TableCell>{stock.quantity}</TableCell>
                      <TableCell>${stock.buy_price.toFixed(2)}</TableCell>
                      <TableCell>${(stock.buy_price * stock.quantity).toLocaleString()}</TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeStock(stock.ticker)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-8">
                <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 dark:text-gray-400">No stocks in portfolio</p>
                <p className="text-sm text-gray-500">Add your first stock to get started</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Portfolio Allocation */}
        <Card>
          <CardHeader>
            <CardTitle>Portfolio Allocation</CardTitle>
            <CardDescription>
              Distribution of your investments
            </CardDescription>
          </CardHeader>
          <CardContent>
            {portfolio.length > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={portfolioData}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {portfolioData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, 'Value']} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="grid grid-cols-2 gap-2 mt-4">
                  {portfolioData.map((entry, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: colors[index % colors.length] }}
                      />
                      <span className="text-sm">{entry.name}</span>
                      <span className="text-sm text-gray-500">({entry.percentage}%)</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="text-center py-8">
                <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 dark:text-gray-400">No allocation data</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* AI Recommendations */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>AI Recommendations</CardTitle>
              <CardDescription>
                Get AI-powered investment recommendations for your portfolio
              </CardDescription>
            </div>
            <Button 
              onClick={getRecommendations}
              disabled={isLoading || portfolio.length === 0}
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Target className="h-4 w-4 mr-2" />
              )}
              Get Recommendations
            </Button>
          </div>
        </CardHeader>
        <CardContent className="max-h-96 overflow-y-auto">
          {recommendations && recommendations.length > 0 ? (
            <div className="space-y-4">
              {recommendations.map((rec, index) => (
                <Card key={index} className="border-l-4 border-l-blue-500">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="font-bold text-lg">{rec.ticker}</span>
                          <Badge className={getRecommendationColor(rec.recommendation)}>
                            {getRecommendationIcon(rec.recommendation)}
                            <span className="ml-1">{rec.recommendation}</span>
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          {rec.justification}
                        </p>
                        {rec.metrics && (
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                            <div>
                              <span className="text-gray-500">Current Price:</span>
                              <span className="font-medium ml-1">${rec.metrics.current_price}</span>
                            </div>
                            <div>
                              <span className="text-gray-500">Target Price:</span>
                              <span className="font-medium ml-1">${rec.metrics.target_price}</span>
                            </div>
                            <div>
                              <span className="text-gray-500">ROE:</span>
                              <span className="font-medium ml-1">{rec.metrics.roe}%</span>
                            </div>
                            <div>
                              <span className="text-gray-500">P/E Ratio:</span>
                              <span className="font-medium ml-1">{rec.metrics.pe_ratio}</span>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400 mb-2">No recommendations yet</p>
              <p className="text-sm text-gray-500">
                Click "Get Recommendations" to analyze your portfolio
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default PortfolioManager


