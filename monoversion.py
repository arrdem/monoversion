#!/usr/bin/env python3

import argparse
from datetime import datetime, timedelta, UTC
from subprocess import CalledProcessError, check_call, check_output

PARSER = argparse.ArgumentParser(__name__)
PARSER.add_argument("--start", default="HEAD")
PARSER.add_argument("--end", default="origin/main")


def _rev_parse(obj):
  return check_output(["git", "rev-parse", obj]).decode("utf-8").strip()


def main():
  opts = PARSER.parse_args()

  start = _rev_parse(opts.start)
  end = _rev_parse(opts.end)

  parent = check_output(["git", "merge-base", start, end]).decode("utf-8").strip()
  previous_timestamp = int(
    check_output(["git", "show", "-s", "--pretty=%ct", parent]).decode("utf-8").strip()
  )

  # Normalize to the UTC timezone Gregorian calendar
  previous_date = datetime.fromtimestamp(previous_timestamp, tz=UTC)

  # Take the previous date and subtract the number of days since monday (day 0
  # in Python), then truncate the time part to 0. This gives you monday of the
  # same week. Note that this WILL NOT underflow from Monday to the previous
  # Monday because we're subtracting 0.
  monday_date = (previous_date - timedelta(days=previous_date.weekday())).replace(
    hour=0, minute=0, second=0
  )

  # Count commits between the merge base and the first commit of its week
  week_commits = (
    check_output(
      [
        "git",
        "log",
        "--oneline",
        f"--since={int(monday_date.timestamp())}",
        f"--until={previous_timestamp}",
      ]
    )
    .splitlines()
    .__len__()
  )

  # Count revisions between us and the merge base.
  # Note we can skip doing that if we're at the merge base.
  branch_commits = 0
  if parent != start:
    branch_commits = (
      check_output(["git", "rev-list", "--ancestry-path", f"{parent}...{start}"])
      .splitlines()
      .__len__()
    )

  # Figure out if we need a dirty marker
  suffix = ""
  try:
    check_call(["git", "diff", "--quiet"])
  except CalledProcessError:
    suffix = ".dirty"

  tail = f"-{branch_commits}.{start[:11]}{suffix}" if branch_commits else ""

  print(f"{monday_date.year}.{monday_date.strftime('%V')}.{week_commits}{tail}")


if __name__ == "__main__":
  main()
