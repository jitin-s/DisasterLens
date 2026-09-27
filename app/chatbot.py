"""
DisasterLens AI Disaster Assistant (आपदा मित्र / EOC Chatbot)
High-precision keyword-indexed search and decision-support assistant.
Answers inquiries regarding portal features, live district telemetry,
prioritization math, resource allocation, and NDMA citizen safety guidelines in English and Hindi.
"""

import re
from typing import Dict, Any, List, Optional
import pandas as pd


class DisasterLensChatbot:
    """
    Advanced keyword-indexed and state-aware conversational assistant for DisasterLens.
    Features:
    - Multi-keyword fuzzy and token matching.
    - Specific district-level real-time data lookup (e.g. Joshimath, Wayanad, Chamoli, Majuli).
    - In-depth portal navigation, feature guides, and UN INFORM math explanations.
    - Official NDMA citizen safety protocols.
    - Natural language responses in English and Hindi.
    """

    def __init__(self):
        pass

    def is_hindi(self, text: str) -> bool:
        """Detects if text contains Devanagari script or common Hindi keywords."""
        devanagari = any('\u0900' <= char <= '\u097F' for char in text)
        hindi_keywords = [
            "kya", "kaise", "batao", "madad", "baad", "khatra", "bache", "kis",
            "kaun", "kaha", "kare", "jila", "suraksha", "nauka", "kitne"
        ]
        lower = text.lower()
        has_keywords = any(kw in lower for kw in hindi_keywords)
        return devanagari or has_keywords

    HINDI_DISTRICT_MAP = {
        "चमोली": "chamoli", "जोशीमठ": "joshimath", "केदारनाथ": "kedarnath",
        "माजुली": "majuli", "वायनाड": "wayanad", "सुपौल": "supaul",
        "सहरसा": "saharsa", "दरभंगा": "darbhanga", "पटना": "patna",
        "पुरी": "puri", "पारादीप": "paradip", "बालासोर": "balasore",
        "मुंबई": "mumbai", "कच्छ": "kutch", "भुज": "bhuj",
        "श्रीनगर": "srinagar", "मनाली": "manali", "कुल्लू": "kullu",
        "शिमला": "shimla", "उत्तरकाशी": "uttarkashi", "पिथौरागढ़": "pithoragarh",
        "चेन्नई": "chennai", "कोच्चि": "kochi", "धेमाजी": "dhemaji",
        "लखीमपुर": "lakhimpur", "काजीरंगा": "kaziranga", "सिल्चर": "silchar",
        "गुवाहाटी": "guwahati", "गोरखपुर": "gorakhpur", "वाराणसी": "varanasi",
        "प्रयागराज": "prayagraj", "अयोध्या": "ayodhya", "सुंदरबन": "sundarbans",
        "दीघा": "digha", "विशाखापट्टनम": "visakhapatnam", "रामेश्वरम": "rameswaram",
        "कन्याकुमारी": "kanyakumari", "गंगटोक": "gangtok", "तवांग": "tawang",
        "लेह": "leh", "कारगिल": "kargil"
    }

    def search_district(self, query: str, df: pd.DataFrame) -> Optional[pd.Series]:
        """Searches if the query mentions any specific district or location from the 105 zones."""
        q_lower = query.lower()
        # Check Devanagari mappings
        for hi_name, en_trans in self.HINDI_DISTRICT_MAP.items():
            if hi_name in query:
                q_lower += f" {en_trans}"
                
        for _, row in df.iterrows():
            name_lower = str(row["zone_name"]).lower()
            state_lower = str(row.get("state", "")).lower()
            zone_id_lower = str(row["zone_id"]).lower()
            
            # Match district tokens (e.g. "joshimath", "wayanad", "chamoli", "majuli", "puri", "kosi")
            name_parts = re.findall(r'\b\w+\b', name_lower)
            for part in name_parts:
                if len(part) >= 4 and part in q_lower:
                    return row
            if zone_id_lower in q_lower:
                return row
        return None

    def respond(
        self,
        query: str,
        current_data: pd.DataFrame,
        summary_metrics: Dict[str, Any],
        scenario_choice: str = "flash_flood_surge",
        lang: str = "en"
    ) -> str:
        """Generates an informed response based on high-precision keyword matching and live state."""
        q = query.strip().lower()
        use_hindi = (lang == "hi") or self.is_hindi(query)

        # ---------------------------------------------------------
        # 1. SPECIFIC DISTRICT / LOCATION LOOKUP BY KEYWORD
        # ---------------------------------------------------------
        district_match = self.search_district(query, current_data)
        if district_match is not None:
            r = district_match
            z_name = r["zone_name"]
            z_state = r.get("state", "India")
            z_rank = r.get("priority_rank", 1)
            z_opi = float(r.get("opi_score", 0.0))
            z_tier = r.get("triage_tier", "Unknown")
            z_flood = float(r.get("flood_gauge_m", 0.0))
            z_road = float(r.get("road_connectivity_pct", 100.0))
            z_pop = int(r.get("total_population", 0))
            z_boats = int(r.get("alloc_sar_boats", 0))
            z_clinics = int(r.get("alloc_medical_clinics", 0))
            z_rations = int(r.get("alloc_ration_kits", 0))
            
            road_status_en = "🚨 SEVERED (<30% - Blocked by water/debris)" if z_road < 30 else f"✅ Open ({z_road:.1f}%)"
            road_status_hi = "🚨 अवरुद्ध (<30% - मलबा या पानी भरा)" if z_road < 30 else f"✅ चालू ({z_road:.1f}%)"

            if use_hindi:
                return (
                    f"📍 **{z_name} ({z_state}) की लाइव आपदा स्थिति रिपोर्ट:**\n\n"
                    f"• **प्राथमिकता रैंक**: #{z_rank} (105 जिलों में से)\n"
                    f"• **खतरा स्कोर (OPI)**: **{z_opi:.1f} / 100** ({z_tier})\n"
                    f"• **जलभराव / बाढ़ स्तर**: {z_flood:.2f} मीटर\n"
                    f"• **सड़क संपर्क स्थिति**: {road_status_hi}\n"
                    f"• **प्रभावित नागरिक**: {z_pop:,}\n\n"
                    f"📦 **आवंटित राहत सामग्री:**\n"
                    f"• बचाव नौकाएं (Boats): **{z_boats}**\n"
                    f"• मोबाइल मेडिकल क्लीनिक: **{z_clinics}**\n"
                    f"• राशन किट: **{z_rations}**\n\n"
                    f"विस्तृत निर्णय विवरण के लिए टैब **'💡 यह क्षेत्र खतरे में क्यों है?'** में {z_name} चुनें।"
                )
            else:
                return (
                    f"📍 **Live Incident Status Report for {z_name} ({z_state}):**\n\n"
                    f"• **National Priority Rank**: #{z_rank} (out of 105 monitored districts)\n"
                    f"• **Danger Score (OPI)**: **{z_opi:.1f} / 100** ({z_tier})\n"
                    f"• **Water Surge / Flood Gauge**: {z_flood:.2f} m\n"
                    f"• **Transit Road Access**: {road_status_en}\n"
                    f"• **Exposed Population**: {z_pop:,} citizens\n\n"
                    f"📦 **Emergency Resources Dispatched:**\n"
                    f"• Search & Rescue Boats: **{z_boats} units**\n"
                    f"• Mobile Trauma Clinics: **{z_clinics} units**\n"
                    f"• Food & Water Packs: **{z_rations} packs**\n\n"
                    f"For a full mathematical breakdown of why {z_name} received this score, view the **'💡 Why is Area at Risk?'** tab."
                )

        # ---------------------------------------------------------
        # 2. RED ALERT VS ORANGE ALERT DIFFERENCE
        # ---------------------------------------------------------
        if any(w in q for w in ["difference", "vs", "antar", "level", "tier", "categories", "अंतर", "श्रेणी", "स्तर"]):
            if use_hindi:
                return (
                    "🚦 **रेड अलर्ट और ऑरेंज अलर्ट में अंतर:**\n\n"
                    "1. 🔴 **रेड अलर्ट (Catastrophic - Tier 1) - स्कोर ≥ 70 / 100:**\n"
                    "   • तत्काल जान-माल का खतरा।\n"
                    "   • अनिवार्य निकासी (Evacuation) आदेश सक्रिय।\n"
                    "   • जीवन-रक्षक नौकाओं और हवाई सहायता को सर्वोच्च प्राथमिकता।\n\n"
                    "2. 🟠 **ऑरेंज अलर्ट (High Priority - Tier 2) - स्कोर 50 से 69.9:**\n"
                    "   • गंभीर आपदा की आशंका और उच्च जोखिम।\n"
                    "   • राहत दलों और प्राथमिक चिकित्सा टीमों की अग्रिम तैनाती।\n"
                    "   • नागरिकों को ऊंचे और सुरक्षित स्थानों पर जाने की चेतावनी।\n\n"
                    "3. 🟡 **येलो अलर्ट (Moderate - Tier 3) - स्कोर 30 से 49.9:**\n"
                    "   • निगरानी स्तर; स्थानीय प्रशासन सतर्क।\n\n"
                    "4. 🟢 **ग्रीन अलर्ट (Low - Tier 4) - स्कोर < 30:**\n"
                    "   • सामान्य स्थिति, कोई तत्काल खतरा नहीं।"
                )
            else:
                return (
                    "🚦 **Difference Between Triage Alert Levels (Tiers):**\n\n"
                    "1. 🔴 **Red Alert (Catastrophic - Tier 1) - Score ≥ 70 / 100:**\n"
                    "   • Immediate threat to human life and total infrastructure collapse.\n"
                    "   • Mandatory evacuation protocols triggered.\n"
                    "   • First priority for amphibious rescue boats and airborne rescues.\n\n"
                    "2. 🟠 **Orange Alert (High Priority - Tier 2) - Score 50 - 69.9:**\n"
                    "   • Severe danger and significant risk of flash floods or debris flow.\n"
                    "   • Pre-deployment of medical response units and food rations.\n"
                    "   • Citizens advised to relocate to designated relief shelters.\n\n"
                    "3. 🟡 **Yellow Alert (Moderate - Tier 3) - Score 30 - 49.9:**\n"
                    "   • Monitored operational threshold; local administration on standby.\n\n"
                    "4. 🟢 **Green (Low Risk - Tier 4) - Score < 30:**\n"
                    "   • Normal conditions within safety parameters."
                )

        # ---------------------------------------------------------
        # 3. SEVERED ROADS & BRIDGES (LOGISTICS BOTTLENECK)
        # ---------------------------------------------------------
        if any(w in q for w in ["road", "bridge", "severed", "cut off", "blocked", "highway", "access", "सड़क", "पुल", "टूटा", "अवरुद्ध", "रास्ता"]):
            severed_df = current_data[current_data["road_connectivity_pct"] < 30.0]
            severed_count = len(severed_df)
            severed_names = ", ".join(severed_df["zone_name"].head(5).tolist()) if severed_count > 0 else "None"
            
            if use_hindi:
                return (
                    f"🚧 **टूटे हुए रास्तों व पुलों का राहत कार्य पर प्रभाव:**\n\n"
                    f"• **वर्तमान स्थिति**: कुल **{severed_count} जिलों** में मुख्य सड़क संपर्क पूरी तरह कट चुका है ({severed_names})।\n"
                    "• **राहत नियम**: जब सड़क संपर्क 30% से कम हो जाता है, तो भारी पहिएदार मेडिकल ट्रक और एम्बुलेंस सड़क मार्ग से नहीं जा सकते।\n"
                    "• **समाधान**: प्रणाली स्वचालित रूप से पहिएदार ट्रकों को रोककर **उभयचर बचाव नौकाओं (Inflatable Boats)** और वायुसेना हेलीकॉप्टर एयरलिफ्ट को सक्रिय करती है।\n\n"
                    "आप साइडबार में '🚧 टूटे हुए पुल / अवरुद्ध रास्ते' से किसी भी जिले का रास्ता बंद करके इसका प्रभाव देख सकते हैं।"
                )
            else:
                return (
                    f"🚧 **Impact of Severed Roads & Bridges on Rescue Operations:**\n\n"
                    f"• **Active Bottlenecks**: Currently, **{severed_count} transport corridors** are severed (<30% connectivity): *{severed_names}*.\n"
                    "• **Physical Constraint Rule**: Wheeled medical trauma trucks cannot physically travel over washed-out bridges or submerged roads.\n"
                    "• **Automated Shift**: The mathematical optimizer enforces $x_{i,\\text{medical}} = 0$ for severed sectors, redirecting supply to **Search & Rescue Boats** and aerial winch drops.\n\n"
                    "You can simulate road closures dynamically using Section 5 in the sidebar."
                )

        # ---------------------------------------------------------
        # 4. DOWNLOAD CSV MANIFEST
        # ---------------------------------------------------------
        if any(w in q for w in ["csv", "manifest", "download", "export", "excel", "report", "डाउनलोड", "मैनिफेस्ट", "रिपोर्ट"]):
            if use_hindi:
                return (
                    "📥 **जिला राहत प्रेषण सूची (CSV) डाउनलोड करने का तरीका:**\n\n"
                    "1. ऊपर दिए गए चौथे टैब **'📋 जिला राहत प्रेषण सूची'** पर क्लिक करें।\n"
                    "2. तालिका के ठीक नीचे दिए गए **'📥 आधिकारिक प्रेषण सूची डाउनलोड करें (CSV फ़ाइल)'** बटन पर क्लिक करें।\n"
                    "3. यह फ़ाइल प्रत्येक जिले को भेजी गई नौकाओं, क्लीनिकों, राशन पैकेटों और जनरेटरों की सटीक संख्या एक्सेल/सीएसवी में सहेज लेगी।"
                )
            else:
                return (
                    "📥 **How to Download the Tactical Dispatch Manifest (CSV):**\n\n"
                    "1. Navigate to **Tab 4: '📋 District Dispatch Manifest'**.\n"
                    "2. Scroll below the deployment table and click the **'📥 Download Official Tactical Dispatch Manifest (CSV)'** button.\n"
                    "3. The CSV contains official dispatch numbers per district: units sent, needed demand, deficit shortages, and road connectivity percentages."
                )

        # ---------------------------------------------------------
        # 5. WHAT-IF WEATHER SIMULATION
        # ---------------------------------------------------------
        if any(w in q for w in ["what if", "simulation", "slider", "rain modifier", "surge", "सिमुलेशन", "स्लाइडर", "वर्षा"]):
            if use_hindi:
                return (
                    "🌧️ **What-If मौसम सिमुलेशन कैसे कार्य करता है:**\n\n"
                    "• **उद्देश्य**: आपदा आने से पहले यह जांचना कि यदि 50% अधिक बारिश हो या हवाएं 70% तेज हों, तो किन जिलों में खतरा बढ़ेगा।\n"
                    "• **उपयोग**: साइडबार में **'4. 🌧️ मौसम में बदलाव (What-If सिमुलेशन)'** में जाकर 'अतिरिक्त वर्षा' या 'अतिरिक्त चक्रवाती हवा' के स्लाइडर को आगे बढ़ाएं।\n"
                    "• **परिणाम**: पूरा पोर्टल, सैटेलाइट नक्शा, खतरा स्कोर और राहत सामग्री की मांग तुरंत नई मौसमीय स्थिति के अनुसार अपडेट हो जाती है।"
                )
            else:
                return (
                    "🌧️ **How the What-If Weather Sandbox Works:**\n\n"
                    "• **Purpose**: Allows commanders to stress-test disaster response before extreme weather strikes.\n"
                    "• **How to Use**: In the left sidebar, navigate to **'4. 🌧️ Weather What-If Simulation'** and adjust the Rainfall (+%) or Peak Wind (+%) sliders.\n"
                    "• **Real-Time Effect**: The ML severity engine immediately recalculates flood heights, re-ranks the 105 districts, and updates rescue resource demands dynamically."
                )

        # ---------------------------------------------------------
        # 6. 72-HOUR FAMILY EMERGENCY KIT
        # ---------------------------------------------------------
        if any(w in q for w in ["kit", "bag", "item", "survival", "72 hour", "सामान", "किट", "थैला", "तैयारी"]):
            if use_hindi:
                return (
                    "🧰 **72-घंटे की परिवार सुरक्षा किट में आवश्यक सामग्री:**\n\n"
                    "1. **💧 स्वच्छ जल व भोजन**: प्रति व्यक्ति प्रतिदिन 3 लीटर पानी, उच्च ऊर्जा वाले सूखे बिस्कुट, फल, और क्लोरीन की गोलियां।\n"
                    "2. **💊 प्राथमिक चिकित्सा**: बैंड-एड, एंटीसेप्टिक, जरूरी दैनिक दवाएं, ओआरएस पैकेट।\n"
                    "3. **🔦 रोशनी व संचार**: अतिरिक्त बैटरी वाली टॉर्च, एएम/एफएम रेडियो, पावर बैंक, आपातकालीन सीटी।\n"
                    "4. **📄 दस्तावेज**: आधार कार्ड, राशन कार्ड, बैंक पासबुक - वाटरप्रूफ प्लास्टिक थैली में बंद।\n\n"
                    "पूरी सूची देखने के लिए टैब **'🛡️ आपदा रोकथाम एवं सुरक्षा निर्देश'** में 5वां उप-टैब देखें।"
                )
            else:
                return (
                    "🧰 **Essential Checklist for 72-Hour Family Emergency Grab-Bag:**\n\n"
                    "1. **💧 Clean Water & Food**: 3 Liters of drinking water per person per day, non-perishable high-energy biscuits, and water purification tablets.\n"
                    "2. **💊 First Aid & Medicines**: Bandages, antiseptic ointments, daily prescription medications, ORS rehydration packs.\n"
                    "3. **🔦 Tools & Power**: LED torch with spare batteries, battery-powered transistor radio, charged power banks, loud whistle.\n"
                    "4. **📄 Documents**: Aadhaar, Voter ID, property and insurance records sealed in a waterproof zip pouch.\n\n"
                    "For full details, open **Tab 5: '🛡️ Prevention & Safety Guidelines'**."
                )

        # ---------------------------------------------------------
        # 7. LIVE WEATHER & SACHET NDMA DISASTER ALERTS
        # ---------------------------------------------------------
        if any(w in q for w in ["sachet", "ndma alert", "cap alert", "early warning", "सचेत", "सचेत अलर्ट"]):
            if use_hindi:
                return (
                    "🚨 **सचेत (SACHET - NDMA / C-DOT) राष्ट्रीय आपदा चेतावनी प्रणाली:**\n\n"
                    "• **सचेत क्या है**: यह भारत सरकार (NDMA और C-DOT) का आधिकारिक CAP v1.2 ऑल-हज़ार्ड अलर्ट पोर्टल है।\n"
                    "• **एजेंसियां**: IMD (चक्रवात/वर्षा), CWC (बाढ़/नदी जलस्तर), GSI (भूस्खलन), और NCS (भूकंप)।\n"
                    "• **DisasterLens एकीकरण**: हमारा पोर्टल हर 15 मिनट में SACHET के लाइव अलर्ट फ़ीड को प्रोसेस करता है और भारत के सभी 205 जिलों के जोखिम स्कोर में सम्मिलित करता है।"
                )
            else:
                return (
                    "🚨 **SACHET (NDMA / C-DOT) National Disaster Early Warning Feed:**\n\n"
                    "• **What is SACHET**: It is the Government of India's unified Common Alerting Protocol (CAP v1.2) platform developed by NDMA & C-DOT.\n"
                    "• **Integrated Agencies**: Ingests real-time alerts from IMD (cyclones & heatwaves), CWC (dam discharges & river floods), GSI (landslide warnings), and NCS (earthquakes).\n"
                    "• **DisasterLens Integration**: DisasterLens queries SACHET in real-time, mapping active warning polygons across all 205 Pan-India districts with zero delay."
                )

        # ---------------------------------------------------------
        # 7B. MULTI-DISASTER PREDICTION & FORECASTING HORIZON
        # ---------------------------------------------------------
        if any(w in q for w in ["predict", "prediction", "forecast", "trajectory", "भविष्यवाणी", "पूर्वानुमान", "अग्रिम अनुमान"]):
            if use_hindi:
                return (
                    "🔮 **DisasterLens बहु-आपदा AI भविष्यवाणी इंजन:**\n\n"
                    "1. **बाढ़ जलभराव प्रक्षेपवक्र (6h, 12h, 24h)**: सूक्ष्म-ऊंचाई (DEM) और जल निकासी क्षमता के आधार पर अगले 24 घंटों में जल स्तर (मीटर में) का अग्रिम पूर्वानुमान।\n"
                    "2. **चक्रवात एवं तूफानी लहर (Storm Surge)**: IMD पैमाने पर डिप्रेशन से सुपर साइक्लोन तक हवा की गति, बैरोमीटर दबाव गिरावट, और हॉलैंड मॉडल द्वारा तटीय लहर की ऊंचाई (मीटर)।\n"
                    "3. **भूस्खलन संभाव्यता (GSI मॉडल)**: ढलान कोण (Slope °) और वर्षा तीव्रता के आधार पर मलबे के बहाव और राष्ट्रीय राजमार्ग अवरोध का जोखिम प्रतिशत (0-100%)।\n"
                    "4. **वेट-बल्ब थर्मल तनाव (Stull फॉर्मूला)**: तापमान और आर्द्रता से मानव जीवन रक्षा सीमा (Tw ≥ 35°C) का पूर्वानुमान।"
                )
            else:
                return (
                    "🔮 **DisasterLens Multi-Disaster AI Prediction Engine:**\n\n"
                    "1. **Flood Inundation Trajectory (6h, 12h, 24h)**: Micro-elevation DEM runoff curves project standing water depth and flash flood probability ahead of time.\n"
                    "2. **Cyclone Gales & Storm Surge**: Categorizes storms (Depression to Super Cyclone) and computes Holland/Jelesnianski coastal surge height (meters).\n"
                    "3. **GSI Landslide Susceptibility**: Evaluates slope angle (°) and precipitation thresholds to predict debris flow probability (%) and mountain corridor cuts.\n"
                    "4. **Wet-Bulb Heatwave Index**: Uses Stull's equation to predict biological survivability ($T_w \\ge 35^\\circ C$ threshold) and time to heatstroke."
                )

        # ---------------------------------------------------------
        # 7C. GOLDEN-HOUR EVACUATION COUNTDOWN (tau_crit)
        # ---------------------------------------------------------
        if any(w in q for w in ["golden hour", "evacuation", "tau", "cutoff", "गोल्डन ऑवर", "निकासी", "रास्ता बंद"]):
            if use_hindi:
                return (
                    "⏳ **गोल्डन-ऑवर निकासी उल्टी गिनती (Golden-Hour Evacuation Countdown - tau_crit):**\n\n"
                    "• **यह क्या है**: यह एक दुर्लभ व अत्यंत महत्वपूर्ण सुविधा है जो गणना करती है कि मुख्य सड़कें व पुल जलमग्न (>0.35m) होने से पहले नागरिकों और एम्बुलेंस के निकलने के लिए कितने घंटे और मिनट शेष हैं।\n"
                    "• **गणितीय आधार**: $\\tau_{\\text{crit}} = \\frac{D_{\\text{cutoff}} - D_{\\text{current}}}{dD/dt}$\n"
                    "• **कार्रवाई निर्देश**: यदि शेष समय 90 मिनट से कम है, तो तत्काल उच्च 4x4 वाहनों से निकासी का आदेश दिया जाता है; समय समाप्त होने पर छतों पर शरण लेने का निर्देश जारी होता है।"
                )
            else:
                return (
                    "⏳ **Golden-Hour Evacuation Countdown ($\\tau_{\\text{crit}}$):**\n\n"
                    "• **What It Is**: A rare, life-critical feature that calculates the exact time remaining (hours and minutes) before arterial road corridors submerge past 0.35m (the impassable threshold for civil vehicles & light ambulances).\n"
                    "• **Mathematical Formulation**: $\\tau_{\\text{crit}} = \\frac{\\text{Navigable Clearance Margin}}{\\text{Net Inundation Rate } dD/dt}$\n"
                    "• **Directives**: Triggers urgent automated triage: 'Open Window' (>4h) $\\rightarrow$ 'Imminent Severance' (<90m) $\\rightarrow$ 'Road Severed: Rooftop Refuge Only'."
                )

        # ---------------------------------------------------------
        # 7D. CASCADING MULTI-HAZARD CHAIN REACTION ENGINE
        # ---------------------------------------------------------
        if any(w in q for w in ["cascade", "cascading", "chain", "compound", "श्रृंखला", "कंपाउंड जोखिम"]):
            if use_hindi:
                return (
                    "⚡ **कैस्केडिंग बहु-आपदा श्रृंखला प्रभाव इंजन (Cascading Hazard Engine):**\n\n"
                    "• वास्तविक आपदाएं कभी अकेली नहीं आतीं। यह इंजन एक-दूसरे से जुड़ी आपदाओं का सिमुलेशन करता है:\n"
                    "  1. **चक्रवाती हवा** $\\rightarrow$ 66kV पावर ग्रिड पतन $\\rightarrow$ अस्पताल आईसीयू व मोबाइल टावर ब्लैकआउट।\n"
                    "  2. **बादल फटना** $\\rightarrow$ पहाड़ी ढलान द्रवीकरण $\\rightarrow$ नदी में मिट्टी का बांध $\\rightarrow$ अचानक विनाशकारी सैलाब।\n"
                    "  3. **तटीय तूफानी लहर** $\\rightarrow$ सीवरेज जल बैकफ्लो $\\rightarrow$ पीने के पानी का प्रदूषण $\\rightarrow$ जलजनित महामारी।\n"
                    "• यह प्रत्येक प्रभाव की संभाव्यता (%) और त्वरित शमन निर्देश प्रदान करता है।"
                )
            else:
                return (
                    "⚡ **Cascading Multi-Hazard Chain Reaction Engine:**\n\n"
                    "• Real disasters compound across civil infrastructure. This engine models cross-hazard trigger networks:\n"
                    "  1. **Cyclone Gales** $\\rightarrow$ Transmission Mast Shear $\\rightarrow$ Power Substation Trip $\\rightarrow$ Hospital ICU & Cell Tower Blackout.\n"
                    "  2. **Cloudburst Deluge** $\\rightarrow$ Slope Liquefaction $\\rightarrow$ Gorge Debris Dam $\\rightarrow$ Catastrophic Flash Breach.\n"
                    "  3. **Storm Surge** $\\rightarrow$ Gravity Drain Inversion $\\rightarrow$ Sewage Conduit Infiltration $\\rightarrow$ Waterborne Outbreak.\n"
                    "• Calculates exact transition probabilities (%) and prioritized engineering mitigations."
                )

        # ---------------------------------------------------------
        # 7E. VERCEL & CLOUD DEPLOYMENT GUIDE
        # ---------------------------------------------------------
        if any(w in q for w in ["vercel", "deploy", "hosting", "cloud run", "हॉस्टिंग", "डिप्लॉय"]):
            if use_hindi:
                return (
                    "🚀 **DisasterLens को Vercel / क्लाउड पर डिप्लॉय करने की विधि:**\n\n"
                    "चूंकि DisasterLens एक पूर्ण विकसित Python Streamlit एप्लिकेशन है, इसे Vercel पर चलाने के दो आसान तरीके हैं:\n\n"
                    "1. **Streamlit Community Cloud (अनुशंसित - 100% निःशुल्क और 2 मिनट में)**:\n"
                    "   • अपने GitHub रिपॉजिटरी में कोड पुश करें।\n"
                    "   • [share.streamlit.io](https://share.streamlit.io) पर जाएं, रिपॉजिटरी चुनें और Main file path को `app/main.py` सेट करें।\n\n"
                    "2. **Vercel डिप्लॉयमेंट (Next.js / Python सर्वरलेस)**:\n"
                    "   • रूट में `vercel.json` बनाएं और Python 3.11+ रनटाइम कॉन्फ़िगर करें।\n"
                    "   • `requirements.txt` में निर्भरताएं रखें।\n"
                    "   • Vercel CLI चलाएं: `npm i -g vercel && vercel`\n\n"
                    "3. **Docker / Render / Google Cloud Run (वैकल्पिक)**:\n"
                    "   • `Dockerfile`: `FROM python:3.11-slim ... CMD streamlit run app/main.py --server.port=8080`"
                )
            else:
                return (
                    "🚀 **How to Deploy DisasterLens to Vercel / Cloud:**\n\n"
                    "DisasterLens is a full-stack Python Streamlit application with predictive AI models. Here are the 2 best deployment pathways:\n\n"
                    "1. **Streamlit Community Cloud (Recommended - Free & 1-Click)**:\n"
                    "   • Push the project to GitHub (`git push origin main`).\n"
                    "   • Visit [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.\n"
                    "   • Select repo `DisasterManagement`, Branch `main`, Main file path `app/main.py`.\n"
                    "   • Click **Deploy**! Live in 90 seconds with automated SSL.\n\n"
                    "2. **Vercel Serverless Deployment**:\n"
                    "   • Ensure `vercel.json` is present with Python WSGI/ASGI serverless route handler.\n"
                    "   • Run `vercel` in terminal to push to Vercel preview & production.\n\n"
                    "3. **Containerized Production (Google Cloud Run / Render / AWS ECS)**:\n"
                    "   • Build Docker image using the provided `Dockerfile`.\n"
                    "   • Command: `streamlit run app/main.py --server.port $PORT --server.address 0.0.0.0`."
                )

        # ---------------------------------------------------------
        # 7F. LIVE WEATHER & OPEN-METEO API
        # ---------------------------------------------------------
        if any(w in q for w in ["weather", "open-meteo", "temperature", "forecast", "live radar", "मौसम", "तापमान", "रडार"]):
            if use_hindi:
                return (
                    "🌐 **लाइव मौसम व ओपन-मेटियो (Open-Meteo) डेटा कैसे देखें:**\n\n"
                    "1. टैब **'🌐 लाइव मौसम एवं डेटा रिपोर्ट'** पर जाएं।\n"
                    "2. भारत के 205 जिलों में से कोई भी जिला चुनें या ऊपर सर्च बार में नाम लिखें।\n"
                    "3. प्रणाली तुरंत उपग्रह से वास्तविक समय का तापमान, हवा की गति, वायु गुणवत्ता (AQI) और वर्षा का सजीव डेटा प्राप्त कर लेगी।"
                )
            else:
                return (
                    "🌐 **How to Query Real-Time Live Weather via Open-Meteo & SACHET:**\n\n"
                    "1. Navigate to **Tab 4: '🌫️ Real-Time Atmospheric & Air Quality Radar'**.\n"
                    "2. Select any of the 205 Pan-India districts from the Global Search bar.\n"
                    "3. DisasterLens fetches live satellite radar telemetry (rain mm/h, wind gusts, pressure, PM2.5, AQI) and active SACHET CAP advisories."
                )


        # ---------------------------------------------------------
        # 8. CURRENT RED ALERT DISTRICTS & LIVE SITUATION
        # ---------------------------------------------------------
        if any(w in q for w in ["red alert", "catastrophic", "khatra", "danger", "worst", "top", "kaunse", "which district", "प्रभावित", "रेड अलर्ट", "खतरा", "सबसे खतरनाक"]):
            catastrophic_zones = current_data[current_data["triage_tier"] == "Catastrophic (Tier 1)"]
            high_zones = current_data[current_data["triage_tier"] == "High Priority (Tier 2)"]
            
            top_cat = catastrophic_zones.head(5)
            names_en = [f"**#{r.get('priority_rank', '#')} {r['zone_name']}** ({r.get('state', 'India')}) - Danger Score: **{r['opi_score']:.1f}**" for _, r in top_cat.iterrows()]
            names_hi = [f"**#{r.get('priority_rank', '#')} {r['zone_name']}** ({r.get('state', 'India')}) - खतरा स्कोर: **{r['opi_score']:.1f}**" for _, r in top_cat.iterrows()]
            
            if use_hindi:
                if len(catastrophic_zones) > 0:
                    return (
                        f"🚨 **वर्तमान में {len(catastrophic_zones)} जिले रेड अलर्ट (अति-गंभीर खतरे) पर हैं:**\n\n"
                        + "\n".join([f"• {n}" for n in names_hi])
                        + f"\n\nइसके अतिरिक्त **{len(high_zones)} जिले** ऑरेंज अलर्ट (उच्च प्राथमिकता) पर हैं। "
                        f"इन क्षेत्रों में कुल **{int(current_data[current_data['opi_score']>=50]['total_population'].sum()):,} नागरिक** प्रभावित हैं। "
                        "आप विस्तृत विवरण पहले टैब **'🚨 राष्ट्रीय मानचित्र एवं खतरा सूची'** में देख सकते हैं।"
                    )
                else:
                    return "✅ **वर्तमान में कोई भी जिला रेड अलर्ट पर नहीं है।** सभी 105 संवेदनशील जिले सामान्य परिचालन सीमा में हैं।"
            else:
                if len(catastrophic_zones) > 0:
                    return (
                        f"🚨 **Currently, {len(catastrophic_zones)} districts are in Red Alert (Catastrophic Danger):**\n\n"
                        + "\n".join([f"• {n}" for n in names_en])
                        + f"\n\nAdditionally, **{len(high_zones)} districts** are on Orange Alert (High Priority). "
                        f"A total of **{int(current_data[current_data['opi_score']>=50]['total_population'].sum()):,} citizens** are critically exposed in these zones. "
                        "You can inspect full details in the first tab: **'🚨 National Map & Danger List'**."
                    )
                else:
                    return "✅ **No districts are currently in Red Alert.** All monitored Indian districts are within normal operational safety thresholds."

        # ---------------------------------------------------------
        # 9. PORTAL FEATURES OVERVIEW
        # ---------------------------------------------------------
        if any(w in q for w in ["feature", "site", "portal", "kya hai", "kaise kaam", "about", "what is this", "overview", "विशेषता", "सुविधा", "कार्य"]):
            if use_hindi:
                return (
                    "🏛️ **DisasterLens पोर्टल की 8 मुख्य विशेषताएं:**\n\n"
                    "1. **🚨 इंटरैक्टिव सैटेलाइट नक्शा**: भारत के 105 संवेदनशील जिलों का सजीव Esri सैटेलाइट मैप (नक्शे पर बिंदु का आकार जनसंख्या और रंग खतरे को दर्शाता है)।\n"
                    "2. **📊 खतरा स्कोर (OPI 1-100)**: यूएन INFORM मानक पर आधारित स्कोर, जो बाढ़, तूफान, गरीबी और अस्पताल की दूरी को मिलाकर सटीक खतरा तय करता है।\n"
                    "3. **💡 निर्णय का कारण (Explainable AI)**: बताता है कि किसी जिले को उच्च प्राथमिकता क्यों दी गई (जैसे 70% बाढ़ और 30% टूटी सड़कें)।\n"
                    "4. **📦 राहत संसाधन आवंटन (Optimization)**: सीमित बचाव नौकाओं (Boats), मोबाइल क्लीनिक, राशन और जनरेटरों का निष्पक्ष वितरण।\n"
                    "5. **📋 जिला राहत सूची (Manifest)**: किस जिले को कितने उपकरण भेजे गए, इसकी सूची व CSV डाउनलोड।\n"
                    "6. **🛡️ आपदा रोकथाम व सुरक्षा निर्देश**: बाढ़, चक्रवात, भूस्खलन और भूकंप से बचने के आधिकारिक एनडीएमए नियम (Dos & Don'ts)।\n"
                    "7. **🆘 आपातकालीन नागरिक SOS फॉर्म**: कोई भी नागरिक या अधिकारी फंसे हुए लोगों की सूचना देकर तुरंत NDRF सहायता टोकन प्राप्त कर सकता है।\n"
                    "8. **🤖 फ्लोटिंग AI आपदा सहायक**: स्क्रीन के नीचे-दाएं कोने में स्थायी सहायक जो आपके हर सवाल का तुरंत जवाब देता है।"
                )
            else:
                return (
                    "🏛️ **Core Features of the DisasterLens National Portal:**\n\n"
                    "1. **🚨 Interactive Real Satellite Map**: Covers 105 vulnerable Indian districts with Esri satellite imagery (zero API keys required). Circle size represents population, and color indicates Danger Level.\n"
                    "2. **📊 Danger Score (OPI 1-100)**: UN INFORM standard index combining hazard telemetry (flood, wind), demographic vulnerability, and infrastructure coping deficits.\n"
                    "3. **💡 Explainable AI (Why Area at Risk?)**: Mathematical breakdown (SHAP) showing the exact reasons why a district received its priority score with human-readable officer briefings.\n"
                    "4. **📦 Rescue Resource Optimizer (MILP)**: Distributes limited boats, mobile clinics, food packs, and generators fairly, enforcing physical bottlenecks (e.g., roads severed <30% cannot use wheeled trucks).\n"
                    "5. **📋 District Deployment Manifest**: Downloadable CSV manifest listing units dispatched, needed, and deficit for every district.\n"
                    "6. **🛡️ Prevention & Safety Guidelines**: Certified NDMA Dos & Don'ts for Floods, Landslides, Cyclones, Earthquakes, and 72-hour family emergency kits.\n"
                    "7. **🆘 Emergency Help & Citizen SOS Form**: Interactive dispatch request form that generates an official tracking token (`NDMA-SOS-2026-XXXXX`) and logs to the active dispatch registry.\n"
                    "8. **🤖 Fixed Floating AI Sahayak**: Always accessible at the bottom-right corner of your screen across all views."
                )

        # ---------------------------------------------------------
        # 10. RESOURCE ALLOCATION & RESCUE BOATS
        # ---------------------------------------------------------
        if any(w in q for w in ["boat", "clinic", "ration", "generator", "allocate", "resource", "optimizer", "नौका", "राशन", "संसाधन", "सामग्री"]):
            rb = summary_metrics.get("resource_breakdown", {})
            boats_sent = rb.get("sar_boats", {}).get("allocated", 0)
            boats_dem = rb.get("sar_boats", {}).get("total_demand", 0)
            clinics_sent = rb.get("medical_clinics", {}).get("allocated", 0)
            clinics_dem = rb.get("medical_clinics", {}).get("total_demand", 0)
            
            if use_hindi:
                return (
                    "📦 **राहत संसाधन आवंटन कैसे कार्य करता है:**\n\n"
                    "• **प्राथमिकता आधार**: उच्चतम खतरा स्कोर (OPI) वाले जिलों को जीवन-रक्षक संसाधन सबसे पहले दिए जाते हैं।\n"
                    "• **टूटे रास्तों का नियम**: यदि किसी जिले में सड़क संपर्क 30% से कम है, तो वहां पहिएदार मेडिकल ट्रक नहीं जा सकते। प्रणाली स्वचालित रूप से वहां बचाव नौकाएं और हवाई सहायता भेजती है।\n"
                    f"• **वर्तमान स्थिति**: मांग में से **{boats_sent} / {boats_dem} बचाव नौकाएं (Boats)** तथा **{clinics_sent} / {clinics_dem} मोबाइल चिकित्सा क्लीनिक** प्रेषित किए जा चुके हैं।\n\n"
                    "आप इसका विस्तृत विश्लेषण टैब **'📦 बचाव संसाधन आवंटन एवं प्रेषण'** में देख सकते हैं।"
                )
            else:
                return (
                    "📦 **How Rescue Resource Allocation Works:**\n\n"
                    "• **Priority Matching**: Districts with the highest danger scores (OPI) receive life-safety assets first.\n"
                    "• **Road Severance Bottleneck**: If a district has severed road connectivity (<30%), wheeled mobile clinics cannot travel. The solver shifts to amphibious rescue boats and airborne supply drops.\n"
                    f"• **Current Stockpile Dispatch**: **{boats_sent} of {boats_dem} Rescue Boats** and **{clinics_sent} of {clinics_dem} Mobile Medical Clinics** have been allocated.\n\n"
                    "You can inspect the full mathematical optimization and demand charts in the **'📦 Rescue Resource Dispatch'** tab."
                )

        # ---------------------------------------------------------
        # 11. EMERGENCY SOS & CONTACTING NDRF
        # ---------------------------------------------------------
        if any(w in q for w in ["sos", "help", "emergency", "contact", "helpline", "phone", "नंबर", "मदद", "सहायता", "फोन", "कॉल"]):
            if use_hindi:
                return (
                    "🆘 **आपातकालीन सहायता एवं संपर्क निर्देश:**\n\n"
                    "1. **तत्काल 24x7 टोल-फ्री हेल्पलाइन नंबर:**\n"
                    "   • 🚨 **112**: राष्ट्रीय आपातकालीन नंबर (पुलिस, दमकल, एम्बुलेंस)\n"
                    "   • 📞 **1078**: एनडीएमए केंद्रीय नियंत्रण कक्ष\n"
                    "   • 🌊 **1070**: राज्य आपदा राहत आयुक्त हेल्पलाइन\n"
                    "   • 🚑 **108**: आपातकालीन मेडिकल एम्बुलेंस\n"
                    "   • 👮 **011-24363260**: एनडीआरएफ मुख्यालय\n\n"
                    "2. **ऑनलाइन आपातकालीन SOS दर्ज करें:**\n"
                    "   पोर्टल के टैब **'🆘 आपातकालीन सहायता एवं नागरिक SOS फॉर्म'** पर जाएं, अपना नाम, मोबाइल नंबर, जिला और फंसे हुए लोगों की संख्या भरें। "
                    "प्रणाली तुरंत एक आधिकारिक **डिस्पैच ट्रैकिंग कोड** (`NDMA-SOS-2026-XXXXX`) जारी कर नजदीकी एनडीआरएफ बटालियन को अलर्ट भेजेगी।"
                )
            else:
                return (
                    "🆘 **Emergency Help & Contact Instructions:**\n\n"
                    "1. **Immediate 24x7 Toll-Free Emergency Helplines:**\n"
                    "   • 🚨 **112**: All-in-One National Emergency (Police, Fire, Ambulance)\n"
                    "   • 📞 **1078**: NDMA Central Control Room\n"
                    "   • 🌊 **1070**: State Disaster Relief Helpline\n"
                    "   • 🚑 **108**: Emergency Trauma Ambulance\n"
                    "   • 👮 **011-24363260**: NDRF HQ Operations\n\n"
                    "2. **Submit an Online Emergency SOS Ticket:**\n"
                    "   Go to tab **'🆘 Emergency Help & Citizen SOS Form'**, enter your contact number, district, and number of people stranded. "
                    "The system will instantly generate an official **NDRF Dispatch Tracking Token** (`NDMA-SOS-2026-XXXXX`) and log the incident to the central EOC registry."
                )

        # ---------------------------------------------------------
        # 12. DISASTER SAFETY: FLOODS, CYCLONES, LANDSLIDES, QUAKES
        # ---------------------------------------------------------
        if any(w in q for w in ["flood", "cyclone", "landslide", "earthquake", "prevent", "safety", "सुरक्षा", "बाढ़", "तूफान", "भूस्खलन", "भूकंप"]):
            if use_hindi:
                return (
                    "🛡️ **आपदा सुरक्षा एवं रोकथाम के मुख्य नियम:**\n\n"
                    "• **🌊 बाढ़ आने पर**: तुरंत ऊंचे स्थानों पर जाएं। मुख्य बिजली का स्विच और गैस सिलेंडर बंद करें। बहते पानी में कभी पैदल या गाड़ी से न जाएं ('Turn Around, Don't Drown')। केवल उबला हुआ पानी पिएं।\n"
                    "• **🏔️ भूस्खलन क्षेत्र में**: यदि दीवारों में दरारें आएं या नदी में अचानक मटमैला पानी बढ़े, तो तुरंत ढलान से दूर हटें।\n"
                    "• **🌀 चक्रवात के समय**: पक्के आश्रय स्थल में रहें। समुद्र तट पर न जाएं। तूफान की आंख (Eye) के समय मिलने वाली अस्थाई शांति में बाहर न निकलें।\n"
                    "• **⚡ भूकंप के दौरान**: **'Drop, Cover, and Hold On'** - मजबूत मेज के नीचे बैठें और सिर को ढकें। लिफ्ट का उपयोग कभी न करें।\n\n"
                    "विस्तृत चेकलिस्ट के लिए टैब **'🛡️ आपदा रोकथाम एवं सुरक्षा निर्देश'** देखें।"
                )
            else:
                return (
                    "🛡️ **Certified NDMA Disaster Safety Protocols:**\n\n"
                    "• **🌊 During Floods**: Move immediately to higher ground. Turn off main power switches and gas cylinders. Never walk or drive through moving water ('Turn Around, Don't Drown'). Drink only boiled or chlorinated water.\n"
                    "• **🏔️ In Landslide Zones**: Watch for warning signs (sticking doors, wall cracks, sudden muddy river surge). Evacuate perpendicular to the path of debris.\n"
                    "• **🌀 During Cyclones**: Remain inside certified cyclone shelters. Stay away from beaches. Do not venture out during the temporary calm eye of the storm.\n"
                    "• **⚡ During Earthquakes**: **'Drop, Cover, and Hold On'** under a sturdy desk. Never use elevators during or after tremors.\n\n"
                    "For full guidelines and the 72-hour family emergency kit checklist, visit the **'🛡️ Prevention & Safety Guidelines'** tab."
                )

        # ---------------------------------------------------------
        # 13. DANGER SCORE / OPI FORMULA
        # ---------------------------------------------------------
        if any(w in q for w in ["opi", "score", "calculate", "math", "formula", "algorithm", "सूत्र", "गणना", "स्कोर"]):
            if use_hindi:
                return (
                    "📊 **खतरा स्कोर (OPI - Operational Priority Index) की गणना कैसे होती है:**\n\n"
                    "DisasterLens संयुक्त राष्ट्र INFORM आपदा मानक का उपयोग करता है:\n"
                    "$$\\text{OPI} = \\left( \\text{Hazard}^{0.4} \\times \\text{Vulnerability}^{0.3} \\times \\text{Lack of Coping}^{0.3} \\right) \\times 100$$\n\n"
                    "1. **आपदा जोखिम (Hazard)**: वर्षा की मात्रा, जल स्तर गेज, और एआई द्वारा अनुमानित क्षति स्कोर।\n"
                    "2. **संवेदनशीलता (Vulnerability)**: गरीबी दर, बुजुर्गों व बच्चों की जनसंख्या।\n"
                    "3. **मुकाबला क्षमता की कमी (Lack of Coping)**: नजदीकी अस्पतालों की कमी और सड़क संपर्क की दूरी।\n\n"
                    "स्कोर 0 से 100 के बीच होता है। 70 से अधिक स्कोर वाले जिले **रेड अलर्ट (Catastrophic)** में रखे जाते हैं।"
                )
            else:
                return (
                    "📊 **How the Danger Score (OPI) is Calculated:**\n\n"
                    "DisasterLens implements the United Nations INFORM Disaster Priority formula:\n"
                    "$$\\text{OPI} = \\left( \\text{Hazard}^{0.4} \\times \\text{Vulnerability}^{0.3} \\times \\text{Lack of Coping}^{0.3} \\right) \\times 100$$\n\n"
                    "1. **Hazard Exposure**: Extreme rainfall volume, river flood gauges, and ML-predicted damage severity.\n"
                    "2. **Demographic Vulnerability**: Poverty ratios, infant and senior citizen density.\n"
                    "3. **Lack of Coping Capacity**: Road connectivity distance and hospital bed shortages.\n\n"
                    "Scores range from 0 to 100. Any score $\\ge 70$ is triaged as **🔴 Catastrophic (Tier 1)**."
                )

        # ---------------------------------------------------------
        # 14. DEFAULT / FALLBACK RESPONSE
        # ---------------------------------------------------------
        if use_hindi:
            return (
                "नमस्ते! मैं **DisasterLens AI आपदा सहायक** हूं। मैं आपकी निम्नलिखित विषयों में सहायता कर सकता हूं:\n\n"
                "• **जिले की लाइव स्थिति**: किसी भी जिले का नाम लिखें (जैसे *'जोशीमठ'*, *'वायनाड'*, *'माजुली'* या *'चमोली'*).\n"
                "• **अलर्ट स्तर**: पूछें *'रेड और ऑरेंज अलर्ट में क्या अंतर है?'*\n"
                "• **राहत आवंटन**: पूछें *'बचाव नौकाओं का आवंटन कैसे होता है?'*\n"
                "• **सड़क रुकावट**: पूछें *'टूटे रास्ते मेडिकल टीमों को कैसे रोकते हैं?'*\n"
                "• **आपदा सुरक्षा**: पूछें *'बाढ़ आने पर क्या करें?'* या *'72 घंटे की किट'*\n"
                "• **मैनिफेस्ट डाउनलोड**: पूछें *'CSV रिपोर्ट कैसे डाउनलोड करें?'*\n\n"
                "कृपया अपना प्रश्न नीचे लिखें या ऊपर दिए गए त्वरित बटनों पर क्लिक करें!"
            )
        else:
            return (
                "Hello! I am the **DisasterLens AI Disaster Assistant**. You can ask me:\n\n"
                "• **Specific District Inquiry**: Type any district name (e.g. *'Joshimath'*, *'Wayanad'*, *'Chamoli'*, *'Majuli'*).\n"
                "• **Alert Tiers**: Ask *'What is the difference between Red and Orange alert?'*\n"
                "• **Resource Allocation**: Ask *'How are rescue boats and clinics allocated?'*\n"
                "• **Road Bottlenecks**: Ask *'How do cut-off roads affect rescue teams?'*\n"
                "• **Safety & Prevention**: Ask *'What to do during a flood?'* or *'72-hour emergency kit items'*.\n"
                "• **Data Export**: Ask *'How to download the CSV manifest?'*\n\n"
                "Type your query below or click one of the suggested inquiry chips above!"
            )
