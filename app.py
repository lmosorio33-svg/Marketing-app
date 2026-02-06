import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
import io
import zipfile
import random
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="InmoTool Pro V8", page_icon="🏠", layout="wide")

# --- FUNCIÓN DE FUENTE SEGURA (ESTA ES LA CLAVE) ---
def cargar_fuente(tipo, tamano):
    """
    Carga las fuentes Roboto que pusiste en la carpeta del proyecto.
    Esto funciona igual en Windows, Mac y Linux (Nube).
    """
    # Nombres EXACTOS de los archivos que descargaste
    archivo_bold = "Roboto-Bold.ttf"
    archivo_regular = "Roboto-Regular.ttf"

    # Elegir cuál archivo usar
    if tipo == "bold":
        ruta_fuente = archivo_bold
    else:
        ruta_fuente = archivo_regular
    
    try:
        # Intenta cargar el archivo que está junto a app.py
        return ImageFont.truetype(ruta_fuente, tamano)
    except:
        # Si entra aquí, es porque NO pusiste los archivos .ttf en la carpeta
        print(f"⚠️ ALERTA: No encontré el archivo '{ruta_fuente}'. Usando fuente fea por defecto.")
        return ImageFont.load_default()

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

    # 1. Foto Principal (Curva)
    img_fachada = img_principal.convert("RGB")
    ALTO_FACHADA = 650
    CURVA = 150
    img_fachada = ImageOps.fit(img_fachada, (W, ALTO_FACHADA), method=Image.LANCZOS)
    mascara = crear_mascara_curva(W, ALTO_FACHADA, CURVA)
    img_fachada.putalpha(mascara)
    lienzo.paste(img_fachada, (0, 0), img_fachada)

    # 2. Cargar Fuentes (Usando los archivos locales)
    font_titulo_grande = cargar_fuente("bold", 130)
    font_titulo_peq = cargar_fuente("regular", 60) # Usamos "regular" para texto normal
    font_subtitulo = cargar_fuente("bold", 40)
    font_texto = cargar_fuente("regular", 30)
    font_precio = cargar_fuente("bold", 55)
    font_contacto = cargar_fuente("regular", 22)

    # 3. Dibujar Textos
    X_MARGIN = 60
    Y_POS = ALTO_FACHADA - CURVA + 50

    draw.text((X_MARGIN, Y_POS), "CASA", font=font_titulo_grande, fill=COLOR_TEXTO)
    Y_POS += 130
    draw.text((X_MARGIN, Y_POS), f"en {tipo_op.lower()}", font=font_titulo_peq, fill=COLOR_TEXTO)
    
    Y_POS += 120
    draw.text((X_MARGIN, Y_POS), "Características:", font=font_subtitulo, fill=COLOR_TEXTO)
    
    bbox_sub = draw.textbbox((0,0), "Características:", font=font_subtitulo)
    ancho_sub = bbox_sub[2] - bbox_sub[0]
    draw.line([(X_MARGIN, Y_POS + 45), (X_MARGIN + ancho_sub, Y_POS + 45)], fill=COLOR_ACENTO, width=3)
    
    Y_POS += 60
    lineas_equip = equipamiento.split(',')
    for linea in lineas_equip[:5]: 
        texto_linea = f"• {linea.strip()}"
        if len(texto_linea) > 35: texto_linea = texto_linea[:32] + "..."
        draw.text((X_MARGIN + 20, Y_POS), texto_linea, font=font_texto, fill=COLOR_TEXTO)
        Y_POS += 45

    # 4. Caja de Precio
    Y_PRECIO = H - 250
    ANCHO_CAJA = 550
    ALTO_CAJA = 100
    draw.rectangle([(X_MARGIN, Y_PRECIO), (X_MARGIN + ANCHO_CAJA, Y_PRECIO + ALTO_CAJA)], fill=COLOR_ACENTO)
    
    bbox = draw.textbbox((0,0), precio, font=font_precio)
    x_txt = X_MARGIN + (ANCHO_CAJA - (bbox[2] - bbox[0])) // 2
    y_txt = Y_PRECIO + (ALTO_CAJA - (bbox[3] - bbox[1])) // 2 - 10
    draw.text((x_txt, y_txt), precio, font=font_precio, fill="black")

    # 5. Datos de Contacto
    Y_CONTACTO = Y_PRECIO + ALTO_CAJA + 30
    draw.text((X_MARGIN, Y_CONTACTO), f"Asesor: {nombre}", font=font_contacto, fill=COLOR_TEXTO)
    draw.text((X_MARGIN, Y_CONTACTO + 30), f"📞 {telefono} | ✉️ {correo}", font=font_contacto, fill=COLOR_TEXTO)

    # 6. Círculos
    config_circulos = [
        {"pos": (550, 500), "diam": 420}, 
        {"pos": (650, 850), "diam": 350}, 
        {"pos": (500, 1100), "diam": 300}
    ]
    fotos_disp = lista_extras if lista_extras else [img_principal]
    
    for i, cfg in enumerate(config_circulos):
        img_base = fotos_disp[i % len(fotos_disp)] 
        img_circ = recortar_circulo_con_borde(img_base, cfg["diam"], COLOR_ACENTO, 8)
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
# (El resto del código de textos sigue igual...)
def generar_textos_virales(tipo, zona, precio, equipamiento, contacto, nombre):
    lista_items = [item.strip() for item in equipamiento.split(',')]
    bullets_estrellas = "\n".join([f"✨ {item}" for item in lista_items])
    bullets_checks = "\n".join([f"✅ {item}" for item in lista_items])
    bullets_uni = "\n".join([f"🎓 {item}" for item in lista_items])

    plantillas = []
    plantillas.append(f"""🏡 {tipo.upper()} DE CASA - ZONA {zona.upper()}\n\n📍 UBICACIÓN PRIVILEGIADA\n💵 {precio}\n\n💠 DISTRIBUCIÓN:\n{bullets_checks}\n\n‼️ SE ACEPTAN CRÉDITOS ‼️\n\nINFORMES:\n📞 {contacto} con {nombre}""")
    plantillas.append(f"""🌳 Casa en {zona}, ubicación inmejorable\n💲 Precio: {precio}\n\nCaracterísticas:\n{bullets_estrellas}\n\n✨ Espacios amplios\n📲 Citas: {contacto} ({nombre})""")
    plantillas.append(f"""🔥 OPORTUNIDAD EN {zona.upper()} 🔥\n💰 PRECIO: {precio}\n\nTu nuevo hogar:\n{bullets_checks}\n\n🏃‍♂️ ¡Que no te la ganen!\n👉 {contacto}""")
    plantillas.append(f"""📍 {zona} | 💲 {precio}\n🏠 Se {tipo.lower()}:\n\n{bullets_estrellas}\n\nℹ️ Citas: {contacto}""")
    plantillas.append(f"""😍 Estrena casa en {zona}\n💎 Inversión: {precio}\n\nDetalles:\n{bullets_estrellas}\n\n🔑 ¡Ven a conocerla!\n📲 {contacto}""")
    plantillas.append(f"""🎓 ¡ATENCIÓN ESTUDIANTES! 🎓\n📍 Zona: {zona} (Ideal UACH/Tec)\n\n💲 Renta: {precio}\n\n¿Buscas depa o casa cerca de la uni?\n{bullets_uni}\n\n✅ Transporte cercano\n✅ Zona segura\n✅ Ideal para Roomies\n\n🍕 ¡Agenda tu visita!\n📲 {contacto} con {nombre}""")
    return plantillas

# --- INTERFAZ ---

with st.sidebar:
    st.header("👤 Datos del Asesor")
    nombre_ag = st.text_input("Nombre:", value="Elena Montes")
    tel_ag = st.text_input("Tel/WhatsApp:", value="614 112 8338")
    email_ag = st.text_input("Email:", value="elena@email.com")

st.title("🏠 InmoTool Pro V8 (Fuentes Incluidas)")
st.markdown("Generador de Marketing Inmobiliario Todo-en-Uno.")

tab1, tab2 = st.tabs(["📸 Diseño Gráfico", "✍️ Textos"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        tipo_op = st.radio("Operación:", ["Venta", "Renta"], horizontal=True)
        precio_in = st.text_input("Precio:", value="$1,950,000 MXN")
    with col2:
        zona_in = st.text_input("Zona:", value="Cordilleras / UACH")
        equip_in = st.text_area("Características (separadas por coma):", value="3 Recámaras, Cerca de la UACH, Cocina integral, Cochera doble")

    st.markdown("---")
    st.info("👇 Nombre del archivo para descargar")
    nombre_archivo = st.text_input("Nombre del archivo:", value="Casa_Cordilleras")
    st.markdown("---")

    col_up1, col_up2 = st.columns(2)
    with col_up1:
        st.subheader("1. Fachada Principal")
        archivo_principal = st.file_uploader("Sube la fachada (Imagen Principal)", type=['jpg', 'png', 'jpeg'], key="main")
    with col_up2:
        st.subheader("2. Interiores")
        archivos_extras = st.file_uploader("Sube el resto (Para los círculos)", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'], key="extras")

    if st.button("🚀 Generar Imágenes"):
        if not archivo_principal:
            st.error("⚠️ Por favor sube al menos la Foto Principal.")
        else:
            with st.spinner('Creando diseño profesional...'):
                zip_buffer = io.BytesIO()
                img_p = Image.open(archivo_principal)
                if archivos_extras:
                    imgs_e = [Image.open(f) for f in archivos_extras]
                else:
                    imgs_e = [img_p]
                imgs_para_circulos = imgs_e.copy()
                random.shuffle(imgs_para_circulos)

                img_portada = procesar_portada_premium(img_p, imgs_para_circulos, tipo_op, precio_in, equip_in, nombre_ag, tel_ag, email_ag)

                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    buf = io.BytesIO()
                    img_portada.save(buf, format='JPEG', quality=95)
                    zf.writestr("01_PORTADA_PREMIUM.jpg", buf.getvalue())
                    buf_f = io.BytesIO()
                    procesar_galeria_simple(img_p).save(buf_f, format='JPEG')
                    zf.writestr("02_fachada.jpg", buf_f.getvalue())
                    for i, img in enumerate(imgs_e, start=3):
                        buf_e = io.BytesIO()
                        procesar_galeria_simple(img).save(buf_e, format='JPEG')
                        zf.writestr(f"{i:02d}_interior.jpg", buf_e.getvalue())

                st.success("¡Diseño generado con éxito!")
                st.subheader("👀 Vista Previa:")
                st.image(img_portada, caption="Portada Generada", use_container_width=True)

                nombre_final = f"{nombre_archivo}.zip" if nombre_archivo else "Pack_Inmobiliario.zip"
                if not nombre_final.endswith(".zip"): nombre_final += ".zip"

                st.download_button(
                    label=f"📥 Descargar {nombre_final}",
                    data=zip_buffer.getvalue(),
                    file_name=nombre_final,
                    mime="application/zip",
                    type="primary"
                )

with tab2:
    st.header("Generador de Textos")
    if st.button("✨ Generar Descripciones"):
        variaciones = generar_textos_virales(tipo_op, zona_in, precio_in, equip_in, tel_ag, nombre_ag)
        col_t1, col_t2 = st.columns(2)
        titulos = ['Formal', 'Visual', 'Urgencia', 'Minimal', 'Emocional', '🎓 ESTUDIANTE']
        
        for i, texto in enumerate(variaciones):
            donde = col_t1 if i % 2 == 0 else col_t2
            with donde:
                st.subheader(f"Opción {i+1}: {titulos[i]}")
                st.text_area(f"txt_{i}", value=texto, height=250)