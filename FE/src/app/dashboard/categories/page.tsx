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
import { categoryService } from '@/services/api';
import { ReusableTable, Column } from '@/components/ReusableTable';

interface Category {
  id: string;
  name: string;
}

export default function CategoriesPage() {
  const { user } = useAuth();
  const theme = useTheme();
  const [categories, setCategories] = useState<Category[]>([]);
  const [deletedCategories, setDeletedCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [currentTab, setCurrentTab] = useState(0);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [newCategory, setNewCategory] = useState({ name: '' });
  const [errors, setErrors] = useState({ name: '' });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        if (currentTab === 0) {
          const data = await categoryService.getCategories();
          setCategories(data || []);
        } else {
          const data = await categoryService.getDeletedCategories();
          setDeletedCategories(data || []);
        }
      } catch (error) {
        showSnackbar('Failed to fetch categories', 'error');
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
    const newErrors = { name: '' };
    let isValid = true;

    if (!newCategory.name.trim()) {
      newErrors.name = 'Category name is required';
      isValid = false;
    }

    if (categories.some(c => c.name === newCategory.name && c.id !== editingCategory?.id)) {
      newErrors.name = 'Category name already exists';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleCreateOrUpdateCategory = async () => {
    if (!validateForm()) return;

    try {
      if (editingCategory) {
        await categoryService.updateCategory(editingCategory.id, newCategory);
        setCategories(categories.map(c => (c.id === editingCategory.id ? { ...c, ...newCategory } : c)));
        showSnackbar('Category updated successfully', 'success');
      } else {
        const createdCategory = await categoryService.createCategory(newCategory);
        setCategories([...categories, createdCategory]);
        showSnackbar('Category created successfully', 'success');
      }
      handleCloseDialog();
    } catch (error) {
      showSnackbar('Failed to save category', 'error');
    }
  };

  const handleDeleteCategory = async (id: string) => {
    try {
      await categoryService.deleteCategory(id);
      setCategories(categories.filter(category => category.id !== id));
      showSnackbar('Category deleted successfully', 'success');
    } catch (error) {
      showSnackbar('Failed to delete category', 'error');
    }
  };

  const handleRestoreCategory = async (id: string) => {
    try {
      await categoryService.restoreCategory(id);
      setDeletedCategories(deletedCategories.filter(category => category.id !== id));
      showSnackbar('Category restored successfully', 'success');
    } catch (error) {
      showSnackbar('Failed to restore category', 'error');
    }
  };

  const handleOpenEditDialog = (category: Category) => {
    setEditingCategory(category);
    setNewCategory({ name: category.name });
    setOpenDialog(true);
  };

  const handleOpenCreateDialog = () => {
    setEditingCategory(null);
    setNewCategory({ name: '' });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingCategory(null);
  };

  const categoryColumns: Column[] = [
    { id: 'name', label: 'Category Name', align: 'center' },
    { id: 'actions', label: 'Actions', align: 'center' }
  ];

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
            Categories
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
          Add Category
        </Button>
      </Box>

      <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="Active Categories" />
        <Tab label="Recently Deleted" />
      </Tabs>

      {loading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <Typography>Loading...</Typography>
        </Box>
      ) : (
        <ReusableTable<Category>
          columns={categoryColumns}
          data={currentTab === 0 ? categories : deletedCategories}
          currentTab={currentTab}
          getCellValue={(category, columnId) => {
            switch (columnId) {
              case 'name': return category.name;
              default: return null;
            }
          }}
          getRowActions={(category) => ({
            primaryActions: [
              {
                icon: <EditIcon />,
                color: 'primary',
                onClick: () => handleOpenEditDialog(category)
              },
              {
                icon: <DeleteIcon />,
                color: 'error',
                onClick: () => handleDeleteCategory(category.id)
              }
            ],
            secondaryActions: [
              {
                icon: <RestoreIcon />,
                color: 'primary',
                onClick: () => handleRestoreCategory(category.id)
              }
            ]
          })}
        />
      )}

      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>{editingCategory ? 'Edit Category' : 'Create New Category'}</DialogTitle>
        <DialogContent>
          <TextField 
            autoFocus
            margin="dense"
            label="Category Name"
            fullWidth value={newCategory.name}
            onChange={(e) => setNewCategory({ name: e.target.value })}
            error={!!errors.name}
            helperText={errors.name}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleCreateOrUpdateCategory} variant="contained">Save</Button>
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