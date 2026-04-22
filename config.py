import os

# Root project folder (folder containing this file)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Common folders
TEST_DIR = os.path.join(ROOT_DIR, "test")
PROMPTS_DIR = os.path.join(TEST_DIR, "test_prompts")
RUN_DIR = os.path.join(TEST_DIR, "run_tests")

# Files
TEST_PROMPTS_V1 = os.path.join(PROMPTS_DIR, "test_prompts.json")
TEST_PROMPTS_V2 = os.path.join(PROMPTS_DIR, "test_prompts_2.json")

MEMORY_FILE = os.path.join(ROOT_DIR, "memory.json")
STATS_FILE = os.path.join(ROOT_DIR, "stats.json")