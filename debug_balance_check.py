from app import app

client = app.test_client()
client.post('/', data={'usuario': 'admin', 'clave': 'Proyecto2026.'}, follow_redirects=False)
page = client.get('/pagos')
html = page.get_data(as_text=True)
print('Debe in html?', 'Debe:' in html)
idx = html.find('Debe')
print('idx', idx)
if idx != -1:
    print(html[max(0, idx-200): idx+400])
else:
    print(html[:1200])
