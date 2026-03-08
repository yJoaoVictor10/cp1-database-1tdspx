import oracledb


def conectar():
    return oracledb.connect(
        user="rm563409",
        password="160507",
        dsn="oracle.fiap.com.br:1521/orcl"
    )


def listar_herois():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_heroi, nome, classe, hp_atual, hp_max, status
        FROM TB_HEROIS
        ORDER BY id_heroi
    """)

    dados = cursor.fetchall()

    cursor.close()
    conn.close()

    return dados


def processar_turno():

    conn = conectar()
    cursor = conn.cursor()

    plsql = """
    DECLARE

        v_dano_nevoa NUMBER := 10;
        v_novo_hp NUMBER;

        CURSOR c_herois IS
            SELECT id_heroi, hp_atual
            FROM TB_HEROIS
            WHERE status = 'ATIVO';

    BEGIN

        FOR heroi IN c_herois LOOP

            v_novo_hp := heroi.hp_atual - v_dano_nevoa;

            UPDATE TB_HEROIS
            SET hp_atual = v_novo_hp
            WHERE id_heroi = heroi.id_heroi;

            IF v_novo_hp <= 0 THEN

                UPDATE TB_HEROIS
                SET status = 'CAIDO',
                    hp_atual = 0
                WHERE id_heroi = heroi.id_heroi;

            END IF;

        END LOOP;

        COMMIT;

    END;
    """

    cursor.execute(plsql)

    cursor.close()
    conn.close()


def handler(request):

    try:

        action = None

        if hasattr(request, "args"):
            action = request.args.get("action")

        if action == "turno":
            processar_turno()

        herois = listar_herois()

        html = """
        <html>
        <head>
        <title>SQLgard RPG Engine</title>
        </head>
        <body>

        <h1>⚔️ SQLgard - Estado dos Heróis</h1>
        """

        for h in herois:

            html += f"""
            <p>
            <b>{h[1]}</b> ({h[2]})<br>
            HP: {h[3]} / {h[4]}<br>
            Status: {h[5]}
            </p>
            """

        html += """
        <a href="/?action=turno">
        <button>Próximo Turno</button>
        </a>

        </body>
        </html>
        """

        return html

    except Exception as e:

        return f"""
        <h2>Erro na aplicação</h2>
        <pre>{str(e)}</pre>
        """