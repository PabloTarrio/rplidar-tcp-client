Thanks for your interest in contributing!

## Workflow
- Create a new branch from `main`.
- Make your changes in that branch.
- Open a Pull Request (PR) to `main`.
- Wait for CI checks to pass (`lint` and `test`) before merging.
- We use **Squash and merge** to keep history clean.

## Requirements to merge
- 1 approval is required (PR review).
- CI must be green:
  - `lint`
  - `test`
- The PR branch must be up to date with `main`.

## Making changes
- Keep PRs small and focused (one change per PR when possible).
- Add or update documentation when behavior changes.

## Commit messages
- Use clear, short messages (imperative mood), e.g.:
  - `Fix navigation timeout`
  - `Add CI badge to README`

## If CI fails
- Open the PR “Checks” tab and review the failing job logs.
- Push fixes to the same PR branch; CI will re-run automatically.

## Questions
If something is unclear, open an issue or start a discussion describing what you tried and what you expected.
