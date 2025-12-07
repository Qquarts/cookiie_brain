"""
Memory PageRank: Google-inspired memory importance scoring
Applies PageRank algorithm to hippocampal memory network

Author: GNJz (Qquarts)
Version: 1.0 (Pro Feature)
"""
import networkx as nx
from collections import defaultdict


class MemoryRank:
    """
    PageRank-based memory importance calculator
    
    Concept:
        Important memories = strongly connected to other memories
        (Like important webpages = many links from other pages)
    
    Usage:
        rank = MemoryRank(hippo_memory)
        scores = rank.calculate()
        importance = scores['cat']  # Get importance of 'cat'
    """
    
    def __init__(self, hippo_memory, cache_enabled=True):
        """
        Initialize MemoryRank calculator
        
        Args:
            hippo_memory: HippoMemory or HippoMemoryPro instance
            cache_enabled: Cache PageRank scores for performance
        """
        self.hippo = hippo_memory
        self.cache_enabled = cache_enabled
        self._cache = {}
        self._last_word_count = 0
    
    def build_graph(self):
        """
        Build memory graph from CA3 recurrent connections
        
        Returns:
            NetworkX DiGraph where:
            - Nodes = word_ids (memories)
            - Edges = CA3 recurrent synapses (memory associations)
            - Edge weights = synapse weights (connection strength)
        """
        G = nx.DiGraph()
        
        # Add all memories as nodes
        for word_id in self.hippo.words.keys():
            G.add_node(word_id)
        
        # Add edges from CA3 recurrent connections
        for word_id, word_info in self.hippo.words.items():
            # Check if this is Pro version (has recurrent synapses)
            if 'synapses_ca3_recurrent' not in word_info:
                continue
            
            # Get CA3 neurons for this word
            ca3_neurons = [self.hippo.ca3_neurons[i] for i in word_info['ca3']]
            
            # Iterate through recurrent synapses
            for syn in word_info['synapses_ca3_recurrent']:
                # Find which word's CA3 neuron this synapse connects to
                target_word_id = self._find_target_word(syn.post_neuron)
                
                if target_word_id and target_word_id != word_id:
                    # Add edge with synapse weight
                    weight = max(0.0, syn.weight)  # Ensure non-negative
                    if G.has_edge(word_id, target_word_id):
                        # Multiple synapses between same words -> sum weights
                        G[word_id][target_word_id]['weight'] += weight
                    else:
                        G.add_edge(word_id, target_word_id, weight=weight)
        
        return G
    
    def _find_target_word(self, neuron):
        """
        Find which word (memory) owns this CA3 neuron
        
        Args:
            neuron: CA3 neuron instance
            
        Returns:
            word_id or None
        """
        # Find neuron index
        try:
            neuron_idx = self.hippo.ca3_neurons.index(neuron)
        except ValueError:
            return None
        
        # Find which word owns this neuron
        for word_id, word_info in self.hippo.words.items():
            if neuron_idx in word_info['ca3']:
                return word_id
        
        return None
    
    def calculate(self, alpha=0.85, max_iter=100, tol=1e-6):
        """
        Calculate PageRank scores for all memories
        
        Args:
            alpha: Damping factor (0.85 = Google's original value)
            max_iter: Maximum iterations
            tol: Convergence tolerance
            
        Returns:
            Dict mapping word_id -> importance score (0.0 ~ 1.0+)
        """
        # Check cache
        current_word_count = len(self.hippo.words)
        if (self.cache_enabled and 
            self._cache and 
            self._last_word_count == current_word_count):
            return self._cache
        
        # Build memory graph
        G = self.build_graph()
        
        # Handle edge cases
        if len(G) == 0:
            return {}
        
        if len(G) == 1:
            # Single memory -> full importance
            return {list(G.nodes())[0]: 1.0}
        
        # Calculate PageRank
        try:
            # Use NetworkX's PageRank implementation
            pagerank_scores = nx.pagerank(
                G, 
                alpha=alpha,
                max_iter=max_iter,
                tol=tol,
                weight='weight'
            )
        except:
            # Fallback: uniform distribution
            pagerank_scores = {word_id: 1.0 / len(G) for word_id in G.nodes()}
        
        # Normalize to 0-1 range for easier interpretation
        if pagerank_scores:
            max_score = max(pagerank_scores.values())
            if max_score > 0:
                pagerank_scores = {
                    word_id: score / max_score 
                    for word_id, score in pagerank_scores.items()
                }
        
        # Update cache
        if self.cache_enabled:
            self._cache = pagerank_scores
            self._last_word_count = current_word_count
        
        return pagerank_scores
    
    def get_score(self, word_id, default=0.5):
        """
        Get importance score for a specific memory
        
        Args:
            word_id: Word identifier
            default: Default score if word not found
            
        Returns:
            Importance score (0.0 ~ 1.0)
        """
        scores = self.calculate()
        return scores.get(word_id, default)
    
    def get_top_memories(self, n=10):
        """
        Get top N most important memories
        
        Args:
            n: Number of memories to return
            
        Returns:
            List of (word_id, score) tuples, sorted by importance
        """
        scores = self.calculate()
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n]
    
    def clear_cache(self):
        """Clear cached PageRank scores"""
        self._cache = {}
        self._last_word_count = 0
    
    def get_stats(self):
        """
        Get statistics about memory network
        
        Returns:
            Dict with graph statistics
        """
        G = self.build_graph()
        scores = self.calculate()
        
        return {
            'num_memories': len(G.nodes()),
            'num_connections': len(G.edges()),
            'avg_connections': len(G.edges()) / max(1, len(G.nodes())),
            'max_importance': max(scores.values()) if scores else 0.0,
            'min_importance': min(scores.values()) if scores else 0.0,
            'avg_importance': sum(scores.values()) / max(1, len(scores)),
        }


def apply_memory_rank(hippo_memory, recall_results, boost_factor=2.0):
    """
    Apply MemoryRank boost to recall results
    
    Args:
        hippo_memory: HippoMemory instance
        recall_results: List of (word_id, score) from recall()
        boost_factor: How much to boost important memories
        
    Returns:
        Re-ranked results with importance boost applied
    """
    if not recall_results:
        return recall_results
    
    # Calculate MemoryRank scores
    ranker = MemoryRank(hippo_memory)
    importance_scores = ranker.calculate()
    
    # Apply boost to recall scores
    boosted_results = []
    for word_id, recall_score in recall_results:
        importance = importance_scores.get(word_id, 0.5)
        # Boost formula: original_score * (1 + importance * boost_factor)
        boosted_score = recall_score * (1.0 + importance * boost_factor)
        boosted_results.append((word_id, boosted_score))
    
    # Re-sort by boosted scores
    boosted_results.sort(key=lambda x: x[1], reverse=True)
    
    return boosted_results

