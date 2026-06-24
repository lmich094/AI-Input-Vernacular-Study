# AI Input Vernacular Study — Results

**Model:** claude-sonnet-4-6
**Questions:** 114 (2 per subject × 57 subjects)
**Total API calls:** 342

---

## Accuracy by Level

| Level | Description | Accuracy |
|-------|-------------|----------|
| L1 | Normal grammar (control) | 95.6% |
| L2 | Texting abbreviations | 95.6% |
| L3 | Texting + word truncation | 93.9% |

## Token Usage by Level

| Level | Avg Input Tokens | Savings vs L1 |
|-------|-----------------|---------------|
| L1 | 127.6 | — |
| L2 | 124.4 | 2.5% |
| L3 | 117.1 | 8.3% |

## Accuracy by Subject

| subject                             |   L1 |   L2 |   L3 |
|:------------------------------------|-----:|-----:|-----:|
| abstract_algebra                    | 100% | 100% | 100% |
| anatomy                             | 100% | 100% | 100% |
| astronomy                           | 100% | 100% | 100% |
| business_ethics                     | 100% | 100% | 100% |
| clinical_knowledge                  | 100% | 100% |  50% |
| college_biology                     | 100% | 100% | 100% |
| college_chemistry                   | 100% | 100% | 100% |
| college_computer_science            | 100% | 100% | 100% |
| college_mathematics                 | 100% | 100% | 100% |
| college_medicine                    | 100% | 100% | 100% |
| college_physics                     | 100% | 100% | 100% |
| computer_security                   | 100% | 100% | 100% |
| conceptual_physics                  | 100% | 100% | 100% |
| econometrics                        | 100% | 100% | 100% |
| electrical_engineering              | 100% | 100% | 100% |
| elementary_mathematics              | 100% | 100% | 100% |
| formal_logic                        |  50% |  50% |  50% |
| global_facts                        | 100% | 100% | 100% |
| high_school_biology                 | 100% | 100% | 100% |
| high_school_chemistry               | 100% | 100% | 100% |
| high_school_computer_science        | 100% | 100% | 100% |
| high_school_european_history        | 100% | 100% | 100% |
| high_school_geography               |  50% | 100% | 100% |
| high_school_government_and_politics | 100% | 100% | 100% |
| high_school_macroeconomics          | 100% | 100% | 100% |
| high_school_mathematics             | 100% | 100% | 100% |
| high_school_microeconomics          | 100% | 100% | 100% |
| high_school_physics                 | 100% | 100% | 100% |
| high_school_psychology              | 100% | 100% | 100% |
| high_school_statistics              | 100% | 100% | 100% |
| high_school_us_history              | 100% | 100% | 100% |
| high_school_world_history           | 100% | 100% | 100% |
| human_aging                         | 100% | 100% | 100% |
| human_sexuality                     | 100% | 100% | 100% |
| international_law                   | 100% | 100% | 100% |
| jurisprudence                       |  50% |  50% |  50% |
| logical_fallacies                   | 100% | 100% | 100% |
| machine_learning                    | 100% |  50% | 100% |
| management                          | 100% | 100% | 100% |
| marketing                           | 100% | 100% |  50% |
| medical_genetics                    | 100% | 100% | 100% |
| miscellaneous                       | 100% | 100% | 100% |
| moral_disputes                      | 100% | 100% | 100% |
| moral_scenarios                     | 100% | 100% |  50% |
| nutrition                           | 100% | 100% | 100% |
| philosophy                          | 100% | 100% | 100% |
| prehistory                          |  50% |  50% |  50% |
| professional_accounting             | 100% | 100% | 100% |
| professional_law                    | 100% | 100% | 100% |
| professional_medicine               | 100% | 100% | 100% |
| professional_psychology             | 100% | 100% | 100% |
| public_relations                    | 100% | 100% | 100% |
| security_studies                    | 100% | 100% | 100% |
| sociology                           | 100% | 100% | 100% |
| us_foreign_policy                   | 100% | 100% | 100% |
| virology                            |  50% |  50% |  50% |
| world_religions                     | 100% | 100% | 100% |

## Key Finding

Abbreviated inputs maintained accuracy within 5% of the L1 baseline (L1: 95.6%, L2: 95.6%, L3: 93.9%) while reducing input tokens by 2.5% at L2 and 8.3% at L3, supporting the hypothesis that vernacular shorthand can reduce token usage without sacrificing quality.
