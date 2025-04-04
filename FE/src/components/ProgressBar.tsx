import { LinearProgress, Box, Typography, Stack } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { formatNumber } from '@/utils/format';

interface ProgressBarProps {
  value: number;
  target: number;
}

export const ProgressBar = ({ value, target }: ProgressBarProps) => {
  const theme = useTheme();
  const percentage = Math.min(Math.round((value / target) * 100), 100);
  
  return (
    <Box sx={{ width: '100%' }}>
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 0.5 }}>
        <Box sx={{ flexGrow: 1 }}>
          <LinearProgress 
            variant="determinate" 
            value={percentage}
            sx={{
              height: 10,
              borderRadius: 5,
              backgroundColor: theme.palette.grey[300],
              '& .MuiLinearProgress-bar': {
                borderRadius: 5,
                backgroundColor: theme.palette.primary.main
              }
            }}
          />
        </Box>
        <Typography variant="body2" color="text.primary" sx={{ minWidth: 40 }}>
          {percentage}%
        </Typography>
      </Stack>

      <Typography variant="body2" color="text.secondary" align="left">
        Saved: {formatNumber(value)}/{formatNumber(target)}
      </Typography>
    </Box>
  );
};