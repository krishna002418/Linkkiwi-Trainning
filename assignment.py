from app1 import Flask

app=Flask(__name__)
#project data dictionary
names=[
   {"id":1,"name":"Krishna","age":25,"city":"Latur","voted":"Yes"},
   {"id":2,"name":"Dipak","age":30,"city":"Pune","voted":"Yes"},
   {"id":3,"name":"Kartik","age":28,"city":"Mumbai","voted":"No"},
   {"id":4,"name":"Mahesh","age":35,"city":"Nagpur","voted":"Yes"},
   {"id":5,"name":"Suresh","age":32,"city":"Chhatrapati Sambhaji Nagar","voted":"No"}
]
#Route for home page
@app.route('/')
def home():
   return'<h1>Online voting system</h1>' '<p>Welcome to the online voting system. Here you can find information about candidates and their voting status.</p>'

#Route for candidate records
@app.route('/Records')
def records():
   output='<h1>Candidate Records</h1>'
   for names in names:
      output+=f"<p>ID: {names['id']}, Name: {names['name']}, Age: {names['age']}, City: {names['city']}, Voted: {names['voted']}</p>"
   return output

#Route for candidate status
@app.route('/Status')
def Status():
   total_candidates=len(names)
   voted_candidates=sum(1 for names in names if names['voted']=='Yes')
   output=f'<h1>Candidate Status</h1><p>Total candidates: {total_candidates}</p><p>Voted candidates: {voted_candidates}</p>'
   return output

if __name__=='__main__':
 app.run(debug=True)