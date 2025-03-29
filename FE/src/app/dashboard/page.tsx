'use client';

import React from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Button, 
  Paper, 
  AppBar, 
  Toolbar, 
  Avatar
} from '@mui/material';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';

export default function Dashboard() {
  const router = useRouter();
  const { user, logout } = useAuth();
  console.log(user);
  

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <ProtectedRoute>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Dashboard
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="body1">
                {user?.username}
              </Typography>
              <Avatar sx={{ bgcolor: 'secondary.main' }}>
                {user?.username?.charAt(0).toUpperCase()}
              </Avatar>
              <Button color="inherit" onClick={handleLogout}>
                Logout
              </Button>
            </Box>
          </Toolbar>
        </AppBar>
        
        <Container maxWidth="lg" sx={{ mt: 4 }}>
          <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h4" gutterBottom>
              Welcome back, {user?.username}!
            </Typography>
            <Typography variant="body1">
              This is a protected page. Only authenticated users can see this content.
            </Typography>
          </Paper>
          
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' }, gap: 3 }}>
            {[1, 2, 3].map((item) => (
              <Paper key={item} elevation={2} sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Dashboard Card {item}
                </Typography>
                <Typography variant="body2">
                  This is a sample dashboard card. In a real application, this would display relevant user data or application features.
                </Typography>
              </Paper>
            ))}
          </Box>
        </Container>
      </Box>
    </ProtectedRoute>
  );
}