from pathlib import Path  # Necessary library for path extracting.


# CONSTANT variable defined in uppercase, points to Path object of current directory + parent + parent. (results in ~/.../pythondb)
ROOT_DIR = Path(__file__).parent.parent
