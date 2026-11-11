import {readFileSync, appendFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import YAML from 'yaml';

const workflow = YAML.parse(readFileSync('.github/workflows/site-checks.yml', 'utf8'));
const steps = workflow.jobs.build.steps;
const packageScripts = JSON.parse(readFileSync('package.json', 'utf8')).scripts;
const keys = text => [...text.matchAll(/\d{4}-\d{2}-\d{2}-[a-z0-9-]+/g)].map(match => match[0]);

export function inventory() {
  let java, gradle, ruby, yaml, jdk21, preserved21;
  const checks = [];
  for (const step of steps) {
    if (step.uses?.startsWith('actions/setup-java')) {
      java = step.id;
      if (String(step.with['java-version']).startsWith('21')) jdk21 = java;
    }
    if (step.uses?.startsWith('gradle/actions/setup-gradle')) gradle = step.id || steps.find(candidate => candidate.id && candidate.with?.['gradle-version'] === step.with['gradle-version'])?.id;
    if (step.uses?.startsWith('ruby/setup-ruby')) ruby = step.id;
    if (step.name?.startsWith('Install the YAML')) yaml = step.id;
    if (step.name?.startsWith('Preserve JDK')) preserved21 = step.id;
    if (!step.id?.startsWith('example_')) continue;
    const command = step.run.replace('npm run test:articles', packageScripts['test:articles']);
    const paths = [...command.matchAll(/(?:scripts|\.pipeline\/drafts)\/[\w./-]+\.py/g)]
      .map(match => match[0]).filter(path => !path.endsWith('build_algorithm_diagrams.py'));
    const source = paths.map(path => readFileSync(path, 'utf8')).join('\n');
    const dependencies = [];
    if (/java|javac|JAVA_HOME|jdk/i.test(source)) dependencies.push(java);
    if (/gradle/i.test(source)) dependencies.push(gradle);
    if (command.includes('check_ruby_environment')) dependencies.push(ruby);
    if (command.includes('check_config_input')) dependencies.push(yaml);
    if (command.includes('DB_SEMAPHORE_JDK21')) dependencies.push(jdk21, preserved21);
    // An explicit saved JDK 21 argument takes precedence over the current toolchain.
    if (command.includes('--jdk "$DB_SEMAPHORE_JDK21"') && !command.includes('--jdk "$JAVA_HOME"')) {
      dependencies.splice(0, dependencies.length, jdk21, preserved21, gradle);
    }
    checks.push({id: step.id, name: step.name, source, keys: new Set(keys(command + '\n' + source)), dependencies: dependencies.filter(Boolean)});
  }
  return checks;
}

export function plan(files, checks = inventory()) {
  const all = steps.map(step => step.id).filter(id => id?.startsWith('runtime_') || id?.startsWith('example_') || id === 'boot_gradle');
  const full = reason => ({steps: all, previews: true, full: true, reason});
  if (!files?.length) return full('No reliable content diff; run the complete suite');
  const selected = new Set();
  let previews = false;
  for (const file of files) {
    if (/^(?:\.github\/|scripts\/|package(?:-lock)?\.json$|\.nvmrc$|astro\.config|tsconfig|src\/content\.config)/.test(file)) return full(`Shared validation or schema changed: ${file}`);
    const article = file.match(/^src\/content\/posts\/(en|ko)\/(.+)\.md$/);
    const draft = file.match(/^\.pipeline\/drafts\/([^/]+)\//);
    if (article || draft) {
      const key = article ? article[2] : draft[1];
      const matches = checks.filter(check => check.keys.has(key));
      if (!matches.length) return full(`No registered runtime for ${key}`);
      for (const check of matches) for (const id of [check.id, ...check.dependencies]) selected.add(id);
      continue;
    }
    if (/^(?:\.pipeline\/(?:technical-translations|translations)|src\/content\/(?:technicalTranslations|translations|renewals))/.test(file)) { previews = true; continue; }
    if (/^src\/(?:layouts|components|lib|pages)\//.test(file)) { previews = true; continue; }
    if (/^src\/content\//.test(file)) { previews = true; continue; }
    if (/^assets\//.test(file)) {
      const matches = checks.filter(check => check.source.includes(file.split('/').at(-1)));
      if (!matches.length) return full(`Shared or unregistered asset changed: ${file}`);
      for (const check of matches) for (const id of [check.id, ...check.dependencies]) selected.add(id);
      continue;
    }
    return full(`Unclassified change: ${file}`);
  }
  return {steps: [...selected], previews, full: false, reason: 'Only affected example runtimes; all site checks remain enabled'};
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  let files;
  const base = process.env.CI_BASE;
  if (/^[a-f0-9]{40}$/.test(base || '') && !/^0+$/.test(base)) {
    try {
      try { execFileSync('git', ['cat-file', '-e', `${base}^{commit}`], {stdio: 'ignore'}); }
      catch { execFileSync('git', ['fetch', '--no-tags', '--depth=1', 'origin', base], {stdio: 'ignore'}); }
      files = execFileSync('git', ['diff', '--name-only', '-z', base, 'HEAD'], {encoding: 'utf8'}).split('\0').filter(Boolean);
    } catch { /* An incomplete diff must select the complete suite. */ }
  }
  const result = plan(files);
  console.log(JSON.stringify(result, null, 2));
  if (process.env.GITHUB_OUTPUT) appendFileSync(process.env.GITHUB_OUTPUT,
    `steps=${JSON.stringify(result.steps)}\npreviews=${result.previews}\n`);
}
