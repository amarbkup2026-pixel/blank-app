import os
import streamlit as st
from google import genai

# Configuration de la page
st.set_page_config(page_title="Assistant E&I Engineering", layout="wide")

st.title("⚡ Assistant IA - Ingénierie Instrumentation & Électricité")
st.markdown("Outil d'aide à la conception et aux calculs E&I propulsé par Gemini.")

# Initialisation du client Gemini (clé gratuite depuis Google AI Studio)
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.warning("Veuillez configurer votre clé API Gemini (GEMINI_API_KEY).")
else:
    client = genai.Client(api_key=api_key)

    # Menu latéral pour choisir le module
    module = st.sidebar.selectbox(
        "Module E&I",
        [
            "Assistant Technique & Normes",
            "Génération de Fiche Technique (Instrument)",
            "Dimensionnement de Câble / Chute de tension",
        ],
    )

    if module == "Assistant Technique & Normes":
        st.subheader("Consultation Normes (ISA / IEC / NEC)")
        user_query = st.text_area(
            "Posez votre question technique (ex: Exigences SIL pour une vanne de sécurité...)"
        )
        if st.button("Interroger l'IA"):
            if user_query:
                with st.spinner("Analyse en cours..."):
                    prompt = (
                        "Tu es un ingénieur senior expert en instrumentation et électricité industrielle. "
                        "Réponds de manière technique, précise et sécuritaire en citant les normes applicables.\n\n"
                        f"Question : {user_query}"
                    )
                    response = client.models.generate_content(
                        model="gemini-2.5-flash", contents=prompt
                    )
                    st.markdown("### Réponse de l'expert :")
                    st.write(response.text)
            else:
                st.error("Veuillez entrer une question.")

    elif module == "Génération de Fiche Technique (Instrument)":
        st.subheader("Générateur de Datasheet Instrument")
        col1, col2 = st.columns(2)
        with col1:
            fluid = st.text_input("Type de fluide", "Eau")
            pressure = st.number_input("Pression de service (bar)", value=10.0)
        with col2:
            temp = st.number_input("Température (°C)", value=25.0)
            inst_type = st.selectbox(
                "Type d'instrument",
                ["Débitmètre électromagnétique", "Transmetteur de pression", "Vanne de régulation"],
            )

        if st.button("Générer la spécification"):
            with st.spinner("Génération de la fiche technique..."):
                prompt = (
                    f"Génère une fiche technique (datasheet) au format structuré pour un {inst_type} "
                    f"soumis aux conditions suivantes : Fluide={fluid}, Pression={pressure} bar, Température={temp} °C. "
                    "Inclus les caractéristiques de raccordement, les matériaux recommandés et les signaux de sortie (ex: 4-20mA HART)."
                )
                response = client.models.generate_content(
                    model="gemini-2.5-flash", contents=prompt
                )
                st.markdown(response.text)

    elif module == "Dimensionnement de Câble / Chute de tension":
        st.subheader("Aide au Calcul de Chute de Tension")
        current = st.number_input("Courant nominal (A)", value=15.0)
        length = st.number_input("Longueur du câble (m)", value=50.0)
        voltage = st.number_input("Tension système (V)", value=400.0)

        if st.button("Analyser la configuration"):
            with st.spinner("Calcul et recommandations..."):
                prompt = (
                    f"Agis en tant qu'ingénieur électricien. Analyse une ligne électrique alimentant une charge de {current}A "
                    f"sur une distance de {length}m sous une tension de {voltage}V. "
                    "Donne une recommandation sur la section minimale du câble en cuivre (en mm²) pour respecter une chute de tension maximale de 3%."
                )
                response = client.models.generate_content(
                    model="gemini-2.5-flash", contents=prompt
                )
                st.markdown(response.text)
