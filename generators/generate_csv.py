"""CLI генератор CSV-файлу з тестовими даними для WordPress."""
import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from app.common.constants import CSV_FILE_PATH, DEFAULT_CSV_ROWS
from app.common.logger import get_logger

log = get_logger(__name__)


# ============================================================
# Пули даних для генерації
# ============================================================

CATEGORIES = [
    "Technology", "Programming", "Web Development", "Design",
    "Marketing", "Business", "Education", "Health",
    "Travel", "Photography",
]

TAGS = [
    "python", "javascript", "fastapi", "django", "flask", "react",
    "vue", "nodejs", "css", "html", "docker", "kubernetes",
    "aws", "azure", "gcp", "sql", "nosql", "mongodb",
    "postgresql", "redis", "git", "github", "ci-cd", "testing",
    "tdd", "agile", "rest-api", "graphql", "microservices", "devops",
]

POST_TITLE_TEMPLATES = [
    "Getting Started with {tag}",
    "Best Practices for {tag}",
    "Why {tag} Matters in 2024",
    "Deep Dive into {tag}",
    "10 Tips for Mastering {tag}",
    "Common Mistakes in {tag}",
    "{tag} vs Alternatives",
    "Building Production-Ready {tag} Apps",
    "The Future of {tag}",
    "{tag} for Beginners",
]

LOREM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris."
)

COMMENT_TEMPLATES = [
    "Great post! Really helpful.",
    "Thanks for sharing this.",
    "I disagree with point 3 -- here's why...",
    "Very insightful, looking forward to more.",
    "This is exactly what I was looking for.",
    "Could you elaborate on the second part?",
    "Bookmarked for later reference.",
    "Just tried this approach -- it works.",
    "Nice writeup. Subscribed.",
    "I had a similar experience recently.",
]

MIME_BY_EXT = {
    "jpg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
    "gif": "image/gif",
}

# Має відповідати полям CsvRowDto
CSV_FIELDS = [
    "post_external_id", "post_title", "post_slug", "post_body",
    "post_status", "post_published_at",
    "author_username", "author_email", "author_role",
    "categories", "tags",
    "media_filename", "media_url", "media_mime_type",
    "comment_author_name", "comment_author_email", "comment_content",
]


# ============================================================
# Генератор
# ============================================================

class CsvGenerator:
    def __init__(self, output_path: Path, target_rows: int, seed: int = 42):
        self._output = output_path
        self._target = target_rows
        random.seed(seed)  # відтворюваність

    def generate(self) -> int:
        log.info(f"Generating CSV (>= {self._target} rows) -> {self._output}")

        # Підготовка пулів
        authors = [self._make_author(i) for i in range(20)]
        media_pool = [self._make_media(i) for i in range(50)]

        rows: List[dict] = []
        post_idx = 0
        while len(rows) < self._target:
            post_idx += 1
            post = self._make_post(post_idx, authors)
            categories = self._pick_pipe_list(CATEGORIES, 1, 3)
            tags = self._pick_pipe_list(TAGS, 1, 4)
            media = random.choice(media_pool) if random.random() < 0.7 else None

            num_comments = random.randint(3, 7)
            for _ in range(num_comments):
                comment = self._make_comment()
                rows.append(self._build_row(post, categories, tags, media, comment))

        self._write_csv(rows)
        log.info(f"Done: {len(rows)} rows ({post_idx} unique posts)")
        return len(rows)

    # ============================================================
    # Helpers
    # ============================================================

    def _make_author(self, idx: int) -> dict:
        return {
            "username": f"author_{idx:03d}",
            "email": f"author_{idx:03d}@example.com",
            "role": random.choice(["author", "editor", "contributor"]),
        }

    def _make_media(self, idx: int) -> dict:
        ext = random.choice(list(MIME_BY_EXT.keys()))
        filename = f"image_{idx:04d}.{ext}"
        return {
            "filename": filename,
            "url": f"/uploads/{filename}",
            "mime_type": MIME_BY_EXT[ext],
        }

    def _make_post(self, idx: int, authors: list) -> dict:
        tag = random.choice(TAGS)
        nice_tag = tag.replace("-", " ").title()
        title = random.choice(POST_TITLE_TEMPLATES).format(tag=nice_tag)
        slug = f"{tag}-{idx:04d}"
        author = random.choice(authors)
        published = datetime.now() - timedelta(days=random.randint(0, 365))
        # 75% постів -- published, 25% -- draft
        status = "published" if random.random() < 0.75 else "draft"
        return {
            "external_id": f"p_{idx:04d}",
            "title": title,
            "slug": slug,
            "body": LOREM * random.randint(1, 3),
            "status": status,
            "published_at": published.isoformat() if status == "published" else "",
            "author": author,
        }

    def _make_comment(self) -> dict:
        idx = random.randint(1, 100)
        return {
            "author_name": f"User {idx:03d}",
            "author_email": f"user{idx:03d}@example.com",
            "content": random.choice(COMMENT_TEMPLATES),
        }

    def _pick_pipe_list(self, source: list, min_n: int, max_n: int) -> str:
        n = random.randint(min_n, max_n)
        return "|".join(random.sample(source, n))

    def _build_row(
        self,
        post: dict,
        categories: str,
        tags: str,
        media: Optional[dict],
        comment: dict,
    ) -> dict:
        author = post["author"]
        return {
            "post_external_id": post["external_id"],
            "post_title": post["title"],
            "post_slug": post["slug"],
            "post_body": post["body"],
            "post_status": post["status"],
            "post_published_at": post["published_at"],
            "author_username": author["username"],
            "author_email": author["email"],
            "author_role": author["role"],
            "categories": categories,
            "tags": tags,
            "media_filename": media["filename"] if media else "",
            "media_url": media["url"] if media else "",
            "media_mime_type": media["mime_type"] if media else "",
            "comment_author_name": comment["author_name"],
            "comment_author_email": comment["author_email"],
            "comment_content": comment["content"],
        }

    def _write_csv(self, rows: List[dict]) -> None:
        with open(self._output, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(rows)


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Generate WordPress test CSV")
    parser.add_argument(
        "--output", type=Path, default=CSV_FILE_PATH,
        help=f"Output path (default: {CSV_FILE_PATH})",
    )
    parser.add_argument(
        "--rows", type=int, default=DEFAULT_CSV_ROWS,
        help=f"Minimum rows (default: {DEFAULT_CSV_ROWS})",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility",
    )
    args = parser.parse_args()

    CsvGenerator(
        output_path=args.output,
        target_rows=args.rows,
        seed=args.seed,
    ).generate()


if __name__ == "__main__":
    main()