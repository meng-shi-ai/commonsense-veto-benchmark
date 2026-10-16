"""Original synthetic development cases. Regenerates public inputs and private labels."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES, GOLD = [], []

def event(eid, date, speaker, text):
    return {"id": eid, "date": date, "speaker": speaker, "text": text}

def pair(pair_id, family, split, query, values, first, left, right, rationale):
    """Each pair differs in precisely the second event's text OR speaker."""
    for variant, (second, answer, evidence) in enumerate((left, right)):
        cid = f"C{len(CASES)+1:03d}"
        CASES.append({"id": cid, "as_of": "2026-09-05", "events": [first, second],
                      "query": query, "allowed_values": values})
        GOLD.append({"id": cid, "pair_id": pair_id, "family": family, "split": split,
                     "variant": variant, "value": answer,
                     "decision": "clarify" if answer is None else "answer",
                     "evidence_sets": [evidence], "annotation_note": rationale[variant]})

pair('P01','explicit_update','dev',
     'What is the user\'s current home city in the available record?', ['Riverton','Lakeview'],
     event('E1','2026-03-01','user','My home is in Riverton.'),
     (event('E2','2026-08-20','user','I moved to Lakeview. That is my home now.'),'Lakeview',['E2']),
     (event('E2','2026-08-20','user','I visited Lakeview. Riverton is still my home.'),'Riverton',['E2']),
     ['An explicit move replaces the old home.','A visit is not a move; the old home is reaffirmed.'])
pair('P02','explicit_update','pilot',
     'Which lunch venue does the user currently prefer in the available record?', ['Cedar','Maple'],
     event('E1','2026-02-01','user','Cedar is my preferred lunch venue.'),
     (event('E2','2026-08-30','user','My preferred lunch venue is now Maple instead of Cedar.'),'Maple',['E2']),
     (event('E2','2026-08-30','user','I tried Maple, but Cedar remains my preferred lunch venue.'),'Cedar',['E2']),
     ['A current preference explicitly supersedes the prior one.','Trying a venue does not replace an explicitly retained preference.'])
pair('P03','durable_vs_temporary','dev',
     'What reply length should be used for this user today, based only on the stated preference?', ['brief','detailed'],
     event('E1','2026-02-28','user','I am starting a planning project.'),
     (event('E2','2026-03-01','user','As my standing preference, use brief replies unless I tell you otherwise.'),'brief',['E2']),
     (event('E2','2026-03-01','user','Only for today, March 1, use brief replies. I am not setting a standing preference.'),None,['E2']),
     ['An explicitly standing preference is not invalidated by elapsed time alone.','The one-day instruction expired; no current length preference is specified.'])
pair('P04','durable_vs_temporary','pilot',
     'For a new September project, which topic is established as the user\'s continuing research focus?', ['robotics','cognitive_autonomy'],
     event('E1','2026-03-01','user','The workshop project ends on March 31.'),
     (event('E2','2026-03-02','user','My continuing research focus is cognitive autonomy, beyond this workshop.'),'cognitive_autonomy',['E2']),
     (event('E2','2026-03-02','user','My focus is cognitive autonomy only for this workshop; I have not selected a continuing focus.'),None,['E1','E2']),
     ['The enduring scope is explicit.','A workshop-only focus cannot establish a later continuing focus.'])
pair('P05','suggestion_vs_commitment','dev',
     'Is the user currently enrolled in SOC 205 according to the record?', ['enrolled','not_enrolled'],
     event('E1','2026-08-20','assistant','You could take SOC 205 to meet the elective requirement.'),
     (event('E2','2026-09-01','user','I officially enrolled in SOC 205.'),'enrolled',['E2']),
     (event('E2','2026-09-01','user','SOC 205 is one option I am considering.'),None,['E1','E2']),
     ['User confirmation establishes enrollment.','A recommendation and consideration do not establish registration or non-registration.'])
pair('P06','suggestion_vs_commitment','pilot',
     'Does the record establish that the user has purchased the Orbit keyboard?', ['purchased','not_purchased'],
     event('E1','2026-08-25','assistant','The Orbit keyboard is an option you could buy.'),
     (event('E2','2026-09-02','user','I bought the Orbit keyboard yesterday.'),'purchased',['E2']),
     (event('E2','2026-09-02','user','I like the idea of buying the Orbit keyboard.'),None,['E1','E2']),
     ['Completed purchase is reported.','Interest does not settle whether a purchase has occurred.'])
pair('P07','correction_and_provenance','dev',
     'Which feedback style does the user explicitly prefer?', ['more_confrontational','gentle'],
     event('E1','2026-08-01','assistant','I take your complaint to mean that you want more confrontational feedback.'),
     (event('E2','2026-08-02','user','No, that interpretation is wrong. I prefer gentle feedback.'),'gentle',['E2']),
     (event('E2','2026-08-02','user','Yes, that interpretation is correct. I prefer more confrontational feedback.'),'more_confrontational',['E2']),
     ['An explicit correction defeats an assistant inference.','The user expressly confirms the interpretation.'])
# Three-event pair: a recent memory summary is not a fresh user update.
base_count = len(CASES)
pair('P08','correction_and_provenance','pilot',
     'What is the user\'s current academic track?', ['cybersecurity','ai'],
     event('E1','2026-07-01','user','I am in the cybersecurity track.'),
     (event('E3','2026-09-04','memory_summary','Current track: cybersecurity.'),'ai',['E2']),
     (event('E3','2026-09-04','user','Current track: cybersecurity.'),'cybersecurity',['E3']),
     ['A newly generated summary does not supersede the explicit user update it contradicts.',
      'A fresh direct user statement does establish a subsequent change.'])
for case in CASES[base_count:]:
    case['events'].insert(1,event('E2','2026-08-20','user','I switched from cybersecurity to the AI track.'))
pair('P09','subject_attribution','dev',
     'Where is the user planning to travel in October?', ['Kyoto','Osaka'],
     event('E1','2026-08-01','user','My roommate and I have separate travel plans.'),
     (event('E2','2026-09-01','user','I am planning to visit Kyoto in October.'),'Kyoto',['E2']),
     (event('E2','2026-09-01','user','My roommate is planning to visit Kyoto in October.'),None,['E1','E2']),
     ['The statement concerns the user.','A roommate\'s itinerary does not establish the user\'s destination.'])
pair('P10','subject_attribution','pilot',
     'Which language is the user currently studying?', ['Japanese','Korean'],
     event('E1','2026-08-01','user','My coworker and I take separate evening classes.'),
     (event('E2','2026-09-01','user','I am currently studying Japanese.'),'Japanese',['E2']),
     (event('E2','2026-09-01','user','My coworker said, "I am currently studying Japanese."'),None,['E1','E2']),
     ['A first-person self-report supplies the fact.','First person within a quotation refers to the coworker, not the user.'])
pair('P11','authorization_scope','dev',
     'Under the user\'s stated instruction, is the assistant authorized to send this draft now? Only classify; do not send anything.', ['authorized','not_authorized'],
     event('E1','2026-09-04','assistant','I have prepared the exact email draft we discussed.'),
     (event('E2','2026-09-05','user','Send that exact email draft now.'),'authorized',['E2']),
     (event('E2','2026-09-05','user','Show me that exact email draft now. Do not send it.'),'not_authorized',['E2']),
     ['Sending this specific draft is expressly authorized.','Showing the draft is authorized; sending is expressly excluded.'])
pair('P12','authorization_scope','pilot',
     'As of September 5, is sending the next weekly project email still authorized? Only classify; do not send anything.', ['authorized','not_authorized'],
     event('E1','2026-08-01','user','You may send my weekly project email each Friday until I cancel this permission.'),
     (event('E2','2026-09-04','user','Keep my existing permission to send the weekly project email.'),'authorized',['E1','E2']),
     (event('E2','2026-09-04','user','Cancel my existing permission to send the weekly project email.'),'not_authorized',['E2']),
     ['The prior scoped permission remains in force and is reaffirmed.','An explicit revocation ends the prior permission.'])

if __name__ == '__main__':
    for name, rows in [('cases.jsonl',CASES),('gold.jsonl',GOLD)]:
        (ROOT/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
    print(f'Wrote {len(CASES)} cases and {len(GOLD)} labels.')
