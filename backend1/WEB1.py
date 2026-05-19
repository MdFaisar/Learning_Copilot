from flask import Flask, render_template, request, redirect, url_for, session, flash
from pythomata import SimpleDFA
from graphviz import Source
import os
import time

app = Flask(__name__)
app.secret_key = "your-secret-key"  


users = {
    "admin": "password123"
}

def parse_dfa_input(form):
    alphabet = set(form['alphabet'].strip().split())
    states = set(form['states'].strip().split())
    initial_state = form['initial_state'].strip()   
    accepting_states = set(form['accepting_states'].strip().split())

    transition_text = form['transitions'].strip().splitlines()
    transition_function = {state: {} for state in states}

    for line in transition_text:
        parts = line.strip().split()
        if len(parts) != 3:
            raise ValueError(f"Invalid transition line: '{line}'")
        from_state, symbol, to_state = parts
        if from_state not in states or to_state not in states or symbol not in alphabet:
            raise ValueError(f"Invalid transition: {line}")
        transition_function[from_state][symbol] = to_state

    return SimpleDFA(states, alphabet, initial_state, accepting_states, transition_function)

def save_dfa_image(dfa, filename="static/dfa_diagram"):
    os.makedirs("static", exist_ok=True)
    minimized_trimmed = dfa.minimize().trim()
    graphviz_digraph = minimized_trimmed.to_graphviz()
    graph = Source(graphviz_digraph.source)
    return graph.render(filename=filename, format="png", cleanup=True)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users and users[username] == password:
            session["username"] = username
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out successfully", "info")
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def index():
    if "username" not in session:
        return redirect(url_for("login"))

    result = None
    word = ""
    error = ""
    image_path = None

    if request.method == "POST":
        try:
            dfa = parse_dfa_input(request.form)
            word = request.form.get("test_word", "")
            result = dfa.accepts(word)
            full_path = save_dfa_image(dfa)
            image_path = os.path.basename(full_path)
        except Exception as e:
            error = str(e)

    return render_template("index.html", result=result, word=word, error=error, image_path=image_path, timestamp=int(time.time()), username=session["username"])

if __name__ == "__main__":
    app.run(debug=True)
