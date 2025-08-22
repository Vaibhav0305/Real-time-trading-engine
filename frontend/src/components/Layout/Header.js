import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Badge,
  Avatar,
  Menu,
  MenuItem,
  Chip,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  AccountCircle as AccountIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Circle as CircleIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

const StyledAppBar = styled(AppBar)(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  borderBottom: `1px solid ${theme.palette.divider}`,
  boxShadow: 'none',
  zIndex: theme.zIndex.drawer + 1,
}));

const StatusChip = styled(Chip)(({ theme, status }) => ({
  backgroundColor: status === 'connected' 
    ? theme.palette.success.main 
    : theme.palette.error.main,
  color: theme.palette.common.white,
  fontSize: '0.75rem',
  height: 24,
  '& .MuiChip-label': {
    padding: '0 8px',
  },
}));

const Header = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [anchorEl, setAnchorEl] = useState(null);
  const [notificationsAnchor, setNotificationsAnchor] = useState(null);

  // Mock data - in real app, this would come from context/state
  const isConnected = true;
  const notifications = 3;
  const currentSymbol = 'AAPL';
  const currentPrice = 150.25;
  const priceChange = 2.15;
  const priceChangePercent = 1.45;

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationsOpen = (event) => {
    setNotificationsAnchor(event.currentTarget);
  };

  const handleNotificationsClose = () => {
    setNotificationsAnchor(null);
  };

  const isMenuOpen = Boolean(anchorEl);
  const isNotificationsOpen = Boolean(notificationsAnchor);

  const menuId = 'primary-search-account-menu';
  const notificationsId = 'notifications-menu';

  return (
    <StyledAppBar position="static">
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        {/* Left side - Current symbol and price */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
            {currentSymbol}
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h6" component="span" sx={{ fontWeight: 600 }}>
              ${currentPrice.toFixed(2)}
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              {priceChange >= 0 ? (
                <TrendingUpIcon 
                  sx={{ 
                    color: theme.palette.success.main, 
                    fontSize: '1rem' 
                  }} 
                />
              ) : (
                <TrendingDownIcon 
                  sx={{ 
                    color: theme.palette.error.main, 
                    fontSize: '1rem' 
                  }} 
                />
              )}
              
              <Typography
                variant="body2"
                sx={{
                  color: priceChange >= 0 ? theme.palette.success.main : theme.palette.error.main,
                  fontWeight: 600,
                }}
              >
                {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)} ({priceChangePercent.toFixed(2)}%)
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Right side - Status, notifications, profile */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Connection Status */}
          <StatusChip
            status={isConnected ? 'connected' : 'disconnected'}
            label={isConnected ? 'Connected' : 'Disconnected'}
            icon={<CircleIcon sx={{ fontSize: '0.75rem' }} />}
          />

          {/* Notifications */}
          <IconButton
            size="large"
            aria-label="show notifications"
            aria-controls={notificationsId}
            aria-haspopup="true"
            onClick={handleNotificationsOpen}
            sx={{ color: theme.palette.text.primary }}
          >
            <Badge badgeContent={notifications} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>

          {/* Profile Menu */}
          <IconButton
            size="large"
            edge="end"
            aria-label="account of current user"
            aria-controls={menuId}
            aria-haspopup="true"
            onClick={handleProfileMenuOpen}
            sx={{ color: theme.palette.text.primary }}
          >
            <Avatar sx={{ width: 32, height: 32, bgcolor: theme.palette.primary.main }}>
              <AccountIcon />
            </Avatar>
          </IconButton>
        </Box>
      </Toolbar>

      {/* Profile Menu */}
      <Menu
        anchorEl={anchorEl}
        id={menuId}
        keepMounted
        open={isMenuOpen}
        onClose={handleProfileMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={handleProfileMenuClose}>Profile</MenuItem>
        <MenuItem onClick={handleProfileMenuClose}>My account</MenuItem>
        <MenuItem onClick={handleProfileMenuClose}>Settings</MenuItem>
        <MenuItem onClick={handleProfileMenuClose}>Logout</MenuItem>
      </Menu>

      {/* Notifications Menu */}
      <Menu
        anchorEl={notificationsAnchor}
        id={notificationsId}
        keepMounted
        open={isNotificationsOpen}
        onClose={handleNotificationsClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={handleNotificationsClose}>
          Order filled: AAPL 100 shares at $150.25
        </MenuItem>
        <MenuItem onClick={handleNotificationsClose}>
          New market data available for GOOGL
        </MenuItem>
        <MenuItem onClick={handleNotificationsClose}>
          System maintenance scheduled for tonight
        </MenuItem>
      </Menu>
    </StyledAppBar>
  );
};

export default Header;
