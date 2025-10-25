import React from 'react';
import { Box, Typography, AppBar, Toolbar, Paper } from '@mui/material';
import { Science as ScienceIcon } from '@mui/icons-material';
import { OpportunitiesPanel } from '../components/OpportunitiesPanel';

export const Home: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Header */}
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <ScienceIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Disease-Protein-Therapy Map (Testing OpportunitiesPanel)
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <Box sx={{ flex: 1, p: 2 }}>
          <Paper sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', p: 4 }}>
            <Typography variant="h5">Testing OpportunitiesPanel...</Typography>
          </Paper>
        </Box>
        
        {/* Right Sidebar - Opportunities */}
        <Box sx={{ width: 400, p: 2, overflow: 'auto', borderLeft: 1, borderColor: 'divider' }}>
          <OpportunitiesPanel />
        </Box>
      </Box>
    </Box>
  );
};
