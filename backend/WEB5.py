from flask import Flask, render_template, request, redirect, url_for, session, flash
from pythomata.impl.simple import SimpleNFA
from pythomata import SimpleDFA
from graphviz import Source
import os
import time

app = Flask(__name__)
app.secret_key = "your-secret-key"
users = {"admin": "password123"}

def regex_to_nfa(regex):
    """
    Simple conversion from regex to NFA (supports only literal concatenation like 'abc')
    """
    states = set()
    transitions = {}
    alphabet = set(regex)
    initial_state = "q0"
    accepting_state = f"q{len(regex)}"

    for i in range(len(regex) + 1):
        states.add(f"q{i}")
        transitions[f"q{i}"] = {}

    for i, symbol in enumerate(regex):
        transitions[f"q{i}"].setdefault(symbol, set()).add(f"q{i+1}")

    return SimpleNFA(
        states,
        alphabet,
        initial_state,
        {accepting_state},
        transitions
    )

def nfa_to_dfa(nfa):
    """Manually convert a SimpleNFA to SimpleDFA using subset construction (supports basic NFAs without epsilon)."""
    from collections import deque

    alphabet = nfa.input_symbols - {'ε'}
    initial_set = frozenset([nfa.initial_state])
    queue = deque([initial_set])
    visited = set()
    dfa_states = set()
    dfa_transitions = {}
    dfa_accepting_states = set()
    state_names = {initial_set: "S0"}
    state_counter = 1

    while queue:
        current = queue.popleft()
        dfa_states.add(state_names[current])
        dfa_transitions[state_names[current]] = {}

        if current & nfa.accepting_states:
            dfa_accepting_states.add(state_names[current])

        for symbol in alphabet:
            next_state = set()
            for nfa_state in current:
                next_state |= nfa.get_successors(nfa_state, symbol)

            next_frozen = frozenset(next_state)
            if next_frozen not in state_names:
                state_names[next_frozen] = f"S{state_counter}"
                state_counter += 1
                queue.append(next_frozen)

            dfa_transitions[state_names[current]][symbol] = state_names[next_frozen]

    return SimpleDFA(
        dfa_states,
        alphabet,
        "S0",
        dfa_accepting_states,
        dfa_transitions
    )

def save_dfa_image(dfa, filename_prefix="static/dfa_diagram"):
    os.makedirs("static", exist_ok=True)
    timestamp = int(time.time())
    filename = f"{filename_prefix}_{timestamp}"

    graphviz_digraph = dfa.to_graphviz()
    graph = Source(graphviz_digraph.source)
    output_path = graph.render(filename=filename, format="png", cleanup=True)
    return output_path

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users and users[username] == password:
            session["username"] = username
            return redirect(url_for("regex_to_dfa"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out", "info")
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def regex_to_dfa():
    if "username" not in session:
        return redirect(url_for("login"))

    result = None
    error = ""
    image_path = None
    regex = ""
    test_string = ""
    lang_desc = ""

    if request.method == "POST":
        regex = request.form.get("regex", "")
        test_string = request.form.get("test_string", "")
        lang_desc = request.form.get("language_desc", "")

        try:
            nfa = regex_to_nfa(regex)
            dfa = nfa_to_dfa(nfa)
            result = dfa.accepts(test_string)
            full_path = save_dfa_image(dfa)
            image_path = os.path.basename(full_path)
        except Exception as e:
            error = str(e)

    return render_template("index5.html",
                           result=result,
                           regex=regex,
                           test_string=test_string,
                           language_desc=lang_desc,
                           image_path=image_path,
                           timestamp=int(time.time()),
                           username=session.get("username"),
                           error=error)

if __name__ == "__main__":
    app.run(debug=True)
