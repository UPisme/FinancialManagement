'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Box, Typography, Container } from '@mui/material';
import AuthForm from '@/components/AuthForm';
import { useAuth } from '@/context/AuthContext';

export default function LoginPage() {
  const router = useRouter();
  const { login, loading, error } = useAuth();
  const [loginError, setLoginError] = useState<string | null>(error);

  const handleLogin = async (data: { email: string; password: string }) => {
    try {
      await login(data.email, data.password);
      router.push('/dashboard'); // Redirect to home page after successful login
    } catch (err: any) {
      setLoginError(err.response?.data?.message || 'Login failed. Please try again.');
    }
  };

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
        <Typography
          component="h1"
          variant="h4"
          sx={{ mb: 4, fontWeight: 'bold', textAlign: 'center' }}
        >
          Welcome Back
        </Typography>
        
        <AuthForm
          type="login"
          onSubmit={handleLogin}
          isLoading={loading}
          error={loginError}
        />
      </Box>
    </Container>
  );
}
