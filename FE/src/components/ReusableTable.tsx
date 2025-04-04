import React from 'react';
import {
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Paper,
  IconButton
} from '@mui/material';

export interface Column {
  id: string;
  label: string;
  align?: 'left' | 'center' | 'right';
  width?: string;
  render?: (data: any) => React.ReactNode;
}

interface ActionButton {
  icon: React.ReactNode;
  color: 'inherit' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  onClick: () => void;
}

interface ReusableTableProps<T> {
  columns: Column[];
  data: T[];
  currentTab: number;
  getCellValue: (item: T, columnId: string) => React.ReactNode;
  getRowActions: (item: T) => {
    primaryActions?: ActionButton[];
    secondaryActions?: ActionButton[];
  };
}

export function ReusableTable<T extends { id: string }>({
  columns,
  data,
  currentTab,
  getCellValue,
  getRowActions
}: ReusableTableProps<T>) {
  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            {columns.map((column) => (
              <TableCell
                key={column.id}
                sx={{
                  fontWeight: 'bold',
                  textAlign: column.align || 'center',
                  width: column.width
                }}
              >
                {column.label}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((item) => {
            const { primaryActions = [], secondaryActions = [] } = getRowActions(item);
            const actions = currentTab === 0 ? primaryActions : secondaryActions;
            
            return (
              <TableRow
                key={item.id}
                hover
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                {columns.map((column) => (
                  <TableCell
                    key={`${item.id}-${column.id}`}
                    sx={{ textAlign: column.align || 'center' }}
                  >
                    {column.id === 'actions' ? (
                      actions.map((action, index) => (
                        <IconButton
                          key={index}
                          onClick={action.onClick}
                          color={action.color}
                          size="small"
                        >
                          {action.icon}
                        </IconButton>
                      ))
                    ) : column.render ? (
                      column.render(item)
                    ) : (
                      getCellValue(item, column.id)
                    )}
                  </TableCell>
                ))}
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
}