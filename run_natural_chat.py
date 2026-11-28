#!/usr/bin/env python3
"""One adaptive Russian user turn per selected model, with persistent shared budget."""
import argparse
import datetime as dt
from decimal import Decimal
import hashlib
import json
import os
import subprocess
from pathlib import Path
import urllib.error
import urllib.request
ROOT=Path(__file__).resolve().parent
MODELS={'gemma':{'id':'google/gemma-4-31b-it','provider':'coreweave/fp4','prompt':'0.1','completion':'0.34'},
        'qwen':{'id':'qwen/qwen3.8-27b','provider':'darkbloom/fp4','prompt':'0.035','completion':'1.5'},
        'deepseek':{'id':'deepseek/deepseek-v4-pro-0813','provider':'relace/fp4','prompt':'0.0999','completion':'5','context':1048576},
        'glm':{'id':'z-ai/glm-5.3','provider':'wafer/us','prompt':'0.0699','completion':'1.4','context':1048576,'reasoning':{'effort':'low'},'max_tokens':4000}}

def payload(model,messages):
    spec=MODELS[model]
    return {'model':spec['id'],'messages':messages,'temperature':0.5,'max_tokens':spec.get('max_tokens',1000),
            'reasoning':spec.get('reasoning',{'enabled':False}),'provider':{'only':[spec['provider']],'allow_fallbacks':False,
            'require_parameters':True,'max_price':{'prompt':float(spec['prompt']),'completion':float(spec['completion']),'request':0}}}

def reserve(state,model):
    spec=MODELS[model]
    amount=(Decimal(spec.get('context',262144))*Decimal(spec['prompt'])+Decimal(spec.get('max_tokens',1000))*Decimal(spec['completion']))/1000000
    spent=Decimal(state['spent_or_reserved_usd'])
    if spent+amount>Decimal(state['cap_usd']):raise ValueError('Shared cap exhausted before request')
    state['spent_or_reserved_usd']=str(spent+amount);return amount

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--turns',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--retry',choices=list(MODELS));p.add_argument('--transport',choices=['urllib','curl'],default='urllib');p.add_argument('--persona-file',type=Path);p.add_argument('--shared-budget',type=Path);p.add_argument('--continue-truncated',action='store_true');p.add_argument('--assistant-prompt',type=Path);args=p.parse_args()
    key=os.environ.get('OPENROUTER_API_KEY')
    if not key:raise SystemExit('Configure key in environment')
    turns=json.loads(args.turns.read_text())
    if not turns or set(turns)-set(MODELS) or any(not isinstance(v,str) or not v.strip() for v in turns.values()):raise SystemExit('Invalid user turns')
    prompt=(args.assistant_prompt or ROOT/'prompts/natural-chat-assistant-v1.txt').read_text();persona=json.loads((args.persona_file or ROOT/'personas/moscow-business-owner-v1.json').read_text())
    args.output.mkdir(parents=True,exist_ok=True);path=args.output/'state.json'
    state=json.loads(path.read_text()) if path.exists() else {'started_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'cap_usd':json.loads(args.shared_budget.read_text())['cap_usd'] if args.shared_budget else '0.30','spent_or_reserved_usd':'0','persona':persona,'assistant_prompt':prompt,'models':MODELS,
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'conversations':{m:{'messages':[{'role':'system','content':prompt}],'responses':[],'status':'ready'} for m in MODELS}}
    assert state['assistant_prompt']==prompt and state['persona']==persona,'Do not change prompts mid-dialogue'
    ledger=json.loads(args.shared_budget.read_text()) if args.shared_budget else None
    if ledger is not None:
        assert ledger['cap_usd']==state['cap_usd'] and Decimal(ledger['spent_or_reserved_usd'])>=0
        state['spent_or_reserved_usd']=ledger['spent_or_reserved_usd']
        state['shared_budget_source']=str(args.shared_budget)
    def save():
        if ledger is not None:
            ledger['spent_or_reserved_usd']=state['spent_or_reserved_usd']
            temp=args.shared_budget.with_suffix('.tmp');temp.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n');temp.replace(args.shared_budget)
        path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
    for model,user in turns.items():
        chat=state['conversations'][model]
        if args.retry==model:
            if chat['status']!='error' or chat['messages'][-1]!={'role':'user','content':user}:raise SystemExit('Retry requires exact interrupted user turn')
            chat.setdefault('error_history',[]).append({'error':chat.get('error'),'diagnostic':chat.get('transport_diagnostic'),'turn':sum(m['role']=='user' for m in chat['messages']),'note':'Manual identical retry; previous reservation retained'})
        elif chat['status']!='ready':
            if args.continue_truncated and chat['status']=='response_limit_or_unexpected_finish' and chat['responses'][-1]['finish_reason']=='length':
                chat.setdefault('continuations_after_limit',[]).append({'after_response':len(chat['responses']),'note':'User responds to actual truncated output; no regeneration'})
            else:raise SystemExit('Prior request not completed; no automatic retry')
        held=reserve(state,model)
        if args.retry!=model:chat['messages'].append({'role':'user','content':user})
        chat['status']='pending';save()
        body=payload(model,chat['messages'])
        request=urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',json.dumps(body,ensure_ascii=False).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+key})
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,req,fp,code,msg,headers,newurl):return None
        try:
            if args.transport=='curl':
                for connection_attempt in range(5):
                    proc=subprocess.run(['curl','--ipv4','--http1.1','--silent','--show-error','--connect-timeout','15','--max-time','180','--request','POST','--header','@-','--data-binary',json.dumps(body,ensure_ascii=False),'--write-out','\n%{http_code}','https://openrouter.ai/api/v1/chat/completions'],input=('Content-Type: application/json\nAuthorization: Bearer '+key+'\n').encode(),capture_output=True)
                    if not proc.returncode:break
                    diagnostic=proc.stderr.decode(errors='replace').replace(key,'[REDACTED]')[:500]
                    before_http=proc.returncode in (6,7) or proc.returncode==35 and 'SSL_connect' in diagnostic or proc.returncode==28 and 'SSL connection timeout' in diagnostic
                    chat.setdefault('connection_failures',[]).append({'exit_code':proc.returncode,'before_http':before_http,'diagnostic':diagnostic})
                    if not before_http or connection_attempt==4:
                        chat['curl_exit_code']=proc.returncode;chat['transport_diagnostic']=diagnostic
                        if before_http:
                            state['spent_or_reserved_usd']=str(Decimal(state['spent_or_reserved_usd'])-held)
                            chat.setdefault('released_reservations',[]).append({'amount':str(held),'reason':'Connection failed before HTTP request'})
                        raise OSError('curl transport code '+str(proc.returncode))
                content,status=proc.stdout.rsplit(b'\n',1);chat['http_status']=int(status)
                if status!=b'200':
                    chat.setdefault('http_errors',[]).append({'status':int(status),'body':content.decode(errors='replace').replace(key,'[REDACTED]')[:4000]})
                    raise ValueError('Unexpected HTTP status')
                data=json.loads(content)
            else:
                with urllib.request.build_opener(NoRedirect).open(request,timeout=300) as response:data=json.load(response)
            usage=data.get('usage') or {};cost=usage.get('cost')
            if cost is not None:
                actual=Decimal(str(cost))
                if not actual.is_finite() or not 0<=actual<=held:raise ValueError('Reported cost outside reserve')
                state['spent_or_reserved_usd']=str(Decimal(state['spent_or_reserved_usd'])-held+actual)
            choice=data['choices'][0];message=choice['message']
            chat['responses'].append({'id':data.get('id'),'model':data.get('model'),'provider':data.get('provider'),
                'usage':usage,'finish_reason':choice.get('finish_reason'),'message':message,'reserved_max_usd':str(held),'transport':args.transport,'driver_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'request_settings':{k:v for k,v in body.items() if k!='messages'}})
            if not isinstance(message.get('content'),str) or message.get('tool_calls'):raise ValueError('Expected ordinary text chat')
            chat['messages'].append({'role':'assistant','content':message['content']})
            chat['status']='ready' if choice.get('finish_reason')=='stop' else 'response_limit_or_unexpected_finish'
            save();print('\n### '+model+'\n'+message['content'],flush=True)
        except urllib.error.HTTPError as exc:
            chat['status']='error';chat['error']='HTTP '+str(exc.code)+'; reservation retained';exc.close();save();raise SystemExit(chat['error']) from None
        except (urllib.error.URLError,TimeoutError,OSError,ValueError,KeyError,IndexError,TypeError) as exc:
            chat['status']='error';chat['error']='Transport/schema/cost error; no automatic retry';chat['error_class']=type(exc).__name__;save();raise SystemExit(chat['error']) from None
    print('\nSpent/reserved USD: '+state['spent_or_reserved_usd'],flush=True)
if __name__=='__main__':main()
