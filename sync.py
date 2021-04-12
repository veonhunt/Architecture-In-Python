import hashlib
import os
from pathlib import Path
import shutil

BLOCKSIZE = 65536

def hash_file(path):
    hasher = hashlib.sha1()
    with path.open('rb') as file:
        buf = file.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)
    return hasher.hexdigest()


def determine_actions(src_hashes, dst_hashes, src_folder, dst_folder):
    # Functional core
	for sha, filename in src_hashes.items():
		if sha not in dst_hashes:	
			# copy from source to dest
			sourcepath = Path(src_folder) / filename
			destpath = Path(dst_folder) / filename
			yield 'copy', sourcepath, destpath
		
		
		elif dst_hashes[sha] != filename:
			# file has different name in dest so, rename
			old_dest = Path(dst_folder) / dst_hashes[sha]
			new_dest = Path(dst_folder) / filename
			yield 'move', old_dest, new_dest
			
	for sha, filename in dst_hashes.items():
		if sha not in src_hashes:
			# remove files that are in dest, but not found in source
			yield 'delete', dst_folder / filename


def sync(source, dest):
	# imperative shell step 1 - gather inputs
	source_hashes = read_paths_and_hashes(source)
	dest_hashes = read_paths_and_hashes(dest)
	
	# step 2 - call functional core
	actions = determine_actions(source_hashes, dest_hashes, source, dest)
	
	# imperative shell step 3 - apply outputs
	for action, *paths in actions:
		if action == 'copy':
			shutil.copyfile(*paths)
		if action == 'move':
			shutil.move(*paths)
		if action == 'delete':
			os.remove(paths[0])


def read_paths_and_hashes(root):
	hashes = {}
	for folder, _, files in os.walk(root):
		for fn in files:
			# keys are hashed contents, value is file name
			hashes[hash_file(Path(folder) / fn)] = fn
	return hashes