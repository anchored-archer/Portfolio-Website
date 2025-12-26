from flask import Flask, render_template, send_file, send_from_directory
import data


app = Flask(__name__)

# # Start the debugger
# if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
#     debugpy.listen(("0.0.0.0", 5678))
#     print("Debugger is listening on port 5678. Waiting for client to attach...")
#     debugpy.wait_for_client()

# Pages
@app.route("/")
@app.route("/index.html")
def render_homepage():
    return render_template('index.html')

@app.route("/work.html")
def render_projects():
    return render_template('work.html')

@app.route("/blog.html")
def render_blog():
    blogs = data.retrive()
    return render_template("blog.html", blogs=blogs)

# JS & CSS
@app.route("/style.css")
def serve_css():
    return send_file("static/style.css")

@app.route("/script.js")
def serve_js():
    return send_file("static/script.js")

@app.route("/images/<path:filename>")
def serve_image_from_folder(filename):
    return send_from_directory("static/images", filename)

@app.route('/blog/<title>')
def blog_post(title):
    blog_title = title.replace("-", " ")
    blog = data.retrieve_single_blog(blog_title)
    if blog:
        return render_template('blog-view.html', blog=blog)
    else:
        return "Post not found", 404

def create_app():
    app = Flask(__name__)
    # routes here
    return app
