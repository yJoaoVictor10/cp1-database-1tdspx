import oracledb
import json

def handler(request):

    try:

        conn = oracledb.connect(
            user="rm563409",
            password="160507",
            dsn="oracle.fiap.com.br:1521/orcl"
        )

        cursor = conn.cursor()

        dano_nevoa = 10

        cursor.execute("""
            SELECT id_heroi, hp_atual
            FROM TB_HEROIS
            WHERE status = 'ATIVO'
        """)

        herois = cursor.fetchall()

        atualizados = []

        for heroi in herois:

            id_heroi = heroi[0]
            hp_atual = heroi[1]

            novo_hp = hp_atual - dano_nevoa

            if novo_hp <= 0:

                cursor.execute("""
                    UPDATE TB_HEROIS
                    SET hp_atual = 0,
                        status = 'CAIDO'
                    WHERE id_heroi = :id
                """, {"id": id_heroi})

                status = "CAIDO"

            else:

                cursor.execute("""
                    UPDATE TB_HEROIS
                    SET hp_atual = :hp
                    WHERE id_heroi = :id
                """, {"hp": novo_hp, "id": id_heroi})

                status = "ATIVO"

            atualizados.append({
                "id": id_heroi,
                "novo_hp": max(novo_hp,0),
                "status": status
            })

        conn.commit()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "evento": "NEVOA_DANO",
                "herois_afetados": atualizados
            })
        }

    except Exception as e:

        return {
            "statusCode": 500,
            "body": str(e)
        }