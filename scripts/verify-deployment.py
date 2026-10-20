"""Full HTTP acceptance suite; uses only this project's authorized .env."""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

base = sys.argv[1].rstrip('/')
settings = dict(line.split('=', 1) for line in
                (Path(__file__).resolve().parents[1] / '.env').read_text().splitlines()
                if line and not line.startswith('#'))
passed = 0
created = []
admin_token = None


def request(path, method='GET', data=None, token=None):
    headers = {}
    if data is not None:
        headers['Content-Type'] = 'application/json'
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(base + path, method=method, headers=headers,
                                 data=json.dumps(data).encode() if data is not None else None)
    try:
        response = urllib.request.urlopen(req, timeout=20)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        raw = response.read()
        try:
            payload = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            payload = raw.decode(errors='replace')
        return response.status, payload


def check(condition, label):
    global passed
    if not condition:
        raise AssertionError(label)
    passed += 1
    print(f'PASS {label}')


try:
    check(request('/')[0] == 200, 'public page')
    check(request('/admin')[0] == 200, 'admin page SPA route')
    check(request('/health') == (200, {'status': 'healthy'}), 'healthy API')
    check(request('/api/admin/questions')[0] == 401, 'anonymous inbox access denied')
    check(request('/api/admin/login', 'POST', {'username': 'admin', 'password': 'wrong'})[0] == 401,
          'incorrect password rejected')
    status, login = request('/api/admin/login', 'POST', {
        'username': settings['ADMIN_USERNAME'], 'password': settings['ADMIN_PASSWORD']})
    check(status == 200 and bool(login.get('access_token')), 'administrator login')
    admin_token = login['access_token']
    check(request('/api/admin/verify', 'POST', token=admin_token)[0] == 200, 'administrator token valid')
    status, message = request('/api/questions', 'POST', {'content': '部署验收留言（自动清理）', 'sender_name': '  测试访客  ', 'images': []})
    check(status == 200 and bool(message.get('question_id')), 'anonymous submission')
    question_id = message['question_id']
    created.append(question_id)
    check(request(f'/api/questions/{question_id}')[0] == 401, 'anonymous single-message access denied')
    check(request('/api/questions/batch', 'POST', [question_id])[0] == 401, 'anonymous batch access denied')
    check(request('/api/questions/batch', 'POST', [question_id], message['access_token'])[0] == 401,
          'sender token cannot read private messages')
    status, inbox = request('/api/admin/questions', token=admin_token)
    check(status == 200 and any(q['id'] == question_id for q in inbox), 'administrator can read submitted message')
    check(next(q for q in inbox if q['id'] == question_id)['sender_name'] == '测试访客', 'optional sender name stored and trimmed')
    status, answered = request(f'/api/admin/questions/{question_id}/answer', 'POST',
                              {'answer_content': '私密验收备注', 'is_public': True}, admin_token)
    check(status == 200 and answered['is_public'] is False, 'answer cannot publish message')
    status, updated = request(f'/api/admin/questions/{question_id}', 'PUT', {'is_public': True}, admin_token)
    check(status == 200 and updated['is_public'] is False, 'visibility update cannot publish message')
    check(request('/api/public/questions') == (200, []), 'public list always empty')
    check(request('/api/questions/revoke', 'POST', {'token': message['access_token']})[0] == 400,
          'processed message cannot be revoked')
    if base.startswith('http://127.0.0.1'):
        for data in [{'content': '   '}, {'content': 'x' * 5001}, {'content': 'hi', 'images': ['/uploads/a.png']}, {'content': 'hi', 'sender_name': 'x' * 41}]:
            check(request('/api/questions', 'POST', data)[0] == 422, 'invalid submission rejected')
    status, revocable = request('/api/questions', 'POST', {'content': '撤回验收（自动清理）'})
    check(status == 200, 'second anonymous submission')
    created.append(revocable['question_id'])
    status, anonymous = request('/api/questions/' + revocable['question_id'], token=admin_token)
    check(status == 200 and anonymous['sender_name'] is None, 'blank sender defaults to anonymous')
    check(request('/api/questions/revoke', 'POST', {'token': revocable['access_token']})[0] == 200,
          'unprocessed message can be revoked')
    created.remove(revocable['question_id'])
    check(request('/uploads/example.png')[0] == 403, 'public attachment access disabled')
    check(request('/api/upload', 'POST', {})[0] == 403, 'uploads disabled')
    if base.startswith('http://127.0.0.1'):
        for index in range(101):
            status, fixture = request('/api/questions', 'POST', {'content': f'历史分页验收 {index}（自动清理）'})
            if status != 200:
                raise RuntimeError('Pagination fixture creation failed')
            created.append(fixture['question_id'])
        visible_ids = set()
        for skip in range(0, 1000000, 100):
            status, page = request(f'/api/admin/questions?skip={skip}&limit=100', token=admin_token)
            if status != 200:
                raise RuntimeError('Administrator pagination request failed')
            visible_ids.update(q['id'] for q in page)
            if len(page) < 100:
                break
        check(set(created).issubset(visible_ids), 'messages beyond newest 100 accessible through pagination')
    print(f'{passed} acceptance checks passed for {base}')
finally:
    if admin_token:
        for question_id in created:
            status, _ = request(f'/api/admin/questions/{question_id}', 'DELETE', token=admin_token)
            if status not in (200, 404):
                raise RuntimeError('Acceptance message cleanup failed')
