import argparse
import pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Target date YYYY-MM-DD")
    args = parser.parse_args()
    pipeline.run_pipeline(args.date)
