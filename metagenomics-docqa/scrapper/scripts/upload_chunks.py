import argparse
import json
from pathlib import Path

import httpx


def main():
    p = argparse.ArgumentParser()
    p.add_argument("jsonl", type=Path)
    p.add_argument("--api", default="http://localhost:8000")
    p.add_argument("--email")
    p.add_argument("--password")
    args = p.parse_args()

    with httpx.Client(base_url=args.api, timeout=60) as c:
        r = c.post("/auth/login", data={"username": args.email, "password": args.password})
        r.raise_for_status()
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        content = args.jsonl.read_bytes()
        files = {"f": (args.jsonl.name, content, "application/json")}
        rr = c.post("/upload/file", headers=headers, files=files)
        print(rr.status_code, rr.text)


if __name__ == "__main__":
    main()


