"""
babyHippo Storage
Save and load memory state to/from JSON files
"""
import json
import os
from datetime import datetime


def save_memory(data, path):
    """
    Save memory data to JSON file
    
    Args:
        data: Dictionary containing memory state
        path: File path to save to
    
    Example:
        save_memory({"words": ["cat", "dog"]}, "memory.json")
    """
    # Add metadata
    data['saved_at'] = datetime.now().isoformat()
    
    # Ensure directory exists
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    # Save to file
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Memory saved: {path}")


def load_memory(path):
    """
    Load memory data from JSON file
    
    Args:
        path: File path to load from
    
    Returns:
        Dictionary containing memory state
    
    Example:
        data = load_memory("memory.json")
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Memory file not found: {path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📂 Memory loaded: {path}")
    if 'saved_at' in data:
        print(f"   Saved at: {data['saved_at']}")
    
    return data


def list_memory_files(directory="."):
    """
    List all memory files in a directory
    
    Args:
        directory: Directory to search (default: current)
    
    Returns:
        List of .json file paths
    """
    if not os.path.exists(directory):
        return []
    
    files = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            files.append(os.path.join(directory, filename))
    
    return sorted(files)


def delete_memory(path):
    """
    Delete a memory file
    
    Args:
        path: File path to delete
    """
    if os.path.exists(path):
        os.remove(path)
        print(f"🗑️  Memory deleted: {path}")
    else:
        print(f"⚠️  File not found: {path}")
