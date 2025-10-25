import React from 'react';
import { Typography, Box } from '@mui/material';

export const TestComponent: React.FC = () => {
  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>
        🎉 Disease-Protein-Therapy Map
      </Typography>
      <Typography variant="body1">
        If you can see this, React is working! The app is loading successfully.
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
        Check the browser console for any JavaScript errors.
      </Typography>
    </Box>
  );
};
