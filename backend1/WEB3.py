from flask import Flask, render_template, request, redirect, url_for, session, flash
from pythomata.impl.simple import SimpleNFA
from graphviz import Source
import os
import time

app = Flask(__name__)
app.secret_key = "your-secret-key"

users = {
    "admin": "password123"
}

def parse_nfa_input(form):
    alphabet = set(form['alphabet'].strip().split())
    states = set(form['states'].strip().split())
    initial_state = form['initial_state'].strip()
    accepting_states = set(form['accepting_states'].strip().split())

    if initial_state not in states:
        raise ValueError("Initial state must be one of the states")
    if not accepting_states.issubset(states):
        raise ValueError("Accepting states must be subset of the states")

    transition_text = form['transitions'].strip().splitlines()
    transition_function = {state: {} for state in states}

    for line in transition_text:
        parts = line.strip().split()
        if len(parts) < 3:
            raise ValueError(f"Invalid transition line: '{line}'")
        from_state, symbol, *to_states = parts
        if from_state not in states or symbol not in alphabet:
            raise ValueError(f"Invalid from-state or symbol in: {line}")
        for target in to_states:
            if target not in states:
                raise ValueError(f"Invalid target state in: {line}")
        transition_function[from_state].setdefault(symbol, set()).update(to_states)

    return SimpleNFA(states, alphabet, initial_state, accepting_states, transition_function)

def accepts_nfa(nfa, word):
    current_states = {nfa.initial_state}
    for symbol in word:
        next_states = set()
        for state in current_states:
            next_states |= nfa.get_successors(state, symbol)
        current_states = next_states
        if not current_states:
            return False
    return bool(current_states & nfa.accepting_states)

def save_nfa_image(nfa, filename_prefix="static/nfa_diagram"):
    os.makedirs("static", exist_ok=True)

    # Add timestamp to filename to avoid conflicts
    timestamp = int(time.time())
    filename = f"{filename_prefix}_{timestamp}.gv"

    graphviz_digraph = nfa.to_graphviz()
    graph = Source(graphviz_digraph.source)

    output_path = graph.render(filename=filename, format="png", cleanup=True)
    return output_path  # e.g., static/nfa_diagram_1632131231.gv.png


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users and users[username] == password:
            session["username"] = username
            flash("Login successful!", "success")
            return redirect(url_for("nfa_index"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out successfully", "info")
    return redirect(url_for("login"))

@app.route("/nfa", methods=["GET", "POST"])
def nfa_index():
    if "username" not in session:
        return redirect(url_for("login"))

    result = None
    word = ""
    error = ""
    image_path = None

    if request.method == "POST":
        try:
            # Parse NFA from form
            nfa = parse_nfa_input(request.form)

            # Save image first (always)
            full_path = save_nfa_image(nfa)
            image_path = os.path.basename(full_path)

            # Then test the word
            word = request.form.get("test_word", "")
            result = accepts_nfa(nfa, word)

        except Exception as e:
            error = str(e)

    return render_template(
        "index3.html",
        result=result,
        word=word,
        error=error,
        image_path=image_path,
        timestamp=int(time.time()),
        username=session["username"]
    )


if __name__ == "__main__":
    app.run(debug=True)
