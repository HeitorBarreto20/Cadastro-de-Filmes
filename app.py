
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "catalogo.db")

def conectar_banco():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    return conexao

def criar_banco():
    conexao = conectar_banco()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS filmes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            genero TEXT NOT NULL,
            ano INTEGER NOT NULL,
            nota REAL NOT NULL CHECK (nota >= 1 AND nota <= 10)
        )
    """)

    conexao.commit()
    conexao.close()

@app.route("/")
def index():
    conexao = conectar_banco()

    filmes = conexao.execute(
        "SELECT * FROM filmes ORDER BY id DESC"
    ).fetchall()

    conexao.close()

    return render_template("index.html", filmes=filmes)

@app.route("/novo", methods=["GET", "POST"])
def novo_filme():
    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        genero = request.form["genero"].strip()
        ano = request.form["ano"]
        nota = request.form["nota"]

        try:
            ano = int(ano)
            nota = float(nota)

            if not titulo or not genero or not 1 <= nota <= 10:
                raise ValueError

            conexao = conectar_banco()

            conexao.execute(
                """INSERT INTO filmes (titulo, genero, ano, nota)
                   VALUES (?, ?, ?, ?)""",
                (titulo, genero, ano, nota)
            )

            conexao.commit()
            conexao.close()

            return redirect(url_for("index"))

        except ValueError:
            return "Dados inválidos. Verifique o ano e a nota.", 400

    return render_template("form.html", filme=None)

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_filme(id):
    conexao = conectar_banco()

    filme = conexao.execute(
        "SELECT * FROM filmes WHERE id = ?", (id,)
    ).fetchone()

    conexao.close()

    if filme is None:
        return "Filme não encontrado.", 404

    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        genero = request.form["genero"].strip()
        ano = request.form["ano"]
        nota = request.form["nota"]

        try:
            ano = int(ano)
            nota = float(nota)

            if not titulo or not genero or not 1 <= nota <= 10:
                raise ValueError

            conexao = conectar_banco()

            conexao.execute(
                """UPDATE filmes
                   SET titulo = ?, genero = ?, ano = ?, nota = ?
                   WHERE id = ?""",
                (titulo, genero, ano, nota, id)
            )

            conexao.commit()
            conexao.close()

            return redirect(url_for("index"))

        except ValueError:
            return "Dados inválidos. Verifique o ano e a nota.", 400

    return render_template("form.html", filme=filme)

@app.route("/excluir/<int:id>", methods=["POST"])
def excluir_filme(id):
    conexao = conectar_banco()

    conexao.execute(
        "DELETE FROM filmes WHERE id = ?", (id,)
    )

    conexao.commit()
    conexao.close()

    return redirect(url_for("index"))

criar_banco()

if __name__ == "__main__":
    app.run(debug=True)
