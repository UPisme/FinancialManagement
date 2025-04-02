'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Box, Typography, Container } from '@mui/material';
import AuthForm from '@/components/AuthForm';
import { useAuth } from '@/context/AuthContext';

export default function RegisterPage() {
  const router = useRouter();
  const { register, loading, error } = useAuth();
  const [registerError, setRegisterError] = useState<string | null>(error);

  const handleRegister = async (data: { username: string; email: string; password: string }) => {
    try {
      await register(data.username, data.email, data.password);
      // Redirect to login page after successful registration
      router.push('/login?registered=true');
    } catch (err: any) {
      setRegisterError(err.response?.data?.message || 'Registration failed. Please try again.');
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
          Create Your Account
        </Typography>
        
        <AuthForm
          type="register"
          onSubmit={handleRegister}
          isLoading={loading}
          error={registerError}
        />
      </Box>
    </Container>
  );
}
