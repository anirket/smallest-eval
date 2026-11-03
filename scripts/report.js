// Turn promptfoo's results.json into a markdown summary for the PR.
// Usage: node scripts/report.js results.json
const fs = require('fs');
const path = require('path');

// The model name isn't in results.json, so read it from app/config.py
const configPy = fs.readFileSync(path.join(__dirname, '..', 'app', 'config.py'), 'utf8');
const MODEL = configPy.match(/MODEL\s*=\s*['"](.+?)['"]/)[1];

// Nearest-rank: the smallest value that p% of values are at or below
function percentile(values, p) {
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.ceil((p / 100) * sorted.length) - 1];
}

function caseName(c) {
  return c.testCase.description || JSON.stringify(c.vars);
}

function summary(cases, data) {
  const passed = cases.filter((c) => c.success).length;
  const totalCost = cases.reduce((sum, c) => sum + (c.cost || 0), 0);
  const latencies = cases.map((c) => c.latencyMs / 1000);
  const tokens = data.results.stats.tokenUsage;
  const version = data.metadata.promptfooVersion;

  return [
    '## Eval results',
    '',
    `**${passed}/${cases.length} passed**`,
    '',
    `- Cost: ₹${totalCost.toFixed(2)} total, ₹${(totalCost / cases.length).toFixed(2)} per case (app only, judge not counted)`,
    `- Latency: p50 ${percentile(latencies, 50).toFixed(1)} s, p95 ${percentile(latencies, 95).toFixed(1)} s`,
    `- Tokens: ${tokens.total.toLocaleString()} app + ${tokens.assertions.total.toLocaleString()} judge`,
    `- Model: \`${MODEL}\`, promptfoo ${version}`,
    '',
  ];
}

function failures(cases) {
  const failed = cases.filter((c) => !c.success);
  if (failed.length === 0) return [];

  const lines = ['### Failures', ''];
  for (const c of failed) {
    lines.push(`**${caseName(c)}**`);
    // An errored case (e.g. the API call failed) has no grading, only an error
    if (!c.gradingResult) {
      lines.push(`- error: ${String(c.error).split('\n')[0]}`, '');
      continue;
    }
    for (const check of c.gradingResult.componentResults) {
      if (!check.pass) lines.push(`- \`${check.assertion.type}\`: ${check.reason}`);
    }
    lines.push('');
  }
  return lines;
}

function allCases(cases) {
  const lines = ['### All cases', '', '| Case | Result | ₹ | Latency |', '|---|---|---|---|'];
  for (const c of cases) {
    const result = c.success ? '✅' : '❌';
    lines.push(`| ${caseName(c)} | ${result} | ${(c.cost || 0).toFixed(2)} | ${(c.latencyMs / 1000).toFixed(1)} s |`);
  }
  return lines;
}

function report(file) {
  const data = JSON.parse(fs.readFileSync(file, 'utf8'));
  const cases = data.results.results;
  return [...summary(cases, data), ...failures(cases), ...allCases(cases)].join('\n');
}

console.log(report(process.argv[2]));
