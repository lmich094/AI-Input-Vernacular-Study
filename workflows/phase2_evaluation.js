export const meta = {
  name: 'phase2-evaluation',
  description: 'Evaluate 114 MMLU questions at 3 input levels (342 agent calls) and write results',
  phases: [
    { title: 'Setup', detail: 'Load question_set.json' },
    { title: 'Evaluate', detail: '342 isolated agent calls — one per question/level pair' },
    { title: 'Report', detail: 'Write CSV, XLSX, and markdown summary via Python' },
  ],
}

const PROJECT_DIR = '/home/liam_michka/tokenUse/AI-Input-Vernacular-Study'

const model = (args && args.model) ? args.model : 'claude-sonnet-4-6'

// Step 1: load question set
phase('Setup')

const loadResult = await agent(
  `Read the file data/question_set.json in ${PROJECT_DIR} and return its contents.`,
  {
    label: 'load-questions',
    schema: {
      type: 'object',
      required: ['entries'],
      properties: { entries: { type: 'array', items: { type: 'object' } } }
    }
  }
)

const entries = loadResult.entries
log(`Loaded ${entries.length} questions. Running ${entries.length * 3} evaluations with model: ${model}`)

// Step 2: evaluate all 342 combinations
phase('Evaluate')

// Must match SYSTEM_PROMPT in phase2_evaluate.py
const SYSTEM_PROMPT = 'You are a helpful assistant. Answer the following multiple choice question by responding with only the letter of the correct answer (A, B, C, or D).'

const ANSWER_SCHEMA = {
  type: 'object',
  required: ['answer'],
  properties: {
    answer: { type: 'string', description: 'Single uppercase letter: A, B, C, or D' }
  }
}

const tasks = entries.flatMap(entry =>
  ['l1', 'l2', 'l3'].map(level => ({ entry, level }))
)

const results = await pipeline(
  tasks,
  ({ entry, level }) => {
    const questionText = entry[level]
    const letters = ['A', 'B', 'C', 'D']
    const choiceLines = entry.choices.map((c, i) => `${letters[i]}) ${c}`).join('\n')
    const userMsg = `${questionText}\n\n${choiceLines}`
    const inputTokensEst = Math.max(1, Math.floor((SYSTEM_PROMPT.length + userMsg.length) / 4))

    return agent(
      `${SYSTEM_PROMPT}\n\n${userMsg}`,
      { label: `eval:${entry.id}:${level}`, schema: ANSWER_SCHEMA, model, phase: 'Evaluate' }
    ).then(evalResult => {
      const rawAnswer = evalResult ? evalResult.answer : ''
      const answerGiven = rawAnswer && rawAnswer.length > 0 ? rawAnswer[0].toUpperCase() : 'X'
      return {
        id: entry.id,
        subject: entry.subject,
        level: level.toUpperCase(),
        question: questionText,
        answer_given: answerGiven,
        correct_answer: entry.correct_answer,
        is_correct: answerGiven === entry.correct_answer,
        input_tokens: inputTokensEst,
        output_tokens: 1,
        total_tokens: inputTokensEst + 1,
        model,
      }
    })
  }
)

const validResults = results.filter(Boolean)

if (validResults.length !== tasks.length) {
  log(`Warning: ${tasks.length - validResults.length} evaluation(s) failed and were filtered out`)
}

log(`Evaluation complete. ${validResults.length}/${tasks.length} results collected.`)

// Step 3: write results via Python
phase('Report')

const safeModel = model.replace(/\//g, '-')

await agent(
  `Run this command in ${PROJECT_DIR}:

echo '${JSON.stringify(validResults)}' | python3 -c "
import json, sys, os
results = json.loads(sys.stdin.read())
from report import write_results, generate_summary_report, save_report
os.makedirs('results', exist_ok=True)
write_results(results, 'results/raw_results_${safeModel}.csv', 'results/raw_results_${safeModel}.xlsx')
save_report(generate_summary_report(results, '${model}'), 'results/summary_report_${safeModel}.md')
print(f'Wrote {len(results)} results to CSV/XLSX')
print(f'Wrote summary to results/summary_report_${safeModel}.md')
"

Confirm the output shows result counts and file paths.`,
  { label: 'write-reports', phase: 'Report' }
)

log(`Results written to results/raw_results_${safeModel}.csv and results/summary_report_${safeModel}.md`)

return { evaluated: validResults.length, model }
