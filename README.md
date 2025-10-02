# Monoversion

A calendar-based verisoning scheme appropriate for trunk-based application development as in a monorepo.

Monoversion versions are structured as follows

```
let y = <year>
    w = <week>
    cw = <commits since first commit of the week to the merge base>
    cb = <commits since the merge base>
    id = <sha7 of HEAD>
    marker = ".dirty" if `git status --porcelain` else ""
in
    f"{y}.{w}.{cw}" + f"-post{cb}.{id:11}{marker}" if (cb > 0 or marker) else ""
```

## Examples

- `2025.23.1` The 23rd week of 2025, 1st commit of the week.
- `2025.28.52-post1.fad96ae6fa8` The 28th week of 2025, 52 commits into the week, one commit into a branch.
- `2025.28.46-post0.9aae26a05be.dirty` The 28th week of 2025, 46 commits since the first commit of the week, +0 (on main), last commit `9aae26a05be`, dirty.

## Version format properties

- Compliant SemVer version https://semver.org/#backusnaur-form-grammar-for-valid-semver-versions
- Sorts by date and sequence of commits to `main` under PyPi/Maven/Semver comparison
- Version sequence depends only on repo history, releases don't need to be tagged
- The current date is not a factor; the only consideration is commit dates
- Branched states are explicitly marked
- Dirty states are explicitly marked
- If a branch is rebased the `main` stem will change but the sequence will remain

Note that due to https://github.com/moby/moby/issues/16304 /
https://github.com/opencontainers/distribution-spec/issues/154, the `+<build>`
syntax which would be more appropriate for attaching the build commit is avoided
so that monovers are usable for Docker artifacts.

## Usage

This repository contains a reference Python purelib implementation of computing
the monoversion for a cloned git repo, and a Github Actions `action.yaml` which
wraps it up for ease of use.

```yaml
...

jobs:
  release:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - id: monoversion
        uses: arrdem/monoversion@2025.40.5
        with:
          trunk: 'origin/your-custom-trunk-branch-name'

      - run: |
        # Run your release usage consuming the monoversion
        ./release.sh ${{ steps.monoversion.outputs.monoversion }}
```

## Credits

Somewhat inspired by https://blog.aspect.build/versioning-releases-from-a-monorepo

Somewhat inspired by https://calver.org/


## License

Copyright 2025 Reid D. 'arrdem' McKenzie.

Published under the terms of the Apache 2.0 license, see [LICENSE](LICENSE.md).
