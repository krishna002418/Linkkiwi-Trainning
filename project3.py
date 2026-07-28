from app1 import Flask, render_template

app = Flask(__name__)

candi=[
    {'Id':1,'name':'Krishna','votes':0,'party':'BJP','city':'Latur'},
      {'Id':2,'name':'Rahul','votes':0,'party':'TMC','city':'Pune'},
      {'Id':3,'name':'Satyam','votes':0,'party':'Congress','city':'Mumbai'},
      {'Id':4,'name':'Kartik','votes':0,'party':'BJP','city':'Thane'},
      {'Id':5,'name':'Satyarth','votes':0,'party':'Shiv Sena','city':'Nashik'},
]
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/candidates")
def candidates():
    return render_template("candidates.html", candidates=candi)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)


