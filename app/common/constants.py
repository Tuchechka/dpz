"""Конфігураційні константи проекту."""
from pathlib import Path

# Корінь проекту (для відносних шляхів)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# База даних
DATABASE_URL = f"sqlite:///{PROJECT_ROOT}/wordpress.db"

# CSV з вихідними даними
CSV_FILE_PATH = PROJECT_ROOT / "wordpress_data.csv"

# Скільки рядків генерувати за замовчуванням
DEFAULT_CSV_ROWS = 1100