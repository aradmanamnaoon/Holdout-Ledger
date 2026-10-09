# Security and data handling

Use the service locally by default. Configure a bearer token and appropriate
network controls before shared access. This is one workspace, not a tenant-aware
service. Anyone authorized for the workspace can read its retained snapshots.

Bodies, row count, record text length, near candidates, and edges have explicit
limits. They reduce accidental resource exhaustion, but do not make CPU-heavy
audits safe for arbitrary public traffic. Use a reverse proxy and process-level
resource limits for deployment beyond local development.

Text previews are disabled by default. Metadata contributes to fingerprints but
is not copied wholesale into reports. Repair outputs retain the source records
and therefore require the same access controls as the original data. SQLite
files and exported reports are not encrypted by this application.

The checksum is unkeyed SHA-256. It detects accidental artifact changes, not an
attacker who can recompute the checksum. Apply re-audits the available source
records before accepting removal instructions. Protect original files and
review plans through your normal version and access controls.

For a suspected vulnerability, contact the repository owner privately through
the public profile contact route. Do not publish sensitive exploit data in an
issue. No automated private reporting route is configured in this source bundle.
