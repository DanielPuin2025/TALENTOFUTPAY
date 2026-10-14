from app import app

client = app.test_client()

login = client.post('/', data={'usuario': 'admin', 'clave': 'admin123'}, follow_redirects=False)
assert login.status_code == 302

resp = client.post('/cambiar_perfil', data={'usuario': 'tesorero', 'clave': 'tesorero123'}, follow_redirects=False)
print('switch_status', resp.status_code, resp.location)
assert resp.status_code == 302
with client.session_transaction() as s:
    assert s['usuario'] == 'tesorero', s
    assert s['rol'] == 'tesorero', s

page = client.get('/recordatorios_pendientes')
html = page.get_data(as_text=True)
print('recordatorios_ok', 'class="boton"' in html, 'white-space: nowrap' in html)
assert 'class="boton"' in html, html[:200]
assert 'white-space: nowrap' in html, html[:400]
print('ALL_OK')
