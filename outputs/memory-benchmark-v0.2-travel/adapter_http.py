"""Optional adapter for a chat-completions-compatible HTTP service. Not used in validation.

Required environment: BENCHMARK_ENDPOINT (full URL), BENCHMARK_MODEL.
Optional: BENCHMARK_API_KEY, BENCHMARK_EXTRA_BODY (JSON object, e.g. sampling settings).
Running this adapter can incur provider charges. Do not place credentials in files.
"""
import json
import os
import sys
import urllib.request
from urllib.parse import urlparse

def main():
    prompt=json.load(sys.stdin)
    endpoint=os.environ['BENCHMARK_ENDPOINT']
    parsed=urlparse(endpoint)
    if parsed.scheme not in ('https','http') or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Use an HTTP(S) URL without embedded credentials')
    if parsed.scheme=='http' and parsed.hostname not in ('localhost','127.0.0.1','::1'):
        raise ValueError('Unencrypted HTTP is supported only for local servers')
    body=json.loads(os.environ.get('BENCHMARK_EXTRA_BODY','{}'))
    if not isinstance(body,dict):raise ValueError('Extra body must be an object')
    body.update(model=os.environ['BENCHMARK_MODEL'],messages=prompt['messages'],stream=False)
    headers={'Content-Type':'application/json'}
    key=os.environ.get('BENCHMARK_API_KEY')
    if key:headers['Authorization']='Bearer '+key
    # No automatic retries or redirect-following: do not duplicate requests or forward keys.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):return None
    req=urllib.request.Request(endpoint,data=json.dumps(body).encode(),headers=headers,method='POST')
    with urllib.request.build_opener(NoRedirect).open(req,timeout=110) as response:
        result=json.load(response)
    content=result['choices'][0]['message']['content']
    prediction=json.loads(content)
    print(json.dumps(prediction,ensure_ascii=False))

if __name__=='__main__':
    try:main()
    except Exception as exc:
        # A provider error may contain private request details; suppress its body.
        print('Adapter failed: '+type(exc).__name__,file=sys.stderr)
        sys.exit(1)
