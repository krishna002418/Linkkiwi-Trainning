from flask import Flask

app=Flask(__name__)

@app.route('/')
def home():
    return '<h1>welcome to my Project</h1>'
@app.route('/about')
def about():
   return'<h1> This is about page</h1>'
@app.route('/contact')
def contact():
   return'<h1> This is contact page</h1>'

if __name__=='__main__':
 app.run(debug=True)


