import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import coseBilkent from 'cytoscape-cose-bilkent';
import { useStore } from '../state/useStore';
import type { GraphNode, GraphEdge } from '../lib/types';

// Register layout
cytoscape.use(coseBilkent);

interface GraphViewProps {
  width?: number;
  height?: number;
  onNodeClick?: (nodeId: string, nodeType: 'disease' | 'protein') => void;
}

export const GraphView: React.FC<GraphViewProps> = ({ 
  width = 800, 
  height = 600,
  onNodeClick 
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  
  const nodes = useStore(state => state.nodes);
  const edges = useStore(state => state.edges);
  const loading = useStore(state => state.loading);
  const error = useStore(state => state.error);
  const selectedNodeId = useStore(state => state.selectedNodeId);
  const setSelected = useStore(state => state.setSelected);

  // Initialize Cytoscape
  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      elements: [],
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#666',
            'label': 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '12px',
            'font-weight': 'bold',
            'color': '#fff',
            'text-outline-width': 2,
            'text-outline-color': '#000'
          }
        },
        {
          selector: 'node[type="disease"]',
          style: {
            'shape': 'ellipse',
            'width': 'data(burden)',
            'height': 'data(burden)',
            'background-color': '#e74c3c'
          }
        },
        {
          selector: 'node[type="protein"]',
          style: {
            'shape': 'roundrectangle',
            'width': 'data(degree)',
            'height': 'data(degree)',
            'background-color': '#3498db'
          }
        },
        {
          selector: 'node[type="protein"][maturity="approved"]',
          style: {
            'background-color': '#27ae60'
          }
        },
        {
          selector: 'node[type="protein"][maturity="trial"]',
          style: {
            'background-color': '#f39c12'
          }
        },
        {
          selector: 'node[type="protein"][maturity="none"]',
          style: {
            'background-color': '#e74c3c'
          }
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': 3,
            'border-color': '#f1c40f'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 'data(strength)',
            'line-color': '#95a5a6',
            'target-arrow-color': '#95a5a6',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier'
          }
        },
        {
          selector: 'edge:selected',
          style: {
            'line-color': '#f1c40f',
            'target-arrow-color': '#f1c40f',
            'width': 4
          }
        }
      ],
      layout: {
        name: 'cose-bilkent',
        animate: true,
        animationDuration: 1000,
        randomize: false,
        nodeRepulsion: 4000,
        idealEdgeLength: 100,
        edgeElasticity: 0.45,
        nestingFactor: 0.1,
        gravity: 0.25,
        numIter: 2500,
        tile: true,
        animationEasing: 'ease-out-bounce',
        fit: true,
        padding: 20,
        boundingBox: undefined,
        nodeDimensionsIncludeLabels: true
      }
    });

    cyRef.current = cy;

    // Add event listeners
    cy.on('tap', 'node', (event) => {
      const node = event.target;
      const nodeId = node.id();
      const nodeType = node.data('type') as 'disease' | 'protein';
      
      setSelected(nodeId, nodeType);
      onNodeClick?.(nodeId, nodeType);
    });

    cy.on('tap', (event) => {
      if (event.target === cy) {
        setSelected(null, null);
      }
    });

    return () => {
      cy.destroy();
    };
  }, []);

  // Update graph data
  useEffect(() => {
    if (!cyRef.current) return;

    const cy = cyRef.current;
    
    // Clear existing elements
    cy.elements().remove();
    
    // Add new elements
    const elements: any[] = [];
    
    // Add nodes
    nodes.forEach(node => {
      elements.push({
        data: {
          id: node.id,
          label: node.label,
          type: node.type,
          burden: Math.max(20, Math.min(60, (node.burden || 0.5) * 60)),
          degree: Math.max(20, Math.min(60, (node.degree || 1) * 8)),
          maturity: node.maturity
        }
      });
    });
    
    // Add edges
    edges.forEach(edge => {
      elements.push({
        data: {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          strength: Math.max(1, Math.min(5, (edge.strength || 0.5) * 5))
        }
      });
    });
    
    cy.add(elements);
    
    // Apply layout
    cy.layout({
      name: 'cose-bilkent',
      animate: true,
      animationDuration: 1000
    }).run();
    
  }, [nodes, edges]);

  // Update selection
  useEffect(() => {
    if (!cyRef.current) return;

    const cy = cyRef.current;
    
    // Clear previous selection
    cy.elements().unselect();
    
    // Select current node
    if (selectedNodeId) {
      const node = cy.getElementById(selectedNodeId);
      if (node.length > 0) {
        node.select();
        cy.center(node);
      }
    }
  }, [selectedNodeId]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (cyRef.current) {
        cyRef.current.resize();
        cyRef.current.fit();
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  if (loading) {
    return (
      <div 
        style={{ 
          width, 
          height, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          backgroundColor: '#f8f9fa',
          border: '1px solid #dee2e6',
          borderRadius: '4px'
        }}
      >
        <div>Loading graph...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div 
        style={{ 
          width, 
          height, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          backgroundColor: '#f8d7da',
          border: '1px solid #f5c6cb',
          borderRadius: '4px',
          color: '#721c24'
        }}
      >
        <div>Error: {error}</div>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef}
      style={{ 
        width, 
        height,
        border: '1px solid #dee2e6',
        borderRadius: '4px',
        backgroundColor: '#fff'
      }}
    />
  );
};
