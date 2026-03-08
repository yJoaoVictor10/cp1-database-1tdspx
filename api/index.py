import os
import oracledb
from flask import Flask, jsonify, request

app = Flask(__name__)


# ==========================
# CONEXÃO COM O BANCO
# ==========================
def get_connection():
    try:
        user = os.environ.get("DB_USER")
        password = os.environ.get("DB_PASSWORD")
        dsn = os.environ.get("DB_DSN")

        if not user or not password or not dsn:
            raise Exception("Variáveis de ambiente DB_USER, DB_PASSWORD ou DB_DSN não configuradas")

        conn = oracledb.connect(
            user=user,
            password=password,
            dsn=dsn
        )

        return conn

    except Exception as e:
        raise Exception(f"Erro ao conectar no Oracle: {str(e)}")


# ==========================
# LISTAR HERÓIS
# ==========================
@app.route("/", methods=["GET"])
def listar_herois():

    try:
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

        return jsonify({
            "status": "ok",
            "herois": herois
        })

    except Exception as e:

        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500


# ==========================
# PROCESSAR PRÓXIMO TURNO
# ==========================
@app.route("/processar", methods=["POST"])
def processar_turno():

    try:

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

        return jsonify({
            "status": "ok",
            "mensagem": "Turno processado com sucesso"
        })

    except Exception as e:

        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500


# ==========================
# ROTA DE TESTE
# ==========================
@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "online",
        "mensagem": "API RPG funcionando"
    })


# ==========================
# HANDLER PARA VERCEL
# ==========================
def handler(request):
    return app(request.environ, lambda status, headers: None)