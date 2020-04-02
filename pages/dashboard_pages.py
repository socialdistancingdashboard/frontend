import streamlit as st

def parse_md_with_local_images(filename):
    ''' 
    streamlit cannot handle local image paths in markdown
    documents, therefore these have to be located and inserted
    via st.image.
    Only looks for images at line start.
    '''
    s = ''
    with open(filename,'r') as f:
        for line in f.readlines():
            if line[:2] == '![':
                st.markdown(s, unsafe_allow_html=True)
                image_url = line.split('](')[1].replace(')','').replace('\n','')
                st.image(image_url)
                s = ''
            else:
                s += line
    st.markdown(s, unsafe_allow_html=True)
    st.markdown('''
                
                ---
                ''')

def st_markdown(filename):
    with open(filename,'r') as f:
        st.markdown(f.read())