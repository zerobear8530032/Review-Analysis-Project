from flask import Flask
from pyngrok import ngrok
app= Flask(__name__)
ngrok.set_auth_token("2ocsOkAtir0rfQIM3f6cdYVQNfZ_3MVnEmcdLzhSETy5yu7gW")
public_url=ngrok.connect(5000).public_url
print(public_url)
@app.route("/")
def home():
    return "home "
print("click here to access",public_url)
app.run(port=5000)
