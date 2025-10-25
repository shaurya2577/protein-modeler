import React, { useEffect, useState } from 'react';
import { Layout } from '../components/Layout';
import { useStore } from '../state/useStore';
import { getGraph } from '../lib/dataClient';
import { initSearchIndex } from '../lib/search';

export const Home: React.FC = () => {
  const setNodes = useStore(state => state.setNodes);
  const setEdges = useStore(state => state.setEdges);
  const setLoading = useStore(state => state.setLoading);
  const setError = useStore(state => state.setError);
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    if (initialized) return;
    
    const loadData = async () => {
      setLoading(true);
      try {
        console.log('Loading graph data...');
        // Load graph data
        const { nodes, edges } = await getGraph();
        console.log('Graph loaded:', { nodes: nodes.length, edges: edges.length });
        setNodes(nodes);
        setEdges(edges);

        // Initialize search index
        try {
          console.log('Initializing search index...');
          await initSearchIndex({ nodes, associations: [] });
          console.log('Search index initialized');
        } catch (error) {
          console.warn('Search index initialization failed:', error);
        }
        
        setInitialized(true);
      } catch (error) {
        console.error('Failed to load data:', error);
        setError(error instanceof Error ? error.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  return <Layout />;
};

