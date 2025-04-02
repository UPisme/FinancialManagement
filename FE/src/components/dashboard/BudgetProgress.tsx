'use client';

import React from 'react';
import {
  Paper,
  Typography,
  Box,
  LinearProgress,
  Grid,
  useTheme,
  Tooltip
} from '@mui/material';

// Sample budget data
const budgetCategories = [
  {
    category: 'Food & Dining',
    spent: 450,
    budget: 600,
    percentage: 75
  },
  {
    category: 'Transportation',
    spent: 320,
    budget: 300,
    percentage: 107
  },
  {
    category: 'Entertainment',
    spent: 180,
    budget: 250,
    percentage: 72
  },
  {
    category: 'Shopping',
    spent: 280,
    budget: 350,
    percentage: 80
  },
  {
    category: 'Utilities',
    spent: 210,
    budget: 200,
    percentage: 105
  }
];

// Helper function to format currency
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
};

// Helper function to determine progress color
const getProgressColor = (percentage: number, theme: any) => {
  if (percentage >= 100) {
    return theme.palette.error.main;
  } else if (percentage >= 80) {
    return theme.palette.warning.main;
  } else {
    return theme.palette.success.main;
  }
};

export default function BudgetProgress() {
  const theme = useTheme();

  return (
    <Paper elevation={2} sx={{ p: 2, borderRadius: 2, mt: 3 }}>
      <Typography variant="h6" component="h2" sx={{ mb: 2 }}>
        Monthly Budget Progress
      </Typography>
      
      <Grid container spacing={2}>
        {budgetCategories.map((item, index) => (
          <Grid item xs={12} key={index} component={"div" as React.ElementType}>
            <Box sx={{ mb: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="body2" fontWeight="medium">
                  {item.category}
                </Typography>
                <Tooltip title={`${item.percentage}% of budget used`} arrow>
                  <Typography variant="body2" color="text.secondary">
                    {formatCurrency(item.spent)} / {formatCurrency(item.budget)}
                  </Typography>
                </Tooltip>
              </Box>
              <LinearProgress
                variant="determinate"
                value={Math.min(item.percentage, 100)}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: `${getProgressColor(item.percentage, theme)}20`,
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: getProgressColor(item.percentage, theme),
                    borderRadius: 4
                  }
                }}
              />
            </Box>
          </Grid>
        ))}
      </Grid>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2, pt: 2, borderTop: `1px solid ${theme.palette.divider}` }}>
        <Typography variant="subtitle2">
          Total Budget
        </Typography>
        <Typography variant="subtitle1" fontWeight="bold">
          {formatCurrency(budgetCategories.reduce((acc, curr) => acc + curr.budget, 0))}
        </Typography>
      </Box>
    </Paper>
  );
}
