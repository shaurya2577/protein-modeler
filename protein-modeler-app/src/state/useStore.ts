import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { shallow } from 'zustand/shallow';
import type { 
  GraphNode, 
  GraphEdge, 
  FilterState, 
  SearchResult, 
  Opportunity
} from '../lib/types';

interface AppState {
  // Graph data
  nodes: GraphNode[];
  edges: GraphEdge[];
  loading: boolean;
  error: string | null;
  
  // Filters
  filters: FilterState;
  
  // Selection
  selectedNodeId: string | null;
  selectedNodeType: 'disease' | 'protein' | null;
  
  // Search
  searchQuery: string;
  searchResults: SearchResult[];
  searchLoading: boolean;
  
  // Opportunities
  opportunities: Opportunity[];
  opportunitiesLoading: boolean;
  
  // UI state
  augmentWithLiveTrials: boolean;
  showDetailsPanel: boolean;
  showOpportunitiesPanel: boolean;
  
  // Actions
  setNodes: (nodes: GraphNode[]) => void;
  setEdges: (edges: GraphEdge[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  setFilter: <K extends keyof FilterState>(key: K, value: FilterState[K]) => void;
  clearFilters: () => void;
  
  setSelected: (nodeId: string | null, nodeType: 'disease' | 'protein' | null) => void;
  clearSelection: () => void;
  
  setSearchQuery: (query: string) => void;
  setSearchResults: (results: SearchResult[]) => void;
  setSearchLoading: (loading: boolean) => void;
  
  setOpportunities: (opportunities: Opportunity[]) => void;
  setOpportunitiesLoading: (loading: boolean) => void;
  
  setAugmentWithLiveTrials: (augment: boolean) => void;
  setShowDetailsPanel: (show: boolean) => void;
  setShowOpportunitiesPanel: (show: boolean) => void;
  
  // Computed getters
  getFilteredNodes: () => GraphNode[];
  getFilteredEdges: () => GraphEdge[];
  getSelectedNode: () => GraphNode | null;
  getHubNodes: () => GraphNode[];
}

export const useStore = create<AppState>()(
  devtools(
    (set, get) => ({
      // Initial state
      nodes: [],
      edges: [],
      loading: false,
      error: null,
      
      filters: {
        category: undefined,
        maturity: undefined,
        hubMinDegree: undefined
      },
      
      selectedNodeId: null,
      selectedNodeType: null,
      
      searchQuery: '',
      searchResults: [],
      searchLoading: false,
      
      opportunities: [],
      opportunitiesLoading: false,
      
      augmentWithLiveTrials: false,
      showDetailsPanel: false,
      showOpportunitiesPanel: true,
      
      // Actions
      setNodes: (nodes) => set({ nodes }),
      setEdges: (edges) => set({ edges }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),
      
      setFilter: (key, value) => 
        set((state) => ({
          filters: { ...state.filters, [key]: value }
        })),
      
      clearFilters: () => 
        set({
          filters: {
            category: undefined,
            maturity: undefined,
            hubMinDegree: undefined
          }
        }),
      
      setSelected: (nodeId, nodeType) => 
        set({ 
          selectedNodeId: nodeId, 
          selectedNodeType: nodeType
        }),
      
      clearSelection: () => 
        set({ 
          selectedNodeId: null, 
          selectedNodeType: null
        }),
      
      setSearchQuery: (query) => set({ searchQuery: query }),
      setSearchResults: (results) => set({ searchResults: results }),
      setSearchLoading: (loading) => set({ searchLoading: loading }),
      
      setOpportunities: (opportunities) => set({ opportunities }),
      setOpportunitiesLoading: (loading) => set({ opportunitiesLoading: loading }),
      
      setAugmentWithLiveTrials: (augment) => set({ augmentWithLiveTrials: augment }),
      setShowDetailsPanel: (show) => set({ showDetailsPanel: show }),
      setShowOpportunitiesPanel: (show) => set({ showOpportunitiesPanel: show }),
      
      // Computed getters
      getFilteredNodes: () => {
        const { nodes, filters } = get();
        let filtered = nodes;
        
        if (filters.category) {
          // This would need to be implemented based on disease categories
          // For now, return all nodes
        }
        
        if (filters.hubMinDegree !== undefined) {
          filtered = filtered.filter(node => 
            node.type === 'disease' || (node.degree && node.degree >= filters.hubMinDegree!)
          );
        }
        
        return filtered;
      },
      
      getFilteredEdges: () => {
        const { edges, filters } = get();
        let filtered = edges;
        
        if (filters.maturity) {
          // This would need to be implemented based on association maturity
          // For now, return all edges
        }
        
        return filtered;
      },
      
      getSelectedNode: () => {
        const { nodes, selectedNodeId } = get();
        if (!selectedNodeId) return null;
        return nodes.find(node => node.id === selectedNodeId) || null;
      },
      
      getHubNodes: () => {
        const { nodes } = get();
        return nodes
          .filter(node => node.type === 'protein' && node.degree && node.degree >= 5)
          .sort((a, b) => (b.degree || 0) - (a.degree || 0));
      }
    }),
    {
      name: 'disease-protein-therapy-store'
    }
  )
);

// Selector hooks with shallow comparison to prevent infinite loops
export const useGraphData = () => useStore(state => ({
  nodes: state.nodes,
  edges: state.edges,
  loading: state.loading,
  error: state.error
}), shallow);

export const useFilters = () => useStore(state => ({
  filters: state.filters,
  setFilter: state.setFilter,
  clearFilters: state.clearFilters
}), shallow);

export const useSelection = () => useStore(state => ({
  selectedNodeId: state.selectedNodeId,
  selectedNodeType: state.selectedNodeType,
  setSelected: state.setSelected,
  clearSelection: state.clearSelection
}), shallow);

export const useSearch = () => useStore(state => ({
  searchQuery: state.searchQuery,
  searchResults: state.searchResults,
  searchLoading: state.searchLoading,
  setSearchQuery: state.setSearchQuery,
  setSearchResults: state.setSearchResults,
  setSearchLoading: state.setSearchLoading
}), shallow);

export const useOpportunities = () => useStore(state => ({
  opportunities: state.opportunities,
  opportunitiesLoading: state.opportunitiesLoading,
  setOpportunities: state.setOpportunities,
  setOpportunitiesLoading: state.setOpportunitiesLoading
}), shallow);

export const useUI = () => useStore(state => ({
  showDetailsPanel: state.showDetailsPanel,
  showOpportunitiesPanel: state.showOpportunitiesPanel,
  augmentWithLiveTrials: state.augmentWithLiveTrials,
  setShowDetailsPanel: state.setShowDetailsPanel,
  setShowOpportunitiesPanel: state.setShowOpportunitiesPanel,
  setAugmentWithLiveTrials: state.setAugmentWithLiveTrials
}), shallow);
