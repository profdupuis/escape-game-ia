
from flask import Flask, render_template, request, redirect, url_for, session
import openai
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET", "POST"])
def accueil():
    if request.method == "POST":
        session["nom"] = request.form["nom"]
        session["prenom"] = request.form["prenom"]
        session["etape"] = 0
        session["score"] = 0
        return redirect(url_for("jeu"))
    return render_template("accueil.html")

@app.route("/jeu", methods=["GET", "POST"])
def jeu():
    reponse_ia = ""
    etape = session.get("etape", 0)
    questions = [
        "Explique ce qu’est la plasticité cérébrale.",
        "Donne un exemple concret de plasticité cérébrale.",
        "Quels sont les mécanismes biologiques impliqués ?"
    ]

    if request.method == "POST":
        question = questions[etape]
        user_input = request.form["reponse"]
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Tu es un professeur de SVT bienveillant qui évalue des réponses d'élèves."},
                    {"role": "user", "content": f"Question : {question}\nRéponse de l'élève : {user_input}\nÉvalue si la réponse est correcte ou non."}
                ]
            )
            reponse_ia = completion["choices"][0]["message"]["content"]
            if "correcte" in reponse_ia.lower() or "bonne réponse" in reponse_ia.lower():
                session["score"] += 1
            session["etape"] += 1
            if session["etape"] >= len(questions):
                return redirect(url_for("resultat"))
        except Exception as e:
            reponse_ia = f"Erreur lors de l'appel à l'API OpenAI : {e}"

    question = questions[etape] if etape < len(questions) else ""
    return render_template("jeu.html", question=question, reponse_ia=reponse_ia)

@app.route("/resultat")
def resultat():
    score = session.get("score", 0)
    nom = session.get("nom", "")
    prenom = session.get("prenom", "")
    return render_template("resultat.html", nom=nom, prenom=prenom, score=score)
