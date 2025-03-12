import streamlit as st
import json
import os

# Stel inloggegevens in
USERNAME = "admin"
PASSWORD = "1234"

# Pad naar het JSON-bestand
DATA_FILE = "data.json"

# Functie om gegevens uit het JSON-bestand te laden
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {"prijs_per_maaltijd": 0.0, "tikkie_link": "", "inschrijvingen": []}

# Functie om gegevens op te slaan in het JSON-bestand
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)

# Laad gegevens uit het bestand
data = load_data()

if 'prijs_per_maaltijd' not in st.session_state:
    st.session_state.prijs_per_maaltijd = data.get("prijs_per_maaltijd", 0.0)

if 'tikkie_link' not in st.session_state:
    st.session_state.tikkie_link = data.get("tikkie_link", "")

if 'inschrijvingen' not in st.session_state:
    st.session_state.inschrijvingen = data.get("inschrijvingen", [])

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Functie om te controleren of de gebruiker is ingelogd
def check_login(username, password):
    return username == USERNAME and password == PASSWORD

# Functie voor de inlogpagina
def login_page():
    st.title("Inloggen")

    username = st.text_input("Gebruikersnaam")
    password = st.text_input("Wachtwoord", type="password")

    if st.button("Inloggen"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.success("Inloggen succesvol!")
        else:
            st.error("Onjuiste gebruikersnaam of wachtwoord!")

# Functie voor de hoofdapp
def main_app():
    st.title("VEGAN FRIDAY")

    # 👉 Altijd tonen van het hoofdmenu (niet automatisch doorsturen naar beheerderspagina)
    page = st.sidebar.selectbox('Kies een pagina', ['Inschrijven', 'Lijst van Inschrijvingen', 'Beheerders'])

    # Inschrijven pagina
    if page == 'Inschrijven':
        st.header('Inschrijf Formulier')

        with st.form(key='my_form'):
            naam = st.text_input('Wat is je naam?')
            aantal = st.number_input('Met hoeveel mensen eet je mee?', min_value=0, max_value=20)

            totaal_prijs = st.session_state.prijs_per_maaltijd * aantal
            st.write(f"Te betalen: {totaal_prijs} EUR")

            feedback = st.text_area('Opmerking')
            betaling_keuze = st.radio("Hoe wil je betalen?", ("Tikkie", "Contant"))

            if betaling_keuze == "Tikkie":
                if st.session_state.tikkie_link:
                    st.write(f"Betalingslink: [Betaal hier]({st.session_state.tikkie_link})")
                    betaald = st.checkbox("Ik heb betaald via Tikkie")
                else:
                    st.warning("De beheerder heeft nog geen Tikkie-link ingevoerd.")
                    betaald = False
            else:
                betaald = True

            if st.form_submit_button('Verstuur'):
                if betaald or betaling_keuze == "Contant":
                    inschrijving = {
                        'Naam': naam,
                        'Aantal mensen': aantal,
                        'Opmerking': feedback,
                        'Betaald': 'Contant' if betaling_keuze == 'Contant' else ('Ja' if betaald else 'Nee'),
                        'Prijs': totaal_prijs
                    }
                    st.session_state.inschrijvingen.append(inschrijving)
                    save_data({
                        "prijs_per_maaltijd": st.session_state.prijs_per_maaltijd,
                        "tikkie_link": st.session_state.tikkie_link,
                        "inschrijvingen": st.session_state.inschrijvingen
                    })
                    st.success('Je hebt je succesvol ingeschreven!')
                else:
                    st.warning("Je moet eerst betalen om je in te schrijven!")

    # Lijst van inschrijvingen pagina
    elif page == 'Lijst van Inschrijvingen':
        st.header('Lijst van Ingeschreven Gebruikers')

        if len(st.session_state.inschrijvingen) == 0:
            st.write('Er zijn nog geen inschrijvingen.')
        else:
            # Totaal aantal mensen berekenen
            totaal_aantal_mensen = sum([inschrijving['Aantal mensen'] for inschrijving in st.session_state.inschrijvingen])

            # Toon het totaal aantal mensen
            st.write(f"Totaal aantal mensen ingeschreven: {totaal_aantal_mensen}")

            # Maak de HTML-tabel voor de inschrijvingen
            html = "<table style='width:100%; border-collapse: collapse;'>"
            html += "<tr style='border-bottom: 2px solid black;'>"
            html += "<th style='padding: 8px; text-align: left;'>Naam</th>"
            html += "<th style='padding: 8px; text-align: left;'>Aantal mensen</th>"
            html += "</tr>"

            # Voeg elke inschrijving toe aan de tabel
            for inschrijving in st.session_state.inschrijvingen:
                html += "<tr style='border-bottom: 1px solid black;'>"
                html += f"<td style='padding: 8px;'>{inschrijving['Naam']}</td>"
                html += f"<td style='padding: 8px;'>{inschrijving['Aantal mensen']}</td>"
                html += "</tr>"

            html += "</table>"

            # Toon de HTML-tabel in Streamlit
            st.markdown(html, unsafe_allow_html=True)

    # Beheerderspagina (alleen toegankelijk na inloggen)
    elif page == 'Beheerders':
        if not st.session_state.logged_in:
            login_page()
        else:
            st.header("Beheerders Pagina")
            st.write("Welkom, je hebt toegang tot de beheerderspagina!")

            # Tikkie-link invoeren
            tikkie_link = st.text_input("Voer de Tikkie betalingslink in:", value=st.session_state.tikkie_link)
            if st.button("Opslaan Tikkie-link"):
                st.session_state.tikkie_link = tikkie_link
                save_data({
                    "prijs_per_maaltijd": st.session_state.prijs_per_maaltijd,
                    "tikkie_link": tikkie_link,
                    "inschrijvingen": st.session_state.inschrijvingen
                })
                st.success("Tikkie-link is opgeslagen.")

            # Prijs per maaltijd invoeren
            prijs_per_maaltijd = st.number_input("Stel de prijs per maaltijd in (EUR):", min_value=0.0, step=0.5, value=st.session_state.prijs_per_maaltijd)
            if prijs_per_maaltijd != st.session_state.prijs_per_maaltijd:
                st.session_state.prijs_per_maaltijd = prijs_per_maaltijd
                save_data({
                    "prijs_per_maaltijd": prijs_per_maaltijd,
                    "tikkie_link": st.session_state.tikkie_link,
                    "inschrijvingen": st.session_state.inschrijvingen
                })
                st.success(f"De prijs per maaltijd is ingesteld op {prijs_per_maaltijd} EUR.")

            # Overzicht van inschrijvingen met betalingsstatus en prijs
            st.subheader("Overzicht van Inschrijvingen met Betalingsstatus")
            if len(st.session_state.inschrijvingen) == 0:
                st.write("Er zijn geen inschrijvingen.")
            else:
                # Totaal aantal mensen berekenen
                totaal_aantal_mensen = sum([inschrijving['Aantal mensen'] for inschrijving in st.session_state.inschrijvingen])

                # Toon het totaal aantal mensen
                st.write(f"Totaal aantal mensen ingeschreven: {totaal_aantal_mensen}")

                # Maak de HTML-tabel voor de beheerderspagina
                html = "<table style='width:100%; border-collapse: collapse;'>"
                html += "<tr style='border-bottom: 2px solid black;'>"
                html += "<th style='padding: 8px; text-align: left;'>Naam</th>"
                html += "<th style='padding: 8px; text-align: left;'>Aantal mensen</th>"
                html += "<th style='padding: 8px; text-align: left;'>Opmerking</th>"
                html += "<th style='padding: 8px; text-align: left;'>Betaald</th>"
                html += "<th style='padding: 8px; text-align: left;'>Prijs</th>"
                html += "</tr>"

                for inschrijving in st.session_state.inschrijvingen:
                    html += "<tr style='border-bottom: 1px solid black;'>"
                    html += f"<td style='padding: 8px;'>{inschrijving['Naam']}</td>"
                    html += f"<td style='padding: 8px;'>{inschrijving['Aantal mensen']}</td>"
                    html += f"<td style='padding: 8px;'>{inschrijving['Opmerking']}</td>"
                    html += f"<td style='padding: 8px;'>{inschrijving['Betaald']}</td>"
                    html += f"<td style='padding: 8px;'>{inschrijving['Prijs']} EUR</td>"
                    html += "</tr>"

                html += "</table>"

                # Toon de HTML-tabel in Streamlit
                st.markdown(html, unsafe_allow_html=True)

            # Verwijderknop
            if st.button("Verwijder alle inschrijvingen"):
                st.session_state.inschrijvingen = []
                save_data({
                    "prijs_per_maaltijd": st.session_state.prijs_per_maaltijd,
                    "tikkie_link": st.session_state.tikkie_link,
                    "inschrijvingen": st.session_state.inschrijvingen
                })
                st.success("Alle inschrijvingen zijn verwijderd!")

# Start de app (controleer loginstatus NIET bij het starten)
main_app()

