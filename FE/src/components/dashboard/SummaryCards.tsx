'use client';

import React from 'react';
import { 
  Grid, 
  Paper, 
  Typography, 
  Box, 
  useTheme,
  LinearProgress,
  Divider
} from '@mui/material';
import { 
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  AccountBalance as AccountBalanceIcon,
  Savings as SavingsIcon
} from '@mui/icons-material';

export default function SummaryCards() {
  const theme = useTheme();

  const summaryData = [
    {
      title: 'Total Balance',
      amount: '$4,567.89',
      change: '+5.2%',
      isPositive: true,
      icon: <AccountBalanceIcon sx={{ fontSize: 40, color: theme.palette.primary.main }} />,
      color: theme.palette.primary.main
    },
    {
      title: 'Monthly Expenses',
      amount: '$1,245.67',
      change: '-2.5%',
      isPositive: false,
      icon: <TrendingDownIcon sx={{ fontSize: 40, color: theme.palette.error.main }} />,
      color: theme.palette.error.main
    },
    {
      title: 'Monthly Income',
      amount: '$3,456.78',
      change: '+3.7%',
      isPositive: true,
      icon: <TrendingUpIcon sx={{ fontSize: 40, color: theme.palette.success.main }} />,
      color: theme.palette.success.main
    },
    {
      title: 'Savings',
      amount: '$2,345.67',
      change: '+8.1%',
      isPositive: true,
      icon: <SavingsIcon sx={{ fontSize: 40, color: theme.palette.info.main }} />,
      color: theme.palette.info.main
    }
  ];

  return (
    <Grid container spacing={3}>
      {summaryData.map((item, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <Paper
            elevation={2}
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 140,
              borderRadius: 2,
              position: 'relative',
              overflow: 'hidden',
              '&::after': {
                content: '""',
                position: 'absolute',
                top: 0,
                right: 0,
                width: '5px',
                height: '100%',
                backgroundColor: item.color,
              }
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                {item.title}
              </Typography>
              {item.icon}
            </Box>
            <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
              {item.amount}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              {item.isPositive ? (
                <TrendingUpIcon fontSize="small" sx={{ color: theme.palette.success.main, mr: 0.5 }} />
              ) : (
                <TrendingDownIcon fontSize="small" sx={{ color: theme.palette.error.main, mr: 0.5 }} />
              )}
              <Typography 
                variant="body2" 
                sx={{ 
                  color: item.isPositive ? theme.palette.success.main : theme.palette.error.main 
                }}
              >
                {item.change} from last month
              </Typography>
            </Box>
          </Paper>
        </Grid>
      ))}
    </Grid>
  );
}
