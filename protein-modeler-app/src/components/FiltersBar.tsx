import React from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Typography,
  Chip,
  Button,
  Paper
} from '@mui/material';
import { useStore } from '../state/useStore';
import type { Maturity } from '../lib/types';

const DISEASE_CATEGORIES = [
  'Autoimmune',
  'Neurodegenerative', 
  'Metabolic',
  'Cardiovascular',
  'Respiratory',
  'Musculoskeletal'
];

const MATURITY_OPTIONS: { value: Maturity; label: string; color: string }[] = [
  { value: 'approved', label: 'Approved', color: '#27ae60' },
  { value: 'trial', label: 'In Trial', color: '#f39c12' },
  { value: 'none', label: 'No Therapy', color: '#e74c3c' }
];

export const FiltersBar: React.FC = () => {
  const filters = useStore(state => state.filters);
  const setFilter = useStore(state => state.setFilter);
  const clearFilters = useStore(state => state.clearFilters);

  const handleCategoryChange = (event: any) => {
    const value = event.target.value;
    setFilter('category', value.length > 0 ? value : undefined);
  };

  const handleMaturityChange = (event: any) => {
    const value = event.target.value;
    setFilter('maturity', value.length > 0 ? value : undefined);
  };

  const handleHubDegreeChange = (event: Event, newValue: number | number[]) => {
    setFilter('hubMinDegree', newValue as number);
  };

  const hasActiveFilters = 
    filters.category?.length || 
    filters.maturity?.length || 
    filters.hubMinDegree !== undefined;

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>
        Filters
      </Typography>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {/* Disease Category Filter */}
        <FormControl fullWidth size="small">
          <InputLabel>Disease Category</InputLabel>
          <Select
            multiple
            value={filters.category || []}
            onChange={handleCategoryChange}
            label="Disease Category"
            renderValue={(selected) => (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {selected.map((value) => (
                  <Chip key={value} label={value} size="small" />
                ))}
              </Box>
            )}
          >
            {DISEASE_CATEGORIES.map((category) => (
              <MenuItem key={category} value={category}>
                {category}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Maturity Filter */}
        <FormControl fullWidth size="small">
          <InputLabel>Therapy Status</InputLabel>
          <Select
            multiple
            value={filters.maturity || []}
            onChange={handleMaturityChange}
            label="Therapy Status"
            renderValue={(selected) => (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {selected.map((value) => {
                  const option = MATURITY_OPTIONS.find(opt => opt.value === value);
                  return (
                    <Chip 
                      key={value} 
                      label={option?.label || value} 
                      size="small"
                      sx={{ 
                        backgroundColor: option?.color,
                        color: 'white',
                        '& .MuiChip-deleteIcon': {
                          color: 'white'
                        }
                      }}
                    />
                  );
                })}
              </Box>
            )}
          >
            {MATURITY_OPTIONS.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box
                    sx={{
                      width: 12,
                      height: 12,
                      borderRadius: '50%',
                      backgroundColor: option.color
                    }}
                  />
                  {option.label}
                </Box>
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Hub Degree Filter */}
        <Box>
          <Typography gutterBottom>
            Hub Proteins (Min Degree): {filters.hubMinDegree || 0}
          </Typography>
          <Slider
            value={filters.hubMinDegree || 0}
            onChange={handleHubDegreeChange}
            min={0}
            max={10}
            step={1}
            marks={[
              { value: 0, label: '0' },
              { value: 5, label: '5' },
              { value: 10, label: '10' }
            ]}
            valueLabelDisplay="auto"
            size="small"
          />
        </Box>

        {/* Clear Filters Button */}
        {hasActiveFilters && (
          <Button
            variant="outlined"
            onClick={clearFilters}
            size="small"
            sx={{ alignSelf: 'flex-start' }}
          >
            Clear Filters
          </Button>
        )}
      </Box>
    </Paper>
  );
};
