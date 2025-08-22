import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  useTheme,
  Paper
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  AccountBalance as AccountBalanceIcon,
  ShowChart as ChartIcon,
  Receipt as ReceiptIcon
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

const PortfolioCard = () => {
  const theme = useTheme();
  
  return (
    <StyledCard>
      <CardContent>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Portfolio Allocation
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2">Stocks</Typography>
            <Typography variant="body2" fontWeight={600}>65%</Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={65}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: theme.palette.divider,
              '& .MuiLinearProgress-bar': {
                backgroundColor: theme.palette.primary.main,
                borderRadius: 4,
              },
            }}
          />
        </Box>
        
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2">Bonds</Typography>
            <Typography variant="body2" fontWeight={600}>25%</Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={25}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: theme.palette.divider,
              '& .MuiLinearProgress-bar': {
                backgroundColor: theme.palette.secondary.main,
                borderRadius: 4,
              },
            }}
          />
        </Box>
        
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2">Cash</Typography>
            <Typography variant="body2" fontWeight={600}>10%</Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={10}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: theme.palette.divider,
              '& .MuiLinearProgress-bar': {
                backgroundColor: theme.palette.warning.main,
                borderRadius: 4,
              },
            }}
          />
        </Box>
      </CardContent>
    </StyledCard>
  );
};

const RecentActivityCard = () => {
  const activities = [
    { type: 'buy', symbol: 'AAPL', quantity: 100, price: 150.25, time: '2 min ago' },
    { type: 'sell', symbol: 'GOOGL', quantity: 50, price: 2800.00, time: '15 min ago' },
    { type: 'buy', symbol: 'TSLA', quantity: 25, price: 245.80, time: '1 hour ago' },
    { type: 'sell', symbol: 'MSFT', quantity: 75, price: 380.50, time: '2 hours ago' },
  ];
  
  return (
    <StyledCard>
      <CardContent>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Recent Activity
        </Typography>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {activities.map((activity, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                p: 1,
                borderRadius: 1,
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip
                  label={activity.type.toUpperCase()}
                  size="small"
                  color={activity.type === 'buy' ? 'success' : 'error'}
                  sx={{ fontSize: '0.7rem' }}
                />
                <Typography variant="body2" fontWeight={600}>
                  {activity.symbol}
                </Typography>
              </Box>
              
              <Box sx={{ textAlign: 'right' }}>
                <Typography variant="body2" fontWeight={600}>
                  {activity.quantity} @ ${activity.price}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {activity.time}
                </Typography>
              </Box>
            </Box>
          ))}
        </Box>
      </CardContent>
    </StyledCard>
  );
};

const Dashboard = () => {
  const theme = useTheme();
  
  return (
    <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700, mb: 4 }}>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Key Metrics */}
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Portfolio Value"
            value="$125,430.50"
            change={2,450.75}
            changePercent={2.0}
            icon={<AccountBalanceIcon sx={{ color: 'white' }} />}
            color="primary"
          />
        </Grid>
        
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Daily P&L"
            value="$2,450.75"
            change={450.25}
            changePercent={22.5}
            icon={<TrendingUpIcon sx={{ color: 'white' }} />}
            color="success"
          />
        </Grid>
        
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Open Orders"
            value="5"
            change={-2}
            changePercent={-28.6}
            icon={<ReceiptIcon sx={{ color: 'white' }} />}
            color="warning"
          />
        </Grid>
        
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Active Positions"
            value="12"
            change={1}
            changePercent={9.1}
            icon={<ChartIcon sx={{ color: 'white' }} />}
            color="info"
          />
        </Grid>
        
        {/* Portfolio and Activity */}
        <Grid item xs={12} md={6}>
          <PortfolioCard />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <RecentActivityCard />
        </Grid>
        
        {/* Market Overview */}
        <Grid item xs={12}>
          <StyledCard>
            <CardContent>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Market Overview
              </Typography>
              
              <Grid container spacing={2}>
                {['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META'].map((symbol) => (
                  <Grid item xs={6} sm={4} md={2} key={symbol}>
                    <Paper
                      sx={{
                        p: 2,
                        textAlign: 'center',
                        backgroundColor: 'rgba(255, 255, 255, 0.02)',
                        border: `1px solid ${theme.palette.divider}`,
                      }}
                    >
                      <Typography variant="h6" fontWeight={600} gutterBottom>
                        {symbol}
                      </Typography>
                      <Typography variant="body2" color="success.main" fontWeight={600}>
                        +2.45%
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        $150.25
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </StyledCard>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
