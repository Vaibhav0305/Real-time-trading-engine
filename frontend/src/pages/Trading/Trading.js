import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  Divider,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  TrendingUp,
  TrendingDown,
  ShowChart,
  AccountBalance,
  Timeline,
  Assessment,
} from '@mui/icons-material';

// Components
import TradingChart from '../../components/Trading/TradingChart';
import OrderBook from '../../components/Trading/OrderBook';
import TradingPanel from '../../components/Trading/TradingPanel';
import MarketDepth from '../../components/Trading/MarketDepth';
import RecentTrades from '../../components/Trading/RecentTrades';
import PositionSummary from '../../components/Trading/PositionSummary';

// Hooks
import { useTrading } from '../../contexts/TradingContext';
import { useWebSocket } from '../../hooks/useWebSocket';

const StyledPaper = styled(Paper)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  borderRadius: 12,
  border: `1px solid ${theme.palette.divider}`,
  background: theme.palette.background.paper,
}));

const TabPanel = ({ children, value, index, ...other }) => (
  <div
    role="tabpanel"
    hidden={value !== index}
    id={`trading-tabpanel-${index}`}
    aria-labelledby={`trading-tab-${index}`}
    {...other}
  >
    {value === index && <Box sx={{ p: 2 }}>{children}</Box>}
  </div>
);

const Trading = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [chartTimeframe, setChartTimeframe] = useState('1D');
  
  const { 
    orderBook, 
    marketData, 
    positions, 
    placeOrder, 
    cancelOrder,
    modifyOrder 
  } = useTrading();

  const { isConnected, lastMessage } = useWebSocket('/ws');

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

  const handleSymbolChange = (symbol) => {
    setSelectedSymbol(symbol);
  };

  const handleTimeframeChange = (timeframe) => {
    setChartTimeframe(timeframe);
  };

  const handleOrderPlacement = async (orderData) => {
    try {
      await placeOrder({
        ...orderData,
        symbol: selectedSymbol,
      });
      // Success notification will be handled by the context
    } catch (error) {
      console.error('Failed to place order:', error);
    }
  };

  const handleOrderCancellation = async (orderId) => {
    try {
      await cancelOrder(orderId);
      // Success notification will be handled by the context
    } catch (error) {
      console.error('Failed to cancel order:', error);
    }
  };

  const handleOrderModification = async (orderId, updates) => {
    try {
      await modifyOrder(orderId, updates);
      // Success notification will be handled by the context
    } catch (error) {
      console.error('Failed to modify order:', error);
    }
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column', p: 2, gap: 2 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h4" component="h1" fontWeight="bold">
            {selectedSymbol}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {marketData?.change >= 0 ? (
              <TrendingUp color="success" />
            ) : (
              <TrendingDown color="error" />
            )}
            <Typography
              variant="h6"
              color={marketData?.change >= 0 ? 'success.main' : 'error.main'}
            >
              ${marketData?.close_price?.toFixed(2) || '0.00'}
            </Typography>
            <Typography
              variant="body2"
              color={marketData?.change >= 0 ? 'success.main' : 'error.main'}
            >
              {marketData?.change >= 0 ? '+' : ''}{marketData?.change?.toFixed(2) || '0.00'} 
              ({marketData?.change_percent?.toFixed(2) || '0.00'}%)
            </Typography>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          {['1H', '1D', '1W', '1M', '3M', '1Y'].map((timeframe) => (
            <Paper
              key={timeframe}
              sx={{
                px: 2,
                py: 1,
                cursor: 'pointer',
                backgroundColor: chartTimeframe === timeframe ? 'primary.main' : 'background.paper',
                color: chartTimeframe === timeframe ? 'white' : 'text.primary',
                '&:hover': {
                  backgroundColor: chartTimeframe === timeframe ? 'primary.dark' : 'action.hover',
                },
              }}
              onClick={() => handleTimeframeChange(timeframe)}
            >
              <Typography variant="body2" fontWeight="medium">
                {timeframe}
              </Typography>
            </Paper>
          ))}
        </Box>
      </Box>

      {/* Main Content */}
      <Grid container spacing={2} sx={{ flex: 1, minHeight: 0 }}>
        {/* Left Column - Chart and Trading Panel */}
        <Grid item xs={12} lg={8} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Chart */}
          <StyledPaper sx={{ flex: 1, minHeight: 400 }}>
            <CardContent sx={{ flex: 1, p: 0 }}>
              <TradingChart
                symbol={selectedSymbol}
                timeframe={chartTimeframe}
                marketData={marketData}
              />
            </CardContent>
          </StyledPaper>

          {/* Trading Panel */}
          <StyledPaper>
            <CardContent>
              <TradingPanel
                symbol={selectedSymbol}
                marketData={marketData}
                onPlaceOrder={handleOrderPlacement}
                onCancelOrder={handleOrderCancellation}
                onModifyOrder={handleOrderModification}
              />
            </CardContent>
          </StyledPaper>
        </Grid>

        {/* Right Column - Order Book, Market Depth, etc. */}
        <Grid item xs={12} lg={4} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Tabs for different views */}
          <StyledPaper>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs
                value={selectedTab}
                onChange={handleTabChange}
                aria-label="trading tabs"
                variant="fullWidth"
              >
                <Tab label="Order Book" icon={<Assessment />} />
                <Tab label="Market Depth" icon={<Timeline />} />
                <Tab label="Trades" icon={<ShowChart />} />
              </Tabs>
            </Box>

            <TabPanel value={selectedTab} index={0}>
              <OrderBook
                symbol={selectedSymbol}
                orderBook={orderBook}
                onPlaceOrder={handleOrderPlacement}
              />
            </TabPanel>

            <TabPanel value={selectedTab} index={1}>
              <MarketDepth
                symbol={selectedSymbol}
                orderBook={orderBook}
              />
            </TabPanel>

            <TabPanel value={selectedTab} index={2}>
              <RecentTrades
                symbol={selectedSymbol}
                trades={[]} // Will be populated from context
              />
            </TabPanel>
          </StyledPaper>

          {/* Position Summary */}
          <StyledPaper>
            <CardContent>
              <PositionSummary
                symbol={selectedSymbol}
                positions={positions}
              />
            </CardContent>
          </StyledPaper>

          {/* Account Summary */}
          <StyledPaper>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <AccountBalance color="primary" />
                <Typography variant="h6">Account Summary</Typography>
              </Box>
              <Divider sx={{ mb: 2 }} />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Available Balance
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  $10,000.00
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Used Margin
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  $2,500.00
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  Free Margin
                </Typography>
                <Typography variant="body2" fontWeight="medium" color="success.main">
                  $7,500.00
                </Typography>
              </Box>
            </CardContent>
          </StyledPaper>
        </Grid>
      </Grid>

      {/* Connection Status */}
      <Box
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          px: 2,
          py: 1,
          borderRadius: 2,
          backgroundColor: isConnected ? 'success.dark' : 'error.dark',
          color: 'white',
          fontSize: '0.875rem',
        }}
      >
        <Box
          sx={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            backgroundColor: isConnected ? 'success.light' : 'error.light',
          }}
        />
        {isConnected ? 'Connected' : 'Disconnected'}
      </Box>
    </Box>
  );
};

export default Trading;
