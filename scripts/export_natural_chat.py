#!/usr/bin/env python3
"""Export actual natural-chat responses; never fabricate or score conversations."""
from decimal import Decimal
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    source=ROOT/'runs/natural-chat-20261128/state.json';state=json.loads(source.read_text())
    out=ROOT/'results/natural-chat-20261128';out.mkdir(exist_ok=True)
    (out/'raw.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
    (out/'assistant-prompt.txt').write_text(state['assistant_prompt'])
    (out/'persona.json').write_text(json.dumps(state['persona'],ensure_ascii=False,indent=2)+'\n')
    counts={};providers={}
    for alias,chat in state['conversations'].items():
        messages=chat['messages'];counts[alias]=sum(m['role']=='assistant' for m in messages)
        providers[alias]=sorted({r.get('provider') for r in chat['responses']})
        lines=['# '+state['models'][alias]['id']+' — разговор с Александром','',
               '[Персона, промпт и наблюдения](natural-chat-ru.md)','',
               'Реплики Александра написаны Codex от лица вымышленного персонажа. Ответы модели приведены без редактирования содержания. Это отдельная история разговора; ответы другой модели ей не передавались.','']
        turn=0
        for m in messages:
            if m['role']=='system':continue
            if m['role']=='user':turn+=1
            lines+=['## '+str(turn)+'. '+('Александр' if m['role']=='user' else 'Модель'),' ',m['content'],'']
        (out/(alias+'-dialogue.md')).write_text('\n'.join(line.rstrip() for line in '\n'.join(lines).splitlines()).rstrip()+'\n')
    cost=sum(Decimal(str(r.get('usage',{}).get('cost') or 0)) for chat in state['conversations'].values() for r in chat['responses'])
    held=Decimal(state['spent_or_reserved_usd']);assert cost<=held<=Decimal(state['cap_usd'])
    retries={alias:len(chat.get('error_history',[])) for alias,chat in state['conversations'].items()}
    pending_errors={alias:chat.get('error') for alias,chat in state['conversations'].items() if chat['status']=='error'}
    notes_path=out/'notes.json';notes=json.loads(notes_path.read_text()) if notes_path.exists() else []
    lines=['# Gemma и Qwen: обычный разговор с владельцем кофейни','',
           'Пробуем разговор на русском с двумя моделями от лица одного вымышленного человека. Цель — увидеть, как они уточняют намерение, реагируют на возражения, удерживают обстоятельства и помогают сформулировать решение. Баллы и выбор победителя здесь не задаются.','',
           '## Персона','',
           'Александр, 41 год, живёт в Москве с женой Ириной и девятилетней дочерью Соней. Владеет двумя небольшими кофейнями. Семья обеспеченная, он сам участвует в работе бизнеса. Это конкретная придуманная биография, а не утверждение о типичном поведении состоятельных москвичей.','',
           'Полная [анкета и инструкция роли](persona.json) предназначены автору пользовательских реплик. Модели получают только [общий промпт помощника](assistant-prompt.txt) и факты, которые Александр сообщает в собственном диалоге.','',
           '## Разговоры','',
           f"- [Gemma: полный диалог](gemma-dialogue.md) — {counts['gemma']} ответов; статус {state['conversations']['gemma']['status']}.",
           f"- [Qwen: полный диалог](qwen-dialogue.md) — {counts['qwen']} ответов; статус {state['conversations']['qwen']['status']}.",'',
           'Первая реплика одинакова: управляющая предлагает декабрьские подарочные наборы с кофе, Александр сомневается и хочет попробовать без большой закупки упаковки. Продолжения написаны после чтения ответов каждой модели: это адаптивные разговоры, а не одинаковая последовательность тестовых заданий. Реплики собеседника и их формулировки тоже влияют на результат.','',
           '## Наблюдения','', '[Подробная оценка естественности и понимания с конкретными примерами](dialogue-assessment-ru.md).','']
    lines += [('- '+note) for note in notes] if notes else ['Подробные наблюдения ещё не добавлены.']
    lines+=['','## Протокол и ограничения','',
            'Использован новый общий промпт обычного собеседника, не системный промпт v3 из теста инструментов. Внешних инструментов, поиска и реальных действий нет. Температура 0.5, до 1000 выходных токенов на ответ, reasoning отключён, полный контекст сохраняется отдельно для каждой модели. Ошибки и ручные повторы перечислены ниже. Успешные ответы не перегенерировались, выбор лучшего варианта не использовался.','',
            'Ручные повторы не вернувших пригодный ответ запросов (с теми же репликами): '+str(retries)+'. Неразрешённые сбои на момент экспорта: '+str(pending_errors)+'. Неопределённые резервы предыдущих попыток сохранены; подтверждённые ошибки установления соединения до отправки HTTP не считаются расходом API. Соединение последовательно пробовалось через urllib, curl HTTP/1.1 и IPv4; успешные ответы от этого не менялись.','',
            'Gemma: `google/gemma-4-31b-it`, закреплённый `coreweave/fp4`. Qwen: `qwen/qwen3.8-27b`, закреплённый `darkbloom/fp4`. Полученные провайдеры: '+str(providers)+'.','',
            f'Стоимость по полученным квитанциям: ${cost:.6f}; потрачено или зарезервировано ${held:.6f} при общем лимите $0.30.','',
            'В самом разговоре Александр не сообщает возраст и доход, поэтому специальную реакцию моделей на эти сведения мы не проверяем. Это одна качественная проба общения. Она не измеряет надёжность бизнес-рекомендаций, не представляет всех пользователей этого возраста и дохода и не устанавливает превосходство модели. Упомянутые в ответах факты и рекомендации не проверялись отдельным исследованием рынка.','',
            '[Все фактические сообщения, параметры запросов и квитанции](raw.json). Код запуска: [run_natural_chat.py](../../run_natural_chat.py); сборка отчёта: [export_natural_chat.py](../../scripts/export_natural_chat.py).']
    (out/'natural-chat-ru.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'answers':counts,'cost':str(cost),'spent_or_reserved':str(held)},ensure_ascii=False))
if __name__=='__main__':main()
