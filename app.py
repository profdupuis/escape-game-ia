from flask import Flask, render_template, request, redirect, url_for, session
import openai
import os
import csv
from datetime import datetime

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
        session["validation"] = False
        return redirect(url_for("jeu"))
    return render_template("accueil.html")

@app.route("/jeu", methods=["GET", "POST"])
def jeu():
    reponse_ia = ""
    etape = session.get("etape", 0)
    validation = session.get("validation", False)
    questions = [
        "Explique ce qu’est la plasticité cérébrale.",
        "Donne un exemple concret de plasticité cérébrale.",
        "Quels sont les mécanismes biologiques impliqués ?"
    ]

    if request.method == "POST":
        if validation:
            session["etape"] += 1
            session["validation"] = False
            return redirect(url_for("jeu"))
        else:
            question = questions[etape]
            user_input = request.form["reponse"]
            try:
                completion = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Tu es un chercheur travaillant dans un centre de recherche en neurosciences. L'élève tente de réactiver un système de sécurité en répondant à trois questions sur la plasticité cérébrale. Tu dois évaluer chaque réponse avec bienveillance. Si, et seulement si, la réponse est correcte, utilise le mot 'correct' ou 'bonne réponse'. Sinon, donne un simple indice ou une piste très succincte. Ne donne jamais la bonne réponse ni un énoncé complet qui pourrait être considére comme une bonne réponse. }
                        {"role": "user", "content": f"Étape {etape+1} sur 3\nQuestion : {question}\nRéponse de l'élève : {user_input}"}
                    ]
                )
                reponse_ia = completion["choices"][0]["message"]["content"]
                if "correct" in reponse_ia.lower() or "bonne réponse" in reponse_ia.lower():
                    session["score"] += 1
                    session["validation"] = True
            except Exception as e:
                reponse_ia = f"Erreur lors de l'appel à l'API OpenAI : {e}"

            session["reponse_ia"] = reponse_ia

    if session.get("etape", 0) >= len(questions):
        return redirect(url_for("resultat"))

    question = questions[etape]
    reponse_ia = session.get("reponse_ia", "") if validation else reponse_ia
    return render_template("jeu.html", question=question, reponse_ia=reponse_ia, validation=validation)

@app.route("/resultat")
def resultat():
    score = session.get("score", 0)
    nom = session.get("nom", "")
    prenom = session.get("prenom", "")
    date_jeu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ligne = [prenom, nom, score, date_jeu]
    with open("scores.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(ligne)
    return render_template("resultat.html", nom=nom, prenom=prenom, score=score)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
