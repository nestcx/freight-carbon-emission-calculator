from flask import Flask, render_template


def create_app():
  app = Flask(__name__, instance_relative_config=True)

  @app.route("/")
  def main():
    return render_template("main.html")
  
  return app

