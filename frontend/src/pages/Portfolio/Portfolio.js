import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  useTheme,
  LinearProgress
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  AccountBalance as AccountBalanceIcon,
  ShowChart as ChartIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  backgroundColor: theme.palette.background.paper,
  border: `1px solid ${theme.palette.divider}`,
  '&:hover': {
    borderColor: theme.palette.primary.main,
    boxShadow: `0 0 20px rgba(0, 212, 170, 0.1)`,
  },
}));

const MetricCard = ({ title, value, change, changePercent, icon, color = 'primary' }) => {
  const theme = useTheme();
  const isPositive = change >= 0;
  
  return (
    <StyledCard>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {title}
          </Typography>
          <Box
            sx={{
              backgroundColor: theme.palette[color].main,
              borderRadius: '50%',
              p: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </Box>
        </Box>
        
        <Typography variant="h4" component="div" sx={{ fontWeight: 700, mb: 1 }}>
          {value}
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {isPositive ? (
            <TrendingUpIcon sx={{ color: theme.palette.success.main, fontSize: '1rem' }} />
          ) : (
            <TrendingDownIcon sx={{ color: theme.palette.error.main, fontSize: '1rem' }} />
          )}
          
          <Typography
            variant="body2"
            sx={{
              color: isPositive ? theme.palette.success.main : theme.palette.error.main,
              fontWeight: 600,
            }}
          >
            {isPositive ? '+' : ''}{change} ({changePercent}%)
          </Typography>
        </Box>
      </CardContent>
    </StyledCard>
  );
};

const Portfolio = () => {
  const theme = useTheme();
  
  // Mock portfolio data
  const portfolioData = {
    totalValue: 125430.50,
    totalChange: 2450.75,
    totalChangePercent: 2.0,
    cashBalance: 25000.00,
    marginUsed: 15000.00,
    availableMargin: 100000.00,
  };

  const positions = [
    {
      symbol: 'AAPL',
      quantity: 100,
      averagePrice: 145.50,
      currentPrice: 150.25,
      marketValue: 15025.00,
      unrealizedPnL: 475.00,
      unrealizedPnLPercent: 3.26,
    },
    {
      symbol: 'GOOGL',
      quantity: 25,
      averagePrice: 2750.00,
      currentPrice: 2800.00,
      marketValue: 70000.00,
      unrealizedPnL: 1250.00,
      unrealizedPnLPercent: 1.82,
    },
    {
      symbol: 'MSFT',
      quantity: 50,
      averagePrice: 375.00,
      currentPrice: 380.50,
      marketValue: 19025.00,
      unrealizedPnL: 275.00,
      unrealizedPnLPercent: 1.47,
    },
    {
      symbol: 'TSLA',
      quantity: 75,
      averagePrice: 240.00,
      currentPrice: 245.80,
      marketValue: 18435.00,
      unrealizedPnL: 435.00,
      unrealizedPnLPercent: 2.42,
    },
    {
      symbol: 'AMZN',
      quantity: 30,
      averagePrice: 3150.00,
      currentPrice: 3200.00,
      marketValue: 96000.00,
      unrealizedPnL: 1500.00,
      unrealizedPnLPercent: 1.59,
    },
  ];

  const allocationData = [
    { category: 'Technology', percentage: 45, value: 56485.00, color: theme.palette.primary.main },
    { category: 'Consumer Discretionary', percentage: 30, value: 37630.00, color: theme.palette.secondary.main },
    { category: 'Financial Services', percentage: 15, value: 18815.00, color: theme.palette.warning.main },
    { category: 'Healthcare', percentage: 10, value: 12543.00, color: theme.palette.info.main },
  ];

  return (
    <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700, mb: 4 }}>
        Portfolio
      </Typography>
      
      <Grid container spacing={3}>
        {/* Key Metrics */}
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Total Portfolio Value"
            value={`$${portfolioData.totalValue.toLocaleString()}`}
            change={portfolioData.totalChange}
            changePercent={portfolioData.totalChangePercent}
            icon={<AccountBalanceIcon sx={{ color: 'white' }} />}
            color="primary"
          />
        </Grid>
        
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Cash Balance"
            value={`$${portfolioData.cashBalance.toLocaleString()}`}
            change={0}
            changePercent={0}
            icon={<AccountBalanceIcon sx={{ color: 'white' }} />}
            color="info"
          />
        </Grid>
        
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Margin Used"
            value={`$${portfolioData.marginUsed.toLocaleString()}`}
            change={0}
            changePercent={0}
            icon={<ChartIcon sx={{ color: 'white' }} />}
            color="warning"
          />
        </Grid>
        
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Available Margin"
            value={`$${portfolioData.availableMargin.toLocaleString()}`}
            change={0}
            changePercent={0}
            icon={<ChartIcon sx={{ color: 'white' }} />}
            color="success"
          />
        </Grid>

        {/* Portfolio Allocation */}
        <Grid item xs={12} md={6}>
          <StyledCard>
            <CardContent>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Portfolio Allocation
              </Typography>
              
              <Box sx={{ mt: 3 }}>
                {allocationData.map((item, index) => (
                  <Box key={index} sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">{item.category}</Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {item.percentage}% (${item.value.toLocaleString()})
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={item.percentage}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: theme.palette.divider,
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: item.color,
                          borderRadius: 4,
                        },
                      }}
                    />
                  </Box>
                ))}
              </Box>
            </CardContent>
          </StyledCard>
        </Grid>

        {/* Performance Chart Placeholder */}
        <Grid item xs={12} md={6}>
          <StyledCard>
            <CardContent>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Performance Overview
              </Typography>
              
              <Box sx={{ 
                height: 200, 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                borderRadius: 2,
                border: `1px dashed ${theme.palette.divider}`
              }}>
                <Typography variant="body2" color="text.secondary">
                  Performance Chart Coming Soon
                </Typography>
              </Box>
            </CardContent>
          </StyledCard>
        </Grid>

        {/* Positions Table */}
        <Grid item xs={12}>
          <StyledCard>
            <CardContent>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Current Positions
              </Typography>
              
              <TableContainer component={Paper} sx={{ backgroundColor: 'transparent' }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Symbol</TableCell>
                      <TableCell align="right">Quantity</TableCell>
                      <TableCell align="right">Avg Price</TableCell>
                      <TableCell align="right">Current Price</TableCell>
                      <TableCell align="right">Market Value</TableCell>
                      <TableCell align="right">Unrealized P&L</TableCell>
                      <TableCell align="right">P&L %</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {positions.map((position, index) => (
                      <TableRow key={index} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight={600}>
                            {position.symbol}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">
                            {position.quantity.toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">
                            ${position.averagePrice.toFixed(2)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" fontWeight={600}>
                            ${position.currentPrice.toFixed(2)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">
                            ${position.marketValue.toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography
                            variant="body2"
                            sx={{
                              color: position.unrealizedPnL >= 0 ? theme.palette.success.main : theme.palette.error.main,
                              fontWeight: 600,
                            }}
                          >
                            {position.unrealizedPnL >= 0 ? '+' : ''}${position.unrealizedPnL.toFixed(2)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={`${position.unrealizedPnLPercent >= 0 ? '+' : ''}${position.unrealizedPnLPercent.toFixed(2)}%`}
                            size="small"
                            color={position.unrealizedPnLPercent >= 0 ? 'success' : 'error'}
                            sx={{ fontSize: '0.75rem' }}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </StyledCard>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Portfolio;
