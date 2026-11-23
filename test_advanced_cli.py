"""CLI integration with a scripted loopback API; never a model or paid request."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler,HTTPServer
import advanced_suite as suite
import run_advanced
from run_unified import ReferenceClient

ROOT=Path(__file__).resolve().parent

class AdvancedCLIChecks(unittest.TestCase):
    def test_offline_check_and_frozen_export(self):
        before=suite.DATA.read_bytes()
        subprocess.run([sys.executable,'scripts/build_advanced_cases.py'],cwd=ROOT,check=True,capture_output=True)
        self.assertEqual(before,suite.DATA.read_bytes())
        result=run_advanced.self_test(suite.CASES)
        self.assertTrue(result['passed']);self.assertEqual(result['boundary_probes_detected'],24)
        self.assertEqual(result['blanket_refusal_controls_rejected'],8)

    def test_incomplete_and_duplicate_coverage(self):
        case=suite.CASES[0];row=suite.run_reference(case)
        summary=suite.summarize([row],[case['id'],'missing'])
        self.assertIsNone(summary['full_suite_points'])
        with self.assertRaises(ValueError):suite.summarize([row,row],[case['id']])

    def test_two_profiles_through_actual_cli_and_http(self):
        case=next(c for c in suite.CASES if c['id']=='ADV-08D')
        clients={};requests=[]
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_POST(self):
                payload=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                requests.append(payload)
                policy=payload['messages'][0]['content']
                turn=sum(m['role']=='user' for m in payload['messages'])-1
                if policy not in clients:clients[policy]=[ReferenceClient(case),None]
                client,previous=clients[policy]
                if previous!=turn:client.begin_turn(turn);clients[policy][1]=turn
                reply=client(payload['messages'],payload['tools'])
                data=json.dumps({'choices':[{'message':reply,'finish_reason':'tool_calls' if reply.get('tool_calls') else 'stop'}],'usage':{}}).encode()
                self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(data)
        server=HTTPServer(('127.0.0.1',0),Handler)
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        try:
            with tempfile.TemporaryDirectory() as temp:
                output=Path(temp)/'run'
                result=subprocess.run([sys.executable,'run_advanced.py','--base-url',f'http://127.0.0.1:{server.server_port}/v1','--model','scripted-fixture','--only',case['id'],'--output',str(output),'--no-thinking'],cwd=ROOT,env={**os.environ,'MODEL_API_KEY':'FAKE_CLI_CREDENTIAL'},capture_output=True,text=True,timeout=30)
                self.assertEqual(result.returncode,0,result.stderr+result.stdout)
                data=json.loads((output/'results.json').read_text())
                self.assertEqual([r['score'] for r in data['results']],[2,2])
                self.assertEqual(set(data['summary']),{'original','v3'})
                for stats in data['summary'].values():self.assertEqual(stats['full_suite_points'],2)
                self.assertNotIn('FAKE_CLI_CREDENTIAL',(output/'results.json').read_text())
                self.assertEqual(len(clients),2)
                for request in requests:
                    self.assertEqual(request['reasoning_effort'],'none')
                    self.assertEqual(request['temperature'],0)
                    for message in request['messages']:
                        if message['role'] in ['system','user']:
                            self.assertNotIn('reference_turns',str(message));self.assertNotIn('"rights"',str(message))
        finally:server.shutdown();server.server_close();worker.join()

if __name__=='__main__':unittest.main()
