import json
import copy
from .helpers import parse_share_string, multiply_shares, add_shares, get_share_tuple_from_edge, update_edge_shares

def calculate_real_shares(network):
    """
    Calculates the real ownership shares for entities in the network.
    
    Args:
        network (list): List of edges representing ownership relationships
        
    Returns:
        list: Updated network with real_lower_share, real_average_share, and real_upper_share values
    """
    # Create edge maps and sort edges
    outgoing_edges, incoming_edges = create_edge_maps(network)
    sorted_edges = sort_edges_by_depth(network)
    
    # Initialize shares
    initialize_shares(network)

    # Iteratively calculate real shares until convergence
    max_iterations = 10
    epsilon = 0.001

    for iteration in range(max_iterations):
        max_change = 0.0
        previous_values_dict = {item['id']: item for item in copy.deepcopy(network)}

        for edge in sorted_edges:
            if not edge['active']:
                continue
            
            source_id = edge['source']
            target_id = edge['target']
            target_depth = edge['target_depth']
            edge_share = parse_share_string(edge['share'])

            if target_depth >= 0:
                max_change = process_upstream_edge(edge, source_id, target_id, edge_share, 
                                                outgoing_edges, previous_values_dict, max_change)
            else:
                max_change = process_downstream_edge(edge, source_id, target_id, edge_share, 
                                                  incoming_edges, previous_values_dict, max_change)

        if max_change < epsilon:
            print(f"Converged after {iteration + 1} iterations.")
            break

    return network

def initialize_shares(edges):
    """
    Initialize real shares for all edges.
    
    Args:
        edges (list): List of edges
    """
    for edge in edges:
        if not edge['active']:
                continue
        if edge['source_depth'] == 0 or edge['target_depth'] == 0:
            # Focus company edges get their direct share values
            edge_share = parse_share_string(edge['share'])
            lower, avg, upper = edge_share
            edge['real_lower_share'] = round(lower * 100.0, 2)
            edge['real_average_share'] = round(avg * 100.0, 2)
            edge['real_upper_share'] = round(upper * 100.0, 2)
        else:
            # Other edges start with zero
            edge['real_lower_share'] = 0.0
            edge['real_average_share'] = 0.0
            edge['real_upper_share'] = 0.0

def create_edge_maps(edges):
    """
    Creates maps of entity ID to outgoing and incoming edges for faster lookup.
    
    Args:
        edges (list): List of edges
        
    Returns:
        tuple: (outgoing_edges, incoming_edges) dictionaries
    """
    outgoing_edges = {}
    incoming_edges = {}
    
    for edge in edges:
        source_id = edge['source']
        target_id = edge['target']
        
        # For owners (target_depth >= 0)
        if edge['target_depth'] >= 0:
            if source_id not in outgoing_edges:
                outgoing_edges[source_id] = []
            outgoing_edges[source_id].append(edge)
            
        # For owned entities (target_depth < 0)
        if edge['target_depth'] < 0:
            if target_id not in incoming_edges:
                incoming_edges[target_id] = []
            incoming_edges[target_id].append(edge)
    
    return outgoing_edges, incoming_edges

def sort_edges_by_depth(edges):
    """
    Sorts edges by depth to process them in the correct order.
    
    Args:
        edges (list): List of edges
        
    Returns:
        list: Sorted edges
    """
    # Split into two groups for different sorting strategies
    upstream_edges = [e for e in edges if e['source_depth'] > 0 and e['target_depth'] >= 0]
    downstream_edges = [e for e in edges if e['target_depth'] < 0]

    # Sort upstream edges by ascending target_depth
    sorted_upstream = sorted(upstream_edges, key=lambda e: e['target_depth'])
    
    # Sort downstream edges by descending target_depth
    sorted_downstream = sorted(downstream_edges, key=lambda e: -e['target_depth'])
    
    # Combine while maintaining order
    return sorted_upstream + sorted_downstream

def calculate_change(edge, previous_values_dict):
    """
    Calculates the change in share value from previous iteration.
    
    Args:
        edge (dict): Current edge
        previous_values_dict (dict): Dictionary of previous edge values
        
    Returns:
        float: Absolute change in lower share value
    """
    previous_edge_data = previous_values_dict.get(edge['id'], {})
    previous_share = float(previous_edge_data.get('real_lower_share', 0.0) or 0.0)
    current_share = edge['real_lower_share']
    return abs(current_share - previous_share)

def process_upstream_edge(edge, source_id, target_id, edge_share, outgoing_edges, previous_values_dict, max_change):
    """
    Process an upstream edge (target_depth >= 0).
    
    Args:
        edge (dict): Edge to process
        source_id: Source entity ID
        target_id: Target entity ID
        edge_share: Parsed share tuple
        outgoing_edges (dict): Map of outgoing edges
        previous_values_dict (dict): Dictionary of previous edge values
        max_change (float): Current maximum change
        
    Returns:
        float: Updated maximum change
    """
    # Calculate direct ownership
    if target_id in outgoing_edges:
        target_edge = outgoing_edges[target_id][0]
        target_share = get_share_tuple_from_edge(target_edge)
        real_share = multiply_shares(edge_share, target_share)
    else:
        real_share = edge_share

    # Update edge with direct ownership
    update_edge_shares(edge, real_share)
    
    # Calculate indirect ownership through other paths
    if source_id in outgoing_edges:
        for indirect_source_edge in outgoing_edges[source_id]:
            if indirect_source_edge.get('id') != edge['id']:
                # Calculate indirect ownership
                indirect_share = parse_share_string(indirect_source_edge.get('share'))
                
                indirect_target_edge = next((e for e in outgoing_edges.get(indirect_source_edge['target'], [])), None)
                if indirect_target_edge and indirect_target_edge.get('real_lower_share') is not None:
                    indirect_target_share = get_share_tuple_from_edge(indirect_target_edge)
                else:
                    indirect_target_share = (0.0, 0.0, 0.0)
                
                # Calculate real indirect share
                if indirect_source_edge['target_depth'] != 0:
                    indirect_real_share = multiply_shares(indirect_share, indirect_target_share)
                else:
                    indirect_real_share = indirect_share
                
                # Combine direct and indirect shares
                new_real_share = add_shares(indirect_real_share, real_share)
                update_edge_shares(edge, new_real_share)
                
                # Calculate change for convergence check
                previous_share = float(previous_values_dict.get(edge['id'], {}).get('real_lower_share', 0.0) or 0.0)
                change = abs(edge['real_lower_share'] - previous_share)
                max_change = max(max_change, change)
    
    return max_change

def process_downstream_edge(edge, source_id, target_id, edge_share, incoming_edges, previous_values_dict, max_change):
    """
    Process a downstream edge (target_depth < 0).
    
    Args:
        edge (dict): Edge to process
        source_id: Source entity ID
        target_id: Target entity ID
        edge_share: Parsed share tuple
        incoming_edges (dict): Map of incoming edges
        previous_values_dict (dict): Dictionary of previous edge values
        max_change (float): Current maximum change
        
    Returns:
        float: Updated maximum change
    """
    # Calculate direct ownership
    if source_id in incoming_edges:
        source_edge = incoming_edges[source_id][0]
        source_share = get_share_tuple_from_edge(source_edge)
        real_share = multiply_shares(edge_share, source_share)
    else:
        real_share = edge_share

    # Update edge with direct ownership
    update_edge_shares(edge, real_share)
    
    # Calculate indirect ownership through other paths
    if target_id in incoming_edges:
        for indirect_target_edge in incoming_edges[target_id]:
            if indirect_target_edge.get('id') != edge['id']:
                # Calculate indirect ownership
                indirect_share = parse_share_string(indirect_target_edge.get('share'))
                
                indirect_source_edge = next((e for e in incoming_edges.get(indirect_target_edge['source'], [])), None)
                if indirect_source_edge and indirect_source_edge.get('real_lower_share') is not None:
                    indirect_source_share = get_share_tuple_from_edge(indirect_source_edge)
                else:
                    indirect_source_share = (0.0, 0.0, 0.0)
                
                # Calculate real indirect share
                if indirect_target_edge['source_depth'] != 0:
                    indirect_real_share = multiply_shares(indirect_share, indirect_source_share)
                else:
                    indirect_real_share = indirect_share
                
                # Combine direct and indirect shares
                new_real_share = add_shares(indirect_real_share, real_share)
                update_edge_shares(edge, new_real_share)
                
                # Calculate change for convergence check
                change = calculate_change(edge, previous_values_dict)
                max_change = max(max_change, change)
    
    return max_change

def main(input_file, output_file):
    """
    Process network data from input file and write results to output file.
    
    Args:
        input_file (str): Path to input JSON file
        output_file (str): Path to output JSON file
    """
    with open(input_file, 'r') as f:
        network = json.load(f)

    result = calculate_real_shares(network)

    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

# For direct script execution
if __name__ == "__main__":
    import sys
    
    # Use command line arguments if provided, otherwise use default paths
    input_path = sys.argv[1] if len(sys.argv) > 1 else 'data/ResightsApS.json'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'data/output.json'
    
    main(input_path, output_path)
