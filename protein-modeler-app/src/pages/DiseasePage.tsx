import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { useStore } from '../state/useStore';
import { getGraph, getDisease } from '../lib/dataClient';
import { initSearchIndex } from '../lib/search';

export const DiseasePage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const setNodes = useStore(state => state.setNodes);
  const setEdges = useStore(state => state.setEdges);
  const setLoading = useStore(state => state.setLoading);
  const setError = useStore(state => state.setError);
  const setSelected = useStore(state => state.setSelected);

  useEffect(() => {
    const loadData = async () => {
      if (!id) return;

      setLoading(true);
      try {
        // Load graph data
        const { nodes, edges } = await getGraph();
        setNodes(nodes);
        setEdges(edges);

        // Initialize search index
        await initSearchIndex({ nodes, associations: [] });

        // Pre-select the disease
        setSelected(id, 'disease');

        // Load disease details to ensure it exists
        await getDisease(id);
      } catch (error) {
        console.error('Failed to load disease data:', error);
        setError(error instanceof Error ? error.message : 'Failed to load disease data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [id]);

  return <Layout showOpportunities={false} />;
};
