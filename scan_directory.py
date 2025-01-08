import os
import json
from pathlib import Path

def scan_directory(start_path):
    """
    Scans a directory and returns a structured representation of its contents.
    Includes files, their sizes, and modification times.
    """
    structure = {
        "path": start_path,
        "type": "directory",
        "contents": []
    }
    
    try:
        with os.scandir(start_path) as entries:
            for entry in entries:
                # Skip hidden files and directories
                if entry.name.startswith('.'):
                    continue
                    
                info = {
                    "name": entry.name,
                    "type": "directory" if entry.is_dir() else "file",
                }
                
                if entry.is_file():
                    # Get file stats
                    stats = entry.stat()
                    info.update({
                        "size": stats.st_size,
                        "modified": stats.st_mtime,
                        "extension": os.path.splitext(entry.name)[1].lower()
                    })
                    structure["contents"].append(info)
                elif entry.is_dir():
                    # Recursively scan subdirectories
                    info.update(scan_directory(entry.path))
                    structure["contents"].append(info)
                    
    except PermissionError:
        structure["error"] = "Permission denied"
        
    return structure

def format_structure(structure, indent=0):
    """
    Formats the directory structure as a readable string.
    """
    output = []
    indent_str = "  " * indent
    
    if "error" in structure:
        return f"{indent_str}[Access Denied]"
    
    for item in sorted(structure["contents"], key=lambda x: (x["type"] != "directory", x["name"])):
        if item["type"] == "directory":
            output.append(f"{indent_str}📁 {item['name']}/")
            if "contents" in item:
                output.append(format_structure(item, indent + 1))
        else:
            size_str = format_size(item["size"])
            output.append(f"{indent_str}📄 {item['name']} ({size_str})")
            
    return "\n".join(output)

def format_size(size):
    """
    Formats file size in a human-readable format.
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"

def main():
    # Get the directory path from user input
    print("Enter the directory path to scan (or press Enter for current directory):")
    path = input().strip() or '.'
    
    # Expand user directory if needed
    path = os.path.expanduser(path)
    
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist.")
        return
        
    # Scan the directory
    structure = scan_directory(path)
    
    # Print formatted structure
    print("\nDirectory Structure:")
    print("===================")
    print(format_structure(structure))
    
    # Save to file
    output_file = "directory_structure.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(format_structure(structure))
    print(f"\nStructure has been saved to {output_file}")

if __name__ == "__main__":
    main()