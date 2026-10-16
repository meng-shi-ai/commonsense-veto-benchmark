# Limitations and interpretation

1. **Synthetic and small.** Cases are inspired by reported experiences but are not verified reproductions of the original private interactions. Explicit rules, complete current records and constrained facts can make tasks easier than natural use.
2. **AI-assisted annotation.** Gold labels and semantic judgments have not received independent human or blinded review. Evidence-set ambiguity in v0.1/v0.2 and two added-detail judgments in v0.4 remain unresolved.
3. **No intervention estimate.** There is no randomized or controlled comparison of a veto mechanism against a baseline. Successful authorization behavior in v0.5 does not demonstrate a mechanism's efficacy.
4. **Memory claims are limited.** Short supplied records, full-history replay and simulated time jumps do not establish durable storage, cross-task retrieval, automatic compression behavior or performance after months of natural interaction.
5. **Harness and configuration.** A Codex environment adds instructions. Requested model identifiers and local configuration checks do not independently verify a server snapshot or internal compute budget. Early versions did not fix reasoning effort. No other provider was evaluated here.
6. **Non-independent observations.** Paired cases share templates; v0.3 contains duplicate missing-date presentations; v0.4 branches share prefixes. Turns are not interchangeable with independent cases. Versions use different scoring units and should not be pooled into a single success rate.
7. **Public exposure.** The cases and labels are openly inspectable. A dev/pilot split does not make the pilot hidden or uncontaminated. New held-out templates and independent labels would be needed to assess generalization.
8. **Results do not settle anecdotes.** A failure not reproduced under simplified conditions neither refutes a user's reported experience nor establishes that the original problem is fixed.
9. **Sanitized derivative.** Machine paths and identifiers were removed for publication. Historical scripts retain symbolic placeholders; original archive hashes will not match every sanitized file. Current public-file integrity is checked separately.

Useful next work would independently review the labels and disputed cases, preregister new unseen scenarios, vary retrieval or summary inputs while keeping tasks fixed, and evaluate an explicitly defined intervention against a matched baseline. Those experiments have not been run in this repository.
