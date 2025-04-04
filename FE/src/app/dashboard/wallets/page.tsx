'use client';
import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  useTheme,
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  Snackbar,
  Alert,
  AlertColor,
  InputAdornment
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Restore as RestoreIcon, Edit as EditIcon } from '@mui/icons-material';
import { useAuth } from '@/context/AuthContext';
import { walletService } from '@/services/api';
import { ReusableTable, Column } from '@/components/ReusableTable';
import { formatNumber } from '@/utils/format';

interface Wallet {
  id: string;
  name: string;
  balance: number;
  currency: string;
}

export default function WalletsPage() {
  const { user } = useAuth();
  const theme = useTheme();
  const [wallets, setWallets] = useState<Wallet[]>([]);
  const [deletedWallets, setDeletedWallets] = useState<Wallet[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [currentTab, setCurrentTab] = useState(0);
  const [editingWallet, setEditingWallet] = useState<Wallet | null>(null);
  const [newWallet, setNewWallet] = useState({
    name: '',
    balance: 0,
    currency: 'VND'
  });
  const [errors, setErrors] = useState({
    name: '',
    balance: ''
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  // Fetch wallets on mount and tab change
  useEffect(() => {
  const fetchData = async () => {
    try {
      setLoading(true);
      if (currentTab === 0) {
        const data = await walletService.getWallets();
        setWallets(Array.isArray(data) ? data.map((w: Wallet) => ({...w, balance: Number(w.balance)})) : []);
      } else {
        const data = await walletService.getDeletedWallets();
        setDeletedWallets(Array.isArray(data) ? data.map((w: Wallet) => ({...w, balance: Number(w.balance)})) : []);
      }
    } catch (error) {
      console.error('Fetch error:', error);
      showSnackbar('Failed to fetch wallets', 'error');
    } finally {
      setLoading(false);
    }
  };
  
  fetchData();
}, [currentTab]);

  const showSnackbar = (message: string, severity: 'success' | 'error') => {
    setSnackbar({ open: true, message, severity });
  };

  const validateForm = () => {
    const newErrors = { name: '', balance: '' };
    let isValid = true;

    if (!newWallet.name.trim()) {
      newErrors.name = 'Wallet name is required';
      isValid = false;
    }

    if (wallets.some(w => w.name === newWallet.name && w.id !== editingWallet?.id)) {
      newErrors.name = 'Wallet name already exists';
      isValid = false;
    }

    if (!editingWallet && newWallet.balance < 0) {
      newErrors.balance = 'Balance cannot be negative';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleCreateOrUpdateWallet = async () => {
    if (!validateForm()) return;

    try {
      if (editingWallet) {
        const updatedWallet = await walletService.updateWallet(
          editingWallet.id,
          newWallet
        );
        setWallets(wallets.map(w => 
          w.id === editingWallet.id ? { ...updatedWallet, balance: w.balance } : w
        ));
        showSnackbar('Wallet updated successfully', 'success');

      } else {
        const createdWallet = await walletService.createWallet(newWallet);
        setWallets([...wallets, { ...createdWallet, balance: Number(createdWallet.balance) || 0 }]);
        showSnackbar('Wallet created successfully', 'success');
      }
      handleCloseDialog();
    } catch (error) {
      console.error('Failed to save wallet:', error);
      showSnackbar('Failed to save wallet', 'error');
    }
  };

  const handleDeleteWallet = async (id: string) => {
    try {
      await walletService.deleteWallet(id);
      setWallets(wallets.filter(wallet => wallet.id !== id));
      showSnackbar('Wallet deleted successfully', 'success');
    } catch (error) {
      console.error('Failed to delete wallet:', error);
      showSnackbar('Failed to delete wallet', 'error');
    }
  };

  const handleRestoreWallet = async (id: string) => {
    try {
      await walletService.restoreWallet(id);
      setDeletedWallets(deletedWallets.filter(wallet => wallet.id !== id));
      showSnackbar('Wallet restored successfully', 'success');
    } catch (error) {
      console.error('Failed to restore wallet:', error);
      showSnackbar('Failed to restore wallet', 'error');
    }
  };

  const handleOpenEditDialog = (wallet: Wallet) => {
    setEditingWallet(wallet);
    setNewWallet({
      name: wallet.name,
      balance: Number(wallet.balance),
      currency: wallet.currency
    });
    setOpenDialog(true);
  };

  const handleOpenCreateDialog = () => {
    setEditingWallet(null);
    setNewWallet({
      name: '',
      balance: 0,
      currency: 'VND'
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingWallet(null);
    setErrors({ name: '', balance: '' });
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const walletColumns: Column[] = [
    { id: 'name', label: 'Wallet Name', align: 'center' },
    { 
      id: 'balance', 
      label: 'Balance', 
      align: 'center',
      render: (wallet: Wallet) => formatNumber(wallet.balance ?? 0)
    },
    { id: 'currency', label: 'Currency', align: 'center' },
    { id: 'actions', label: 'Actions', align: 'center' }
  ];

  const [displayBalance, setDisplayBalance] = useState(formatNumber(newWallet.balance));

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            My Wallets
          </Typography>
        </Box>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
          onClick={handleOpenCreateDialog}
          sx={{ 
            borderRadius: 2,
            boxShadow: theme.shadows[2],
            px: 3
          }}
        >
          Add Wallet
        </Button>
      </Box>

      <Tabs value={currentTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Active Wallets" />
        <Tab label="Recently Deleted" />
      </Tabs>

      {loading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <Typography>Loading...</Typography>
        </Box>
      ) : (
        <ReusableTable<Wallet>
          columns={walletColumns}
          data={currentTab === 0 ? wallets : deletedWallets}
          currentTab={currentTab}
          getCellValue={(wallet, columnId) => {
            switch (columnId) {
              case 'name': return wallet.name;
              case 'currency': return wallet.currency;
              default: return null;
            }
          }}
          getRowActions={(wallet) => ({
            primaryActions: [
              {
                icon: <EditIcon />,
                color: 'primary',
                onClick: () => handleOpenEditDialog(wallet)
              },
              {
                icon: <DeleteIcon />,
                color: 'error',
                onClick: () => handleDeleteWallet(wallet.id)
              }
            ],
            secondaryActions: [
              {
                icon: <RestoreIcon />,
                color: 'primary',
                onClick: () => handleRestoreWallet(wallet.id)
              }
            ]
          })}
        />
      )}

      {/* Add/Edit Wallet Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>
          {editingWallet ? 'Edit Wallet' : 'Create New Wallet'}
        </DialogTitle>

        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Wallet Name"
            fullWidth
            value={newWallet.name}
            onChange={(e) => setNewWallet({...newWallet, name: e.target.value})}
            error={!!errors.name}
            helperText={errors.name}
            sx={{ mt: 1 }}
          />

          {!editingWallet && (
            <TextField
              margin="dense"
              label="Initial Balance"
              type="number"
              fullWidth
              value={newWallet.balance}
              onChange={(e) => setNewWallet({
                ...newWallet, 
                balance: e.target.value === '' ? 0 : Number(e.target.value)
              })}
              error={!!errors.balance}
              helperText={errors.balance}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    {newWallet.currency === 'VND' ? '₫' : 
                     newWallet.currency === 'USD' ? '$' : 
                     newWallet.currency === 'CNY' ? '¥' : '₩'}
                  </InputAdornment>
                ),
              }}
            />
          )}

          <FormControl fullWidth margin="dense">
            <InputLabel>Currency</InputLabel>
            <Select
              value={newWallet.currency}
              label="Currency"
              onChange={(e) => setNewWallet({...newWallet, currency: e.target.value})}
            >
              <MenuItem value="VND">🇻🇳 VND</MenuItem>
              <MenuItem value="USD">🇺🇸 USD</MenuItem>
              <MenuItem value="CNY">🇨🇳 CNY</MenuItem>
              <MenuItem value="KRW">🇰🇷 KRW</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>

        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleCreateOrUpdateWallet} variant="contained">
            {editingWallet ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
        
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({...snackbar, open: false})}
      >
        <Alert 
          onClose={() => setSnackbar({...snackbar, open: false})}
          severity={snackbar.severity as AlertColor} 
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
}