import React from 'react';
import { Box, Typography, useTheme } from '@mui/material';

const LineChart = ({ data }) => {
  const theme = useTheme();

  // This is a placeholder component that would use Nivo charts in a real implementation
  // For now, we'll just display a placeholder message

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
        p: 2,
      }}
    >
      <Typography variant="body1" color="text.secondary" align="center">
        Line Chart Visualization
      </Typography>
      <Typography
        variant="body2"
        color="text.secondary"
        align="center"
        sx={{ mt: 1 }}
      >
        This would display a line chart comparing predicted vs actual values
      </Typography>
      <Box
        sx={{
          mt: 2,
          width: '100%',
          height: '70%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          position: 'relative',
        }}
      >
        {/* Simulate chart lines */}
        <Box
          sx={{
            position: 'absolute',
            top: '30%',
            left: 0,
            right: 0,
            height: '2px',
            backgroundColor: theme.palette.primary.main,
            zIndex: 1,
            '&::before': {
              content: '""',
              position: 'absolute',
              top: -10,
              left: '80%',
              borderLeft: `2px solid ${theme.palette.primary.main}`,
              borderBottom: `2px solid ${theme.palette.primary.main}`,
              width: 10,
              height: 10,
              transform: 'rotate(-45deg)',
            },
          }}
        />

        <Box
          sx={{
            position: 'absolute',
            top: '40%',
            left: 0,
            right: 0,
            height: '2px',
            backgroundColor: theme.palette.secondary.main,
            zIndex: 1,
            '&::before': {
              content: '""',
              position: 'absolute',
              top: -10,
              left: '75%',
              borderLeft: `2px solid ${theme.palette.secondary.main}`,
              borderBottom: `2px solid ${theme.palette.secondary.main}`,
              width: 10,
              height: 10,
              transform: 'rotate(-45deg)',
            },
          }}
        />

        {/* Legend */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            display: 'flex',
            justifyContent: 'center',
            gap: 4,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Box
              sx={{
                width: 12,
                height: 12,
                backgroundColor: theme.palette.primary.main,
                mr: 1,
              }}
            />
            <Typography variant="caption">Predictions</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Box
              sx={{
                width: 12,
                height: 12,
                backgroundColor: theme.palette.secondary.main,
                mr: 1,
              }}
            />
            <Typography variant="caption">Actual</Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default LineChart;
