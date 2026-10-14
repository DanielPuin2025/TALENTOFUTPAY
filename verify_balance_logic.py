from pathlib import Path

app_text = Path('app.py').read_text(encoding='utf-8')
template_text = Path('templates/pagos.html').read_text(encoding='utf-8')

assert 'calcular_saldo_pendiente' in app_text
assert '80000 - float(valor_pago or 0)' in app_text
assert 'Debe:' in template_text
assert 'Math.max(0, 80000 - pago)' in template_text
assert '30.000' in template_text or '30000' in template_text
print('BALANCE_LOGIC_OK')
