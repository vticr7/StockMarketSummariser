import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { TrendingUp, TrendingDown, BarChart2, Clock } from 'lucide-react';

const StockDashboard = ({ stockData, marketOverview, lastUpdated }) => {
  const [selectedStock, setSelectedStock] = useState(stockData[0]?.Symbol || '');
  const [selectedView, setSelectedView] = useState('price');

  const getCurrentStock = () => stockData.find(stock => stock.Symbol === selectedStock) || stockData[0];
  const currentStock = getCurrentStock();

  // Transform historical data for charts
  const getChartData = () => {
    const stock = getCurrentStock();
    if (!stock?.['Historical Data']) return [];
    
    return Object.entries(stock['Historical Data']).map(([date, data]) => ({
      date: new Date(date).toLocaleDateString(),
      price: data.Close,
      volume: data.Volume,
    }));
  };

  const chartData = getChartData();

  // Calculate market cap in trillions
  const marketCapInTrillions = marketOverview && 
    (marketOverview['Total Market Cap'] / 1000).toFixed(2);

  // Calculate market breadth percentage
  const marketBreadthPercentage = marketOverview && 
    (marketOverview['Market Breadth'] * 100).toFixed(1);

  // Calculate average PE
  const averagePE = marketOverview && 
    marketOverview['Average P/E'].toFixed(2);

  return (
    <div className="bg-gray-50 min-h-screen">
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        {/* Header with Last Updated */}
        <div className="flex justify-between items-center bg-white p-4 rounded-lg shadow-sm">
          <h1 className="text-2xl font-bold text-gray-900">Market Analysis Dashboard</h1>
          <div className="flex items-center text-gray-500">
            <Clock className="w-4 h-4 mr-2" />
            <span className="text-sm">Last Updated: {lastUpdated}</span>
          </div>
        </div>

        {/* Market Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="bg-white shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Total Market Cap</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">₹{marketCapInTrillions}T</div>
            </CardContent>
          </Card>
          <Card className="bg-white shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Market Breadth</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{marketBreadthPercentage}%</div>
            </CardContent>
          </Card>
          <Card className="bg-white shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Average P/E</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{averagePE}</div>
            </CardContent>
          </Card>
        </div>

        {/* Stock Selector */}
        <Card className="bg-white shadow-sm">
          <CardContent className="p-4">
            <select 
              value={selectedStock} 
              onChange={(e) => setSelectedStock(e.target.value)}
              className="w-full p-2 border rounded-lg mb-4 bg-white"
            >
              {stockData.map(stock => (
                <option key={stock.Symbol} value={stock.Symbol}>
                  {stock['Company Name']} ({stock.Symbol})
                </option>
              ))}
            </select>

            {/* Current Stock Info */}
            {currentStock && (
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h2 className="text-xl font-bold">{currentStock['Company Name']}</h2>
                  <p className="text-gray-500">{currentStock.Symbol}</p>
                </div>
                <div className="flex items-center">
                  <span className="text-2xl font-bold mr-2">
                    ₹{currentStock['Current Price'].toFixed(2)}
                  </span>
                  <div className={`flex items-center ${currentStock['Daily Change %'] >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {currentStock['Daily Change %'] >= 0 ? 
                      <TrendingUp className="w-5 h-5" /> : 
                      <TrendingDown className="w-5 h-5" />
                    }
                    <span className="ml-1">
                      {Math.abs(currentStock['Daily Change %']).toFixed(2)}%
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* PE Comparison */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">Stock P/E</p>
                <p className="text-xl font-bold">
                  {currentStock?.['P/E Ratio']?.toFixed(2) || 'N/A'}
                </p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">Sector P/E</p>
                <p className="text-xl font-bold">
                  {currentStock?.['Sector P/E']?.toFixed(2) || 'N/A'}
                </p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">P/E vs Sector</p>
                <p className="text-xl font-bold">
                  {currentStock?.['P/E vs Sector'] 
                    ? `${((currentStock['P/E vs Sector'] - 1) * 100).toFixed(1)}%`
                    : 'N/A'}
                </p>
              </div>
            </div>

            {/* Charts */}
            <div className="space-y-4">
              <div className="flex space-x-4">
                <button
                  onClick={() => setSelectedView('price')}
                  className={`px-4 py-2 rounded-lg flex items-center ${
                    selectedView === 'price' ? 'bg-blue-100 text-blue-600' : 'text-gray-600'
                  }`}
                >
                  <LineChart className="w-4 h-4 mr-2" />
                  Price History
                </button>
                <button
                  onClick={() => setSelectedView('volume')}
                  className={`px-4 py-2 rounded-lg flex items-center ${
                    selectedView === 'volume' ? 'bg-blue-100 text-blue-600' : 'text-gray-600'
                  }`}
                >
                  <BarChart2 className="w-4 h-4 mr-2" />
                  Volume
                </button>
              </div>

              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  {selectedView === 'price' ? (
                    <LineChart data={chartData}>
                      <XAxis 
                        dataKey="date" 
                        tick={{ fontSize: 12 }}
                        interval={Math.floor(chartData.length / 6)}
                      />
                      <YAxis 
                        tick={{ fontSize: 12 }}
                        domain={['auto', 'auto']}
                      />
                      <Tooltip />
                      <Line 
                        type="monotone" 
                        dataKey="price" 
                        stroke="#2563eb" 
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  ) : (
                    <BarChart data={chartData}>
                      <XAxis 
                        dataKey="date"
                        tick={{ fontSize: 12 }}
                        interval={Math.floor(chartData.length / 6)}
                      />
                      <YAxis 
                        tick={{ fontSize: 12 }}
                      />
                      <Tooltip />
                      <Bar 
                        dataKey="volume" 
                        fill="#2563eb"
                        opacity={0.8}
                      />
                    </BarChart>
                  )}
                </ResponsiveContainer>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default StockDashboard;