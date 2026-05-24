from pathlib import Path
import os

PACKAGE_DIR = Path(__file__).resolve().parent
BASE_DIR = PACKAGE_DIR.parent

DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "current_model"
SAVE_DIR = BASE_DIR / "saved_models"
MMSEQS_CACHE_DIR = BASE_DIR / "mmseqs_storage"


from .model import *
from .utils import *