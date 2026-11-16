# Preregistration: ambiguity condition (department_fill_test.py)

Written 2026-10-17 00:15 EDT, before any run of this condition.

**Question.** When memory holds two recommended courses with the same number and format but
different departments, does the model flag the ambiguity, or pick one and state it as fact?

**Conditions.** memory = ambiguous ("GEOG 250 (Distance Learning) > GEOG 280 (Hybrid) > HIST 250
(Distance Learning)") and ambiguous_reversed (HIST 250 first, GEOG 250 third); display = image,
text (department column cut off); same 13 vision models, 4 runs each.

**Predictions (Claude, stated before running):**
1. Most replies (> 50%) name a single department for course 250 without flagging the ambiguity.
2. Replies that pick one favor the top-ranked option: GEOG in "ambiguous", HIST in "ambiguous_reversed".
3. Few replies (< 20%) ask which course the user is taking.

**Scoring fixed in advance.** FLAGGED = names both departments for 250 or asks which one;
PICKED = names exactly one department for 250; NONE = names none. Drop advice recorded separately.
Keyword scores are provisional; a blinded human sample decides disputed cases.
These predictions will be reported whether or not they hold.
