'use client';

import React from 'react';
import {
  Paper,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
  Divider,
  Button,
  useTheme
} from '@mui/material';
import {
  ShoppingCart as ShoppingCartIcon,
  Fastfood as FastfoodIcon,
  DirectionsCar as DirectionsCarIcon,
  Home as HomeIcon,
  LocalHospital as LocalHospitalIcon,
  School as SchoolIcon
} from '@mui/icons-material';

// Sample transaction data
const transactions = [
  {
    id: 1,
    title: 'Grocery Shopping',
    amount: -85.75,
    date: '2025-03-28',
    category: 'Shopping',
    // icon: <ShoppingCartIcon />
  },
  {
    id: 2,
    title: 'Restaurant Dinner',
    amount: -42.50,
    date: '2025-03-27',
    category: 'Food',
    // icon: <FastfoodIcon />
  },
  {
    id: 3,
    title: 'Salary Deposit',
    amount: 3500.00,
    date: '2025-03-25',
    category: 'Income',
    // icon: <HomeIcon />
  },
  {
    id: 4,
    title: 'Gas Station',
    amount: -45.30,
    date: '2025-03-24',
    category: 'Transportation',
    // icon: <DirectionsCarIcon />
  },
  {
    id: 5,
    title: 'Medical Checkup',
    amount: -120.00,
    date: '2025-03-23',
    category: 'Healthcare',
    // icon: <LocalHospitalIcon />
  }
];

// Helper function to format currency
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  }).format(amount);
};

// Helper function to get icon color based on category
const getCategoryColor = (category: string, theme: any) => {
  const categoryColors: Record<string, string> = {
    Shopping: theme.palette.info.main,
    Food: theme.palette.warning.main,
    Income: theme.palette.success.main,
    Transportation: theme.palette.primary.main,
    Healthcare: theme.palette.error.main,
    Education: theme.palette.secondary.main
  };
  
  return categoryColors[category] || theme.palette.grey[500];
};

export default function RecentTransactions() {
  const theme = useTheme();

  return (
    <Paper elevation={2} sx={{ p: 2, borderRadius: 2, mt: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" component="h2">
          Recent Transactions
        </Typography>
        <Button size="small" color="primary">
          View All
        </Button>
      </Box>
      
      <List sx={{ width: '100%' }}>
        {transactions.map((transaction, index) => (
          <React.Fragment key={transaction.id}>
            <ListItem alignItems="flex-start" sx={{ py: 1.5 }}>
              {/* <ListItemAvatar>
                <Avatar sx={{ bgcolor: getCategoryColor(transaction.category, theme) }}>
                  {transaction.icon}
                </Avatar>
              </ListItemAvatar> */}
              <ListItemText
                primary={transaction.title}
                secondary={
                  <React.Fragment>
                    <Typography
                      component="span"
                      variant="body2"
                      color="text.primary"
                    >
                      {new Date(transaction.date).toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric', 
                        year: 'numeric' 
                      })}
                    </Typography>
                    {' — '}
                    <Chip 
                      label={transaction.category} 
                      size="small" 
                      sx={{ 
                        fontSize: '0.7rem', 
                        height: 20,
                        backgroundColor: `${getCategoryColor(transaction.category, theme)}20`,
                        color: getCategoryColor(transaction.category, theme),
                        ml: 1
                      }} 
                    />
                  </React.Fragment>
                }
              />
              <Typography 
                variant="body1" 
                sx={{ 
                  fontWeight: 'bold',
                  color: transaction.amount >= 0 ? theme.palette.success.main : theme.palette.error.main
                }}
              >
                {formatCurrency(transaction.amount)}
              </Typography>
            </ListItem>
            {index < transactions.length - 1 && (
              <Divider variant="inset" component="li" />
            )}
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
}
