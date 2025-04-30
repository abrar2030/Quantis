import React from 'react';
import { Box, Typography, useTheme } from '@mui/material';

const BarChart = ({ data }) => {
  const theme = useTheme();
  
  // This is a placeholder component that would use Nivo charts in a real implementation
  // For now, we'll just display a placeholder with simulated bars
  
  return (
    <Box 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: theme.palette.background.default,
        borderRadius: 1,
        p: 2
      }}
    >
      <Typography variant="body1" color="text.secondary" align="center">
        Feature Importance
      </Typography>
      <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1, mb: 3 }}>
        Top 5 influential features in the model
      </Typography>
      
      <Box sx={{ width: '100%', height: '70%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        {data.map((item, index) => (
          <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Typography variant="caption" sx={{ width: 80, mr: 1 }}>
              {item.feature}
            </Typography>
            <Box 
              sx={{ 
                height: 20, 
                width: `${item.value * 100}%`, 
                backgroundColor: theme.palette.primary.main,
                opacity: 0.7 + ((5-index) * 0.06), // Decreasing opacity for lower values
                borderRadius: 1
              }} 
            />
            <Typography variant="caption" sx={{ ml: 1 }}>
              {(item.value * 100).toFixed(0)}%
            </Typography>
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default BarChart;
