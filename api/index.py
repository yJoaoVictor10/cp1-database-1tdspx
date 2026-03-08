import os
import oracledb
from flask import Flask, jsonify, request

app = Flask(__name__)

def get_connection():
    return oracledb.connect(
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        dsn=os.environ["DB_DSN"]
    )


@app.route("/")
def listar_herois():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_heroi, nome, classe, hp_atual, hp_max, status
        FROM TB_HEROIS
        ORDER BY id_heroi
    """)

    herois = []

    for row in cursor:
        herois.append({
            "id": row[0],
            "nome": row[1],
            "classe": row[2],
            "hp_atual": row[3],
            "hp_max": row[4],
            "status": row[5]
        })

    cursor.close()
    conn.close()

    return jsonify(herois)


@app.route("/processar", methods=["POST"])
def proximo_turno():

    conn = get_connection()
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

    return jsonify({"mensagem": "Turno processado com sucesso!"})


# necessário para o Vercel
def handler(request):
    return app(request.environ, lambda status, headers: None)