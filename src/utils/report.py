import os
import glob
from distutils.dir_util import copy_tree

import src.constants.path as path


def get_latest_dirpath(dir_path):
    return max(glob.glob(os.path.join(dir_path, '*/')), key=os.path.getmtime)


def generate(dir_name):
    production_dir = path.PRODUCTION_HISTORICAL_RAWDATA_DIR_PATH
    from_dir = os.path.join(production_dir, dir_name)
    to_dir = os.path.join(path.REPORTS_DIR, dir_name)

    copy_tree(from_dir, to_dir)


def generate_latest():
    production_dir = path.PRODUCTION_HISTORICAL_RAWDATA_DIR_PATH
    from_dir = get_latest_dirpath(production_dir)
    dir_name = from_dir.split('/')[-2]

    generate(dir_name)
