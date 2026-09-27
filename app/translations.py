"""
DisasterLens Bilingual Localization Dictionary (English & Hindi)
Provides accessible, plain-language translations for citizens and disaster officers.
"""

TRANSLATIONS = {
    "en": {
        # Portal Header
        "dept_title_hi": "राष्ट्रीय आपदा प्रबंधन प्राधिकरण • गृह मंत्रालय, भारत सरकार",
        "dept_title_en": "National Disaster Management Authority (NDMA) • Govt. of India",
        "portal_title": "DisasterLens • National Disaster Decision & Relief Support Portal",
        "portal_subtitle": "Official Emergency Decision-Support, Vulnerability Analysis & Resource Optimization • 105 Real Indian Districts",
        "live_eoc_badge": "CENTRAL EOC ACTIVE • 24x7 GRID MONITORING",
        "lang_switch_label": "Language / भाषा",
        
        # Helpline Bar
        "helpline_banner_title": "NATIONAL EMERGENCY HELPLINES (TOLL-FREE 24x7):",
        "helpline_national": "National Emergency",
        "helpline_ndma": "NDMA Control Room",
        "helpline_state": "State Disaster Relief",
        "helpline_ambulance": "Medical & Ambulance",
        "helpline_ndrf": "NDRF HQ",
        
        # Sidebar
        "sidebar_title": "NDMA CONTROL ROOM",
        "sidebar_subtitle": "Emergency Simulation & Deployment Settings",
        "sec_scenario": "1. 🚨 Active Disaster Scenario",
        "sec_region": "2. 📍 Region of India to Monitor",
        "sec_map": "3. 🗺️ Satellite Map Style",
        "sec_weather": "4. 🌧️ Weather What-If Simulation",
        "sec_severance": "5. 🚧 Roads & Bridges Blocked",
        "sec_stockpile": "6. 📦 Central Relief Supplies Available",
        
        # Scenario Options
        "sc_flood": "🌊 Monsoon Heavy Rain & River Overflow",
        "sc_cyclone": "🌀 Severe Coastal Cyclone & Storm Surge",
        "sc_blackout": "⚡ Power Grid Failure & Infrastructure Outage",
        "sc_baseline": "🌤️ Normal Baseline (Controlled River Flow)",
        
        # Region Options
        "reg_all": "All India (105 Vulnerable Districts)",
        "reg_himalayan": "🏔️ Himalayan & Mountain States (Uttarakhand, Himachal, J&K, Ladakh, Sikkim, Arunachal)",
        "reg_rivers": "🌊 Major River Basins (Ganga, Brahmaputra, Kosi, Rapti, Mahanadi)",
        "reg_bay_of_bengal": "🌀 Bay of Bengal Cyclone Coast (Odisha, Andhra, Tamil Nadu, Sundarbans)",
        "reg_arabian": "🌴 Arabian Sea & Western Ghats (Kerala, Maharashtra, Gujarat, Goa, Karnataka)",
        
        # Map Options
        "map_esri": "🛰️ Real Satellite Imagery (Esri World - 100% Free, No Key)",
        "map_osm": "🗺️ OpenStreetMap (Detailed Roads & Towns - No Key)",
        "map_topo": "🏔️ OpenTopoMap (Topographic Mountain Terrain - No Key)",
        "map_light": "☀️ Positron (Clean Light Map - No Key)",
        "map_mapbox": "🔑 Custom Mapbox Satellite (Requires Optional Key)",
        
        # Sliders & Inputs
        "slider_rain": "Extra Rainfall / Cloudburst (+%):",
        "slider_wind": "Extra Storm Wind Velocity (+%):",
        "input_severed": "Select Cut-Off Districts (Bridge / Road Washed Away):",
        "input_boats": "NDRF Rescue Boats Available:",
        "input_clinics": "Mobile Trauma Medical Clinics:",
        "input_rations": "Food & Clean Water Kits (100-pack):",
        "input_generators": "Emergency Power Generators:",
        "sidebar_footer_addr": "NDMA Bhawan, A-1 Safdarjung Enclave, New Delhi\nToll-Free Helpline: 1078 | 112",
        
        # Alerts
        "alert_red_title": "CRITICAL NATIONAL RED ALERT • IMMEDIATE LIFE-SAFETY EVACUATION REQUIRED",
        "alert_red_desc": "{count} DISTRICTS / SECTORS ARE IN CATASTROPHIC DANGER ({names}...). An estimated {pop:,} citizens are at extreme risk of river deluge, flash floods, or landslide collapse. {severed} transport corridors are completely cut off (<30% road access), requiring mandatory amphibious rescue boats and airborne supply drops.",
        "alert_orange_title": "ORANGE OPERATIONAL ALERT • HIGH EMERGENCY PREPAREDNESS ACTIVE",
        "alert_orange_desc": "{count} DISTRICTS require urgent response deployment. Relief resources are being dispatched from central stockpiles.",
        "alert_green_title": "ALL REGIONS WITHIN NORMAL OPERATIONAL THRESHOLDS",
        "alert_green_desc": "No districts currently require emergency red evacuation alerts. River gauges and weather radar are normal.",
        
        # KPIs
        "kpi_monitored": "Monitored Locations",
        "kpi_red": "🔴 Red Alert (Catastrophic)",
        "kpi_red_sub": "Danger Level ≥ 70 / 100",
        "kpi_orange": "🟠 Orange Alert (High)",
        "kpi_orange_sub": "Danger Level 50 - 69.9",
        "kpi_exposed": "👥 People in Danger Area",
        "kpi_exposed_sub": "Citizens Exposed to Hazard",
        "kpi_dispatched": "📦 Supplies Dispatched",
        "kpi_dispatched_sub": "{alloc} of {total} Units Sent",
        
        # Navigation Tabs
        "tab_map": "🚨 National Map & Danger List",
        "tab_why": "💡 Why is Area at Risk?",
        "tab_dispatch": "📦 Rescue Resource Dispatch",
        "tab_manifest": "📋 District Dispatch Manifest",
        "tab_prevention": "🛡️ Prevention & Safety Guidelines",
        "tab_sos": "🆘 Emergency Help & Citizen SOS Form",
        "tab_chatbot": "🤖 AI Disaster Assistant (Chatbot)",
        "tab_weather": "🌐 Live Weather & Data Reports",
        
        # Tab 1: Map & Danger List
        "t1_header": "Geospatial Disaster Map & Danger Priority Queue ({count} Indian Locations)",
        "t1_caption": "Live decision-support map combining real satellite imagery, hazard gauges, and official priority scores.",
        "t1_map_title": "Interactive Real Satellite Map",
        "t1_map_caption": "ℹ️ Click any circle on the map to see elevation, water surge, road connectivity, and critical hospital assets.",
        "t1_queue_title": "Priority Danger Queue (Ranked #1 to #105)",
        "t1_filter_label": "Filter Locations by Threat Level:",
        "t1_f_all": "All Sectors",
        "t1_f_red": "🔴 Red Alert (Catastrophic)",
        "t1_f_orange": "🟠 Orange Alert (High)",
        "t1_f_severed": "⚠️ Roads Cut Off",
        
        # Tab 2: Why Area at Risk
        "t2_header": "💡 Why is this Area at Risk? (Plain-Language Decision Explanation)",
        "t2_desc": "Every priority score is broken down into simple, human-understandable factors so disaster relief officers and citizens can understand exactly why emergency teams are being dispatched.",
        "t2_select": "Choose a District or Location to Inspect:",
        "t2_briefing_title": "OFFICIAL INCIDENT COMMAND BRIEFING FOR {name} ({state})",
        "t2_factors_title": "Key Risk Factors Driving Danger Score:",
        "t2_radar_title": "Hazard vs Vulnerability Comparison:",
        "t2_table_title": "Detailed Risk Driver Values:",
        
        # Tab 3: Resource Dispatch
        "t3_header": "📦 Rescue Resource Allocation & Dispatch (Constrained Optimization)",
        "t3_desc": "DisasterLens calculates how to fairly distribute limited national supplies (rescue boats, mobile medical units, food rations, and power generators) to save the maximum number of lives while obeying physical constraints like cut-off roads and depot limits.",
        "t3_status": "Optimization Status:",
        "t3_score": "Life-Safety Protection Score:",
        "t3_how_it_works": "How the Decision Formula Works (Simple Explanation):",
        "t3_rule1": "1. **Priority Matching**: Districts with the highest danger scores (OPI) get first priority for life-saving equipment.",
        "t3_rule2": "2. **Road Bottleneck Rule**: If a district's roads are severed (below 30% connectivity), heavy wheeled medical trucks CANNOT travel by road. Only amphibious rescue boats and aerial supplies are authorized.",
        "t3_rule3": "3. **Stockpile Guard**: The system never dispatches more equipment than what is physically stored in national depots.",
        
        # Tab 4: Manifest
        "t4_header": "📋 Official District Rescue Dispatch List (National Manifest)",
        "t4_desc": "Exact deployment numbers showing how many rescue boats, mobile medical clinics, food rations, and generators have been authorized for dispatch to each district.",
        "t4_download": "📥 Download Official Tactical Dispatch Manifest (CSV)",
        
        # Tab 6: SOS Form
        "t6_header": "🆘 Emergency Help & Citizen SOS Dispatch Request",
        "t6_desc": "Report life-threatening situations, stranded persons, or infrastructure cut-offs directly to the National Disaster Management Authority and NDRF Field Control Room.",
        "t6_form_title": "EMERGENCY SOS & RESCUE DISPATCH FORM",
        "t6_form_sub": "Submissions are transmitted directly to the State Emergency Operations Center (SEOC) and nearest NDRF Battalion.",
        "t6_name": "Full Name / Reporting Officer *",
        "t6_phone": "Emergency Contact Number *",
        "t6_district": "District / Disaster Zone *",
        "t6_type": "Emergency Type *",
        "t6_trapped": "Estimated People Trapped / Affected *",
        "t6_route": "Road / Access Route Condition *",
        "t6_resource": "Most Urgent Resource Needed *",
        "t6_landmark": "Exact Landmark / Village / GPS *",
        "t6_details": "Additional Incident Situation & Distress Details:",
        "t6_submit": "🚨 SUBMIT EMERGENCY SOS TO NDMA / NDRF CONTROL ROOM",
        "t6_reg_title": "Active Emergency SOS Dispatch Registry (Live Grid)",
        
        # Chatbot Tab
        "cb_header": "🤖 AI DisasterLens Assistant (आपदा मित्र / EOC Chatbot)",
        "cb_desc": "Ask any question about how DisasterLens works, live danger in any district, disaster prevention guidelines, or emergency rescue procedures.",
        "cb_placeholder": "Ask a question about the portal, danger scores, safety tips, or emergency response...",
        "cb_chips_title": "Suggested Quick Questions:"
    },
    
    "hi": {
        # Portal Header
        "dept_title_hi": "राष्ट्रीय आपदा प्रबंधन प्राधिकरण • गृह मंत्रालय, भारत सरकार",
        "dept_title_en": "National Disaster Management Authority (NDMA) • Govt. of India",
        "portal_title": "DisasterLens • राष्ट्रीय आपदा निर्णय एवं राहत सहायता पोर्टल",
        "portal_subtitle": "आपातकालीन निर्णय-समर्थन, संवेदनशीलता विश्लेषण एवं राहत संसाधन आवंटन प्रणाली • भारत के 105 संवेदनशील जिले",
        "live_eoc_badge": "केंद्रीय आपातकालीन नियंत्रण कक्ष सक्रिय • 24x7 निगरानी",
        "lang_switch_label": "भाषा / Language",
        
        # Helpline Bar
        "helpline_banner_title": "राष्ट्रीय आपातकालीन हेल्पलाइन नंबर (टोल-फ्री 24x7):",
        "helpline_national": "राष्ट्रीय आपातकाल",
        "helpline_ndma": "एनडीएमए नियंत्रण कक्ष",
        "helpline_state": "राज्य आपदा राहत",
        "helpline_ambulance": "एम्बुलेंस एवं चिकित्सा",
        "helpline_ndrf": "एनडीआरएफ मुख्यालय",
        
        # Sidebar
        "sidebar_title": "एनडीएमए नियंत्रण कक्ष",
        "sidebar_subtitle": "आपदा सिमुलेशन एवं राहत प्रबंधन सेटिंग्स",
        "sec_scenario": "1. 🚨 सक्रिय आपदा परिदृश्य चुनें",
        "sec_region": "2. 📍 भारत का क्षेत्र चुनें",
        "sec_map": "3. 🗺️ सैटेलाइट मानचित्र प्रकार",
        "sec_weather": "4. 🌧️ मौसम में बदलाव (What-If सिमुलेशन)",
        "sec_severance": "5. 🚧 टूटे हुए पुल / अवरुद्ध रास्ते",
        "sec_stockpile": "6. 📦 केंद्रीय राहत सामग्री भंडार उपलब्ध",
        
        # Scenario Options
        "sc_flood": "🌊 भारी मानसूनी बारिश एवं नदियों में बाढ़",
        "sc_cyclone": "🌀 तीव्र समुद्री चक्रवात एवं तूफानी लहरें",
        "sc_blackout": "⚡ पावर ग्रिड विफलता एवं बुनियादी ढांचा ठप",
        "sc_baseline": "🌤️ सामान्य स्थिति (नियंत्रित नदी प्रवाह)",
        
        # Region Options
        "reg_all": "संपूर्ण भारत (105 संवेदनशील जिले)",
        "reg_himalayan": "🏔️ हिमालयी एवं पर्वतीय राज्य (उत्तराखंड, हिमाचल, जेएंडके, लद्दाख, सिक्किम, अरुणाचल)",
        "reg_rivers": "🌊 प्रमुख नदी घाटियां (गंगा, ब्रह्मपुत्र, कोसी, राप्ती, महानदी)",
        "reg_bay_of_bengal": "🌀 बंगाल की खाड़ी तटीय क्षेत्र (ओडिशा, आंध्र प्रदेश, तमिलनाडु, सुंदरबन)",
        "reg_arabian": "🌴 अरब सागर एवं पश्चिमी घाट (केरल, महाराष्ट्र, गुजरात, गोवा, कर्नाटक)",
        
        # Map Options
        "map_esri": "🛰️ वास्तविक सैटेलाइट मैप (Esri World - 100% निःशुल्क, बिना चाबी)",
        "map_osm": "🗺️ ओपन-स्ट्रीट मैप (सड़कें व शहर - निःशुल्क)",
        "map_topo": "🏔️ टोपोग्राफिक मैप (पर्वतीय भूभाग - निःशुल्क)",
        "map_light": "☀️ लाइट मैप (साफ नक्शा - निःशुल्क)",
        "map_mapbox": "🔑 मैपबॉक्स सैटेलाइट (वैकल्पिक टोकन आवश्यक)",
        
        # Sliders & Inputs
        "slider_rain": "अतिरिक्त वर्षा / बादल फटना (+%):",
        "slider_wind": "अतिरिक्त चक्रवाती हवा की गति (+%):",
        "input_severed": "संपर्क टूटे जिले चुनें (पुल या सड़क बह जाने पर):",
        "input_boats": "उपलब्ध एनडीआरएफ बचाव नौकाएं (Boats):",
        "input_clinics": "उपलब्ध मोबाइल चिकित्सा व ट्रॉमा क्लीनिक:",
        "input_rations": "उपलब्ध राशन व स्वच्छ जल किट (100 का पैकेट):",
        "input_generators": "उपलब्ध भारी आपातकालीन जनरेटर:",
        "sidebar_footer_addr": "एनडीएमए भवन, ए-1 सफदरजंग एन्क्लेव, नई दिल्ली\nटोल-फ्री हेल्पलाइन: 1078 | 112",
        
        # Alerts
        "alert_red_title": "अति-गंभीर राष्ट्रीय रेड अलर्ट • तत्काल जीवन-सुरक्षा व निकासी आवश्यक",
        "alert_red_desc": "{count} जिले / क्षेत्र अति-गंभीर खतरे में हैं ({names}...). अनुमानित {pop:,} नागरिक बाढ़, बादल फटने या भूस्खलन के भारी जोखिम में हैं। {severed} प्रमुख यातायात संपर्क मार्ग पूरी तरह कट चुके हैं (<30% सड़क संपर्क), जिनके लिए तुरंत बचाव नौकाओं व हेलीकॉप्टर की आवश्यकता है।",
        "alert_orange_title": "ऑरेंज अलर्ट • उच्च आपातकालीन तत्परता सक्रिय",
        "alert_orange_desc": "{count} जिलों में तत्काल राहत दल तैनात करने की आवश्यकता है। केंद्रीय भंडार से राहत सामग्री भेजी जा रही है।",
        "alert_green_title": "सभी क्षेत्र सामान्य सीमा के भीतर हैं",
        "alert_green_desc": "वर्तमान में किसी भी जिले में रेड अलर्ट की आवश्यकता नहीं है। नदी स्तर और रडार सामान्य हैं।",
        
        # KPIs
        "kpi_monitored": "निगरानी में जिले",
        "kpi_red": "🔴 रेड अलर्ट (अति-गंभीर)",
        "kpi_red_sub": "खतरा स्कोर ≥ 70 / 100",
        "kpi_orange": "🟠 ऑरेंज अलर्ट (उच्च)",
        "kpi_orange_sub": "खतरा स्कोर 50 - 69.9",
        "kpi_exposed": "👥 खतरे में प्रभावित नागरिक",
        "kpi_exposed_sub": "आपदा क्षेत्र में कुल आबादी",
        "kpi_dispatched": "📦 राहत सामग्री प्रेषित",
        "kpi_dispatched_sub": "{total} में से {alloc} यूनिट भेजी गईं",
        
        # Navigation Tabs
        "tab_map": "🚨 राष्ट्रीय मानचित्र एवं खतरा सूची",
        "tab_why": "💡 यह क्षेत्र खतरे में क्यों है?",
        "tab_dispatch": "📦 बचाव संसाधन आवंटन एवं प्रेषण",
        "tab_manifest": "📋 जिला राहत प्रेषण सूची",
        "tab_prevention": "🛡️ आपदा रोकथाम एवं सुरक्षा निर्देश",
        "tab_sos": "🆘 आपातकालीन सहायता एवं नागरिक SOS फॉर्म",
        "tab_chatbot": "🤖 AI आपदा सहायक (चैटबॉट)",
        "tab_weather": "🌐 लाइव मौसम एवं डेटा रिपोर्ट",
        
        # Tab 1: Map & Danger List
        "t1_header": "जियोस्पेशियल आपदा मानचित्र एवं खतरा प्राथमिकता सूची ({count} भारतीय स्थान)",
        "t1_caption": "सैटेलाइट इमेजरी, जल स्तर गेज और आधिकारिक खतरा स्कोर का सजीव निर्णय-समर्थन नक्शा।",
        "t1_map_title": "इंटरैक्टिव वास्तविक सैटेलाइट नक्शा",
        "t1_map_caption": "ℹ️ नक्शे पर किसी भी बिंदु पर क्लिक करके ऊंचाई, जल स्तर, सड़क संपर्क और नजदीकी अस्पताल देखें।",
        "t1_queue_title": "प्राथमिकता खतरा सूची (#1 से #105 तक क्रमबद्ध)",
        "t1_filter_label": "खतरे के स्तर के अनुसार फ़िल्टर करें:",
        "t1_f_all": "सभी क्षेत्र",
        "t1_f_red": "🔴 रेड अलर्ट (अति-गंभीर)",
        "t1_f_orange": "🟠 ऑरेंज अलर्ट (उच्च)",
        "t1_f_severed": "⚠️ सड़क मार्ग अवरुद्ध",
        
        # Tab 2: Why Area at Risk
        "t2_header": "💡 यह क्षेत्र खतरे में क्यों है? (सरल भाषा में निर्णय का कारण)",
        "t2_desc": "प्रत्येक प्राथमिकता स्कोर को सरल मानवीय कारणों में विभाजित किया गया है ताकि राहत अधिकारी और नागरिक यह समझ सकें कि वहां आपातकालीन दल क्यों भेजे जा रहे हैं।",
        "t2_select": "निरीक्षण के लिए कोई भी जिला या स्थान चुनें:",
        "t2_briefing_title": "{name} ({state}) के लिए आधिकारिक आपातकालीन कमान ब्रीफिंग",
        "t2_factors_title": "खतरे का कारण बनने वाले मुख्य कारक:",
        "t2_radar_title": "आपदा बनाम संवेदनशीलता तुलना:",
        "t2_table_title": "विस्तृत जोखिम संकेतक मान:",
        
        # Tab 3: Resource Dispatch
        "t3_header": "📦 बचाव संसाधन आवंटन एवं प्रेषण (वैज्ञानिक अनुकूलन)",
        "t3_desc": "DisasterLens सीमित राष्ट्रीय राहत सामग्री (बचाव नौकाएं, मोबाइल चिकित्सा क्लीनिक, भोजन राशन और जनरेटर) को सबसे अधिक जीवन बचाने के लिए न्यायसंगत रूप से आवंटित करता है।",
        "t3_status": "अनुकूलन स्थिति:",
        "t3_score": "जीवन-सुरक्षा संरक्षण स्कोर:",
        "t3_how_it_works": "निर्णय सूत्र कैसे कार्य करता है (सरल व्याख्या):",
        "t3_rule1": "1. **प्राथमिकता मिलान**: जिस जिले का खतरा स्कोर (OPI) सबसे अधिक है, उसे सबसे पहले जीवन-रक्षक उपकरण दिए जाते हैं।",
        "t3_rule2": "2. **सड़क रुकावट नियम**: यदि किसी जिले की सड़क टूटी हुई है (30% से कम संपर्क), तो वहां पहिएदार मेडिकल ट्रक नहीं जा सकते। वहां केवल उभयचर बचाव नौकाएं और हवाई आपूर्ति की अनुमति है।",
        "t3_rule3": "3. **भंडार सीमा**: प्रणाली कभी भी केंद्रीय डिपो में उपलब्ध सामग्री से अधिक उपकरण नहीं भेजती।",
        
        # Tab 4: Manifest
        "t4_header": "📋 आधिकारिक जिला राहत प्रेषण सूची (राष्ट्रीय मैनिफेस्ट)",
        "t4_desc": "प्रत्येक जिले को भेजी गई बचाव नौकाओं, मोबाइल चिकित्सा इकाइयों, राशन पैकेटों और जनरेटरों की आधिकारिक संख्या।",
        "t4_download": "📥 आधिकारिक प्रेषण सूची डाउनलोड करें (CSV फ़ाइल)",
        
        # Tab 6: SOS Form
        "t6_header": "🆘 आपातकालीन सहायता एवं नागरिक SOS प्रेषण फॉर्म",
        "t6_desc": "फंसे हुए लोगों, जलभराव या टूटे हुए रास्तों की सूचना सीधे राष्ट्रीय आपदा प्रबंधन प्राधिकरण और एनडीआरएफ नियंत्रण कक्ष को भेजें।",
        "t6_form_title": "आपातकालीन SOS एवं बचाव अनुरोध फॉर्म",
        "t6_form_sub": "यह अनुरोध सीधे राज्य आपातकालीन केंद्र (SEOC) और नजदीकी एनडीआरएफ बटालियन को प्रेषित किया जाता है।",
        "t6_name": "पूरा नाम / रिपोर्टिंग अधिकारी का नाम *",
        "t6_phone": "आपातकालीन संपर्क मोबाइल नंबर *",
        "t6_district": "जिला / आपदा क्षेत्र चुनें *",
        "t6_type": "आपात स्थिति का प्रकार *",
        "t6_trapped": "फंसे हुए / प्रभावित लोगों की अनुमानित संख्या *",
        "t6_route": "सड़क व रास्ते की स्थिति *",
        "t6_resource": "सबसे जरूरी सहायता की आवश्यकता *",
        "t6_landmark": "सटीक लैंडमार्क / गांव / स्थान का पता *",
        "t6_details": "स्थिति का विवरण एवं कोई विशेष आवश्यकता:",
        "t6_submit": "🚨 एनडीएमए / एनडीआरएफ नियंत्रण कक्ष को आपातकालीन SOS भेजें",
        "t6_reg_title": "सक्रिय आपातकालीन SOS प्रेषण पंजी (Live Registry)",
        
        # Chatbot Tab
        "cb_header": "🤖 AI आपदा मित्र (DisasterLens सहायक चैटबॉट)",
        "cb_desc": "DisasterLens पोर्टल की विशेषताओं, किसी भी जिले के खतरे, आपदा सुरक्षा उपायों, या राहत कार्यों के बारे में कोई भी प्रश्न पूछें।",
        "cb_placeholder": "पोर्टल, खतरे के स्तर, सुरक्षा नियमों या सहायता के बारे में पूछें...",
        "cb_chips_title": "सुझाए गए तुरंत पूछने वाले प्रश्न:"
    }
}


def get_text(key: str, lang: str = "en", **kwargs) -> str:
    """Safely retrieves translated string for a given key and language."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    text = lang_dict.get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
