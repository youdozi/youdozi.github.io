#!/usr/bin/env python3
"""Run both documented Querydsl files and the Specification comparison twice."""
from pathlib import Path
import os,re,shutil,subprocess,sys,tempfile
from xml.etree import ElementTree as ET
from check_querydsl_example import extract as extract_setup

EXTRA = {
    'src/main/java/example/EmployeeRepository.java',
    'src/main/java/example/EmployeeSpecs.java',
    'src/test/java/example/QueryStrategyTest.java',
}
SCENARIOS = {
    'exactEqualityPreservesDuplicates','missingValueReturnsNoRows',
    'wildcardCharactersAreLiteralForEquality','andCanEliminateAllRows',
    'orKeepsMatchesAndDuplicatesInOrder','nullRequiresAnExplicitPredicate',
    'stringAttributeTypoFailsAtRuntime','equalityHelpersRejectNull',
}


def extract(language):
    text=Path(f'src/content/posts/{language}/2023-09-05-querydsl-no-release.md').read_text()
    blocks=re.findall(r'^### `([^`]+)`\n\n```java\n([\s\S]*?)\n```',text,re.M)
    files=dict(blocks)
    if set(files)!=EXTRA or len(files)!=len(EXTRA):
        raise ValueError(f'{language}: expected the three complete comparison files')
    return {**extract_setup(language),**files}


def main():
    if not shutil.which('gradle'):raise SystemExit('Gradle8.4 and JDK17 required')
    english,korean=extract('en'),extract('ko')
    if english!=korean:raise SystemExit('Paired query-strategy project files differ')
    env=os.environ.copy()
    if sys.platform=='darwin':
        env['JAVA_HOME']=subprocess.check_output(['/usr/libexec/java_home','-v','17'],text=True).strip()
    version=subprocess.check_output(['gradle','--version'],env=env,text=True,timeout=30)
    gradle=re.search(r'^Gradle (\S+)',version,re.M);jvm=re.search(r'^JVM:\s+(\S+)',version,re.M)
    if not gradle or gradle.group(1)!='8.4' or not jvm or not jvm.group(1).startswith('17.'):
        raise SystemExit('Use Gradle8.4 running on JDK17 for this reproduction')
    print(f'[environment] Gradle {gradle.group(1)}; JVM {jvm.group(1)}.',flush=True)
    with tempfile.TemporaryDirectory(prefix='youdozi-query-strategy-') as directory:
        root=Path(directory)
        for name,code in english.items():
            path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(code+'\n')
        for iteration in [1,2]:
            subprocess.run(['gradle','-p',directory,'--no-daemon','clean','test'],env=env,check=True,timeout=240)
            for path in ['build/generated/sources/annotationProcessor/java/main/example/QEmployee.java','build/classes/java/main/example/QEmployee.class']:
                if not (root/path).is_file():raise SystemExit('Missing generated Q source or compiled class')
            if list((root/'src').rglob('QEmployee.*')):raise SystemExit('Generated Q types leaked into source')
            suites=[ET.parse(p).getroot() for p in (root/'build/test-results/test').glob('TEST-*.xml')]
            counts={s.get('name'):int(s.get('tests','0')) for s in suites}
            if counts!={'example.EmployeeQueryTest':2,'example.QueryStrategyTest':8}:
                raise SystemExit(f'Unexpected test suite coverage: {counts}')
            if any(int(s.get(key,'0')) for s in suites for key in ['failures','errors','skipped']):
                raise SystemExit('A comparison test failed or was skipped')
            names={t.get('name').removesuffix('()') for s in suites if s.get('name')=='example.QueryStrategyTest' for t in s.findall('testcase')}
            if names!=SCENARIOS:raise SystemExit(f'Missing required comparison scenarios: {names}')
            print(f'[ok] Clean run {iteration}: five setup files + three comparison files; 2 baseline + 8 contract tests passed; QEmployee regenerated.',flush=True)


if __name__=='__main__':main()
