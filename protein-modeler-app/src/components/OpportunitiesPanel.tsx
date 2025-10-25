import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  Box,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Download as DownloadIcon,
  Science as ProteinIcon,
  LocalHospital as DiseaseIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';
import { useStore } from '../state/useStore';
import { getOpportunities } from '../lib/dataClient';
// import { generateRationale } from '../lib/scoring';
import type { Opportunity } from '../lib/types';

export const OpportunitiesPanel: React.FC = () => {
  const opportunities = useStore(state => state.opportunities);
  const opportunitiesLoading = useStore(state => state.opportunitiesLoading);
  const setOpportunities = useStore(state => state.setOpportunities);
  const setOpportunitiesLoading = useStore(state => state.setOpportunitiesLoading);
  const setSelected = useStore(state => state.setSelected);
  const [limit, setLimit] = useState(20);

  // Load opportunities
  useEffect(() => {
    const loadOpportunities = async () => {
      setOpportunitiesLoading(true);
      try {
        const opps = await getOpportunities(limit);
        setOpportunities(opps);
      } catch (error) {
        console.error('Failed to load opportunities:', error);
      } finally {
        setOpportunitiesLoading(false);
      }
    };

    loadOpportunities();
  }, [limit]);

  const handleRowClick = (opportunity: Opportunity) => {
    // Select both nodes in the graph
    setSelected(opportunity.disease_id, 'disease');
    // Note: In a real implementation, you'd want to highlight the edge between the nodes
  };

  const handleDownloadCSV = () => {
    const csvContent = [
      'Disease,Protein,Score,Rationale',
      ...opportunities.map(opp => 
        `"${opp.disease_name || opp.disease_id}","${opp.protein_name || opp.protein_id}","${opp.gap_score.toFixed(3)}","${opp.rationale}"`
      ).join('\n')
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'therapeutic-opportunities.csv';
    link.click();
    URL.revokeObjectURL(url);
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'success';
    if (score >= 0.4) return 'warning';
    return 'error';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 0.7) return 'High';
    if (score >= 0.4) return 'Medium';
    return 'Low';
  };

  return (
    <Paper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TrendingUpIcon />
          <Typography variant="h6">
            Therapeutic Opportunities
          </Typography>
        </Box>
        <Tooltip title="Download CSV">
          <IconButton onClick={handleDownloadCSV} size="small">
            <DownloadIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Ranked by gap score - higher scores indicate better therapeutic opportunities
      </Typography>

      {opportunitiesLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : opportunities.length === 0 ? (
        <Alert severity="info">
          No opportunities found. Try adjusting your filters.
        </Alert>
      ) : (
        <TableContainer sx={{ flex: 1, overflow: 'auto' }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                <TableCell>Disease</TableCell>
                <TableCell>Protein</TableCell>
                <TableCell align="center">Score</TableCell>
                <TableCell>Rationale</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {opportunities.map((opportunity, index) => (
                <TableRow
                  key={`${opportunity.disease_id}-${opportunity.protein_id}`}
                  hover
                  onClick={() => handleRowClick(opportunity)}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <DiseaseIcon fontSize="small" color="error" />
                      {opportunity.disease_name || opportunity.disease_id}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <ProteinIcon fontSize="small" color="primary" />
                      {opportunity.protein_name || opportunity.protein_id}
                    </Box>
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      label={`${(opportunity.gap_score * 100).toFixed(0)}%`}
                      size="small"
                      color={getScoreColor(opportunity.gap_score)}
                      variant="outlined"
                    />
                    <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                      {getScoreLabel(opportunity.gap_score)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ 
                      maxWidth: 200, 
                      overflow: 'hidden', 
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}>
                      {opportunity.rationale}
                    </Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          Showing {opportunities.length} opportunities
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            size="small"
            variant="outlined"
            onClick={() => setLimit(Math.max(10, limit - 10))}
            disabled={limit <= 10}
          >
            Show Less
          </Button>
          <Button
            size="small"
            variant="outlined"
            onClick={() => setLimit(limit + 10)}
          >
            Show More
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};
