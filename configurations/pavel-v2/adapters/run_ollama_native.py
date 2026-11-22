"""Run the frozen text suite with Ollama's local JSON chat transport."""
import json
import os
import time
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request

import run_portable
from voice_benchmark import local_http_opener

def native_messages(messages):
    names = {}
    history = []
    for message in messages:
        role = message['role']
        item = {'role': role, 'content': message.get('content') or ''}
        if role == 'tool':
            item['tool_name'] = names[message['tool_call_id']]
        calls = []
        for i, call in enumerate(message.get('tool_calls', [])):
            function = call['function']
            names[call['id']] = function['name']
            calls.append({'type': 'function', 'function': {
                'index': i, 'name': function['name'],
                'arguments': json.loads(function['arguments']),
            }})
        if calls:
            item['tool_calls'] = calls
        history.append(item)
    return history

def completion(passport, messages, seed):
    parts = urlsplit(passport['endpoint'])
    endpoint = urlunsplit(parts._replace(path='/api/chat'))
    limits = run_portable.engine.LIMITS
    payload = {
        'model': passport['model'], 'messages': native_messages(messages),
        'tools': run_portable.engine.TOOLS, 'stream': False,
        'options': {'temperature': limits['temperature'],
                    'num_predict': limits['max_tokens'], 'seed': seed},
    }
    if os.environ.get('GEB_MATCHED_PROFILE') == '1':
        payload['options'].update(num_ctx=4096, num_predict=1024, top_k=40, top_p=0.95, min_p=0.0)
    if os.environ.get('GEB_OLLAMA_NO_THINK') == '1':
        payload['think'] = False
    request = Request(endpoint, json.dumps(payload).encode(),
                      {'Content-Type': 'application/json'})
    start = time.perf_counter()
    with local_http_opener().open(request, timeout=limits['request_timeout_seconds']) as response:
        data = json.load(response)
    if not data.get('done') or not data.get('message'):
        raise ValueError('Ollama did not return a completed chat message')
    source = data['message']
    thinking = source.get('thinking') or ''
    message = {'role': 'assistant', 'content': source.get('content') or None}
    calls = []
    for i, call in enumerate(source.get('tool_calls', [])):
        function = call['function']
        calls.append({'id': f'call-{len(messages)}-{i}', 'type': 'function', 'function': {
            'name': function['name'],
            'arguments': json.dumps(function['arguments'], ensure_ascii=False),
        }})
    if calls:
        message['tool_calls'] = calls
    reason = data.get('done_reason')
    if not message['content'] and not calls and not thinking and reason != 'length':
        raise ValueError('Ollama returned an empty chat message')
    return message, {
        'seconds': time.perf_counter() - start, 'first_event_seconds': None,
        'usage': {'prompt_tokens': data.get('prompt_eval_count'),
                  'completion_tokens': data.get('eval_count')},
        'finish_reason': reason, 'reasoning_content': thinking,
        'transport': 'Ollama native /api/chat JSON, stream=false',
        'request_options': payload['options'],
        'thinking_request': payload.get('think'),
    }

if __name__ == '__main__':
    run_portable.engine.completion = completion
    run_portable.main()
