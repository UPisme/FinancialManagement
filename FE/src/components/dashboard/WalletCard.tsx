'use client';
import { Card, CardContent, Typography, IconButton, Box } from '@mui/material';
import { Delete as DeleteIcon } from '@mui/icons-material';

interface WalletCardProps {
  wallet: {
    id: string;
    name: string;
    balance: number;
    currency: string;
  };
  onDelete: (id: string) => void;
}

export default function WalletCard({ wallet, onDelete }: WalletCardProps) {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between">
          <Box>
            <Typography variant="h6">{wallet.name}</Typography>
            <Typography variant="body2" color="text.secondary">
              {wallet.currency}
            </Typography>
            <Typography variant="h5" mt={1}>
              ${wallet.balance.toFixed(2)}
            </Typography>
          </Box>
          <IconButton 
            onClick={() => onDelete(wallet.id)}
            color="error"
          >
            <DeleteIcon />
          </IconButton>
        </Box>
      </CardContent>
    </Card>
  );
}