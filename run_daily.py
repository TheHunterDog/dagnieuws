import argparse
import os
import shutil

import pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Target date YYYY-MM-DD")
    args = parser.parse_args()

    digest_path, date_str = pipeline.run_pipeline(args.date)
    print(f"Digest path: {digest_path}")
    print(f"Date string: {date_str}")
#     Copy to web/src/content/daily_digests/
    os.makedirs(f"web/src/content/daily_digests", exist_ok=True)


# copy digest path to web/src/content/daily_digests/ and replace always
    if os.path.exists(f"web/src/content/daily_digests/{date_str}.md"):
        os.remove(f"web/src/content/daily_digests/{date_str}.md")
    shutil.copy(digest_path, f"web/src/content/daily_digests/{date_str}.md")


