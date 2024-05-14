import os

def list_files_with_sizes(startpath):
    """ Returns a list of files and their sizes from the given startpath. """
    file_list = []
    for root, dirs, files in os.walk(startpath):
        for file in files:
            filepath = os.path.join(root, file)
            size = os.path.getsize(filepath)
            file_list.append((filepath, size))
    return file_list

def sort_files_dfs(file_list):
    """ Sorts files by their depth-first search order in the directory tree. """
    
    
    file_list.sort(key=lambda item: (item[0].count(os.sep), item[0]))
    # file_list.sort(key=lambda item: (item[0].count(os.sep), item[0].split(os.sep)[-2], item[0].split(os.sep)[-1]))
    file_list.reverse()
    return file_list

def chunk_directories(file_list, startpath, max_size=1e9):
    """ Groups files into directory-based chunks where each chunk has a cumulative size <= max_size. """
    dir_dict = {}
    for filepath, size in file_list:
        # Determine the top-level subdirectory
        sub_path = filepath[len(startpath):].strip(os.sep).split(os.sep)[0]
        full_dir_path = os.path.join(startpath, sub_path)
        if full_dir_path not in dir_dict:
            dir_dict[full_dir_path] = 0
        dir_dict[full_dir_path] += size

    # Now aggregate into chunks
    chunks = []
    current_chunk = []
    current_size = 0
    for dir_path, total_size in dir_dict.items():
        if current_size + total_size > max_size:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = [dir_path]
            current_size = total_size
        else:
            current_chunk.append(dir_path)
            current_size += total_size
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def generate_cp_commands(chunks, dest_directory):
    """ Generates cp commands to copy each chunk to the destination directory. """
    commands = []
    for i, chunk in enumerate(chunks):
        files = ' '.join([f"'{f}'" for f in chunk])
        command = f"cp {files} '{dest_directory}'"
        commands.append(command)
    return commands

# Parameters
source_directory = '/path/to/source'
destination_directory = '/path/to/destination'

# Get files and sizes
files_with_sizes = list_files_with_sizes(source_directory)

# Sort files by DFS order
sorted_files = sort_files_dfs(files_with_sizes)

# Chunk files by directory
chunks = chunk_directories(sorted_files, source_directory)

# Generate commands
cp_commands = generate_cp_commands(chunks, destination_directory)

# Output commands
for cmd in cp_commands:
    print(cmd)
