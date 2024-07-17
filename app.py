from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

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
    draw.text((500, 2000), "Contact", font=contact_font, fill='#6565D6')
    draw.text((500, 2200), phone, font=details_font, fill='#33221B')
    draw.text((500, 2300), email, font=details_font, fill='#33221B')

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
        profile_pic = profile_pic.resize((1400, 1400))
        mask = Image.new('L', profile_pic.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 1400, 1400), fill=255)
        card.paste(profile_pic, (1450, 742), mask)

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
        encoded_img_data = base64.b64encode(img_io.getvalue()).decode('utf-8')

        return redirect(url_for('result', img_data=encoded_img_data))

    return render_template('index.html')

@app.route('/result')
def result():
    img_data = request.args.get('img_data')
    if not img_data:
        flash('No image data found. Please generate a card first.')
        return redirect(url_for('index'))
    return render_template('result.html', img_data=img_data)

@app.route('/download')
def download():
    img_data = request.args.get('img_data')
    if not img_data:
        flash('No image data found. Please generate a card first.')
        return redirect(url_for('index'))
    img_bytes = base64.b64decode(img_data)
    return send_file(io.BytesIO(img_bytes), mimetype='image/png', as_attachment=True, download_name='business_card.png')

if __name__ == '__main__':
    app.run(debug=True)
