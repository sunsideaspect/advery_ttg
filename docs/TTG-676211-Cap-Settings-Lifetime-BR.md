# TTG-676211 — Налаштування кап: DAILY / HOURLY / LIFETIME

## Бізнес-рекомендації щодо впровадження Lifetime Cap у блоці налаштування кап

## 1. Мета рішення
Мета рішення — розширити блок налаштування кап додаванням режиму `LIFETIME` на рівні `Partner Offer Name`, щоб менеджер міг обмежувати загальну кількість кліків на весь період оферу.

Рішення повинно:
- дати контроль total cap для prepay-сценаріїв;
- зменшити перевитрати кліків;
- залишити простий та зрозумілий UX для менеджера.

## 2. Загальний принцип рішення
Блок налаштування кап підтримує 3 режими:
- `DAILY`
- `HOURLY`
- `LIFETIME`

Режими `DAILY/HOURLY/LIFETIME` — окрема логіка капування і не повʼязані з іншим функціоналом.

Поле `Global Cap` є єдиним полем введення цільового ліміту, але індикатори праворуч залежать від вибраного режиму:
- у `DAILY/HOURLY`: показуємо 2 числа (сьогодні / вчора);
- у `LIFETIME`: показуємо тільки 1 число (накопичені кліки за весь час).

## 3. Що означають цифри праворуч
1. Перша цифра — кількість кліків на капу за сьогодні.
2. Друга цифра — кількість кліків на капу за вчора.

Для `LIFETIME` друга цифра не має сенсу, тому:
- відображається лише одна цифра (накопичено за lifetime);
- друга цифра прихована.

## 4. Схема роботи налаштування
Основні елементи блоку:
1. Назва блоку: `Cap Settings`.
2. Поле `Global Cap`.
3. Права зона в полі:
   - числові індикатори (залежно від режиму);
   - кнопка `Edit`;
   - кнопка `Reset` (лише для `LIFETIME`, якщо ввімкнено).
4. Група періодичності: `[DAILY | HOURLY | LIFETIME]`.
5. Група дії: `[EXCLUDE | RETURN]`.

## 5. Логіка редагування Lifetime Cap
### Базові правила
1. Менеджер може змінити значення `Global Cap` у `LIFETIME`.
2. При зміні виконується перевірка відносно фактичного `spentClicksLifetime`.

### Критичний кейс (запит користувача)
Поточний стан:
- cap = 1000
- already spent = 800
- менеджер змінює cap на 700

Рекомендована поведінка:
- нове значення зберігається (`newCap = 700`);
- система одразу переводить стан у `cap reached` (бо 800 >= 700);
- нові кліки блокуються згідно обраної дії (`EXCLUDE` або `RETURN`);
- показуємо менеджеру попередження:  
  `New cap is lower than already spent clicks. Cap is reached immediately.`

### UX для edit у LIFETIME
При спробі зберегти `newCap < spentClicksLifetime`:
- показати confirm modal;
- текст:  
  `You set cap below current spent clicks. Traffic will be stopped immediately. Continue?`
- кнопки: `Cancel` / `Apply`.

Якщо менеджер натискає `Apply` — зберігаємо та активуємо `cap reached` миттєво.

## 6. Додаткові user cases (edge cases)
1. `newCap = spentClicksLifetime`  
   - cap вважається досягнутим одразу;
   - нові кліки блокуються.
2. `newCap > spentClicksLifetime`  
   - cap залишається активною до досягнення нового порогу.
3. `newCap <= 0` або нечислове значення  
   - валідація: не дозволяти save, показати error.
4. Зміна режиму `DAILY -> LIFETIME`  
   - у правому куті перемикаємо індикатор на 1 число (lifetime spent).
5. Зміна режиму `LIFETIME -> DAILY/HOURLY`  
   - повертаємо 2 числа (today/yesterday).
6. Натискання `Reset` у `LIFETIME`  
   - скидає lifetime-лічильник (залежить від backend-політики доступу і аудиту).

## 7. Функціональні вимоги
1. Назва блоку в UI: `Cap Settings` (без згадок Frequency Cap).
2. Періодичність: `DAILY | HOURLY | LIFETIME`.
3. `Global Cap` видимий у всіх режимах.
4. `DAILY/HOURLY`:
   - показуються 2 індикатори: today / yesterday.
5. `LIFETIME`:
   - показується 1 індикатор: lifetime spent;
   - другий індикатор прихований.
6. `Edit` доступний у всіх режимах.
7. `Reset` відображається тільки в `LIFETIME`.
8. При `newCap <= spentClicksLifetime` у `LIFETIME`:
   - показати warning/confirm;
   - після підтвердження — негайний `cap reached`.

## 8. Acceptance Criteria
1. У блоці `Cap Settings` є 3 режими: `DAILY`, `HOURLY`, `LIFETIME`.
2. У `DAILY/HOURLY` видно 2 цифри (today/yesterday).
3. У `LIFETIME` видно лише 1 цифру (lifetime).
4. При `LIFETIME` + `newCap < spentClicksLifetime` система попереджає і після підтвердження одразу блокує нові кліки.
5. `Reset` є тільки у `LIFETIME`.

## 9. Таблиця відповідності: бізнес-вимога — реалізація — статус
| Бізнес-вимога | Наша реалізація | Статус |
|---|---|---|
| Прибрати привʼязку до Frequency Cap | Назва блоку `Cap Settings`, окрема логіка режимів | OK |
| Для lifetime не показувати 2-гу цифру | У `LIFETIME` рендеримо лише 1 індикатор | OK |
| Пояснити meaning цифр | today/yesterday у daily/hourly; lifetime total у lifetime | OK |
| Продумати edit при зменшенні капи | confirm + immediate cap reached при `newCap <= spent` | OK |
| Додати edge cases | Розділ 6 з кейсами | OK |

## 10. Макет (Confluence HTML)
Інтерактивний макет збережено у файлі:

`mockups/ttg-676211/index.html`

Interactive URL:
`https://sunsideaspect.github.io/advery_ttg/mockups/ttg-676211/`

## Changelog
| Дата | Тип зміни | Розділ | Опис зміни | Автор | Коментар |
|---|---|---|---|---|---|
| 2026-03-18 | Initial | All | Початковий BR + mockup | Cloud Agent | Draft |
| 2026-03-18 | Update | 1-9 | Прибрано згадки Frequency Cap, додано логіку лічильників і edit lifetime | Cloud Agent | Updated |

## Q&A
| Питання | Коментар | Статус |
|---|---|---|
| Хто має право на Reset у lifetime? | Рекомендується RBAC (admin/ops) | Open |
| Чи потрібен аудит edit/reset? | Рекомендується log actor + timestamp + old/new cap | Open |

## Meetings Log
| Дата | Тип зустрічі | Учасники | Основні рішення | Наступні кроки |
|---|---|---|---|---|
| TBD | Grooming | PM / BE / FE | Підтвердити API-поведінку для immediate cap reached | Зафіксувати контракт |

## Risks & Mitigation
| Ризик | Опис | Ймовірність | Вплив | Мітігація |
|---|---|---|---|---|
| Різне трактування цифр | Менеджери можуть не розуміти today/yesterday vs lifetime | Середня | Середній | Tooltip/label для індикаторів |
| Агресивне зменшення cap | Різка зупинка трафіку | Середня | Високий | Confirm modal + warning |
| Неочевидний reset | Неконтрольоване скидання lifetime | Низька | Високий | RBAC + audit log |

