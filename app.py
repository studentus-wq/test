from flask import Flask, request
import zipfile, os
import smtplib
from email.message import EmailMessage
import cloudinary
import cloudinary.uploader

app = Flask(name)

cloudinary.config(
  cloud_name = os.environ['CLOUD_NAME'],
  api_key = os.environ['API_KEY'],
  api_secret = os.environ['API_SECRET']
)

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist("images")
    
    if len(files) > 5:
        return "Max 5 images allowed"

    zip_name = "client.zip"
    with zipfile.ZipFile(zip_name, 'w') as z:
        for f in files:
            if f.content_length > 10*1024*1024:
                return "File too big"
            f.save(f.filename)
            z.write(f.filename)
            cloudinary.uploader.upload(f.filename, folder="clients")
            os.remove(f.filename)

    msg = EmailMessage()
    msg['Subject'] = 'New Client Upload'
    msg['From'] = os.environ['GMAIL_USER']
    msg['To'] = os.environ['GMAIL_USER']
    msg.set_content("Client uploaded 5 images")

    with open(zip_name, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='zip', filename=zip_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(os.environ['GMAIL_USER'], os.environ['GMAIL_PASS'])
        smtp.send_message(msg)

    os.remove(zip_name)
    return "Done"

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
