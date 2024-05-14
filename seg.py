import os
from collections import defaultdict

def list_files_with_sizes(startpath):
    """ Returns a list of files and their sizes from the given startpath. """
    file_list = []
    for root, dirs, files in os.walk(startpath):
        for file in files:
            filepath = os.path.join(root, file)
            size = os.path.getsize(filepath)
            file_list.append((filepath, size))
    return file_list

def print_tree(node, indent=0):
    """ Prints the tree structure, indenting child nodes. """
    # Print the current node's name with indentation
    print(' ' * indent + node.name + f" ({node.total_size})")
    # Recursively print each child, increasing the indentation
    for child in node.children.values():
        print_tree(child, indent + 2)
    # Optionally, list files at this node with further indentation
    if node.files:
        for file, size in node.files:
            print(' ' * (indent + 2) + os.path.basename(file) + f" ({size} bytes)")


class TreeNode:
    """ A node in the directory tree. """
    def __init__(self, name):
        self.name = name
        self.children = defaultdict(lambda: None)  # Temporarily set to None
        self.files = []
        self.total_size = 0

    def get_child(self, name):
        """ Retrieves a child node, creating it if it does not exist. """
        if not self.children[name]:
            self.children[name] = TreeNode(name)
        return self.children[name]

def build_tree(file_list):
    """ Builds a tree from the given list of files. """
    root = TreeNode('root')
    for filepath, size in file_list:
        parts = filepath.strip(os.sep).split(os.sep)
        current = root
        for part in parts[:-1]:  # Traverse through parts, skipping the last one (file)
            current = current.get_child(part)
        current.files.append((filepath, size))
        # current.total_size += size
        # print_tree(root)
    return root

# def dfs_collect_batches(node, max_size=1e9):
def dfs_collect_batches(node, max_size=999):
    """ Collects batches of files using DFS, ensuring no batch exceeds the max_size. """
    batches = []
    current_batch = []
    current_batch_size = 0

    # Process current node's files
    for filepath, size in node.files:
        if current_batch_size + size > max_size:
            batches.append(current_batch)
            current_batch = []
            current_batch_size = 0
        current_batch.append(filepath)
        current_batch_size += size

    # Process child nodes
    for child in node.children.values():
        child_batches = dfs_collect_batches(child, max_size)
        for batch in child_batches:
            batch_size = sum(os.path.getsize(f) for f in batch)
            if current_batch_size + batch_size > max_size:
                batches.append(current_batch)
                current_batch = []
                current_batch_size = 0
            current_batch.extend(batch)
            current_batch_size += batch_size

    if current_batch:
        batches.append(current_batch)
    return batches

def recalculate_sizes(node):
    """ Recalculates the total size of each node to include the size of all its children. """
    # Start with the size of direct files under this node
    total_size = sum(size for _, size in node.files)
    # Add the size of all children
    for child in node.children.values():
        child_size = recalculate_sizes(child)  # Recursively calculate the size for children
        total_size += child_size
    node.total_size = total_size  # Update the node's total size
    return total_size  # Return the total size for use by parent nodes

def generate_cp_commands(batches, dest_directory):
    """ Generates cp commands to copy each batch to the destination directory. """
    commands = []
    for batch in batches:
        files = ' '.join([f"'{f}'" for f in batch])
        command = f"cp {files} '{dest_directory}'"
        commands.append(command)
    return commands

# Parameters
source_directory = '/path/to/source'
destination_directory = '/path/to/destination'

# Get files and sizes
files_with_sizes = list_files_with_sizes(source_directory)

# Build the directory tree
tree_root = build_tree(files_with_sizes)

print_tree(tree_root)

# Recalculate sizes
recalculate_sizes(tree_root)

print_tree(tree_root)

# Collect batches of files
batches = dfs_collect_batches(tree_root)

# Generate commands
cp_commands = generate_cp_commands(batches, destination_directory)

# Output commands
for cmd in cp_commands:
    print(cmd)
