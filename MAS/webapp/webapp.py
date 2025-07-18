from flask import Flask, render_template

class WebApplication:
    def __init__(self):
        self._app = Flask(__name__)
        
        self._app.add_url_rule("/", view_func=self.index)

    @staticmethod
    def index():
        return render_template("base.html")
    

    def run(self):
        self._app.run(debug=True)


if __name__ == "__main__":
    webapp = WebApplication()
    webapp.run()
