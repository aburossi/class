import streamlit as st
import pandas as pd
import os
import random
from io import BytesIO
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

st.title('Lostopf & Timer')

# Managing the text files for name selection
directory_path = 'klassen'
if not os.path.exists(directory_path):
    st.error(f"Directory '{directory_path}' does not exist.")
else:
    text_files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
    st.write('<h2>Klassenliste auswählen:</h2>', unsafe_allow_html=True)
    selected_file = st.selectbox('Klassen', text_files)

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

# Option for manual name input
manual_input = st.checkbox('Manuelle Eingabe der Namen')
if manual_input:
    names_input = st.text_area("Namen eingeben (jeder Name in einer neuen Zeile):")
    if names_input:
        st.session_state.names_list = [name.strip() for name in names_input.split('\n') if name.strip()]
        st.session_state.original_names_list = st.session_state.names_list.copy()
else:
    if selected_file:
        full_file_path = os.path.join(directory_path, selected_file)
        if 'current_file' not in st.session_state or st.session_state.current_file != selected_file:
            with open(full_file_path, 'r') as file:
                st.session_state.names_list = [line.strip() for line in file.readlines()]
                st.session_state.original_names_list = st.session_state.names_list.copy()
            st.session_state.current_file = selected_file

col1, col2 = st.columns([3, 2])

with col1:
    st.write("<h2>Teilnehmer:</h2>", unsafe_allow_html=True)
    if 'names_list' in st.session_state:
        st.dataframe(pd.DataFrame(st.session_state.names_list, columns=["Namen"]))
        
        if st.button('Zufallsname auswählen') and st.session_state.names_list:
            random_name = random.choice(st.session_state.names_list)
            st.session_state.names_list.remove(random_name)
            st.success(f"Auswahl: {random_name}")
            st.dataframe(pd.DataFrame(st.session_state.names_list, columns=["Namen"]))
        
        if st.button('Liste zurücksetzen'):
            st.session_state.names_list = st.session_state.original_names_list.copy()
            st.dataframe(pd.DataFrame(st.session_state.names_list, columns=["Namen"]))

        num_groups = st.number_input('Anzahl der Gruppen', min_value=1, value=2, step=1)
        if st.button('Gruppen erstellen'):
            random.shuffle(st.session_state.names_list)
            groups = {f'Gruppe {i+1}': [] for i in range(num_groups)}
            for index, name in enumerate(st.session_state.names_list):
                groups[f'Gruppe {(index % num_groups) + 1}'].append(name)
            
            buffer = create_group_image(groups)
            st.download_button(label="Download Groups as Image", data=buffer, file_name="groups.png", mime="image/png")
            
            # Option to export groups to CSV
            group_df = pd.DataFrame([(group, name) for group, names in groups.items() for name in names], columns=["Gruppe", "Name"])
            csv = group_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download Groups as CSV", data=csv, file_name="groups.csv", mime="text/csv")

with col2:
    st.write("<h2>Timer:</h2>", unsafe_allow_html=True)
    timer_minutes = st.number_input('Minuten', min_value=0, value=0, step=1)
    if st.button('Start Timer'):
        if 'timer_start' not in st.session_state:
            st.session_state.timer_start = time.time()
            st.session_state.timer_duration = timer_minutes * 60
        else:
            # Reset the timer if start button is pressed again
            st.session_state.timer_start = time.time()
            st.session_state.timer_duration = timer_minutes * 60

    if 'timer_start' in st.session_state:
        current_time = time.time()
        elapsed_time = current_time - st.session_state.timer_start
        remaining_time = st.session_state.timer_duration - elapsed_time
        
        if remaining_time > 0:
            mins, secs = divmod(remaining_time, 60)
            timer_value = '{:02d}:{:02d}'.format(int(mins), int(secs))
            st.markdown(f'<h2>Verbleibende Zeit: {timer_value}</h2>', unsafe_allow_html=True)
            st_autorefresh(interval=1000, key="timer_refresh")
        else:
            st.markdown("<h2>Zeit ist um</h2>", unsafe_allow_html=True)
            del st.session_state['timer_start']
            del st.session_state['timer_duration']
    
    # Embed YouTube video timer
    st.write("<h2>Alternativer Timer:</h2>", unsafe_allow_html=True)
    st.components.v1.iframe("https://www.youtube.com/embed/qgnDbQ1aM54", width=560, height=315)

