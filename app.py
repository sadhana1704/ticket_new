from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

tickets = []

agents = {
    "Billing Team": ["Alice", "Bob"],
    "Technical Team": ["Charlie", "David"],
    "Support Team": ["Eve", "Frank"]
}

def analyze_ticket(text):
    text = text.lower()

    score = 0

    if "payment" in text or "refund" in text:
        category = "Billing"
        score += 3
    elif "login" in text:
        category = "Account"
        score += 2
    elif "error" in text or "bug" in text:
        category = "Technical"
        score += 3
    else:
        category = "General"
        score += 1

    if "urgent" in text:
        score += 3

    if score >= 5:
        priority = "High"
        time = "1 hour"
    elif score >= 3:
        priority = "Medium"
        time = "4 hours"
    else:
        priority = "Low"
        time = "1 day"

    if category == "Billing":
        team = "Billing Team"
    elif category == "Technical":
        team = "Technical Team"
    else:
        team = "Support Team"

    return category, priority, team, time


def assign_agent(team):
    team_agents = agents[team]
    loads = {a: 0 for a in team_agents}

    for t in tickets:
        if t["assigned"] == team:
            loads[t["agent"]] += 1

    return min(loads, key=loads.get)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    ticket = request.form["ticket"]

    category, priority, team, time = analyze_ticket(ticket)
    agent = assign_agent(team)

    data = {
        "id": len(tickets),
        "issue": ticket,
        "category": category,
        "priority": priority,
        "assigned": team,
        "agent": agent,
        "time": time,
        "created": datetime.now().strftime("%H:%M:%S")
    }

    tickets.append(data)

    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", tickets=tickets)


@app.route("/ticket/<int:id>")
def ticket_detail(id):
    return render_template("ticket.html", ticket=tickets[id])


@app.route("/analytics")
def analytics():
    return render_template("analytics.html", tickets=tickets)


@app.route("/search", methods=["GET", "POST"])
def search():
    results = []
    if request.method == "POST":
        q = request.form["query"].lower()
        results = [t for t in tickets if q in t["issue"].lower()]
    return render_template("search.html", results=results)


@app.route("/agents")
def agent_page():
    return render_template("agents.html", agents=agents)


if __name__ == "__main__":
    app.run(debug=True)