'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { Box, Button, CircularProgress, Typography } from '@mui/material';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [redirecting, setRedirecting] = useState(false);

  useEffect(() => {
    // Simple function to check if a token exists in localStorage
    const hasToken = () => {
      if (typeof window !== 'undefined') {
        return !!localStorage.getItem('authToken');
      }
      return false;
    };

    console.log('ProtectedRoute - Auth State:', { 
      user: !!user, 
      loading, 
      hasToken: hasToken() 
    });
    
    // Only check authentication after loading is complete
    if (!loading && !redirecting) {
      // If no user and no token, redirect to login
      if (!user && !hasToken()) {
        console.log('ProtectedRoute - Authentication required, redirecting to login');
        setRedirecting(true);
        router.push('/login');
      } else {
        console.log('ProtectedRoute - Authentication verified, rendering content');
      }
    }
  }, [user, loading, router, redirecting]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  // If we're redirecting, show nothing to prevent flash
  if (redirecting) {
    return null;
  }
  
  // If no user but we're not redirecting yet (e.g., has token), show content
  // This allows the page to render while we're waiting for the API
  if (!user && typeof window !== 'undefined' && !localStorage.getItem('authToken')) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Typography variant="body1">You need to be logged in to view this page</Typography>
        <Button variant="contained" color="primary" onClick={() => router.push('/login')} sx={{ mt: 2 }}>
          Go to Login
        </Button>
      </Box>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;