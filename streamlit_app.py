import os
import streamlit as st
from google import genai
from google.genai import types

# ------------------------------------------------------------------------------
# Configuration de la page Streamlit
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="IA Engineering Instrumentation & Électricité",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------------------
# Initialisation du client Google GenAI (Gemini)
# ------------------------------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.sidebar.error("⚠️ Clé API Gemini manquante !")
    st.sidebar.info(
        "Veuillez configurer `GEMINI_API_KEY` dans vos secrets Streamlit "
        "ou dans vos variables d'environnement."
    )
    api_key_input = st.sidebar.text_input("Saisir la clé API Gemini :", type="password")
    if api_key_input:
        api_key = api_key_input

if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None

# ------------------------------------------------------------------------------
# En-tête principal
# ------------------------------------------------------------------------------
st.title("⚡ Copilote IA pour Ingénierie Instrumentation & Électricité")
st.markdown("""
Cette application assiste les ingénieurs I&E dans la rédaction de spécifications, 
le dimensionnement d'équipements, la conformité aux normes (ISA, IEC, NEC) et le diagnostic de pannes.
""")

# ------------------------------------------------------------------------------
# Menu de Navigation dans la barre latérale
# ------------------------------------------------------------------------------
st.sidebar.header("🛠️ Modules I&E")
module = st.sidebar.radio(
    "Sélectionnez un outil :",
    [
        "📋 Générateur de Fiches Techniques (Datasheets)",
        "📐 Dimensionnement Câbles & Chute de Tension",
        "🔀 Sélection & Sizing de Vannes de Régulation",
        "📚 Expert Normes (IEC, ISA, ATEX / HazLoc)",
        "🛠️ Diagnostic de Boucle de Régulation / Dépannage"
    ]
)

# System Instruction commune pour définir le rôle de l'IA
SYSTEM_INSTRUCTION_EI = """
Tu es un ingénieur senior expert en Instrumentation, Contrôle-Commande et Électricité Industrielle (I&E).
Tu maîtrises parfaitement les normes internationales (ISA, IEC 60079, IEC 61508, IEC 60287, NEC, NFPA 70).
Tes réponses doivent être techniques, structurées, rigoureuses et orientées sécurité industrielle.
Quand cela s'applique, inclus les formules mathématiques, les unités SI et les références normatives exactes.
"""

# ------------------------------------------------------------------------------
# MODULE 1 : Générateur de Fiches Techniques
# ------------------------------------------------------------------------------
if module == "📋 Générateur de Fiches Techniques (Datasheets)":
    st.header("📋 Génération de Fiche Technique d'Instrument (ISA-20 Style)")
    
    col1, col2 = st.columns(2)
    with col1:
        tag = st.text_input("Tag de l'instrument", value="PIT-101A")
        inst_type = st.selectbox(
            "Type d'instrument",
            [
                "Transmetteur de pression relative/absolue",
                "Transmetteur de pression différentielle",
                "Débitmètre électromagnétique",
                "Débitmètre Massique Coriolis",
                "Transmetteur de niveau à radar à ondes guidées",
                "Vanne de régulation pneumatique"
            ]
        )
        fluid = st.text_input("Fluide du procédé", value="Eau de refroidissement")
        zone_atex = st.selectbox("Zone Explosible (ATEX / IECEx)", ["Non Dangereuse", "Zone 1 (Ex d)", "Zone 1 (Ex ia)", "Zone 2 (Ex ec)"])

    with col2:
        p_op = st.number_input("Pression de service (bar g)", value=6.5)
        t_op = st.number_input("Température de service (°C)", value=45.0)
        protocol = st.selectbox("Signal / Protocole de communication", ["4-20 mA HART", "Foundation Fieldbus", "Profibus PA", "Modbus RTU RS485"])
        sil_req = st.selectbox("Exigence de Sécurité (SIL)", ["Sans objet", "SIL 1", "SIL 2", "SIL 3"])

    if st.button("🚀 Générer la Datasheet", type="primary"):
        if not client:
            st.error("Veuillez d'abord fournir une clé API Gemini.")
        else:
            with st.spinner("Rédaction de la fiche technique en cours..."):
                prompt = f"""
                Génère une fiche technique d'instrumentation complète et professionnelle pour le Tag **{tag}**.
                
                **Données de procédé et spécifications :**
                - Type d'instrument : {inst_type}
                - Fluide : {fluid}
                - Pression d'opération : {p_op} bar g
                - Température d'opération : {t_op} °C
                - Classification Zone Explosible : {zone_atex}
                - Signal / Protocole : {protocol}
                - Niveau d'intégrité de sécurité : {sil_req}
                
                Organise le résultat sous forme de tableaux Markdown avec les sections :
                1. Informations Générales & Identification
                2. Conditions de Procédé & Matériaux en Contact (Body / Wetted Parts)
                3. Caractéristiques Électriques & Raccordements (Cable Entry, Enclosure IP/NEMA)
                4. Performance & Précision
                5. Certifications & Normes applicables
                """
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION_EI,
                        temperature=0.2
                    )
                )
                st.markdown(response.text)

# ------------------------------------------------------------------------------
# MODULE 2 : Dimensionnement Câbles & Chute de Tension
# ------------------------------------------------------------------------------
elif module == "📐 Dimensionnement Câbles & Chute de Tension":
    st.header("📐 Verification & Dimensionnement de Câble Électrique")
    
    col1, col2 = st.columns(2)
    with col1:
        tension_type = st.selectbox("Type d'alimentation", ["Trifasé 400V AC", "Monophasé 230V AC", "Continu 24V DC"])
        puissance_kw = st.number_input("Puissance de la charge (kW)", value=15.0)
        cos_phi = st.slider("Facteur de puissance (cos φ)", 0.70, 1.00, 0.85)
        longueur = st.number_input("Longueur du câble (mètres)", value=120.0)

    with col2:
        matériau = st.radio("Matériau du conducteur", ["Cuivre", "Aluminium"])
        isolation = st.selectbox("Isolation du câble", ["XLPE (90°C)", "PVC (70°C)"])
        max_vdrop_pct = st.number_input("Chute de tension max autorisée (%)", value=3.0)
        mode_pose = st.text_input("Mode de pose / Température ambiante", value="Sur chemin de câbles perforé, Amb. 40°C")

    if st.button("🧮 Calculer et Analyser", type="primary"):
        if not client:
            st.error("Veuillez d'abord fournir une clé API Gemini.")
        else:
            with st.spinner("Analyse du dimensionnement..."):
                prompt = f"""
                Analyse et dimensionne la section du câble pour l'installation électrique suivante :
                
                - Alimentation : {tension_type}
                - Puissance : {puissance_kw} kW (cos φ = {cos_phi})
                - Longueur : {longueur} m
                - Conducteur : {matériau}
                - Isolation : {isolation}
                - Mode de pose / Conditions : {mode_pose}
                - Chute de tension maximale admise : {max_vdrop_pct}%
                
                Fournis :
                1. Le calcul du courant nominal / d'emploi ($I_b$).
                2. Le calcul théorique de la chute de tension ($\Delta U$) pour les sections standard (ex: 2.5, 4, 6, 10, 16, 25, 35, 50 mm²).
                3. La section minimale recommandée ($mm^2$) pour respecter la contrainte de chute de tension.
                4. Les facteurs de correction applicables selon l'IEC 60364-5-52.
                """
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION_EI,
                        temperature=0.1
                    )
                )
                st.markdown(response.text)

# ------------------------------------------------------------------------------
# MODULE 3 : Sélection & Sizing de Vannes
# ------------------------------------------------------------------------------
elif module == "🔀 Sélection & Sizing de Vannes de Régulation":
    st.header("🔀 Calcul du Cv/Kv & Recommandation de Vanne")
    
    col1, col2 = st.columns(2)
    with col1:
        fluide_vanne = st.text_input("Fluide", value="Huile thermique")
        debit_max = st.number_input("Débit maximal ($m^3/h$)", value=45.0)
        p1 = st.number_input("Pression en amont $P_1$ (bar a)", value=8.0)
    with col2:
        p2 = st.number_input("Pression en aval $P_2$ (bar a)", value=5.5)
        temp_val = st.number_input("Température (°C)", value=120.0)
        sg = st.number_input("Densité relative (Viscosité / SG)", value=0.88)

    if st.button("🔍 Calculer le $K_v$ et Sélectionner", type="primary"):
        if not client:
            st.error("Veuillez d'abord fournir une clé API Gemini.")
        else:
            with st.spinner("Calcul en cours..."):
                prompt = f"""
                Effectue le prédimensionnement de la vanne de régulation selon les normes IEC 60534 / ISA 75.01 :
                
                - Fluide : {fluide_vanne}
                - Débit volumique $Q$ : {debit_max} m³/h
                - Pression amont $P_1$ : {p1} bar a
                - Pression aval $P_2$ : {p2} bar a ($\Delta P = {p1 - p2:.2f}$ bar)
                - Température $T$ : {temp_val} °C
                - Densité relative $SG$ : {sg}
                
                Tâches :
                1. Calcule le coefficient de débit théorique $K_v$ et $C_v$.
                2. Vérifie s'il y a un risque de cavitation ou de flashing ($\Delta P_{{max}}$ / Choked flow).
                3. Recommande le type de vanne (Globe, Papillon, Cône/Segment) et la caractéristique d'ouverture (Égale pourcentage, Linéaire).
                4. Suggère le diamètre nominal (DN) et le type d'actionneur (Pneumatique Membrane-Ressort avec Positionneur Intelligente HART).
                """
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION_EI,
                        temperature=0.2
                    )
                )
                st.markdown(response.text)

# ------------------------------------------------------------------------------
# MODULE 4 : Expert Normes
# ------------------------------------------------------------------------------
elif module == "📚 Expert Normes (IEC, ISA, ATEX / HazLoc)":
    st.header("📚 Consultation Normes & Directives Techniques")
    
    query = st.text_area(
        "Posez votre question sur les normes I&E :",
        height=120,
        placeholder="Exemple: Quelle est la différence entre les modes de protection Ex d et Ex ia selon l'IEC 60079 ?"
    )
    
    if st.button("🔎 Analyser la Norme", type="primary"):
        if not query:
            st.warning("Veuillez saisir une question.")
        elif not client:
            st.error("Veuillez d'abord fournir une clé API Gemini.")
        else:
            with st.spinner("Consultation de la base de connaissances normatives..."):
                prompt = f"Question d'ingénierie normatives : {query}"
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION_EI,
                        temperature=0.2
                    )
                )
                st.markdown(response.text)

# ------------------------------------------------------------------------------
# MODULE 5 : Diagnostic & Dépannage
# ------------------------------------------------------------------------------
elif module == "🛠️ Diagnostic de Boucle de Régulation / Dépannage":
    st.header("🛠️ Diagnostic & Troubleshooting I&E")
    
    symptom = st.text_area(
        "Décrivez le problème constaté sur le terrain :",
        height=120,
        placeholder="Exemple: Le transmetteur de pression 4-20mA indique un signal bloqué à 21.5 mA sur l'entrée de l'automate (DCS) alors que la pression est normale."
    )
    
    if st.button("🛠️ Diagnostiquer", type="primary"):
        if not symptom:
            st.warning("Veuillez décrire le problème.")
        elif not client:
            st.error("Veuillez d'abord fournir une clé API Gemini.")
        else:
            with st.spinner("Analyse des causes racines (Root Cause Analysis)..."):
                prompt = f"""
                Applique une méthodologie rigoureuse de recherche de pannes industrielles pour le cas suivant :
                
                **Symptôme / Problème :** {symptom}
                
                Fournis :
                1. Les causes probables (matérielles, câblage, configuration, procédé).
                2. Un guide étape par étape pour le technicien/ingénieur de maintenance avec les outils à utiliser (multimètre, communicateur HART, calibrateur de boucle).
                3. Les précautions de sécurité à prendre avant toute intervention sur site (Permis de travail, Consignation/LOTO, Zone ATEX).
                """
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION_EI,
                        temperature=0.3
                    )
                )
                st.markdown(response.text)
