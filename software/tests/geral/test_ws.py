import json

s = '{ "message": "hello world!!!" }'

obj : dict = json.loads(s)

if 'message' in obj:
    print(obj['message'])