import React, { useState } from 'react';
import {
  Drawer,
  Box,
  Typography,
  Button,
  Paper,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  CircularProgress
} from '@mui/material';
import {
  Close as CloseIcon,
  CloudUpload as UploadIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import Papa from 'papaparse';
import { useStore } from '../state/useStore';
import type { Disease, Protein, Association } from '../lib/types';

interface ImportDrawerProps {
  open: boolean;
  onClose: () => void;
}

interface ParsedData {
  diseases: Disease[];
  proteins: Protein[];
  associations: Association[];
  errors: string[];
}

export const ImportDrawer: React.FC<ImportDrawerProps> = ({ open, onClose }) => {
  const setNodes = useStore(state => state.setNodes);
  const setEdges = useStore(state => state.setEdges);
  const [parsedData, setParsedData] = useState<ParsedData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = async (acceptedFiles: File[]) => {
    if (acceptedFiles.length !== 3) {
      setError('Please upload exactly 3 files: diseases.csv, proteins.csv, and associations.csv');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const files = {
        diseases: acceptedFiles.find(f => f.name.includes('diseases')),
        proteins: acceptedFiles.find(f => f.name.includes('proteins')),
        associations: acceptedFiles.find(f => f.name.includes('associations'))
      };

      if (!files.diseases || !files.proteins || !files.associations) {
        throw new Error('Files must be named diseases.csv, proteins.csv, and associations.csv');
      }

      const results: ParsedData = {
        diseases: [],
        proteins: [],
        associations: [],
        errors: []
      };

      // Parse diseases
      const diseasesText = await files.diseases.text();
      const diseasesResult = Papa.parse(diseasesText, { header: true });
      if (diseasesResult.errors.length > 0) {
        results.errors.push(`Diseases CSV errors: ${diseasesResult.errors.map(e => e.message).join(', ')}`);
      }
      results.diseases = diseasesResult.data as Disease[];

      // Parse proteins
      const proteinsText = await files.proteins.text();
      const proteinsResult = Papa.parse(proteinsText, { header: true });
      if (proteinsResult.errors.length > 0) {
        results.errors.push(`Proteins CSV errors: ${proteinsResult.errors.map(e => e.message).join(', ')}`);
      }
      results.proteins = proteinsResult.data as Protein[];

      // Parse associations
      const associationsText = await files.associations.text();
      const associationsResult = Papa.parse(associationsText, { header: true });
      if (associationsResult.errors.length > 0) {
        results.errors.push(`Associations CSV errors: ${associationsResult.errors.map(e => e.message).join(', ')}`);
      }
      results.associations = associationsResult.data as Association[];

      setParsedData(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to parse CSV files');
    } finally {
      setLoading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv']
    },
    multiple: true
  });

  const handleImport = async () => {
    if (!parsedData) return;

    setLoading(true);
    try {
      // Rebuild graph with imported data
      const nodes: any[] = [];
      const edges: any[] = [];

      // Add disease nodes
      parsedData.diseases.forEach(disease => {
        nodes.push({
          id: disease.id,
          type: 'disease',
          label: disease.name,
          burden: disease.burden_score || 0.5,
          degree: undefined,
          maturity: undefined
        });
      });

      // Add protein nodes
      parsedData.proteins.forEach(protein => {
        const degree = parsedData.associations.filter(a => a.protein_id === protein.id).length;
        nodes.push({
          id: protein.id,
          type: 'protein',
          label: protein.symbol || protein.name || protein.id,
          burden: undefined,
          degree,
          maturity: undefined
        });
      });

      // Add edges
      parsedData.associations.forEach(assoc => {
        edges.push({
          id: assoc.id,
          source: assoc.disease_id,
          target: assoc.protein_id,
          strength: assoc.association_strength || 0.5
        });
      });

      setNodes(nodes);
      setEdges(edges);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to import data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      sx={{
        '& .MuiDrawer-paper': {
          width: 500,
          maxWidth: '90vw'
        }
      }}
    >
      <Box sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">Import Data</Typography>
          <Button onClick={onClose} size="small">
            <CloseIcon />
          </Button>
        </Box>

        <Paper
          {...getRootProps()}
          sx={{
            p: 4,
            textAlign: 'center',
            border: '2px dashed',
            borderColor: isDragActive ? 'primary.main' : 'grey.300',
            backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
            cursor: 'pointer',
            mb: 2
          }}
        >
          <input {...getInputProps()} />
          <UploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {isDragActive ? 'Drop files here' : 'Upload CSV Files'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Upload diseases.csv, proteins.csv, and associations.csv
          </Typography>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
            <CircularProgress />
          </Box>
        )}

        {parsedData && (
          <>
            <Typography variant="h6" gutterBottom>
              Import Preview
            </Typography>
            
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <CheckIcon color="success" />
                </ListItemIcon>
                <ListItemText
                  primary={`${parsedData.diseases.length} diseases`}
                  secondary="Disease nodes"
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon>
                  <CheckIcon color="success" />
                </ListItemIcon>
                <ListItemText
                  primary={`${parsedData.proteins.length} proteins`}
                  secondary="Protein nodes"
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon>
                  <CheckIcon color="success" />
                </ListItemIcon>
                <ListItemText
                  primary={`${parsedData.associations.length} associations`}
                  secondary="Graph edges"
                />
              </ListItem>
            </List>

            {parsedData.errors.length > 0 && (
              <>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle2" color="error" gutterBottom>
                  Warnings:
                </Typography>
                <List dense>
                  {parsedData.errors.map((error, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <ErrorIcon color="warning" />
                      </ListItemIcon>
                      <ListItemText
                        primary={error}
                        secondary="Data may be incomplete"
                      />
                    </ListItem>
                  ))}
                </List>
              </>
            )}

            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                onClick={handleImport}
                disabled={loading}
                fullWidth
              >
                Import Data
              </Button>
              <Button
                variant="outlined"
                onClick={onClose}
                fullWidth
              >
                Cancel
              </Button>
            </Box>
          </>
        )}
      </Box>
    </Drawer>
  );
};
