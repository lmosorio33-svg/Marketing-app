import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
import io
import zipfile
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="InmoTool Pro V6", page_icon="🏠", layout="wide")

# --- FUNCIONES GRÁFICAS (MOTOR DE DISEÑO) ---

def crear_mascara_curva(ancho, alto, altura_curva):
    mascara = Image.new('L', (ancho, alto), 0)
    draw = ImageDraw.Draw(mascara)
    draw.rectangle([(0, 0), (ancho, alto - altura_curva)], fill=255)
    draw.ellipse([(0, alto - 2 * altura_curva), (ancho, alto)], fill=255)
    return mascara

def recortar_circulo_con_borde(img, diametro, color_borde, grosor_borde):
    img = img.convert("RGB")
    lado_min = min(img.size)
    img = ImageOps.fit(img, (lado_min, lado_min), method=Image.LANCZOS)
    img = img.resize((diametro, diametro), Image.LANCZOS)
    mascara = Image.new('L', (diametro, diametro), 0)
    draw_mask = ImageDraw.Draw(mascara)
    draw_mask.ellipse((0, 0, diametro, diametro), fill=255)
    img_circular = Image.new('RGBA', (diametro, diametro), (0, 0, 0, 0))
    img_circular.paste(img, (0, 0), mascara)
    draw_borde = ImageDraw.Draw(img_circular)
    draw_borde.ellipse((0, 0, diametro-1, diametro-1), outline=color_borde, width=grosor_borde)
    return img_circular

def procesar_portada_premium(img_principal, lista_extras, tipo_op, precio, equipamiento, nombre, telefono, correo):
    W, H = 1000, 1400
    COLOR_FONDO = "#0e7a5b"
    COLOR_ACENTO = "#f3c623"
    COLOR_TEXTO = "white"
    
    lienzo = Image.new('RGB', (W, H), COLOR_FONDO)
    draw = ImageDraw.Draw(lienzo)

    img_fachada = img_principal.convert("RGB")
    ALTO_FACHADA = 650
    CURVA = 150
    img_fachada = ImageOps.fit(img_fachada, (W, ALTO_FACHADA), method=Image.LANCZOS)
    mascara = crear_mascara_curva(W, ALTO_FACHADA, CURVA)
    img_fachada.putalpha(mascara)
    lienzo.paste(img_fachada, (0, 0), img_fachada)

    try:
        font_titulo_grande = ImageFont.truetype("arialbd.ttf", 130)
        font_titulo_peq = ImageFont.truetype("arial.ttf", 60)
        font_subtitulo = ImageFont.truetype("arialbd.ttf", 40)
        font_texto = ImageFont.truetype("arial.ttf", 30)
        font_precio = ImageFont.truetype("arialbd.ttf", 55)
        font_contacto = ImageFont.truetype("arial.ttf", 22)
    except:
        font_titulo_grande = font_titulo_peq = font_subtitulo = font_texto = font_precio = font_contacto = ImageFont.load_default()

    X_MARGIN = 60
    Y_POS = ALTO_FACHADA - CURVA + 50

    draw.text((X_MARGIN, Y_POS), "CASA", font=font_titulo_grande, fill=COLOR_TEXTO)
    Y_POS += 130
    draw.text((X_MARGIN, Y_POS), f"en {tipo_op.lower()}", font=font_titulo_peq, fill=COLOR_TEXTO)
    
    Y_POS += 120
    draw.text((X_MARGIN, Y_POS), "Características:", font=font_subtitulo, fill=COLOR_TEXTO, underline=True)
    Y_POS += 60
    lineas_equip = equipamiento.split(',')
    for linea in lineas_equip[:5]: 
        texto_linea = f"• {linea.strip()}"
        if len(texto_linea) > 35: texto_linea = texto_linea[:32] + "..."
        draw.text((X_MARGIN + 20, Y_POS), texto_linea, font=font_texto, fill=COLOR_TEXTO)
        Y_POS += 45

    Y_PRECIO = H - 250
    ANCHO_CAJA = 550
    ALTO_CAJA = 100
    draw.rectangle([(X_MARGIN, Y_PRECIO), (X_MARGIN + ANCHO_CAJA, Y_PRECIO + ALTO_CAJA)], fill=COLOR_ACENTO)
    
    bbox = draw.textbbox((0,0), precio, font=font_precio)
    x_txt = X_MARGIN + (ANCHO_CAJA - (bbox[2] - bbox[0])) // 2
    y_txt = Y_PRECIO + (ALTO_CAJA - (bbox[3] - bbox[1])) // 2 - 10
    draw.text((x_txt, y_txt), precio, font=font_precio, fill="black")

    Y_CONTACTO = Y_PRECIO + ALTO_CAJA + 30
    draw.text((X_MARGIN, Y_CONTACTO), f"Asesor: {nombre}", font=font_contacto, fill=COLOR_TEXTO)
    draw.text((X_MARGIN, Y_CONTACTO + 30), f"📞 {telefono} | ✉️ {correo}", font=font_contacto, fill=COLOR_TEXTO)

    config_circulos = [{"pos": (550, 500), "diam": 420}, {"pos": (650, 850), "diam": 350}, {"pos": (500, 1100), "diam": 300}]
    fotos_para_circulos = lista_extras[:3] if len(lista_extras) >= 3 else lista_extras
    for i, img_extra in enumerate(fotos_para_circulos):
        cfg = config_circulos[i]
        img_circ = recortar_circulo_con_borde(img_extra, cfg["diam"], COLOR_ACENTO, 8)
        lienzo.paste(img_circ, cfg["pos"], img_circ)

    return lienzo

def procesar_galeria_simple(img):
    img = img.convert("RGB")
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.05)
    target_width = 1080
    ratio = target_width / img.width
    target_height = int(img.height * ratio)
    return img.resize((target_width, target_height), Image.LANCZOS)

# --- GENERADOR DE TEXTOS ---

def generar_textos_virales(tipo, zona, precio, equipamiento, contacto, nombre):
    
    lista_items = [item.strip() for item in equipamiento.split(',')]
    
    # Listas de bullets
    bullets_estrellas = "\n".join([f"✨ {item}" for item in lista_items])
    bullets_checks = "\n".join([f"✅ {item}" for item in lista_items])
    bullets_uni = "\n".join([f"🎓 {item}" for item in lista_items]) # Bullet estudiante

    plantillas = []

    # 1. Formal
    t1 = f"""🏡 {tipo.upper()} DE CASA - ZONA {zona.upper()}\n\n📍 UBICACIÓN PRIVILEGIADA\n💵 {precio}\n\n💠 DISTRIBUCIÓN:\n{bullets_checks}\n\n‼️ SE ACEPTAN CRÉDITOS ‼️\n\nINFORMES:\n📞 {contacto} con {nombre}"""
    plantillas.append(t1)

    # 2. Visual
    t2 = f"""🌳 Casa en {zona}, ubicación inmejorable\n💲 Precio: {precio}\n\nCaracterísticas:\n{bullets_estrellas}\n\n✨ Espacios amplios\n📲 Citas: {contacto} ({nombre})"""
    plantillas.append(t2)

    # 3. Urgencia
    t3 = f"""🔥 OPORTUNIDAD EN {zona.upper()} 🔥\n💰 PRECIO: {precio}\n\nTu nuevo hogar:\n{bullets_checks}\n\n🏃‍♂️ ¡Que no te la ganen!\n👉 {contacto}"""
    plantillas.append(t3)

    # 4. Minimalista
    t4 = f"""📍 {zona} | 💲 {precio}\n🏠 Se {tipo.lower()}:\n\n{bullets_estrellas}\n\nℹ️ Citas: {contacto}"""
    plantillas.append(t4)

    # 5. Emocional
    t5 = f"""😍 Estrena casa en {zona}\n💎 Inversión: {precio}\n\nDetalles:\n{bullets_estrellas}\n\n🔑 ¡Ven a conocerla!\n📲 {contacto}"""
    plantillas.append(t5)
    
    # 6. ESTUDIANTE / FORÁNEO (NUEVO ESTILO)
    t6 = f"""🎓 ¡ATENCIÓN ESTUDIANTES / FORÁNEOS! 🎓\n📍 Zona: {zona} (Ideal UACH/Tec)\n\n💲 Renta: {precio}\n\n¿Buscas depa o casa cerca de la uni? Checa esto:\n{bullets_uni}\n\n✅ Transporte cercano\n✅ Zona segura\n✅ Ideal para Roomies\n\n🍕 ¡Agenda tu visita entre clases!\nManda WhatsApp al: 📲 {contacto} con {nombre}"""
    plantillas.append(t6)

    return plantillas

# --- INTERFAZ ---

with st.sidebar:
    st.header("👤 Datos del Asesor")
    nombre_ag = st.text_input("Nombre:", value="Elena Montes")
    tel_ag = st.text_input("Tel/WhatsApp:", value="614 112 8338")
    email_ag = st.text_input("Email:", value="elena@email.com")

st.title("🏠 InmoTool Pro V6")
st.markdown("Generador de Marketing Inmobiliario Todo-en-Uno.")

tab1, tab2 = st.tabs(["📸 Diseño Gráfico", "✍️ Textos"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        tipo_op = st.radio("Operación:", ["Venta", "Renta"], horizontal=True)
        precio_in = st.text_input("Precio:", value="$1,950,000 MXN")
    with col2:
        zona_in = st.text_input("Zona:", value="Cordilleras / UACH")
        equip_in = st.text_area("Características:", value="3 Recámaras, Cerca de la UACH, Cocina integral, Parada de camión cerca")

    st.markdown("---")
    
    # CAMPO NUEVO: NOMBRE DEL ARCHIVO
    st.info("👇 Escribe cómo quieres que se llame el archivo descargable")
    nombre_archivo = st.text_input("Nombre del archivo (sin .zip):", value="Casa_Cordilleras_ClienteX")
    
    st.markdown("---")

    col_up1, col_up2 = st.columns(2)
    with col_up1:
        st.subheader("1. Fachada Principal")
        archivo_principal = st.file_uploader("Sube aquí la fachada", type=['jpg', 'png', 'jpeg'], key="main")
    with col_up2:
        st.subheader("2. Interiores")
        archivos_extras = st.file_uploader("Sube aquí el resto", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'], key="extras")

    if st.button("🚀 Generar Imágenes"):
        if not archivo_principal or not archivos_extras:
            st.error("⚠️ Sube al menos la fachada y una foto extra.")
        else:
            with st.spinner('Diseñando...'):
                zip_buffer = io.BytesIO()
                img_p = Image.open(archivo_principal)
                imgs_e = [Image.open(f) for f in archivos_extras]
                imgs_para_circulos = imgs_e.copy()
                random.shuffle(imgs_para_circulos)
                
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    # Portada
                    img_portada = procesar_portada_premium(img_p, imgs_para_circulos, tipo_op, precio_in, equip_in, nombre_ag, tel_ag, email_ag)
                    buf = io.BytesIO()
                    img_portada.save(buf, format='JPEG', quality=95)
                    zf.writestr("01_PORTADA_PREMIUM.jpg", buf.getvalue())
                    
                    st.success("¡Diseño listo!")
                    st.image(img_portada, use_container_width=True)
                    
                    # Galería
                    buf_f = io.BytesIO()
                    procesar_galeria_simple(img_p).save(buf_f, format='JPEG')
                    zf.writestr("02_fachada.jpg", buf_f.getvalue())
                    
                    for i, img in enumerate(imgs_e, start=3):
                        buf_e = io.BytesIO()
                        procesar_galeria_simple(img).save(buf_e, format='JPEG')
                        zf.writestr(f"{i:02d}_interior.jpg", buf_e.getvalue())
                
                # USAMOS EL NOMBRE PERSONALIZADO
                nombre_final = f"{nombre_archivo}.zip" if nombre_archivo else "Pack_Inmobiliario.zip"
                if not nombre_final.endswith(".zip"): nombre_final += ".zip"

                st.download_button(f"📥 Descargar {nombre_final}", data=zip_buffer.getvalue(), file_name=nombre_final, mime="application/zip", type="primary")

with tab2:
    st.header("Generador de Textos")
    if st.button("✨ Generar Descripciones"):
        variaciones = generar_textos_virales(tipo_op, zona_in, precio_in, equip_in, tel_ag, nombre_ag)
        col_t1, col_t2 = st.columns(2)
        nombres_estilos = ['Formal', 'Visual', 'Urgencia', 'Minimal', 'Emocional', '🎓 ESTUDIANTE / FORÁNEO']
        
        for i, texto in enumerate(variaciones):
            donde_mostrar = col_t1 if i % 2 == 0 else col_t2
            with donde_mostrar:
                st.subheader(f"Opción {i+1}: {nombres_estilos[i]}")
                st.text_area(f"copy_{i}", value=texto, height=300, label_visibility="collapsed")