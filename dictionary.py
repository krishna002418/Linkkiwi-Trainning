from flask import Flask

app=Flask(__name__)
#project data dictionary
candidate=[
   {"name":"Krishna","age":25,"city":"Latur"},
   {"name":"Dipak","age":30,"city":"Pune"},
   {"name":"Kartik","age":28,"city":"Mumbai"},
   {"name":"Mahesh","age":35,"city":"Nagpur"}
]
@app.route('/')
def home():
  #create using HTML
   html='<h1>Online voting system - Candidates</h1>'
   html+='<ul>'
   for c in candidate:
      html+=f"<li>{c['name']} - Age: {c['age']}, City: {c['city']}</li>"
   html+='</ul>'
   return html
@app.route('/about')
def about():
   return'<h1> This is Online voting system</h1>'
@app.route('/contact')
def contact():
   return'<h1> All candidates votes show here</h1>'

if __name__=='__main__':
 app.run(debug=True)