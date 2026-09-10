import argparse
import pandas as pd


def transform(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["email"] = result["email"].str.strip().str.lower()
    result["order_date"] = pd.to_datetime(result["order_date"], errors="raise")
    result["amount"] = pd.to_numeric(result["amount"], errors="raise")
    return result.drop_duplicates("order_id")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="sample/orders.csv")
    parser.add_argument("--output", default="output/orders.parquet")
    args = parser.parse_args()
    transform(pd.read_csv(args.input)).to_parquet(args.output, index=False)

