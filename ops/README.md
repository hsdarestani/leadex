# Operations

Production deployments run automatically after the CI workflow succeeds on the main branch.

The deployment target is managed by the `leadex.service` systemd unit and validated through the `/health` endpoint.
