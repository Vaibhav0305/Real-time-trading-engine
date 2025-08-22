import React from 'react';
import { Box } from '@mui/material';
import { styled } from '@mui/material/styles';

const LayoutContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  minHeight: '100vh',
  backgroundColor: theme.palette.background.default,
  color: theme.palette.text.primary,
}));

const MainContent = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  overflow: 'hidden',
}));

const Layout = ({ children }) => {
  return (
    <LayoutContainer>
      <MainContent>
        {children}
      </MainContent>
    </LayoutContainer>
  );
};

export default Layout;
