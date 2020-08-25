# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.getcwd())
from watcher import Watcher

# input: abs/path/to/dir/to/be/watched
if __name__ == "__main__":
    src_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    config = {'SRC_PATH': src_path,'DB_HOST': 'localhost', 'DB_NAME': 'bmat', 'DB_USER': 'postgres', 'DB_PASSWORD': 'postgres'}
    Watcher(config).run()