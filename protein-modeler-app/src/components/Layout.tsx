import React from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Paper
} from '@mui/material';
import { Science as ScienceIcon } from '@mui/icons-material';
import { GraphView } from './GraphView';
import { FiltersBar } from './FiltersBar';
import { SearchBox } from './SearchBox';
import { OpportunitiesPanel } from './OpportunitiesPanel';
import { DetailsPanel } from './DetailsPanel';

interface LayoutProps {
  showOpportunities?: boolean;
  showFilters?: boolean;
  showSearch?: boolean;
  graphWidth?: number;
  graphHeight?: number;
}

export const Layout: React.FC<LayoutProps> = ({
  showOpportunities = true,
  showFilters = true,
  showSearch = true,
  graphWidth = 800,
  graphHeight = 600
}) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Header */}
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <ScienceIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Disease-Protein-Therapy Map
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Left Sidebar - Filters */}
        {showFilters && (
          <Box sx={{ width: 300, p: 2, overflow: 'auto', borderRight: 1, borderColor: 'divider' }}>
            {showSearch && (
              <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Search
                </Typography>
                <SearchBox />
              </Paper>
            )}
            <FiltersBar />
          </Box>
        )}

        {/* Center - Graph */}
        <Box sx={{ flex: 1, p: 2, display: 'flex', flexDirection: 'column' }}>
          <Paper sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <GraphView 
              width={graphWidth} 
              height={graphHeight}
            />
          </Paper>
        </Box>

        {/* Right Sidebar - Opportunities */}
        {showOpportunities && (
          <Box sx={{ width: 400, p: 2, overflow: 'auto', borderLeft: 1, borderColor: 'divider' }}>
            <OpportunitiesPanel />
          </Box>
        )}
      </Box>

      {/* Details Panel */}
      <DetailsPanel />
    </Box>
  );
};
