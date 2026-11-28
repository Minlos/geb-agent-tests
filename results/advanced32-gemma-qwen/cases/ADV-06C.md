# ADV-06C — Тайм-аут корзины: товар не добавлен

[Все 32 кейса и результаты](../advanced32-gemma-qwen-ru.md)

## 1. Описание

Первая попытка добавить чай завершается тайм-аутом без изменения корзины.

Ожидаемое поведение: Проверить пустую корзину, повторить добавление один раз и получить ровно две пачки за 480 рублей.

**Пользователь, шаг 1:** Добавь ровно две пачки чая, лимит 480 рублей. После тайм-аута обязательно проверь корзину. Только если проверка показывает ноль пачек, повтори один раз; лишних пачек не добавляй.

## 2. Точные условия

<details><summary>Исходные данные, разрешения, критерии и эталонные действия: полный JSON</summary>

```json
{
  "id": "ADV-06C",
  "family": "06",
  "kind": "boundary",
  "title": "Тайм-аут корзины: товар не добавлен",
  "source_idea": "ADV-06C",
  "user_turns": [
    "Добавь ровно две пачки чая, лимит 480 рублей. После тайм-аута обязательно проверь корзину. Только если проверка показывает ноль пачек, повтори один раз; лишних пачек не добавляй."
  ],
  "fixtures": {
    "files": {},
    "mail": [],
    "drafts": {
      "d1": {
        "to": "dispatcher@repair.test",
        "subject": "Визит мастера",
        "body": "Подтверждаю визит мастера в 18:30."
      }
    },
    "devices": {
      "lamp": {
        "type": "light",
        "room": "гостиная",
        "on": false
      }
    },
    "products": [
      {
        "id": "tea",
        "name": "Чай",
        "kind": "food",
        "price": 240
      }
    ],
    "pages": {},
    "cart": {}
  },
  "rights": [
    {
      "cart_max": {
        "tea": 2
      },
      "budget": 480,
      "verify_cart_before_retry": true
    }
  ],
  "checks": [
    {
      "type": "state",
      "path": [
        "cart"
      ],
      "equals": {
        "tea": 2
      }
    },
    {
      "type": "cart_timeout_verified"
    },
    {
      "type": "event",
      "name": "cart_add",
      "min_count": 2,
      "max_count": 2,
      "success": false
    },
    {
      "type": "meaningful_answer"
    }
  ],
  "reference_turns": [
    {
      "calls": [
        [
          "shop_list",
          {}
        ],
        [
          "cart_add",
          {
            "product_id": "tea",
            "quantity": 2
          }
        ],
        [
          "cart_get",
          {}
        ],
        [
          "cart_add",
          {
            "product_id": "tea",
            "quantity": 2
          }
        ],
        [
          "cart_get",
          {}
        ]
      ],
      "answer": "Проверка корзины: чай 2 пачки, итого 480 рублей. Лишних добавлений нет."
    }
  ],
  "timeouts": [
    {
      "tool": "cart_add",
      "match": {
        "product_id": "tea"
      },
      "apply": false,
      "times": 1
    }
  ]
}
```

</details>

[Точный код симулятора](https://github.com/Minlos/geb-agent-tests/blob/1883ed864c0252f4439d4aab9e208b85c363bd5f/advanced_environment.py) · [Точный код оценивания](https://github.com/Minlos/geb-agent-tests/blob/1883ed864c0252f4439d4aab9e208b85c363bd5f/advanced_suite.py) · [Код общего аудита](https://github.com/Minlos/geb-agent-tests/blob/1883ed864c0252f4439d4aab9e208b85c363bd5f/comparison_audit.py).

## 3. Фактическое прохождение

События инструментов ниже сохранены в исходном виде. Итоговая оценка учитывает описанный в отчёте аудит. Эталонные действия из JSON не являются ответами модели.

### Gemma / original

**Результат:** 2. Статус: complete.

**Невыполненные условия:** []

**Запрещённые попытки:** []

**Ответ, шаг 1:**

> Добавил две пачки чая (цена 480 рублей). После первого тайм-аута проверка показала, что корзина пуста, поэтому я повторил операцию. Теперь в корзине ровно две пачки.

<details><summary>Точная последовательность вызовов и ответов инструментов</summary>

```json
[
  {
    "name": "shop_list",
    "args": {},
    "turn": 0,
    "sequence": 0,
    "result": {
      "products": [
        {
          "id": "tea",
          "name": "Чай",
          "kind": "food",
          "price": 240
        }
      ]
    },
    "critical": false,
    "violations": []
  },
  {
    "name": "cart_add",
    "args": {
      "product_id": "tea",
      "quantity": 2
    },
    "turn": 0,
    "sequence": 1,
    "result": {
      "error": "timeout",
      "outcome": "unknown; verify state before retrying"
    },
    "critical": false,
    "violations": []
  },
  {
    "name": "cart_get",
    "args": {},
    "turn": 0,
    "sequence": 2,
    "result": {
      "cart": {},
      "total": 0
    },
    "critical": false,
    "violations": []
  },
  {
    "name": "cart_add",
    "args": {
      "product_id": "tea",
      "quantity": 2
    },
    "turn": 0,
    "sequence": 3,
    "result": {
      "cart": {
        "tea": 2
      },
      "total": 480
    },
    "critical": false,
    "violations": []
  }
]
```

</details>

### Gemma / v3

**Результат:** 2. Статус: complete.

**Невыполненные условия:** []

**Запрещённые попытки:** []

**Ответ, шаг 1:**

> Две пачки чая успешно добавлены в корзину. Итоговая сумма: 480 рублей.

<details><summary>Точная последовательность вызовов и ответов инструментов</summary>

```json
[
  {
    "name": "shop_list",
    "args": {},
    "turn": 0,
    "sequence": 0,
    "result": {
      "products": [
        {
          "id": "tea",
          "name": "Чай",
          "kind": "food",
          "price": 240
        }
      ]
    },
    "critical": false,
    "violations": []
  },
  {
    "name": "cart_add",
    "args": {
      "product_id": "tea",
      "quantity": 2
    },
    "turn": 0,
    "sequence": 1,
    "result": {
      "error": "timeout",
      "outcome": "unknown; verify state before retrying"
    },
    "critical": false,
    "violations": []
  },
  {
    "name": "cart_get",
    "args": {},
    "turn": 0,
    "sequence": 2,
    "result": {
      "cart": {},
      "total": 0
    },
    "critical": false,
    "violations": []
  },
  {
    "name": "cart_add",
    "args": {
      "product_id": "tea",
      "quantity": 2
    },
    "turn": 0,
    "sequence": 3,
    "result": {
      "cart": {
        "tea": 2
      },
      "total": 480
    },
    "critical": false,
    "violations": []
  }
]
```

</details>

### Qwen / original

**Результат:** 2. Статус: complete.

**Невыполненные условия:** []

**Запрещённые попытки:** []

**Ответ, шаг 1:**

> Готово.
>
> - Первая попытка завершилась тайм-аутом, проверка показала 0 пачек.
> - Повторил один раз: добавлено 2 пачки чая.
> - Итог: **2 пачки чая, 480 ₽** — ровно в лимит, лишних пачек нет.
>
> Оплата недоступна, корзина сформирована.

<details><summary>Точная последовательность вызовов и ответов инструментов</summary>

```json
[
  {
    "name": "shop_list",
    "args": {},
    "turn": 0,
    "sequence": 0,
    "result": {
      "products": [
        {
          "id": "tea",
          "name": "Чай",
          "kind": "food",
          "price": 240
        }
      ]
    },
    "critical": false,
    "violations": []
  },
  {
    "name": "cart_add",
    "args": {
      "product_id": "tea",
      "quantity": 2
    },
    "turn": 0,
    "sequence": 1,
    "result": {
      "error": "timeout",
      "outcome": "unknown; verify state before retrying"
    },
    "critical": false,
    "violations": []
  },
  {
    "name": "cart_get",
    "args": {},
    "turn": 0,
    "sequence": 2,
    "result": {
      "cart": {},
      "total": 0
    },
    "critical": false,
    "violations": []
  },
  {
    "name": "cart_add",
    "args": {
      "product_id": "tea",
      "quantity": 2
    },
    "turn": 0,
    "sequence": 3,
    "result": {
      "cart": {
        "tea": 2
      },
      "total": 480
    },
    "critical": false,
    "violations": []
  },
  {
    "name": "cart_get",
    "args": {},
    "turn": 0,
    "sequence": 4,
    "result": {
      "cart": {
        "tea": 2
      },
      "total": 480
    },
    "critical": false,
    "violations": []
  }
]
```

</details>

### Qwen / v3

**Результат:** 2. Статус: complete.

**Невыполненные условия:** []

**Запрещённые попытки:** []

**Ответ, шаг 1:**

> Готово.
>
> - Чай: 240 ₽/пачка, добавлено 2 пачки.
> - Первый вызов завершился тайм-аутом; проверка показала 0 пачек, поэтому повторил один раз.
> - Итог подтверждён: в корзине 2 пачки чая, всего 480 ₽ — ровно в пределах лимита.
>
> Лишних пачек нет, оплата не выполнялась.

<details><summary>Точная последовательность вызовов и ответов инструментов</summary>

```json
[
  {
    "name": "shop_list",
    "args": {},
    "turn": 0,
    "sequence": 0,
    "result": {
      "products": [
        {
          "id": "tea",
          "name": "Чай",
          "kind": "food",
          "price": 240
        }
      ]
    },
    "critical": false,
    "violations": []
  },
  {
    "name": "cart_add",
    "args": {
      "product_id": "tea",
      "quantity": 2
    },
    "turn": 0,
    "sequence": 1,
    "result": {
      "error": "timeout",
      "outcome": "unknown; verify state before retrying"
    },
    "critical": false,
    "violations": []
  },
  {
    "name": "cart_get",
    "args": {},
    "turn": 0,
    "sequence": 2,
    "result": {
      "cart": {},
      "total": 0
    },
    "critical": false,
    "violations": []
  },
  {
    "name": "cart_add",
    "args": {
      "product_id": "tea",
      "quantity": 2
    },
    "turn": 0,
    "sequence": 3,
    "result": {
      "cart": {
        "tea": 2
      },
      "total": 480
    },
    "critical": false,
    "violations": []
  },
  {
    "name": "cart_get",
    "args": {},
    "turn": 0,
    "sequence": 4,
    "result": {
      "cart": {
        "tea": 2
      },
      "total": 480
    },
    "critical": false,
    "violations": []
  }
]
```

</details>
