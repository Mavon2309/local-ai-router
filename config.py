import os

# =====================================
# ROOT
# =====================================
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# =====================================
# TESTING SYSTEM
# =====================================
TEST_DIR = os.path.join(ROOT_DIR, "test")
DATASETS_DIR = os.path.join(TEST_DIR, "datasets")
RESULTS_DIR = os.path.join(TEST_DIR, "results")

# default dataset
DEFAULT_DATASET = "v3"


def get_dataset_path(name=None):
    """
    Returns full path to dataset JSON.
    Example: get_dataset_path("v3") → test/datasets/v3.json
    """
    name = name or DEFAULT_DATASET
    return os.path.join(DATASETS_DIR, f"{name}.json")


# =====================================
# CORE FILES
# =====================================
MEMORY_FILE = os.path.join(ROOT_DIR, "memory.json")
STATS_FILE = os.path.join(ROOT_DIR, "stats.json")