"""Reproducible planning audit; never runs product acceptance or changes inputs."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import argparse
import difflib
import hashlib
import json
import re
import shutil

ROOT = Path('E:/aaa-project/rag')
PLAN = ROOT / '_bmad-output/planning-artifacts'
OUT = PLAN / 'ir-sp-review-2026-10-16'
CE = PLAN / 'ce-review-2026-10-16'


def stamp():
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')


def info(path):
    data = path.read_bytes()
    return {'path': path.as_posix(), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest(),
            'lines': len(data.decode('utf-8-sig').splitlines())}


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def freeze():
    assert not (OUT / 'input-manifest.json').exists(), 'Refusing to overwrite audit baseline'
    entries = json.loads((CE / 'current-manifest.json').read_text(encoding='utf-8'))
    paths = [Path(item['path']) for item in entries]
    paths += [CE / 'acceptance-allocation.md', CE / 'review-record.md']
    snapshots = []
    for path in paths:
        target = OUT / 'baseline' / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        snapshots.append({**info(path), 'snapshot': target.as_posix()})
    save('input-manifest.json', {'frozen_at': stamp(), 'artifacts': snapshots,
                                'runtime_tests': 'not-executed'})
    print(json.dumps({'frozen_artifacts': len(snapshots), 'runtime_tests': 'not-executed'}))


def check():
    manifest = json.loads((OUT / 'input-manifest.json').read_text(encoding='utf-8'))
    integrity = []
    changes = []
    for item in manifest['artifacts']:
        path, old = Path(item['path']), Path(item['snapshot'])
        assert info(old)['sha256'] == item['sha256'], f'Baseline changed: {old}'
        current = info(path)
        integrity.append({**current, 'unchanged': current['sha256'] == item['sha256']})
        if current['sha256'] != item['sha256']:
            changes.extend(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),
                           path.read_text(encoding='utf-8-sig').splitlines(True),
                           fromfile=item['snapshot'], tofile=item['path']))
    (OUT / 'changes.diff').write_text(''.join(changes), encoding='utf-8')
    text = (PLAN / 'epics.md').read_text(encoding='utf-8-sig')
    matches = list(re.finditer(r'^### Story (\d+\.\d+)[：:]([^\n]*)', text, re.M))
    stories = {}
    for n, match in enumerate(matches):
        body = text[match.end():matches[n + 1].start() if n + 1 < len(matches) else len(text)]
        deps = re.search(r'\*\*依赖：\*\*(.*?)。\*\*来源：\*\*', body)
        dep_text = deps[1] if deps else ''
        positive = dep_text.split('不依赖', 1)[0]
        stories[match[1]] = {'title': match[2].strip(),
                            'line': text[:match.start()].count('\n') + 1,
                            'preconditions': dep_text,
                            'dependencies': re.findall(r'(?<![\d.])\d+\.\d+(?![\d.])', positive),
                            'gwt_count': len(re.findall(r'^- \*\*Given\*\*', body, re.M))}
    missing = [(sid, d) for sid, s in stories.items() for d in s['dependencies'] if d not in stories]
    def ancestors(sid, trail=()):
        if sid in trail:
            raise ValueError('Dependency cycle: ' + ' -> '.join((*trail, sid)))
        result = set()
        for dep in stories[sid]['dependencies']:
            if dep in stories:
                result.add(dep)
                result |= ancestors(dep, (*trail, sid))
        return result
    closure = {sid: sorted(ancestors(sid)) for sid in stories}
    forward = [(sid, d) for sid, s in stories.items() for d in s['dependencies']
               if tuple(map(int, d.split('.'))) >= tuple(map(int, sid.split('.')))]
    allocation = (CE / 'acceptance-allocation.md').read_text(encoding='utf-8-sig')
    checks = {
        'nine_epics': len(re.findall(r'^## Epic \d+[：:]', text, re.M)) == 9,
        'forty_two_stories': len(stories) == 42,
        'no_missing_dependencies': not missing,
        'no_forward_dependencies': not forward,
        'all_original_23_ac_groups_allocated': set(re.findall(r'\| AC-(\d{2})-', allocation)) == {f'{i:02}' for i in range(1, 24)},
        's2_doc_no_budget_or_mix': '2.5' in closure['4.1'] and not {'2.3', '2.6'} & set(closure['4.1']),
        'doc_gate_no_budget': '2.3' not in closure['2.5'],
        'mix_gate_has_doc_and_budget': {'2.3', '2.5'} <= set(closure['2.6']),
        's3_has_budget_and_mix': {'2.3', '2.6'} <= set(closure['5.1']),
        's0_no_p0_or_s7': not any(d.startswith(('2.', '9.')) for d in closure['1.5']),
        's1_no_p0': not any(d.startswith('2.') for d in closure['3.7']),
        'f0_independent': not stories['9.1']['dependencies'],
        'source_before_resource_view': '4.3' not in closure['4.2'],
        'manual_structure_before_answer': '7.2' not in closure['7.1'],
        'deployment_prep_before_recovery': '8.4' not in closure['8.3'],
    }
    files = [PLAN / 'epics.md', CE / 'acceptance-allocation.md', CE / 'story-traceability.md']
    files += list(OUT.glob('*.md'))
    implementation = ROOT / '_bmad-output/implementation-artifacts'
    if implementation.exists():
        files += list(implementation.glob('*.md'))
    issues, links = [], 0
    for path in files:
        body = path.read_text(encoding='utf-8-sig')
        for match in re.finditer(r'\]\((/[^)]+)\)', body):
            links += 1
            location = re.fullmatch(r'(.+?)(?::(\d+))?', match[1].split('#', 1)[0])
            target = Path(location[1].lstrip('/'))
            if not target.exists():
                issues.append({'source': path.as_posix(), 'target': match[1], 'problem': 'missing'})
            elif location[2] and not 1 <= int(location[2]) <= len(target.read_text(encoding='utf-8-sig').splitlines()):
                issues.append({'source': path.as_posix(), 'target': match[1], 'problem': 'line-out-of-range'})
        if re.search(r'^<{7}|^={7}|^>{7}', body, re.M):
            issues.append({'source': path.as_posix(), 'problem': 'conflict marker'})
    checks['local_links_valid'] = not issues
    save('story-dependencies.json', {'stories': stories, 'closure': closure, 'missing': missing,
                                    'forward': forward, 'runtime_tests': 'not-executed'})
    save('document-checks.json', {'checked_at': stamp(), 'checks': checks,
         'failed': [name for name, passed in checks.items() if not passed],
         'input_integrity': integrity, 'baseline_integrity': True,
         'local_links_checked': links, 'issues': issues,
         'gwt_count': sum(s['gwt_count'] for s in stories.values()),
         'scope': 'document structure and explicit dependencies; semantic adjudication in review-record.md',
         'runtime_tests': 'not-executed'})
    print(json.dumps({'checks': len(checks), 'failed': [k for k,v in checks.items() if not v],
                      'local_links_checked': links, 'issues': issues, 'stories': len(stories),
                      'changed_inputs': [i['path'] for i in integrity if not i['unchanged']]}, ensure_ascii=False))


def runtime():
    """Initialize, never advance or reset, runtime evidence tracking after IR PASS."""
    import yaml
    assert re.search(r'^gate: PASS$', (PLAN / 'implementation-readiness.md').read_text(encoding='utf-8'), re.M)
    destination = ROOT / '_bmad-output/implementation-artifacts/runtime-acceptance-status.yaml'
    assert not destination.exists(), 'Refusing to reset existing runtime evidence'
    allocation = CE / 'acceptance-allocation.md'
    cases = []
    for number, line in enumerate(allocation.read_text(encoding='utf-8').splitlines(), 1):
        if line.startswith('| AC-'):
            _, ident, theme, responsibility, _ = line.split('|')
            cases.append({'id': ident.strip(), 'responsibility': responsibility.strip(),
                          'source': f'[验收分派](/{allocation.as_posix()}:{number})',
                          'execution_status': 'not-executed', 'evidence': []})
    gates = [
        ('S0', ['1.1', '1.2', '1.3', '1.4', '1.5'], '任何真实外发前，含P0/接入验证'),
        ('P0-LIMITS', ['2.1'], '每个真实用途/动作的首次调用前核定实际限制及合法凭据/样例'),
        ('P0-FORMAT-SOURCE-EMBEDDING', ['2.2'], 'S2按对应格式/来源/embedding子门逐项消费；不是五格式整体假通过'),
        ('P0-BUDGET', ['2.3'], 'S3非零生成及实际完整预算前；不反向阻S2文档档位'),
        ('P0-VISION', ['2.4'], 'S5真正图意与整期完成前'),
        ('P0-DOC-1', ['2.5'], 'S2启用1档前，独立于DOC-4和生成预算/MIX'),
        ('P0-DOC-4', ['2.5'], 'S2启用4档前；未证4档不开4档'),
        ('P0-MIX-1', ['2.6'], '实际1档查询/生成与文档并存组合开放前'),
        ('P0-MIX-4', ['2.6'], '实际4档查询/生成与文档并存组合开放前'),
        ('R01-S0', ['1.3', '1.4', '1.5'], '任何真实外发前；旧包恢复8.4再验，不后移首验'),
        ('R02-S1', ['3.1', '3.7'], 'S1身份入口开放前'),
        ('R03-S1-FACILITY', ['3.2', '3.7'], 'S1设施入口开放前，真实浏览器负例'),
        ('R03-S2-RESOURCE', ['4.3'], 'S2资源/原件/页图/提取/citation入口开放前'),
        ('R03-S3-HISTORY', ['5.4'], 'S3答案/重放/历史/operation入口开放前'),
        ('R03-S4-COMPARISON', ['6.2'], '新增比较入口开放前复验，不能只引用S1成绩'),
        ('R04-S2', ['4.3'], 'S2资源入口开放前完整安全媒体正反例'),
        ('S1', ['3.7'], 'S1全部到期子例汇总通过后开放身份/业务写入口'),
        ('S2', ['4.5'], 'S2全部到期子例及已用DOC/格式/来源/embedding通过后进入S3'),
        ('S3', ['5.6'], 'S3全部到期子例、预算及实际MIX组合证据齐备'),
        ('S4', ['6.2'], '排障与比较完整场景开发检查'),
        ('S5', ['7.2'], 'SC-4表格/OCR/真正图意，不以平均分替代'),
        ('S6-TARGET-4C4GB', ['8.3'], '上线前目标机DOC/MIX实际档位补证，不以开发机替代'),
        ('S6-TRUSTED-RECOVERY', ['8.4'], '上线前T1–T6、同包两次新epoch及第一轮凭据失效'),
        ('F0', ['9.1'], '任何首次调优前；无代码/S6前置'),
        ('S7-SM-1-7', ['9.4'], '整期完成前按原32题/金标/全部SM及独立权限分母验收'),
    ]
    data = {'project': 'RAG_all', 'initialized_at': stamp(),
            'planning_gate': 'PASS', 'implementation_started': False,
            'runtime_acceptance': 'not-executed',
            'status_semantics': 'not-executed=尚未运行，无运行结论；不是failed，也不是已核凭据缺失blocked。证据齐备后逐子门更新，不从故事/文档PASS推定。',
            'consumption_rule': 'DOC/MIX的1/4档分别消费；一条Story整体backlog不得覆盖已经取得的真实子门证据，也不得凭backlog以外的规划状态假通过。本次全部未执行。',
            'gates': [{'id': ident, 'responsible_stories': owners, 'earliest_gate': earliest,
                       'execution_status': 'not-executed', 'evidence': []} for ident, owners, earliest in gates],
            'acceptance_subcase_groups': cases}
    assert len(cases) == 45
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=110), encoding='utf-8')
    reloaded = yaml.safe_load(destination.read_text(encoding='utf-8'))
    assert all(row['execution_status'] == 'not-executed' and not row['evidence']
               for row in reloaded['gates'] + reloaded['acceptance_subcase_groups'])
    save('runtime-status-validation.json', {'valid': True, 'gate_entries': len(gates),
        'subcase_groups': len(cases), 'all_not_executed': True, 'evidence_fabricated': False,
        'status_file': destination.as_posix(), 'runtime_tests': 'not-executed'})
    print(json.dumps({'initialized_runtime_gates': len(gates), 'allocated_subcase_groups': len(cases),
                      'all_not_executed': True, 'status_file': destination.as_posix()}, ensure_ascii=False))


def finalize():
    import yaml
    previous_ir = OUT / 'baseline/_bmad-output/planning-artifacts/implementation-readiness.md'
    old_link = f'/{(PLAN / "implementation-readiness.md").as_posix()}:'
    frozen_link = f'/{previous_ir.as_posix()}:'
    for stem in ('review-acceptance-p0', 'review-dependencies-repairs'):
        source = OUT / (stem + '.original.md')
        original = source.read_text(encoding='utf-8')
        prefix = ('> 主John阅读版说明：原报告意见和结论保持不变；仅将已被本轮裁决替代的旧CA IR链接迁到审时baseline。'
                  f'完整原样文本见[原报告](/{source.as_posix()}:1)。\n\n')
        (OUT / (stem + '.md')).write_text(prefix + original.replace(old_link, frozen_link), encoding='utf-8')
    manifest_path = OUT / 'final-manifest.json'
    # Link validation needs the final manifest's target to exist; the complete manifest is written last.
    if not manifest_path.exists():
        save('final-manifest.json', {'status': 'assembling'})
    save('completion-checks.json', {'status': 'assembling'})
    check()
    documents = json.loads((OUT / 'document-checks.json').read_text(encoding='utf-8'))
    integrity = documents['input_integrity']
    changed = [item['path'] for item in integrity if not item['unchanged']]
    assert changed == [(PLAN / 'implementation-readiness.md').as_posix()], changed
    assert not documents['failed'], documents['failed']
    assert (PLAN / 'implementation-readiness.md').read_bytes() == (OUT / 'implementation-readiness.md').read_bytes()
    implementation = ROOT / '_bmad-output/implementation-artifacts'
    sprint_path = implementation / 'sprint-status.yaml'
    sprint = yaml.safe_load(sprint_path.read_text(encoding='utf-8'))
    status = sprint['development_status']
    epics = {key: value for key, value in status.items() if re.fullmatch(r'epic-\d+', key)}
    stories = {key: value for key, value in status.items() if re.match(r'^\d+-\d+-', key)}
    retros = {key: value for key, value in status.items() if re.fullmatch(r'epic-\d+-retrospective', key)}
    runtime_data = yaml.safe_load((implementation / 'runtime-acceptance-status.yaml').read_text(encoding='utf-8'))
    runtime_rows = runtime_data['gates'] + runtime_data['acceptance_subcase_groups']
    validate = json.loads((OUT / 'sprint-validate.json').read_text(encoding='utf-8'))
    sync = json.loads((OUT / 'sprint-sync-check.json').read_text(encoding='utf-8'))
    assert len(epics) == 9 and len(stories) == 42 and len(retros) == 9
    assert set(epics.values()) == set(stories.values()) == {'backlog'}
    assert set(retros.values()) == {'optional'}
    assert len(runtime_data['gates']) == 25 and len(runtime_data['acceptance_subcase_groups']) == 45
    assert all(row['execution_status'] == 'not-executed' and not row['evidence'] for row in runtime_rows)
    assert validate['valid'] and not validate['problems']
    assert sync['in_sync'] and not sync['changed'] and not sync['new_entries'] and not sync['dropped_orphans']
    completion = {'status': 'complete', 'completed_at': stamp(), 'planning_gate': 'PASS',
                  'independent_final_reports_received': 2, 'material_findings': 0,
                  'baseline_artifacts': len(integrity), 'baseline_integrity': documents['baseline_integrity'],
                  'changed_preexisting_inputs': changed, 'unchanged_other_input_artifacts': 16,
                  'ce_final_three_unchanged': True, 'authoritative_ir_matches_saved_verdict': True,
                  'epics_backlog': len(epics), 'stories_backlog': len(stories), 'retrospectives_optional': len(retros),
                  'runtime_gate_groups_not_executed': 25, 'acceptance_subcase_groups_not_executed': 45,
                  'sprint_valid': True, 'sprint_in_sync': True,
                  'accepted_parser_note': 'Epic List at epics.md:136 is a summary heading, not a tenth epic; all 9/42 parsed',
                  'static_checks_passed': len(documents['checks']), 'local_links_checked': documents['local_links_checked'],
                  'product_runtime_tests': 'not-executed'}
    save('completion-checks.json', completion)
    files = [path for path in OUT.iterdir() if path.is_file() and path != manifest_path]
    files += [PLAN / 'implementation-readiness.md', PLAN / 'epics.md',
              CE / 'acceptance-allocation.md', CE / 'story-traceability.md']
    files += [path for path in implementation.iterdir() if path.is_file()]
    save('final-manifest.json', {'status': 'final', 'finalized_at': stamp(), 'review_started': '2026-10-16',
          'planning_gate': 'PASS', 'artifacts': [info(path) for path in sorted(files)],
          'baseline_manifest': (OUT / 'input-manifest.json').as_posix(),
          'runtime_tests': 'not-executed', 'manifest_excludes_itself': True,
          'excluded_temporary_paths': ['.runtime/', '__pycache__/']})
    final = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert all(info(Path(item['path']))['sha256'] == item['sha256'] for item in final['artifacts'])
    print(json.dumps(completion, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['freeze', 'check', 'runtime', 'finalize'])
    args = parser.parse_args()
    {'freeze': freeze, 'check': check, 'runtime': runtime, 'finalize': finalize}[args.action]()
