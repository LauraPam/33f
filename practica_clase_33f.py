import streamlit as st
from groq import Groq

import os
import glob
import re

st.set_page_config(page_title="Actividad de Clase 33: El Esqueleto de la Misión", layout="wide")

# ------------------------------------------------------------
# 1. FUNCIONES PARA MANEJAR MULTIPLES CHATS (ARCHIVOS TXT)
# ------------------------------------------------------------
def limpiar_nombre_archivo(nombre):
    """Convierte el nombre del usuario en un nombre de archivo válido."""
    nombre_seguro = nombre.strip().lower().replace(" ", "_")
    return re.sub(r'[^a-z0-9_]', '', nombre_seguro)

def listar_chats():
    """Busca todos los archivos de chat en el directorio actual."""
    archivos = glob.glob("chat_*.txt")
    chats = []
    for f in archivos:
        nombre_limpio = f.replace("chat_", "").replace(".txt", "").replace("_", " ").capitalize()
        chats.append(nombre_limpio)
    chats.sort()
    return chats

def guardar_en_historial(nombre_chat, pregunta, respuesta):
    """Añade una nueva entrada al archivo txt del chat seleccionado."""
    nombre_seguro = limpiar_nombre_archivo(nombre_chat)
    nombre_archivo = f"chat_{nombre_seguro}.txt"
    with open(nombre_archivo, mode="a", encoding="utf-8") as f:
        f.write(f"Pregunta Usuario:\n{pregunta}\n")
        f.write(f"Respuesta IA:\n{respuesta}\n")
        f.write("--------------------------------------------------------------------------------\n")

def leer_historial(nombre_chat):
    """Devuelve el contenido completo del chat seleccionado."""
    if not nombre_chat:
        return ""
    nombre_seguro = limpiar_nombre_archivo(nombre_chat)
    nombre_archivo = f"chat_{nombre_seguro}.txt"
    try:
        with open(nombre_archivo, mode="r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def obtener_historial_para_ia(nombre_chat):
    """Lee el archivo de texto y lo formatea como la lista de mensajes para Groq."""
    contenido = leer_historial(nombre_chat)
    mensajes_ia = []
    
    if not contenido:
        return mensajes_ia

    bloques = contenido.split("--------------------------------------------------------------------------------\n")
    
    for bloque in bloques:
        if "Pregunta Usuario:" in bloque and "Respuesta IA:" in bloque:
            partes = bloque.split("Respuesta IA:\n")
            pregunta = partes[0].replace("Pregunta Usuario:\n", "").strip()
            respuesta = partes[1].strip()
            
            mensajes_ia.append({"role": "user", "content": pregunta})
            mensajes_ia.append({"role": "assistant", "content": respuesta})
            
    return mensajes_ia

def eliminar_chat_fisico(nombre_chat):
    """Elimina permanentemente el archivo txt del chat seleccionado."""
    nombre_seguro = limpiar_nombre_archivo(nombre_chat)
    nombre_archivo = f"chat_{nombre_seguro}.txt"
    if os.path.exists(nombre_archivo):
        os.remove(nombre_archivo)

def obtener_system_prompt(nivel):
    """Devuelve el texto del system prompt según la elección del usuario."""
    if nivel == "Básico":
        return "Actúa como una IA básica. Responde de forma muy escueta a todas las consultas del usuario."
    elif nivel == "Medio":
        return "Actúa como una IA con conocimientos medios. Responde de forma resumida a las consultas del usuario."
    elif nivel == "Experto":
        return "Actúa como una IA experta. Responde con detalle y profundidad a todas las consultas del usuario."
    else:
        st.error("Por favor selecciona un nivel de experto en IA.")
        return "Eres un asistente útil."
# ------------------------------------------------------------
# 2. CONFIGURACIÓN DE LA BARRA LATERAL (GESTIÓN DE CHATS)
# ------------------------------------------------------------
with st.sidebar:
    st.title("🚀 Actividad de Clase: El Esqueleto de la Misión")
    st.image("img/lala.jpeg", caption="Imagen Añadida Laura Pam")
    
    st.divider()
    st.subheader("📁 Gestión de Chats")
    
    lista_de_chats = listar_chats()
    
    if not lista_de_chats:
        lista_de_chats = ["Chat principal"]
        with open("chat_chat_principal.txt", "w", encoding="utf-8") as f:
            f.write("")
        
    # Crear nuevo chat
    with st.popover("➕ Crear Nuevo Chat"):
        nuevo_nombre = st.text_input("Nombre del chat:", placeholder="Ej. Tarea Historia, Dudas Python...")
        if st.button("Confirmar y Crear"):
            if nuevo_nombre.strip() != "":
                nombre_formateado = nuevo_nombre.strip().capitalize()
                nombre_seguro = limpiar_nombre_archivo(nombre_formateado)
                with open(f"chat_{nombre_seguro}.txt", "w", encoding="utf-8") as f:
                    f.write("")
                st.session_state.chat_actual = nombre_formateado
                st.rerun()
            else:
                st.warning("El nombre no puede estar vacío.")

    # Control de estados de sesión
    if "chat_actual" not in st.session_state:
        st.session_state.chat_actual = lista_de_chats[0]

    if st.session_state.chat_actual not in lista_de_chats:
        st.session_state.chat_actual = lista_de_chats[0]

    # Selector de chat activo
    chat_seleccionado = st.selectbox(
        "Selecciona el chat activo:",
        lista_de_chats,
        index=lista_de_chats.index(st.session_state.chat_actual),
        key="selector_chat"
    )
    st.session_state.chat_actual = chat_seleccionado

    # BOTÓN PARA DESCARGAR EL HISTORIAL ACTUAL
    st.divider()
    st.subheader("📥 Exportar")
    historial_bruto = leer_historial(st.session_state.chat_actual)
    
    st.download_button(
        label="⬇️ Descargar Historial (.txt)",
        data=historial_bruto,
        file_name=f"historial_{limpiar_nombre_archivo(st.session_state.chat_actual)}.txt",
        mime="text/plain",
        disabled=not bool(historial_bruto.strip())
    )

    # BOTÓN PARA BORRAR EL HISTORIAL ACTUAL
    st.subheader("⚠️ Zona de Peligro")
    with st.popover("🗑️ Eliminar Chat Actual"):
        st.warning(f"¿Seguro que deseas borrar permanentemente el archivo de '{st.session_state.chat_actual}'?")
        if st.button("Sí, borrar para siempre"):
            eliminar_chat_fisico(st.session_state.chat_actual)
            st.toast(f"Archivo de {st.session_state.chat_actual} eliminado.")
            # Forzar reajuste de la sesión al primer chat disponible
            nuevos_chats = listar_chats()
            st.session_state.chat_actual = nuevos_chats[0] if nuevos_chats else "Chat principal"
            st.rerun()
    # Historial bruto de depuración en la barra lateral
    st.divider()
    st.subheader(f"Archivo de texto bruto:")
    st.text_area("Contenido del archivo actual", historial_bruto if historial_bruto else "Vacío", height=150)
# ------------------------------------------------------------
# 3. CUERPO PRINCIPAL DE LA APLICACIÓN
# ------------------------------------------------------------
st.subheader("Práctica clase día 33f - entrenamiento para tarea final de módulo")
st.info(f"💬 Conversando actualmente en: **{st.session_state.chat_actual}**")

col1, col2 = st.columns([3, 1])  # Proporción para dar más espacio visual al chat (col1)

with col2:
    st.markdown("### ⚙️ Parámetros de la IA")
    temperatura = st.slider(
        "Seleccione temperatura de pensamiento IA",
        min_value=0.0, max_value=2.0, value=0.7, step=0.1
    )

    nivel = st.selectbox(
        "Seleccione TIPO de expert en IA",
        ["Básico", "Medio", "Experto"]
    )

# ------------------------------------------------------------
# 4. RENDERIZADO VISUAL E INTERFACES DE CHAT (EN COL1)
# ------------------------------------------------------------
with col1:
    st.markdown("### 💬 Interfaz de Chat")
    
    historial_pantalla = obtener_historial_para_ia(st.session_state.chat_actual)
    
    # Renderizamos los mensajes dentro de la caja con scroll
    contenedor_chat = st.container(height=450, border=True)
    with contenedor_chat:
        if not historial_pantalla:
            st.caption("No hay mensajes en este chat todavía. Escribe tu consulta en la barra inferior.")
        else:
            for msg in historial_pantalla:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    
# BARRA DE ESCRITURA FLOTANTE NATIVA (correctamente indentada en col1)
prompt = st.chat_input("Escribe tu consulta aquí y presiona Enter...")
# ------------------------------------------------------------
# 5. LÓGICA DE PROCESAMIENTO AL RECIBIR ENTRADA DEL CHAT_INPUT
# ------------------------------------------------------------
if prompt:
    if prompt.strip() != "":
        try:
            historial_previo = obtener_historial_para_ia(st.session_state.chat_actual)
            system_prompt = obtener_system_prompt(nivel)
            
            mensajes_completos = [{"role": "system", "content": system_prompt}] + historial_previo + [{"role": "user", "content": prompt}]
            
            cliente = Groq(api_key=st.secrets["GROQ_API_KEY"])
            respuesta = cliente.chat.completions.create(
                model="llama-3.1-8b-instant",  
                messages=mensajes_completos,
                temperature=temperatura
            )
            texto_respuesta = respuesta.choices[0].message.content
            
            # Guardamos e inmediatamente refrescamos para pintar los cambios en el contenedor
            guardar_en_historial(st.session_state.chat_actual, prompt, texto_respuesta)
            st.rerun()
            
        except Exception as e:
            st.error(f"Fallo en el enlace con la IA: {e}")


