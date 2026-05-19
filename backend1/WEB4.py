from flask import Flask, render_template, request, redirect, url_for, session, flash
from pythomata.impl.simple import SimpleNFA
from graphviz import Source
import os
import time

app = Flask(__name__)
app.secret_key = "your-secret-key"

users = {"admin": "password123"}

def parse_nfa_input(form):
    alphabet = set(form['alphabet'].strip().split())
    states = set(form['states'].strip().split())
    initial_state = form['initial_state'].strip()
    accepting_states = set(form['accepting_states'].strip().split())

    epsilon = 'ε'
    alphabet.add(epsilon)

    transition_text = form['transitions'].strip().splitlines()
    transition_function = {state: {} for state in states}

    for line in transition_text:
        parts = line.strip().split()
        from_state, symbol, *to_states = parts

        if symbol.lower() in {'e', 'epsilon'}:
            symbol = epsilon

        if from_state not in states or not set(to_states).issubset(states):
            raise ValueError(f"Invalid transition: {line}")
        if symbol not in alphabet:
            raise ValueError(f"Symbol '{symbol}' not in alphabet")

        if symbol in transition_function[from_state]:
            transition_function[from_state][symbol].update(to_states)
        else:
            transition_function[from_state][symbol] = set(to_states)

    return SimpleNFA(states, alphabet, initial_state, accepting_states, transition_function)

def epsilon_closure(nfa, state_set):
    epsilon = 'ε'
    closure = set(state_set)
    stack = list(state_set)
    closure_steps = []

    while stack:
        state = stack.pop()
        for next_state in nfa.get_successors(state, epsilon):
            if next_state not in closure:
                closure.add(next_state)
                stack.append(next_state)
                closure_steps.append((state, next_state))  # Track steps
    return closure, closure_steps

def accepts_nfa_with_epsilon(nfa, word):
    epsilon = 'ε'
    current_states, steps = epsilon_closure(nfa, {nfa.initial_state})
    all_steps = [("start", s) for s in current_states]
    
    for symbol in word:
        next_states = set()
        for state in current_states:
            next_states |= nfa.get_successors(state, symbol)
        
        # Now take epsilon closure of next_states
        current_states, epsilon_steps = epsilon_closure(nfa, next_states)
        steps.extend(epsilon_steps)
    
    accepted = bool(current_states & nfa.accepting_states)
    return accepted, steps


def save_nfa_image(nfa, closure_steps, filename_prefix="static/nfa_diagram"):
    os.makedirs("static", exist_ok=True)
    timestamp = int(time.time())
    filename = f"{filename_prefix}_{timestamp}.gv"

    graphviz_digraph = nfa.to_graphviz()
    dot = graphviz_digraph.source

    # Highlight closure transitions in red
    for from_state, to_state in closure_steps:
        dot = dot.replace(f'{from_state} -> {to_state} [label="ε"]',
                          f'{from_state} -> {to_state} [label="ε", color=red, fontcolor=red]')

    graph = Source(dot)
    output_path = graph.render(filename=filename, format="png", cleanup=True)
    return output_path

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users and users[username] == password:
            session["username"] = username
            return redirect(url_for("nfa_index"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out", "info")
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
            nfa = parse_nfa_input(request.form)
            word = request.form.get("test_word", "")

            result, closure_steps = accepts_nfa_with_epsilon(nfa, word)
            full_path = save_nfa_image(nfa, closure_steps)
            image_path = os.path.basename(full_path)

        except Exception as e:
            error = str(e)

    return render_template(
        "index4.html",
        result=result,
        word=word,
        error=error,
        image_path=image_path,
        timestamp=int(time.time()),
        username=session.get("username")
    )

if __name__ == "__main__":
    app.run(debug=True)
