import streamlit as st
import pandas as pd
import os
import random
import time
import matplotlib.pyplot as plt
from io import BytesIO

st.title('EDUnews Lostopf & Timer')

# Managing the Excel files for name selection
directory_path = 'klassen'
excel_files = [f for f in os.listdir(directory_path) if f.endswith('.xlsx')]
st.write('<h2>Klassenliste auswählen:</h2>', unsafe_allow_html=True)
selected_file = st.selectbox('Klassen', excel_files)

def create_group_image(groups):
    fig, ax = plt.subplots()
    group_text = "\n".join([f"{group}: {', '.join(names)}" for group, names in groups.items()])
    ax.text(0.05, 0.95, group_text, fontsize=12, ha='left', va='top', wrap=False)
    ax.axis('off')
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    return buffer

if selected_file:
    full_file_path = os.path.join(directory_path, selected_file)
    if 'current_file' not in st.session_state or st.session_state.current_file != selected_file:
        df = pd.read_excel(full_file_path)
        st.session_state.names_list = df.iloc[:, 0].tolist()
        st.session_state.current_file = selected_file

    col1, col2 = st.columns([3, 2])

    with col1:
        st.write("<h2>Teilnehmer:</h2>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(st.session_state.names_list, columns=["Namen"]))
        
        if st.button('Zufallsname auswählen') and st.session_state.names_list:
            random_name = random.choice(st.session_state.names_list)
            st.session_state.names_list.remove(random_name)
            st.success(f"Auswahl: {random_name}")
            st.dataframe(pd.DataFrame(st.session_state.names_list, columns=["Namen"]))
        
        if st.button('Liste zurücksetzen'):
            df = pd.read_excel(full_file_path)
            st.session_state.names_list = df.iloc[:, 0].tolist()
            st.dataframe(pd.DataFrame(st.session_state.names_list, columns=["Namen"]))

        num_groups = st.number_input('Anzahl der Gruppen', min_value=1, value=2, step=1)
        if st.button('Gruppen erstellen'):
            random.shuffle(st.session_state.names_list)
            groups = {f'Gruppe {i+1}': [] for i in range(num_groups)}
            for index, name in enumerate(st.session_state.names_list):
                groups[f'Gruppe {(index % num_groups) + 1}'].append(name)
            
            buffer = create_group_image(groups)
            st.download_button(label="Download Groups as Image", data=buffer, file_name="groups.png", mime="image/png")

    with col2:
        st.write("<h2>Timer:</h2>", unsafe_allow_html=True)
        timer_minutes = st.number_input('Minuten', min_value=0, value=0, step=1)
        if st.button('Start Timer'):
            timer_container = st.empty()
            t = int(timer_minutes * 60)
            while t > 0:
                mins, secs = divmod(t, 60)
                timer_value = '{:02d}:{:02d}'.format(mins, secs)
                timer_container.markdown(f'<h2>Verbleibende Zeit: {timer_value}</h2>', unsafe_allow_html=True)
                time.sleep(1)
                t -= 1
            timer_container.markdown("<h2>Zeit ist um</h2>", unsafe_allow_html=True)
