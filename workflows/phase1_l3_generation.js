export const meta = {
  name: 'phase1-l3-generation',
  description: 'Generate L3 abbreviation variants for all MMLU questions and save question_set.json',
  phases: [
    { title: 'Load', detail: 'Run Python script to generate L1+L2 and save raw_questions.json' },
    { title: 'Generate L3', detail: '114 agent calls — one per question — to produce L3 text' },
    { title: 'Save', detail: 'Assemble question_set.json via Python' },
  ],
}

// Step 1: generate raw questions (L1 + L2) via Python
phase('Load')
await agent(
  'Run the command: cd /home/liam_michka/tokenUse/AI-Input-Vernacular-Study && python3 phase1_generate_questions.py\n\nConfirm that data/raw_questions.json was created and report how many entries it contains.',
  { label: 'generate-raw' }
)

const rawResult = await agent(
  'Read the file data/raw_questions.json in /home/liam_michka/tokenUse/AI-Input-Vernacular-Study and return its contents as a JSON array.',
  {
    label: 'read-raw',
    schema: {
      type: 'object',
      required: ['entries'],
      properties: {
        entries: { type: 'array', items: { type: 'object' } }
      }
    }
  }
)

const entries = rawResult.entries

log(`Loaded ${entries.length} raw questions. Generating L3 variants...`)

// Step 2: generate L3 for each entry
phase('Generate L3')

const L3_SCHEMA = {
  type: 'object',
  required: ['l3'],
  properties: {
    l3: { type: 'string', description: 'The abbreviated L3 version of the question' }
  }
}

const l3Results = await pipeline(
  entries,
  (entry) => agent(
    `You are a text abbreviation engine. Your job is to shorten words in the input text where the abbreviated form would still be understandable to a human reader. Do not change any words that are already short (4 characters or fewer). Do not alter proper nouns, numbers, or answer choices. Return only the abbreviated text with no explanation.\n\nAbbreviate this text:\n${entry.l2}`,
    { label: `l3:${entry.id}`, schema: L3_SCHEMA, model: 'haiku', phase: 'Generate L3' }
  )
)

// Step 3: assemble and save question_set.json
phase('Save')

const finalEntries = entries.map((entry, i) => ({
  id: entry.id,
  subject: entry.subject,
  correct_answer: entry.correct_answer,
  choices: entry.choices,
  l1: entry.l1,
  l2: entry.l2,
  l3: (l3Results[i] && l3Results[i].l3) ? l3Results[i].l3 : entry.l2,
  l3_generation_model: 'claude-haiku-4-5-20251001',
}))

const savePrompt = `Write the following JSON to the file data/question_set.json in /home/liam_michka/tokenUse/AI-Input-Vernacular-Study (overwrite if exists):

${JSON.stringify(finalEntries, null, 2)}

Then confirm the file was written and report the entry count.`

await agent(savePrompt, { label: 'save-question-set', phase: 'Save' })

log(`Phase 1 complete. ${finalEntries.length} entries saved to data/question_set.json.`)
log('Next: review data/question_set.json, then commit it to the repo.')

return { count: finalEntries.length }
