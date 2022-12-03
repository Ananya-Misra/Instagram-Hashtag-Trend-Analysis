
# importing Flask and other modules
from flask import Flask, request, render_template

# Flask constructor
app = Flask(__name__)


# A decorator used to tell the application
# which URL is associated function
@app.route('/search', methods=["GET", "POST"])
def gfg():
    if request.method == "POST":
        # getting input with name = fname in HTML form
        user_name = request.form.get("uname")
        # getting input with name = lname in HTML form
        search_page = request.form.get("search")
        return "Your name is " + user_name + " and your searched page is "+search_page
    return render_template("search.html")


if __name__ == '__main__':
    app.run(debug=True)
