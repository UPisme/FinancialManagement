'use client';

import React, { useState } from 'react';
import { 
  Box, 
  Drawer, 
  List, 
  ListItem, 
  ListItemButton, 
  ListItemIcon, 
  ListItemText, 
  Divider, 
  IconButton,
  Typography,
  useMediaQuery,
  useTheme
} from '@mui/material';
import { 
  Dashboard as DashboardIcon,
  Receipt as ReceiptIcon,
  Category as CategoryIcon,
  BarChart as BarChartIcon,
  Settings as SettingsIcon,
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  Wallet as WalletIcon,
  Savings as SavingsGoalIcon,
  AccountBalance as BudgetIcon
} from '@mui/icons-material';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const DRAWER_WIDTH = 240;

interface SidebarProps {
  open: boolean;
  onToggle: () => void;
}

export default function Sidebar({ open, onToggle }: SidebarProps) {
  const pathname = usePathname();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Wallets', icon: <WalletIcon />, path: '/dashboard/wallets' },
    { text: 'Transactions', icon: <ReceiptIcon />, path: '/dashboard/transactions' },
    { text: 'Categories', icon: <CategoryIcon />, path: '/dashboard/categories' },
    { text: 'Goals', icon: <SavingsGoalIcon />, path: '/dashboard/goals' },
    { text: 'Budgets', icon: <BudgetIcon />, path: '/dashboard/budgets' },
    { text: 'Reports', icon: <BarChartIcon />, path: '/dashboard/reports' },
  ];

  const drawer = (
    <>
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        padding: theme.spacing(1, 1),
        ...theme.mixins.toolbar 
      }}>
        <Typography variant="h6" sx={{ ml: 2, fontWeight: 'bold' }}>
          Wallet Wizard
        </Typography>
        <IconButton onClick={onToggle}>
          <ChevronLeftIcon />
        </IconButton>
      </Box>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <Link href={item.path} style={{ textDecoration: 'none', width: '100%', color: 'inherit' }}>
              <ListItemButton
                selected={pathname === item.path}
                sx={{
                  minHeight: 48,
                  justifyContent: open ? 'initial' : 'center',
                  px: 2.5,
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(0, 0, 0, 0.08)',
                    borderLeft: `4px solid ${theme.palette.primary.main}`,
                    '&:hover': {
                      backgroundColor: 'rgba(0, 0, 0, 0.12)',
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: open ? 3 : 'auto',
                    justifyContent: 'center',
                    color: pathname === item.path ? theme.palette.primary.main : 'inherit'
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text} 
                  sx={{ 
                    opacity: open ? 1 : 0,
                    color: pathname === item.path ? theme.palette.primary.main : 'inherit'
                  }} 
                />
              </ListItemButton>
            </Link>
          </ListItem>
        ))}
      </List>
    </>
  );

  return (
    <Box component="nav" sx={{ width: { sm: open ? DRAWER_WIDTH : 0 }, flexShrink: { sm: 0 } }}>
      {isMobile ? (
        <Drawer
          variant="temporary"
          open={open}
          onClose={onToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: DRAWER_WIDTH,
              boxShadow: theme.shadows[5]
            },
          }}
        >
          {drawer}
        </Drawer>
      ) : (
        <Drawer
          variant="permanent"
          open={open}
          sx={{
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: DRAWER_WIDTH,
              transition: theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
              }),
              ...(!open && {
                overflowX: 'hidden',
                transition: theme.transitions.create('width', {
                  easing: theme.transitions.easing.sharp,
                  duration: theme.transitions.duration.leavingScreen,
                }),
                width: theme.spacing(7),
              }),
            },
          }}
        >
          {drawer}
        </Drawer>
      )}
    </Box>
  );
}
