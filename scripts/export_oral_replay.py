#!/usr/bin/env python3
"""Export the short-dialogue Alexander replay and preserve earlier draft personas."""
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def words(t):return len(re.findall(r'[^\W_]+(?:[-’\'][^\W_]+)*',t,re.UNICODE))
def main():
    source=ROOT/'runs/natural-chat-alexander-oral-v2-20261128/state.json'
    if not source.exists():source=ROOT/'results/natural-chat-alexander-oral-v2-20261128/raw.json'
    s=read(source)
    old=read(ROOT/'results/natural-chat-20261128/raw.json')
    out=ROOT/'results/natural-chat-alexander-oral-v2-20261128';out.mkdir(exist_ok=True)
    assert s['assistant_prompt']==(ROOT/'prompts/natural-voice-assistant-v2.txt').read_text()
    assert hashlib.sha256((ROOT/'configurations/natural-chat-oral-v2/run_natural_chat.py').read_bytes()).hexdigest()==s['source_sha256']
    summary={}
    for model,chat in s['conversations'].items():
        assert chat['status']=='ready' and len(chat['responses'])==6
        assert [m['role'] for m in chat['messages']]==['system']+['user','assistant']*6
        assert chat['messages'][1]==old['conversations'][model]['messages'][1]
        answers=[m['content'] for m in chat['messages'] if m['role']=='assistant']
        assert answers==[r['message']['content'] for r in chat['responses']]
        before=[m['content'] for m in old['conversations'][model]['messages'] if m['role']=='assistant']
        summary[model]={'answers':6,'first_words_before':words(before[0]),'first_words_now':words(answers[0]),
                        'max_words_before':max(map(words,before)),'max_words_now':max(map(words,answers))}
        page=['# Александр — '+s['models'][model]['id']+': повтор с короткими репликами','', '[Промпт, условия и наблюдения](oral-replay-ru.md)','']
        n=0
        for msg in chat['messages']:
            if msg['role']=='system':continue
            if msg['role']=='user':n+=1
            page+=['## '+str(n)+'. '+('Александр' if msg['role']=='user' else 'Модель'),'',msg['content'],'']
        (out/(model+'-dialogue.md')).write_text('\n'.join(line.rstrip() for line in '\n'.join(page).splitlines()).rstrip()+'\n')
    (out/'raw.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
    (out/'persona.json').write_text(json.dumps(s['persona'],ensure_ascii=False,indent=2)+'\n')
    (out/'assistant-prompt.txt').write_text(s['assistant_prompt'])
    ledger_path=ROOT/'runs/natural-chat-additional-20261128/budget.json'
    ledger=read(ledger_path) if ledger_path.exists() else read(out/'summary.json')['series_budget']
    cost=sum(Decimal(str(r['usage'].get('cost') or 0)) for c in s['conversations'].values() for r in c['responses'])
    assert Decimal(ledger['spent_or_reserved_usd'])<=Decimal('0.30')
    lines=['# Александр: повтор короткого разговора с Gemma и Qwen','',
           'Повторяем разговор вымышленного владельца двух московских кофеен: проверка спроса на подарочные наборы, затем поездка с женой. Начальная реплика совпадает с первым опытом. Для каждого помощника сохранены шесть обменов.','',
           '## Что задано до начала','',
           'Общий системный промпт задаёт устный формат: одна мысль за раз, обычно одна–три короткие фразы, без статей и меню вариантов. Человек не должен постоянно настраивать стиль ответов в ходе разговора. Естественная просьба что-то сформулировать допустима, но не является основным способом общения.','',
           '```text',s['assistant_prompt'].strip(),'```','',
           '[Персона и инструкция автору пользовательских реплик](persona.json). Codex пишет за Александра после фактических ответов модели: добавляет обстоятельства, соглашается или возражает по существу. Это текстовая имитация устного обмена. Звук, перебивания, распознавание речи и задержки живого разговора здесь не проверяются.','',
           '## Полные разговоры','',
           '- [Gemma: все реплики](gemma-dialogue.md).','- [Qwen: все реплики](qwen-dialogue.md).','',
           'В этом повторе Александр ни разу не просит переписать ответ, изменить стиль или говорить короче. Например, он сообщает про две кофейни, выбирает размер пробной партии, уточняет желаемый темп отдыха и завершает разговор собственным решением.','',
           '## Длина ответов','',
           '| Показатель | Gemma: первый опыт | Gemma: повтор | Qwen: первый опыт | Qwen: повтор |','|---|---:|---:|---:|---:|',
           '| Слов в первом ответе на одинаковую реплику | '+str(summary['gemma']['first_words_before'])+' | '+str(summary['gemma']['first_words_now'])+' | '+str(summary['qwen']['first_words_before'])+' | '+str(summary['qwen']['first_words_now'])+' |',
           '| Самый длинный ответ из шести, слов | '+str(summary['gemma']['max_words_before'])+' | '+str(summary['gemma']['max_words_now'])+' | '+str(summary['qwen']['max_words_before'])+' | '+str(summary['qwen']['max_words_now'])+' |','',
           'Слова посчитаны автоматически по буквенным и цифровым группам. Это ориентир объёма, не баллы качества. Изменены и системный промпт, и способ написания последующих пользовательских реплик. Поэтому разницу всего разговора нельзя приписать только промпту; одна пара ответов также не устанавливает устойчивый эффект.','',
           '## Что видно по содержанию','',
           '- Первая Gemma предлагает предзаказ двумя фразами; первая Qwen — небольшую партию тремя. Разговор больше не начинается со страницы вариантов.',
           '- Gemma после отказа от предоплаты ещё предлагает бронирование; Александр объясняет, что это тоже лишняя организация, и выбирает готовые наборы на витрине. Это уточнение дела, а не редактирование речи помощника.',
           '- Qwen сначала предлагает 20–30 наборов без данных о спросе, затем принимает пять на каждую точку и неделю наблюдения. Короткая форма сама по себе не делает бизнес-вывод надёжным.',
           '- В семейной теме Gemma после уточнения предлагает провести время вместе в медленном темпе. Qwen даже после слов «хочу с ней весь день» снова пишет «пусть идёт, но не тащит тебя за собой». Александр возражает, что никто его не тащит. Краткость не устранила приписывание конфликта и возврат к неподходящему предложению.',
           '- В финале обе модели реагируют на решение сначала поговорить с женой, а потом планировать. Запросов на переписывание не было, успешные ответы не перегенерировались.','',
           '## Параметры и стоимость','',
           'Gemma `google/gemma-4-31b-it` через `coreweave/fp4`; Qwen `qwen/qwen3.8-27b` через `darkbloom/fp4`. Температура 0.5, максимум 1000 выходных токенов, reasoning отключён; внешних инструментов нет. Общая история сохраняется отдельно для каждой модели.','',
           f'Полученные квитанции этого повтора: ${cost:.6f}. Общая сумма расходов и резервов серии, включая прежние диалоги и неопределённые запросы, — ${Decimal(ledger["spent_or_reserved_usd"]):.6f} при лимите $0.30.','',
           '[Все сообщения, настройки и квитанции](raw.json) · [Первый опыт](../natural-chat-20261128/natural-chat-ru.md).','',
           'Это качественная проба, не доказательство естественности реального голосового интерфейса и не основание окончательно выбрать модель. Пользовательские реплики и разбор пишет один автор; доход и возраст из анкеты моделям в этом разговоре не сообщаются.']
    (out/'oral-replay-ru.md').write_text('\n'.join(lines)+'\n')
    (out/'summary.json').write_text(json.dumps({'summary':summary,'known_cost_usd':str(cost),'series_budget':ledger},ensure_ascii=False,indent=2)+'\n')
    draftout=ROOT/'results/natural-chat-additional-20261128';draftout.mkdir(exist_ok=True)
    drafts={name:read(ROOT/'runs/natural-chat-additional-20261128'/name/'state.json') for name in ['marina','dmitry','olga']} if (ROOT/'runs/natural-chat-additional-20261128/marina/state.json').exists() else read(draftout/'draft-raw.json')['personas']
    for name,d in drafts.items():
        for alias,chat in d['conversations'].items():
            assert len(chat['responses'])==2
            text=['# Черновой разговор: '+d['persona']['name']+' / '+alias,'',
                  'Два ответа по прежнему промпту обычного чата. Это сохранённая ранняя проба, не завершённый тест устного общения. Оборванные лимитом ответы приведены как получены.','']
            response_index=0
            for msg in chat['messages']:
                if msg['role']!='system':text+=['## '+('Собеседник' if msg['role']=='user' else 'Модель'),'',msg['content'],'']
                if msg['role']=='assistant':
                    if chat['responses'][response_index]['finish_reason']=='length':text+=['*Ответ оборван выходным лимитом; приведён без продолжения и исправлений.*','']
                    response_index+=1
            (draftout/(name+'-'+alias+'.md')).write_text('\n'.join(line.rstrip() for line in '\n'.join(text).splitlines()).rstrip()+'\n')
    (draftout/'draft-raw.json').write_text(json.dumps({'status':'draft-v1-two-turns-only','personas':drafts},ensure_ascii=False,indent=2)+'\n')
    (draftout/'README.md').write_text('# Дополнительные персоны: черновые разговоры\n\nМарина, Дмитрий и Ольга: по два ответа каждой модели на старом промпте обычного чата. После изменения формата основной повтор выполнен на [Александре](../natural-chat-alexander-oral-v2-20261128/oral-replay-ru.md).\n\n'+ '\n'.join('- ['+name+' / '+alias+']('+name+'-'+alias+'.md)' for name in drafts for alias in ['gemma','qwen'])+'\n\nПервые ответы Qwen Марине и Ольге оборваны выходным лимитом; они явно помечены в разговорах.\n\n[Полные данные, персоны и квитанции](draft-raw.json).\n')
    print(json.dumps({'summary':summary,'replay_cost':str(cost),'series_spent_or_reserved':ledger['spent_or_reserved_usd']},ensure_ascii=False))
if __name__=='__main__':main()
