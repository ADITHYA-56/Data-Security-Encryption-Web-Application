from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from cryptography.fernet import Fernet
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # For flash messages

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

key = Fernet.generate_key()
cipher = Fernet(key)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt_page():
    if request.method == 'POST':
        # Check if user uploaded a file
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            
            with open(file_path, 'rb') as f:
                encrypted_data = cipher.encrypt(f.read())
            
            encrypted_file_path = os.path.join(UPLOAD_FOLDER, f"encrypted_{file.filename}")
            with open(encrypted_file_path, 'wb') as f:
                f.write(encrypted_data)
            
            flash("File encrypted successfully!", "success")
            return send_file(encrypted_file_path, as_attachment=True)

        # Encrypt text
        text = request.form.get('text')
        if text:
            encrypted_text = cipher.encrypt(text.encode()).decode()
            return render_template('encrypt.html', encrypted=encrypted_text, key=key.decode())
    
    return render_template('encrypt.html')

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt_page():
    if request.method == 'POST':
        # File decryption
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            
            try:
                with open(file_path, 'rb') as f:
                    decrypted_data = cipher.decrypt(f.read())
                
                decrypted_file_path = os.path.join(UPLOAD_FOLDER, f"decrypted_{file.filename}")
                with open(decrypted_file_path, 'wb') as f:
                    f.write(decrypted_data)
                
                flash("File decrypted successfully!", "success")
                return send_file(decrypted_file_path, as_attachment=True)
            except:
                flash("Invalid file or encryption key!", "danger")

        # Text decryption
        encrypted_text = request.form.get('encrypted_text')
        try:
            decrypted_text = cipher.decrypt(encrypted_text.encode()).decode()
            return render_template('decrypt.html', decrypted=decrypted_text)
        except:
            flash("Invalid encrypted text or key!", "danger")

    return render_template('decrypt.html')

if __name__ == '__main__':
    app.run(debug=True)
