from app import app


def test_cambiar_perfil_allows_switching_accounts():
    client = app.test_client()

    response = client.post(
        "/cambiar_perfil",
        data={"usuario": "tesorero", "clave": "tesorero123"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session["usuario"] == "tesorero"
        assert session["rol"] == "tesorero"


def test_recordatorios_vistas_con_boton_estable():
    client = app.test_client()
    client.post("/", data={"usuario": "admin", "clave": "admin123"}, follow_redirects=False)

    response = client.get("/recordatorios_pendientes")
    html = response.get_data(as_text=True)

    assert 'class="boton"' in html
    assert "white-space: nowrap" in html
