import sqlite3
from app import app

conn = sqlite3.connect('talentofutpay.db')
jugadora_id = conn.execute('SELECT id FROM jugadoras ORDER BY id LIMIT 1').fetchone()[0]
conn.close()

client = app.test_client()
client.post('/', data={'usuario': 'admin', 'clave': 'Proyecto2026.'}, follow_redirects=False)
client.post('/pagos', data={
    'jugadora_id': str(jugadora_id),
    'mes': 'Enero',
    'fecha': '2026-08-31',
    'valor': '50000',
    'estado': 'Pagado',
    'metodo_pago': 'Efectivo',
}, follow_redirects=False)

page = client.get('/pagos')
html = page.get_data(as_text=True)
print('debe_30000', 'Debe:' in html and '30000' in html)
assert 'Debe:' in html, html[:300]
assert '30000' in html, html[:300]
print('ALL_OK')
