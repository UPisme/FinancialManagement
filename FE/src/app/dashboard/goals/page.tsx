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
  Tabs,
  Tab,
  Snackbar,
  Alert,
  AlertColor
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Restore as RestoreIcon, Edit as EditIcon } from '@mui/icons-material';
import { useAuth } from '@/context/AuthContext';
import { goalService } from '@/services/api';
import { ReusableTable, Column } from '@/components/ReusableTable';
import { ProgressBar } from '@/components/ProgressBar';

interface Goal {
    id: string;
    name: string;
    target_amount: number;
    saved_amount: number;
    deadline: string;
  }

export default function GoalsPage() {
  const { user } = useAuth();
  const theme = useTheme();
  const [goals, setGoals] = useState<Goal[]>([]);
  const [deletedGoals, setDeletedGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [currentTab, setCurrentTab] = useState(0);
  const [editingGoal, setEditingGoal] = useState<Goal | null>(null);
  const [newGoal, setNewGoal] = useState({
    name: '',
    target_amount: 0,
    saved_amount: 0,
    deadline: ''
  });
  const [errors, setErrors] = useState({
    name: '',
    target_amount: '',
    saved_amount: '',
    deadline: ''
  });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        if (currentTab === 0) {
          const data = await goalService.getGoals();
          setGoals(data || []);
        } else {
          const data = await goalService.getDeletedGoals();
          setDeletedGoals(data || []);
        }
      } catch (error) {
        showSnackbar('Failed to fetch goals', 'error');
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
    const newErrors = {
      name: '',
      target_amount: '',
      saved_amount: '', 
      deadline: ''
    };
    let isValid = true;
  
    // Validate name
    if (!newGoal.name.trim()) {
      newErrors.name = 'Goal name is required';
      isValid = false;
    } else if (goals.some(g => g.name === newGoal.name && g.id !== editingGoal?.id)) {
      newErrors.name = 'Goal name already exists';
      isValid = false;
    }
  
    // Validate target amount
    if (newGoal.target_amount === null || newGoal.target_amount === undefined || Number(newGoal.target_amount) <= 0) {
      newErrors.target_amount = 'Target amount is required and must be greater than 0';
      isValid = false;
    }
  
    // Validate saved amount
    if (newGoal.saved_amount < 0) {
      newErrors.saved_amount = 'Saved amount cannot be negative';
      isValid = false;
    }
  
    // Validate deadline
    if (!newGoal.deadline) {
      newErrors.deadline = 'Deadline is required';
      isValid = false;
    } else {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const deadlineDate = new Date(newGoal.deadline);
      
      if (deadlineDate < today) {
        newErrors.deadline = 'Deadline must be in the future';
        isValid = false;
      }
    }
  
    setErrors(newErrors);
    return isValid;
  };

  const handleCreateOrUpdateGoal = async () => {
    if (!validateForm()) return;
  
    try {
      if (editingGoal) {
        await goalService.updateGoal(editingGoal.id, newGoal);
        setGoals(goals.map(g => (g.id === editingGoal.id ? { ...g, ...newGoal } : g)));
        showSnackbar('Goal updated successfully', 'success');
      } else {
        const createdGoal = await goalService.createGoal(newGoal);
        setGoals([...goals, createdGoal]);
        showSnackbar('Goal created successfully', 'success');
      }
      handleCloseDialog();
    } catch (error) {
      showSnackbar('Failed to save goal', 'error');
    }
  };

  const handleDeleteGoal = async (id: string) => {
    try {
      await goalService.deleteGoal(id);
      setGoals(goals.filter(goal => goal.id !== id));
      showSnackbar('Goal deleted successfully', 'success');
    } catch (error) {
      showSnackbar('Failed to delete goal', 'error');
    }
  };

  const handleRestoreGoal = async (id: string) => {
    try {
      await goalService.restoreGoal(id);
      setDeletedGoals(deletedGoals.filter(goal => goal.id !== id));
      showSnackbar('Goal restored successfully', 'success');
    } catch (error) {
      showSnackbar('Failed to restore goal', 'error');
    }
  };

  const handleOpenEditDialog = (goal: Goal) => {
    setEditingGoal(goal);
    setNewGoal({ 
        name: goal.name,
        target_amount: Number(goal.target_amount),
        saved_amount: Number(goal.saved_amount),
        deadline: goal.deadline
    });
    setOpenDialog(true);
  };

  const handleOpenCreateDialog = () => {
    setEditingGoal(null);
    setNewGoal({ 
        name: '',
        target_amount: 0,
        saved_amount: 0,
        deadline: '' 
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingGoal(null);
  };

  const goalColumns: Column[] = [
    { 
      id: 'name', 
      label: 'Goal Name', 
      align: 'center',
      width: '25%'
    },
    { 
      id: 'progress', 
      label: 'Progress', 
      align: 'center',
      width: '35%',
      render: (goal: Goal) => (
        <ProgressBar 
          value={goal.saved_amount} 
          target={goal.target_amount} 
        />
      )
    },
    { 
      id: 'deadline', 
      label: 'Deadline', 
      align: 'center',
      width: '20%',
      render: (goal: Goal) => goal.deadline ? new Date(goal.deadline).toLocaleDateString() : '-'
    },
    { 
      id: 'actions', 
      label: 'Actions', 
      align: 'center',
      width: '20%'
    }
  ];

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
            Goals
        </Typography>
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
          Add Goal
        </Button>
      </Box>

      <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="Active Goals" />
        <Tab label="Recently Deleted" />
      </Tabs>

      {loading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <Typography>Loading...</Typography>
        </Box>
      ) : (
        <ReusableTable<Goal>
          columns={goalColumns}
          data={currentTab === 0 ? goals : deletedGoals}
          currentTab={currentTab}
          getCellValue={(goal, columnId) => {
            switch (columnId) {
              case 'name': return goal.name;
              default: return null;
            }
          }}
          getRowActions={(goal) => ({
            primaryActions: [
              {
                icon: <EditIcon />,
                color: 'primary',
                onClick: () => handleOpenEditDialog(goal)
              },
              {
                icon: <DeleteIcon />,
                color: 'error',
                onClick: () => handleDeleteGoal(goal.id)
              }
            ],
            secondaryActions: currentTab === 1 ? [
              {
                icon: <RestoreIcon />,
                color: 'primary',
                onClick: () => handleRestoreGoal(goal.id)
              }
            ] : []
          })}
        />
      )}

      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>{editingGoal ? 'Edit Goal' : 'Create New Goal'}</DialogTitle>
        <DialogContent>
            <TextField
                autoFocus
                margin="dense"
                label="Goal Name"
                fullWidth
                value={newGoal.name}
                onChange={(e) => setNewGoal({...newGoal, name: e.target.value})}
                error={!!errors.name}
                helperText={errors.name}
                sx={{ mt: 1 }}
            />
            
            <TextField
                margin="dense"
                label="Target Amount"
                type="number"
                fullWidth
                value={newGoal.target_amount || ''}
                onChange={(e) => setNewGoal({
                ...newGoal, 
                target_amount: e.target.value === '' ? 0 : Number(e.target.value)
                })}
                error={!!errors.target_amount}
                helperText={errors.target_amount}
                inputProps={{ min: "0.01", step: "0.01" }}
            />
            
            <TextField
                margin="dense"
                label="Saved Amount"
                type="number"
                fullWidth
                value={newGoal.saved_amount}
                onChange={(e) => setNewGoal({
                ...newGoal, 
                saved_amount: e.target.value === '' ? 0 : Number(e.target.value)
                })}
                error={!!errors.saved_amount}
                helperText={errors.saved_amount}
                inputProps={{ min: "0" }}
            />
            
            <TextField
              margin="dense"
              label="Deadline"
              type="date"
              fullWidth
              required 
              InputLabelProps={{ shrink: true }}
              value={newGoal.deadline}
              onChange={(e) => setNewGoal({
                ...newGoal, 
                deadline: e.target.value
              })}
              error={!!errors.deadline}
              helperText={errors.deadline}
            />
        </DialogContent>
        <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button onClick={handleCreateOrUpdateGoal} variant="contained">
            {editingGoal ? 'Update' : 'Create'}
            </Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={snackbar.open} autoHideDuration={6000} onClose={() => setSnackbar({ ...snackbar, open: false })}>
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