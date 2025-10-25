import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  Typography,
  CircularProgress,
  Chip
} from '@mui/material';
import { Search as SearchIcon, Science as ProteinIcon, LocalHospital as DiseaseIcon } from '@mui/icons-material';
import { useStore } from '../state/useStore';
import { querySearch } from '../lib/search';
import type { SearchResult } from '../lib/types';

interface SearchBoxProps {
  onResultSelect?: (result: SearchResult) => void;
}

export const SearchBox: React.FC<SearchBoxProps> = ({ onResultSelect }) => {
  const searchQuery = useStore(state => state.searchQuery);
  const searchResults = useStore(state => state.searchResults);
  const searchLoading = useStore(state => state.searchLoading);
  const setSearchQuery = useStore(state => state.setSearchQuery);
  const setSearchResults = useStore(state => state.setSearchResults);
  const setSearchLoading = useStore(state => state.setSearchLoading);
  const [showResults, setShowResults] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);

  // Debounced search
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setShowResults(false);
      return;
    }

    setSearchLoading(true);
    setShowResults(true);

    const timeoutId = setTimeout(() => {
      try {
        const results = querySearch(searchQuery, 10);
        setSearchResults(results);
        setSearchLoading(false);
      } catch (error) {
        console.error('Search failed:', error);
        setSearchResults([]);
        setSearchLoading(false);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
    setSelectedIndex(-1);
  };

  const handleResultClick = useCallback((result: SearchResult) => {
    setShowResults(false);
    setSearchQuery('');
    onResultSelect?.(result);
  }, [onResultSelect]);

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (!showResults || searchResults.length === 0) return;

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        setSelectedIndex(prev => 
          prev < searchResults.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        event.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        event.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < searchResults.length) {
          handleResultClick(searchResults[selectedIndex]);
        } else if (searchResults.length > 0) {
          handleResultClick(searchResults[0]);
        }
        break;
      case 'Escape':
        setShowResults(false);
        setSelectedIndex(-1);
        break;
    }
  };

  const getResultIcon = (type: 'disease' | 'protein') => {
    return type === 'disease' ? <DiseaseIcon /> : <ProteinIcon />;
  };

  const getResultColor = (type: 'disease' | 'protein') => {
    return type === 'disease' ? '#e74c3c' : '#3498db';
  };

  return (
    <Box sx={{ position: 'relative', width: '100%' }}>
      <TextField
        fullWidth
        placeholder="Search diseases, proteins, or evidence..."
        value={searchQuery}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onFocus={() => setShowResults(true)}
        InputProps={{
          startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
          endAdornment: searchLoading ? (
            <CircularProgress size={20} />
          ) : null
        }}
        size="small"
      />

      {showResults && (searchResults.length > 0 || searchLoading) && (
        <Paper
          sx={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            zIndex: 1000,
            mt: 1,
            maxHeight: 300,
            overflow: 'auto',
            boxShadow: 3
          }}
        >
          {searchLoading ? (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <CircularProgress size={20} />
              <Typography variant="body2" sx={{ mt: 1 }}>
                Searching...
              </Typography>
            </Box>
          ) : searchResults.length > 0 ? (
            <List dense>
              {searchResults.map((result, index) => (
                <ListItem
                  key={result.id}
                  button
                  onClick={() => handleResultClick(result)}
                  sx={{
                    backgroundColor: index === selectedIndex ? 'action.hover' : 'transparent',
                    '&:hover': {
                      backgroundColor: 'action.hover'
                    }
                  }}
                >
                  <ListItemIcon sx={{ color: getResultColor(result.type) }}>
                    {getResultIcon(result.type)}
                  </ListItemIcon>
                  <ListItemText
                      primary={result.label || result.id}
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                        <Chip
                          label={result.type}
                          size="small"
                          sx={{
                            backgroundColor: getResultColor(result.type),
                            color: 'white',
                            fontSize: '0.75rem'
                          }}
                        />
                        <Typography variant="caption" color="text.secondary">
                          Score: {(result.score * 100).toFixed(0)}%
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          ) : (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                No results found
              </Typography>
            </Box>
          )}
        </Paper>
      )}
    </Box>
  );
};
