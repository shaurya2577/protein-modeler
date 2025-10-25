import React, { useState, useEffect } from 'react';
import {
  Drawer,
  Box,
  Typography,
  Tabs,
  Tab,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Divider,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Close as CloseIcon,
  Science as ProteinIcon,
  LocalHospital as DiseaseIcon,
  Link as LinkIcon
} from '@mui/icons-material';
import { useStore } from '../state/useStore';
import { getDisease, getProtein } from '../lib/dataClient';
import { explainProtein, explainDisease } from '../lib/explain';
import { semanticNeighbors } from '../lib/search';
import type { DiseaseWithAssociations, ProteinWithContext, SearchResult } from '../lib/types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 2 }}>{children}</Box>}
    </div>
  );
}

export const DetailsPanel: React.FC = () => {
  const selectedNodeId = useStore(state => state.selectedNodeId);
  const selectedNodeType = useStore(state => state.selectedNodeType);
  const clearSelection = useStore(state => state.clearSelection);
  const setShowDetailsPanel = useStore(state => state.setShowDetailsPanel);
  
  // Show panel when there's a selection
  const showDetailsPanel = selectedNodeId !== null;
  
  const [tabValue, setTabValue] = useState(0);
  const [data, setData] = useState<DiseaseWithAssociations | ProteinWithContext | null>(null);
  const [explanation, setExplanation] = useState<string>('');
  const [related, setRelated] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load data when selection changes
  useEffect(() => {
    if (!selectedNodeId || !selectedNodeType) {
      setData(null);
      setExplanation('');
      setRelated([]);
      return;
    }

    setLoading(true);
    setError(null);

    const loadData = async () => {
      try {
        if (selectedNodeType === 'disease') {
          const diseaseData = await getDisease(selectedNodeId);
          setData(diseaseData);
          setExplanation(explainDisease(diseaseData.disease, diseaseData));
        } else {
          const proteinData = await getProtein(selectedNodeId);
          setData(proteinData);
          setExplanation(explainProtein(proteinData.protein, proteinData));
        }

        // Load related items
        try {
          const relatedItems = await semanticNeighbors(selectedNodeId, 5);
          setRelated(relatedItems);
        } catch (err) {
          console.warn('Failed to load related items:', err);
          setRelated([]);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [selectedNodeId, selectedNodeType]);

  const handleClose = () => {
    setShowDetailsPanel(false);
    clearSelection();
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (!showDetailsPanel || !selectedNodeId || !selectedNodeType) {
    return null;
  }

  const isDisease = selectedNodeType === 'disease';
  const nodeData = data as DiseaseWithAssociations | ProteinWithContext;

  return (
    <Drawer
      anchor="right"
      open={showDetailsPanel}
      onClose={handleClose}
      sx={{
        '& .MuiDrawer-paper': {
          width: 400,
          maxWidth: '90vw'
        }
      }}
    >
      <Box sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {isDisease ? <DiseaseIcon /> : <ProteinIcon />}
            <Typography variant="h6">
              {isDisease ? 'Disease Details' : 'Protein Details'}
            </Typography>
          </Box>
          <Button onClick={handleClose} size="small">
            <CloseIcon />
          </Button>
        </Box>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : nodeData ? (
          <>
            <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 2 }}>
              <Tab label="Overview" />
              <Tab label="Evidence" />
              <Tab label="Therapies" />
              <Tab label="Trials" />
              <Tab label="Related" />
            </Tabs>

            <TabPanel value={tabValue} index={0}>
              <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="h6" gutterBottom>
                  {isDisease 
                    ? (nodeData as DiseaseWithAssociations).disease.name 
                    : (nodeData as ProteinWithContext).protein.symbol || (nodeData as ProteinWithContext).protein.name
                  }
                </Typography>
                {isDisease ? (
                  <Typography variant="body2" color="text.secondary">
                    Category: {(nodeData as DiseaseWithAssociations).disease.category || 'Unknown'}
                    {(nodeData as DiseaseWithAssociations).disease.burden_score && (
                      <> • Burden: {((nodeData as DiseaseWithAssociations).disease.burden_score! * 100).toFixed(0)}%</>
                    )}
                  </Typography>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    {(nodeData as ProteinWithContext).protein.uniprot_id} • {(nodeData as ProteinWithContext).protein.family || 'Unknown family'}
                    {(nodeData as ProteinWithContext).protein.pathways && (
                      <> • Pathways: {(nodeData as ProteinWithContext).protein.pathways!.slice(0, 2).join(', ')}</>
                    )}
                  </Typography>
                )}
              </Paper>

              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  AI Explanation
                </Typography>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                  {explanation}
                </Typography>
              </Paper>
            </TabPanel>

            <TabPanel value={tabValue} index={1}>
              <Typography variant="h6" gutterBottom>
                Evidence
              </Typography>
              {isDisease ? (
                <List>
                  {(nodeData as DiseaseWithAssociations).associations.map((assoc, index) => (
                    <React.Fragment key={assoc.id}>
                      <ListItem>
                        <ListItemIcon>
                          <ProteinIcon />
                        </ListItemIcon>
                        <ListItemText
                          primary={assoc.protein.symbol || assoc.protein.name}
                          secondary={
                            <Box>
                              <Typography variant="body2" sx={{ mb: 1 }}>
                                {assoc.evidence_text}
                              </Typography>
                              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                {assoc.association_strength && (
                                  <Chip
                                    label={`${(assoc.association_strength * 100).toFixed(0)}% confidence`}
                                    size="small"
                                    color="primary"
                                  />
                                )}
                                {assoc.maturity && (
                                  <Chip
                                    label={assoc.maturity}
                                    size="small"
                                    color={
                                      assoc.maturity === 'approved' ? 'success' :
                                      assoc.maturity === 'trial' ? 'warning' : 'error'
                                    }
                                  />
                                )}
                              </Box>
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < (nodeData as DiseaseWithAssociations).associations.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <List>
                  {(nodeData as ProteinWithContext).diseases.map((disease, index) => (
                    <React.Fragment key={disease.id}>
                      <ListItem>
                        <ListItemIcon>
                          <DiseaseIcon />
                        </ListItemIcon>
                        <ListItemText
                          primary={disease.disease.name}
                          secondary={
                            <Box>
                              <Typography variant="body2" sx={{ mb: 1 }}>
                                {disease.evidence_text}
                              </Typography>
                              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                {disease.association_strength && (
                                  <Chip
                                    label={`${(disease.association_strength * 100).toFixed(0)}% confidence`}
                                    size="small"
                                    color="primary"
                                  />
                                )}
                                {disease.maturity && (
                                  <Chip
                                    label={disease.maturity}
                                    size="small"
                                    color={
                                      disease.maturity === 'approved' ? 'success' :
                                      disease.maturity === 'trial' ? 'warning' : 'error'
                                    }
                                  />
                                )}
                              </Box>
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < (nodeData as ProteinWithContext).diseases.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </TabPanel>

            <TabPanel value={tabValue} index={2}>
              <Typography variant="h6" gutterBottom>
                Therapies
              </Typography>
              {isDisease ? (
                <Typography color="text.secondary">
                  No direct therapies for diseases. Check associated proteins.
                </Typography>
              ) : (nodeData as ProteinWithContext).therapies.length > 0 ? (
                <List>
                  {(nodeData as ProteinWithContext).therapies.map((therapy) => (
                    <ListItem key={therapy.id}>
                      <ListItemText
                        primary={therapy.name}
                        secondary={
                          <Box>
                            <Typography variant="body2">
                              Status: {therapy.status}
                            </Typography>
                            {therapy.indications && (
                              <Typography variant="body2" color="text.secondary">
                                Indications: {therapy.indications.join(', ')}
                              </Typography>
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography color="text.secondary">
                  No approved therapies for this protein.
                </Typography>
              )}
            </TabPanel>

            <TabPanel value={tabValue} index={3}>
              <Typography variant="h6" gutterBottom>
                Clinical Trials
              </Typography>
              {isDisease ? (
                <Typography color="text.secondary">
                  No direct trials for diseases. Check associated proteins.
                </Typography>
              ) : (nodeData as ProteinWithContext).trials.length > 0 ? (
                <List>
                  {(nodeData as ProteinWithContext).trials.map((trial) => (
                    <ListItem key={trial.id}>
                      <ListItemText
                        primary={trial.nct_id}
                        secondary={
                          <Box>
                            <Typography variant="body2">
                              {trial.phase} • {trial.status}
                            </Typography>
                            {trial.condition && (
                              <Typography variant="body2" color="text.secondary">
                                Condition: {trial.condition}
                              </Typography>
                            )}
                            {trial.link && (
                              <Button
                                size="small"
                                startIcon={<LinkIcon />}
                                href={trial.link}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                View Trial
                              </Button>
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography color="text.secondary">
                  No clinical trials found for this protein.
                </Typography>
              )}
            </TabPanel>

            <TabPanel value={tabValue} index={4}>
              <Typography variant="h6" gutterBottom>
                Related Items
              </Typography>
              {related.length > 0 ? (
                <List>
                  {related.map((item) => (
                    <ListItem key={item.id}>
                      <ListItemIcon>
                        {item.type === 'disease' ? <DiseaseIcon /> : <ProteinIcon />}
                      </ListItemIcon>
                      <ListItemText
                        primary={item.label}
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Chip
                              label={item.type}
                              size="small"
                              color={item.type === 'disease' ? 'error' : 'primary'}
                            />
                            <Typography variant="caption">
                              Score: {(item.score * 100).toFixed(0)}%
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography color="text.secondary">
                  No related items found.
                </Typography>
              )}
            </TabPanel>
          </>
        ) : null}
      </Box>
    </Drawer>
  );
};
