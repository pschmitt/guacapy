# Agent instructions

`guacapy` is a Python client library for managing Apache Guacamole resources. Follow the existing manager and client patterns in `guacapy/`.

## Working and validation

- Use the Poetry project configuration and documented development commands for dependency management and checks.
- Keep API behavior and tests aligned when changing client methods or managers; run the focused tests and configured checks when available.
- Before changing GitHub Actions, check whether [pschmitt/ci-workflows](https://github.com/pschmitt/ci-workflows) provides a reusable workflow or action. Preserve current behavior and check coverage, and use `@main` for shared workflow or action references.
