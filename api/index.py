from flask import Flask, render_template, request, send_file, redirect, url_for
from PIL import Image, ImageDraw, ImageFont,ImageOps
import io
import base64
import os
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

TEMP_DIR = 'temp/'

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def create_card(name, title, email, phone, logo=None, profile_pic=None):
    # Load the background image
    background = Image.open('static/background.png')
    card = background.copy()
    draw = ImageDraw.Draw(card)

    # Load fonts
    name_font = ImageFont.truetype("static/font/Poppins-Bold.ttf", 220)
    title_font = ImageFont.truetype("static/font/Poppins-Regular.ttf", 100)
    details_font = ImageFont.truetype("static/font/Poppins-Regular.ttf", 60)
    contact_font = ImageFont.truetype("static/font/Poppins-Bold.ttf", 100)

    # Add text
    draw.text((150, 1300), name, font=name_font, fill='#33221B')
    draw.text((150, 1600), title, font=title_font, fill='#33221B')
    draw.text((500, 2000), "Contact", font=contact_font, fill='#6565D6')  # Moved down and right
    draw.text((500, 2200), phone, font=details_font, fill='#33221B')  # Moved down and right
    draw.text((500, 2300), email, font=details_font, fill='#33221B')  # Moved down and right

    # Add logo if provided
    if logo:
        logo = Image.open(logo).convert("RGBA")
        logo = logo.resize((1000, 1000), Image.Resampling.LANCZOS)
        datas = logo.getdata()
        newData = []
        for item in datas:
            if item[0] > 220 and item[1] > 220 and item[2] > 220:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        logo.putdata(newData)
        card.paste(logo, (130, 530), logo)


    # Add profile picture if provided
    if profile_pic:
        profile_pic = Image.open(profile_pic)
        profile_pic = profile_pic.resize((1400, 1400))  # Resize based on radius
        mask = Image.new('L', profile_pic.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 1400, 1400), fill=255)  # Draw mask with circle
        card.paste(profile_pic, (1450, 742), mask)  # Adjust based on center coordinates and radius

    return card

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        title = request.form['title']
        email = request.form['email']
        phone = request.form['phone']
        logo = request.files['logo'] if 'logo' in request.files else None
        profile_pic = request.files['profile_pic'] if 'profile_pic' in request.files else None

        card = create_card(name, title, email, phone, logo, profile_pic)
        
        img_io = io.BytesIO()
        card.save(img_io, 'PNG')
        img_io.seek(0)
        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(TEMP_DIR, filename)

        with open(filepath, 'wb') as f:
            f.write(img_io.getvalue())

        return redirect(url_for('result', filename=filename))

    return render_template('index.html')

@app.route('/result')
def result():
    filename = request.args.get('filename')
    return render_template('result.html', filename=filename)

@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.join(TEMP_DIR, filename)
    return send_file(filepath, mimetype='image/png', as_attachment=True, download_name='business_card.png')

if __name__ == '__main__':
    app.run(debug=True)
