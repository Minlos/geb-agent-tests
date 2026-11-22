"""Budgeted OpenRouter transport; independent of scenario definitions and grading."""
import copy
from decimal import Decimal
import json
import urllib.error
import urllib.request

from run_tests import APIError

PROVIDER = {'sort': 'price', 'require_parameters': True,
            'max_price': {'prompt': 0.5, 'completion': 2, 'request': 0}}


class Budget:
    def __init__(self, cap, initial_spend='0'):
        self.cap, self.spent = Decimal(str(cap)), Decimal(str(initial_spend))
        if not self.cap.is_finite() or not self.spent.is_finite() or not 0 <= self.spent <= self.cap:
            raise ValueError('Invalid spending cap or initial spend')

    def reserve(self, context, max_tokens):
        if type(context) is not int or type(max_tokens) is not int or min(context, max_tokens) < 1:
            raise ValueError('Context and output limits must be positive integers')
        # Full advertised model context at provider-enforced price ceilings.
        amount = Decimal(context) * Decimal('0.5') / 1000000 + Decimal(max_tokens) * 2 / 1000000
        if self.spent + amount > self.cap:
            raise APIError('Aggregate budget guard stopped before request')
        self.spent += amount
        return amount

    def settle(self, reserved, cost):
        if cost is None:
            return  # Unknown billing conservatively keeps the whole reservation.
        cost = Decimal(str(cost))
        if not cost.is_finite() or not 0 <= cost <= reserved:
            raise APIError('Reported usage cost outside reserved bound; stop for review')
        self.spent += cost - reserved


class Client:
    def __init__(self, model, key, context, budget, max_tokens=1024, timeout=300):
        self.model, self.key, self.context, self.budget = model, key, context, budget
        self.max_tokens, self.timeout = max_tokens, timeout
        self.responses = []

    def __call__(self, messages, tools):
        held = self.budget.reserve(self.context, self.max_tokens)
        payload = {'model': self.model, 'messages': messages, 'tools': tools,
                   'tool_choice': 'auto', 'temperature': 0, 'max_tokens': self.max_tokens,
                   'reasoning': {'enabled': False}, 'provider': PROVIDER}
        req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',
             json.dumps(payload, ensure_ascii=False).encode(),
             headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.key})
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        try:
            with urllib.request.build_opener(NoRedirect).open(req, timeout=self.timeout) as response:
                data = json.load(response)
        except urllib.error.HTTPError as exc:
            status = exc.code; exc.close()
            raise APIError('HTTP ' + str(status) + '; no automatic retry; reservation retained') from None
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            raise APIError('Transport/JSON error; no automatic retry; reservation retained') from None
        try:
            usage = data.get('usage') or {}
            self.budget.settle(held, usage.get('cost'))
            choice = data['choices'][0]
            message = choice['message']
            self.responses.append({'id': data.get('id'), 'provider': data.get('provider'),
                'model': data.get('model'), 'finish_reason': choice.get('finish_reason'),
                'message': copy.deepcopy(message), 'usage': copy.deepcopy(usage),
                'reserved_max_usd': str(held)})
            if choice.get('finish_reason') == 'length':
                raise APIError('Model response hit output-token limit')
            if not isinstance(message, dict):
                raise APIError('Invalid assistant message')
            return {k: message[k] for k in ('role', 'content', 'tool_calls') if k in message}
        except (KeyError, IndexError, TypeError, ValueError):
            raise APIError('Invalid API response schema') from None
