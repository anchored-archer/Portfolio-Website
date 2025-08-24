from flask import Flask, render_template, send_file
import data
import blog_handeler
import multiprocessing
app = Flask(__name__)

# Pages
@app.route("/")
@app.route("/index.html")
def render_homepage():
    return render_template('index.html')

@app.route("/projects.html")
def render_projects():
    return render_template('projects.html')

@app.route("/contact.html")
def render_contact_page():
    return render_template("contact.html")

@app.route("/blog.html")
def render_blog():
    blogs = data.retrive()
    print(blogs)
    return render_template("blog.html", blogs=blogs)

# JS & CSS
@app.route("/styles.css")
def serve_css():
    return send_file("static/styles.css")

@app.route("/project-script.js")
def serve_js():
    return send_file("static/project-script.js")

# API: To be Implemeneted 
# @app.route("/api/get-blog-summary")
# def serve_summary():
#     ...

if __name__ == "__main__":
    update_proc = multiprocessing.Process(target=blog_handeler.run, daemon=True)
    update_proc.start()
    app.run(debug=False)
