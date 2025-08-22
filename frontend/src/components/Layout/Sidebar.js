import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Typography,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  ShowChart as TradingIcon,
  AccountBalance as PortfolioIcon,
  Receipt as OrdersIcon,
  Star as WatchlistIcon,
  Settings as SettingsIcon,
  TrendingUp as ChartIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

const DRAWER_WIDTH = 280;

const StyledDrawer = styled(Drawer)(({ theme }) => ({
  width: DRAWER_WIDTH,
  flexShrink: 0,
  '& .MuiDrawer-paper': {
    width: DRAWER_WIDTH,
    boxSizing: 'border-box',
    backgroundColor: theme.palette.background.paper,
    borderRight: `1px solid ${theme.palette.divider}`,
  },
}));

const LogoSection = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3, 2),
  borderBottom: `1px solid ${theme.palette.divider}`,
  textAlign: 'center',
}));

const LogoText = styled(Typography)(({ theme }) => ({
  fontSize: '1.5rem',
  fontWeight: 700,
  background: 'linear-gradient(45deg, #00d4aa, #4dffdf)',
  backgroundClip: 'text',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
}));

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Trading', icon: <TradingIcon />, path: '/trading' },
  { text: 'Portfolio', icon: <PortfolioIcon />, path: '/portfolio' },
  { text: 'Orders', icon: <OrdersIcon />, path: '/orders' },
  { text: 'Watchlist', icon: <WatchlistIcon />, path: '/watchlist' },
  { text: 'Charts', icon: <ChartIcon />, path: '/charts' },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
];

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleNavigation = (path) => {
    navigate(path);
  };

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <StyledDrawer
      variant={isMobile ? 'temporary' : 'permanent'}
      anchor="left"
    >
      <LogoSection>
        <LogoText>VittCott</LogoText>
        <Typography variant="caption" color="text.secondary">
          Trading Platform
        </Typography>
      </LogoSection>
      
      <Divider />
      
      <List sx={{ pt: 2 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              onClick={() => handleNavigation(item.path)}
              selected={isActive(item.path)}
              sx={{
                mx: 1,
                borderRadius: 2,
                mb: 0.5,
                '&.Mui-selected': {
                  backgroundColor: 'rgba(0, 212, 170, 0.1)',
                  '&:hover': {
                    backgroundColor: 'rgba(0, 212, 170, 0.15)',
                  },
                },
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color: isActive(item.path) ? theme.palette.primary.main : 'inherit',
                  minWidth: 40,
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                primaryTypographyProps={{
                  fontWeight: isActive(item.path) ? 600 : 400,
                  color: isActive(item.path) ? theme.palette.primary.main : 'inherit',
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </StyledDrawer>
  );
};

export default Sidebar;
