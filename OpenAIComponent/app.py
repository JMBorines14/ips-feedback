import os

import openai
import sys
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/summarize", methods=("GET", "POST"))
def summarize():
    if request.method == "POST":
        #essay = request.form["essay"]
        essay = request.args.get("essay")
        if essay == None:
            essay = request.form["essay"]
        response = openai.Completion.create(
            model="text-davinci-002",
            max_tokens=100,
            prompt=summarize_prompt(essay),
            temperature=0.6,
        )
        return response
        #return redirect(url_for("summarize", result=response.choices[0].text))

    result = request.args.get("result")
    return render_template("summarizer.html", result=result)

@app.route("/codecheck", methods=("GET", "POST"))
def codecheck():
    if request.method == "POST":
        code = request.args.get("code")
        if code == None:
            code = request.form["code"]
        response = openai.Completion.create(
            model="text-davinci-002",
            max_tokens=500,
            prompt=codecheck_prompt(code),
            temperature=0.6,
        )
        return response

    result = request.args.get("result")
    return render_template("codechecker.html", result=result)


def summarize_prompt(text):
    return """Summarize the following essay to a 5th grader reading level: {}""".format(
        text.capitalize()
    )

def codecheck_prompt(code):
    return """Describe the function of the following code and determing any errors or inefficies: {}""".format(
        code.capitalize()
    )

