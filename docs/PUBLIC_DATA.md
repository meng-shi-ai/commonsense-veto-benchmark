# Public derivative and data handling

The source is the previously verified v0.1–v0.5 archive (SHA256 `300a45542c177bdc987e581964c8776fcce99a3411a18061b4baf3c1d03384d2`). It was read without modification. No evaluations were rerun or selectively dropped during publication.

## Processing

- Preserve all 436 archived source files, including case data, labels, code, model answers, review records, simulator calls/states and failed startup attempts.
- Replace private home/workspace paths and machine-specific executable/temporary paths with symbolic placeholders.
- Replace 123 session or trace UUIDs consistently with public pseudonyms. Withhold the reverse mapping. This retains equality and branch relationships without publishing actual resumable identifiers.
- Scan for email addresses, common credential formats and private-path remnants. Authentication stores, API keys and the source archive are not published.
- Remove personalized introductory wording and one application-specific editorial section from a historical report. Retain its experimental findings and limitations. Synthetic case dialogue and relevant generated experimental dialogue remain research data; no surrounding personal chat transcript is added.
- Replace four root-level private-archive packaging files with this release's documentation and integrity manifest. The per-file [processing record](sanitization-record.json) lists changed hashes and categories without including private values.

These edits mean the public archive is not byte-identical to the private source. Old experimental hashes remain provenance; use `PUBLIC_MANIFEST.json` for public bytes. Metadata timestamps, token usage, item identifiers and experiment case IDs are retained where they are needed to understand runs. Generic per-turn item IDs are not account/session credentials.

The supplied roster and travel facts are synthetic experiment settings, not verified enrollment records or real-world travel advice. No real registration action was performed. No license has been selected.
