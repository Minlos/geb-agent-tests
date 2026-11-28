"""Recompute the report offline from archived conversations and verdicts."""
import json
from decimal import Decimal
from pathlib import Path

root = Path(__file__).resolve().parent
report = root.parent / 'natural-chat-frontier-20261128/comparison-ru.md'
models = [('A','deepseek','DeepSeek V4 Pro 0813'),('B','fable','Claude Fable 5.2'),('C','qwen','Qwen3.8-27B'),('D','gemma','Gemma 4 31B'),('E','glm','GLM-5.3')]
def read(p):
    return json.loads((root/p).read_text())
review = read('review.json')
notes = {
    'fable':'Уточнила минимальную партию, услышала ответ «пятьдесят» и предложила попробовать пять наборов без коробок. Дала короткую фразу для разговора с женой. Слабое место — прогноз восьми-десяти продаж за декабрь по двум продажам за одну неделю.',
    'deepseek':'Сохранила возможность подержать кружку в руках и предложила общий ценник. В отпуске сначала предложила разойтись днём, затем приняла уточнение о совместной прогулке после завтрака.',
    'gemma':'Когда Александр отказался вести тетрадку, предложила бланк или форму для той же записи заявок. После второго уточнения переключилась на готовый набор. В семейной теме естественно спросила о музеях.',
    'glm':'Придумала дом и квартиры. Предложила удвоить закупку после трёх продаж из десяти, хотя семь наборов ещё оставались. Признала, что додумала конфликт с Ирой, когда Александр её поправил.',
    'qwen':'Предположила, что подарки нужны для офиса. Приняла предложенную маленькую партию, но в разговоре об отпуске ввела «буферное утренне» и продолжила объяснять «буфер» даже после прямого возражения.'
}
rows=[]; total=Decimal(0); judges=Decimal(0); ids=set(); openings=set()
for alias,name,title in models:
    s=read(name+'.json');m=s['messages'];r=s['receipts']
    assert len(r)==6 and [t['role'] for t in m]==['system']+['user','assistant']*6
    assert m[0]['content']==(report.parent/'assistant-prompt.txt').read_text()
    openings.add(m[1]['content']);ids.update(x['id'] for x in r)
    page=['# Александр — '+title,'','[Общее сравнение](../natural-chat-frontier-20261128/comparison-ru.md)','']
    for i,t in enumerate(m[1:]):
        page += [f"## {1+i//2}. "+('Александр' if i%2==0 else 'Модель'),'',t['content'],'']
    (root/(name+'.md')).write_text('\n'.join(page))
    b=read('judge/'+alias+'-request.json')
    assert json.loads(b['messages'][1]['content'])==[dict(turn=i+1,user=m[1+2*i]['content'],device=m[2+2*i]['content']) for i in range(6)]
    d=read('judge/'+alias+'-response.json')
    v=json.loads(d['choices'][0]['message']['content'])
    g=[v[k]['score'] for k in ('understanding','usefulness','spoken')]
    assert all(type(x)==int and 1<=x<=5 for x in g+review[name])
    rows.append((title,name,review[name],g))
    total+=sum(Decimal(str(x['usage']['cost'])) for x in r)
    judges+=Decimal(str(d['usage']['cost']))
assert len(ids)==30 and len(openings)==1
lines=['# Александр и пять моделей в роли домашней голосовой станции','',
       'Пять новых сессий, по шесть ответов в каждой. У всех одинаковые начальная реплика, персона и системный промпт. Далее Codex писал каждую реплику Александра после чтения ответа именно этой модели. Общие темы — кофе для подарочных наборов и отпуск с женой. Детали и вопросы различаются между диалогами.','',
       '## Полные диалоги','']+['- ['+title+'](../alexander-fresh/'+name+'.md)' for title,name,_,_ in rows]+['',
       '## Промпт и условия','','[Системный промпт](assistant-prompt.txt) · [Персона Александра](persona.json) · [Промпт независимого судьи](../alexander-fresh/judge/prompt.txt).',
       '', 'Для каждого диалога сохранены настройки модели, сообщения и квитанции. Включая Fable, все первые ответы получены заново. Проверяем русский текст для произнесения вслух. Аудио и время отклика не измерялись.','',
       '## Оценка моделей для домашней станции','','Каждый критерий получает от 1 до 5 баллов за весь диалог. Итог — среднее трёх оценок. Codex выставил баллы до отправки разговоров Grok. Grok получил по одному обезличенному запросу на модель.','']
for idx,label in [(2,'Оценка Codex'),(3,'Независимая оценка Grok 4.3')]:
    lines+=['### '+label,'','| Модель | Понимание | Польза | Удобно слушать | Среднее из 5 |','|---|---:|---:|---:|---:|']
    for row in sorted(rows,key=lambda x:-sum(x[idx])):
        title,name=row[:2];v=row[idx];avg=f'{sum(v)/3:.2f}'.replace('.',',')
        lines+=['| ['+title+'](../alexander-fresh/'+name+'.md) | '+' | '.join(map(str,v))+' | '+avg+' |']
    lines+=['']
lines+=['## Почему оценки различаются','']+['- **'+title+'.** '+notes[name] for title,name,_,_ in sorted(rows,key=lambda x:-sum(x[2]))]+['',
        'В обосновании Grok для Gemma есть проверяемая ошибка. В четвёртом ходе она спросила, в какие музеи хочет Ира, а судья написал, что она продолжила обсуждать подарочные наборы. Баллы судьи приведены как получены. Одна адаптивная беседа на модель позволяет сравнить наблюдаемые ответы, но вопросы разной сложности ограничивают точность рейтинга.','',
        f'Квитанции за 30 ответов моделей в этом повторе составили ${total}, за пять оценок Grok — ${judges}. [Данные и скрипт пересчёта](../alexander-fresh/) · [Запросы и ответы судьи](../alexander-fresh/judge/) · [Оборудование для GLM и DeepSeek](hardware-cost-ru.md).']
report.write_text('\n'.join(lines)+'\n')
print('\n'.join(x for x in lines if x.startswith('| [')))
