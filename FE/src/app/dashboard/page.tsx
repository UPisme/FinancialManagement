'use client';

import React from 'react';
import { 
  Box, 
  Typography, 
  Grid,
  Paper,
  Button,
  useTheme
} from '@mui/material';
import { useAuth } from '@/context/AuthContext';
import SummaryCards from '@/components/dashboard/SummaryCards';
import RecentTransactions from '@/components/dashboard/RecentTransactions';
import BudgetProgress from '@/components/dashboard/BudgetProgress';
import { Add as AddIcon } from '@mui/icons-material';

export default function Dashboard() {
  const { user } = useAuth();
  const theme = useTheme();

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Welcome back, {user?.username}! Here's your financial overview.
          </Typography>
        </Box>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
          sx={{ 
            borderRadius: 2,
            boxShadow: theme.shadows[2],
            px: 3
          }}
        >
          Add Expense
        </Button>
      </Box>

      {/* Summary Cards */}
      <SummaryCards />
      
      {/* Main Content Grid */}
      <Grid container spacing={3} sx={{ mt: 1 }}>
        {/* Left Column - Recent Transactions */}
        <Grid item xs={12} md={8}>
          <RecentTransactions />
          
          {/* Expense Distribution Chart - Placeholder */}
          <Paper elevation={2} sx={{ p: 2, borderRadius: 2, mt: 3, height: 300, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <Typography variant="h6" color="text.secondary">
              Expense Distribution Chart
            </Typography>
          </Paper>
        </Grid>
        
        {/* Right Column - Budget Progress */}
        <Grid item xs={12} md={4}>
          <BudgetProgress />
          
          {/* Upcoming Bills - Placeholder */}
          <Paper elevation={2} sx={{ p: 2, borderRadius: 2, mt: 3, height: 300, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <Typography variant="h6" color="text.secondary">
              Upcoming Bills
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </>
  );
}