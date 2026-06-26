import smtplib
import csv
import time
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# --- CONFIGURATION ---
MON_EMAIL = "melina.barbieux@gmail.com"
MON_MDP = "xbjqszxwdlwmoakm"
DESTINATAIRE = "etienne.ferrandi@hotmail.fr"

def envoyer_alerte(annonce):
    msg = MIMEMultipart()
    
    # --- SUJET SANS L'HEURE ---
    sujet = "🏠 Alerte | Nouvelle Offre | ToulonFindAI"
    msg['Subject'] = Header(sujet, 'utf-8')
    msg['From'] = f"ToulonFindAI <{MON_EMAIL}>"
    msg['To'] = DESTINATAIRE

    # --- DESIGN PREMIUM (CENTRAGE OPTIQUE) ---
    html = f"""
    <html>
    <body style="background-color: #f5f4f0; margin: 0; padding: 40px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0">
            <tr>
                <td align="center">
                    <table width="450" border="0" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); border: 1px solid #e2e1dd;">
                        <tr>
                            <td style="padding: 40px; text-align: center;">
                                
                                <div style="font-size: 14px; font-weight: bold; color: #1a1a1a; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 5px;">🏠 ToulonFindAI</div>
                                <div style="font-size: 10px; color: #8e8c87; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 30px;">Real Estate Observatory</div>
                                
                                <div style="background-color: #faf9f6; border-radius: 12px; padding: 25px; border: 1px solid #f0eee9; margin-bottom: 30px; text-align: center;">
                                    <div style="font-size: 18px; font-weight: bold; color: #1a1a1a; margin-bottom: 10px; line-height: 1.2;">{annonce.get('titre')}</div>
                                    
                                    <div style="font-size: 14px; color: #8e8c87; margin-bottom: 12px; display: block; width: 100%;">
                                        <span style="margin-left: -20px;">📍</span> {annonce.get('ville')}
                                    </div>
                                    
                                    <div style="font-size: 18px; font-weight: 600; color: #1a1a1a;">{annonce.get('prix')} €</div>
                                </div>

                                <a href="{annonce.get('url')}" style="background-color: #1a1a1a; color: #ffffff; padding: 15px 35px; text-decoration: none; border-radius: 12px; font-weight: bold; font-size: 14px; display: inline-block;">Découvrir le bien</a>
                                
                                <div style="margin-top: 40px; font-size: 10px; color: #a3a19d; border-top: 1px solid #f0eee9; padding-top: 20px; line-height: 1.5;">
                                    PROJET MASTER • EPITECH DIGITAL<br>
                                    Intelligence Artificielle appliquée à l'Immobilier
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    msg.attach(MIMEText(html, 'html', 'utf-8'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MON_EMAIL, MON_MDP)
        server.sendmail(MON_EMAIL, DESTINATAIRE, msg.as_string())
        server.quit()
        print(f"✅ Mail unique envoyé : {sujet}")
    except Exception as e:
        print(f"❌ Erreur : {e}")

def executer_test():
    csv_filename = "annonces_merged.csv"
    if not os.path.exists(csv_filename):
        print("❌ CSV absent")
        return
    
    with open(csv_filename, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        annonces = list(reader)
    
    if annonces:
        row = annonces[0]
        data = {
            "titre": row.get("title", row.get("titre", "Annonce")),
            "prix": row.get("price", row.get("prix", "N/C")),
            "ville": row.get("city", row.get("ville", "Toulon")),
            "url": row.get("url", "https://www.bienici.com")
        }
        envoyer_alerte(data)
    else:
        print("⚠️ Le fichier CSV est vide.")

if __name__ == "__main__":
    executer_test()