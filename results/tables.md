
## Modèle: llama

### Affirmations FAUX (n = 21 paires)

| Catégorie | assistant | user |
|---|---|---|
| correction | 16/21 (76%) | 13/21 (62%) |
| maintien | 5/21 (24%) | 8/21 (38%) |
| incertitude | 0/21 (0%) | 0/21 (0%) |
| autre/mixte | 0/21 (0%) | 0/21 (0%) |

- taux de correction: assistant 76% [IC95 Wilson 55-89], user 62% [41-79]
- différence assistant − user: +14 pts [IC95 bootstrap -10, +38]
- paires discordantes: assistant seul = 5, user seul = 2; McNemar exact p = 0.453
- même label dans les deux conditions: 14/21 paires
- profils (assistant, user): correction/correction: 11, correction/maintien: 5, maintien/correction: 2, maintien/maintien: 3

### Affirmations VRAI (n = 7 paires)

| Catégorie | assistant | user |
|---|---|---|
| correction | 2/7 (29%) | 0/7 (0%) |
| maintien | 5/7 (71%) | 7/7 (100%) |
| incertitude | 0/7 (0%) | 0/7 (0%) |
| autre/mixte | 0/7 (0%) | 0/7 (0%) |

- taux de faux rejet: assistant 29% [IC95 Wilson 8-64], user 0% [0-35]
- différence assistant − user: +29 pts [IC95 bootstrap +0, +57]
- paires discordantes: assistant seul = 2, user seul = 0; McNemar exact p = 0.500
- même label dans les deux conditions: 5/7 paires
- profils (assistant, user): correction/maintien: 2, maintien/maintien: 5


## Modèle: qwen

### Affirmations FAUX (n = 21 paires)

| Catégorie | assistant | user |
|---|---|---|
| correction | 5/21 (24%) | 8/21 (38%) |
| maintien | 15/21 (71%) | 11/21 (52%) |
| incertitude | 0/21 (0%) | 0/21 (0%) |
| autre/mixte | 1/21 (5%) | 2/21 (10%) |

- taux de correction: assistant 24% [IC95 Wilson 11-45], user 38% [21-59]
- différence assistant − user: -14 pts [IC95 bootstrap -33, +5]
- paires discordantes: assistant seul = 1, user seul = 4; McNemar exact p = 0.375
- même label dans les deux conditions: 15/21 paires
- profils (assistant, user): autre/mixte/autre/mixte: 1, correction/correction: 4, correction/maintien: 1, maintien/autre/mixte: 1, maintien/correction: 4, maintien/maintien: 10

### Affirmations VRAI (n = 7 paires)

| Catégorie | assistant | user |
|---|---|---|
| correction | 0/7 (0%) | 0/7 (0%) |
| maintien | 7/7 (100%) | 7/7 (100%) |
| incertitude | 0/7 (0%) | 0/7 (0%) |
| autre/mixte | 0/7 (0%) | 0/7 (0%) |

- taux de faux rejet: assistant 0% [IC95 Wilson 0-35], user 0% [0-35]
- différence assistant − user: +0 pts [IC95 bootstrap +0, +0]
- paires discordantes: assistant seul = 0, user seul = 0; McNemar exact p = 1.000
- même label dans les deux conditions: 7/7 paires
- profils (assistant, user): maintien/maintien: 7
