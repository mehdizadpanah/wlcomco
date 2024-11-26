from flask import Flask, render_template
from user_repository import get_all_users

app = Flask(__name__)

@app.route('/')
def list_users():
    users = get_all_users()
    return render_template('users.html', users=users)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
