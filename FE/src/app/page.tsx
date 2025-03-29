'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { 
  Box, 
  Typography, 
  Container, 
  Button, 
  Paper, 
  AppBar, 
  Toolbar, 
  Avatar,
  CircularProgress
} from '@mui/material';
import { useAuth } from '@/context/AuthContext';

export default function Home() {
  const router = useRouter();
  const { user, loading, logout } = useAuth();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (!user) {
    return (
      <Container maxWidth="lg">
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            py: 4,
          }}
        >
          <Paper elevation={3} sx={{ p: 4, width: '100%', maxWidth: 600, textAlign: 'center' }}>
            <Typography variant="h4" component="h1" gutterBottom>
              Welcome to Wallet Wizard
            </Typography>
            <Typography variant="body1" paragraph>
              Sign in to track your gold like a wizard!
            </Typography>
            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center', gap: 2 }}>
              <Button 
                variant="contained" 
                color="primary" 
                onClick={() => router.push('/login')}
              >
                Sign In
              </Button>
              <Button 
                variant="outlined" 
                onClick={() => router.push('/register')}
              >
                Create Account
              </Button>
            </Box>
          </Paper>
        </Box>
      </Container>
    );
  }

  return (
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
            Welcome back, {user.username}!
          </Typography>
          <Typography variant="body1">
            You are now signed in to your account.
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
  );
}
