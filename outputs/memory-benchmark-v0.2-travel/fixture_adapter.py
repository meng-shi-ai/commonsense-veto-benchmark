"""Fixed fixture for runner plumbing. THIS IS NOT A MODEL."""
import json
import sys
json.load(sys.stdin)
print(json.dumps({'decision':'clarify','value':None,'evidence_ids':[]}))
