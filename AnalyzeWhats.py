import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.util import ngrams
import io

nltk.download("stopwords")
stop_words = set(stopwords.words("portuguese"))

# 📌 Configuração do Login
def check_password():
    """Verifica se o usuário e senha estão corretos."""
    def password_entered():
        if (
            st.session_state.get("username") == "projetoestaciobeatriz"
            and st.session_state.get("password") == "Scrum@2025"
        ):
            st.session_state["authenticated"] = True
        else:
            st.session_state["authenticated"] = False
            st.warning("Usuário ou senha incorretos!")

    if "authenticated" not in st.session_state:
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password")
        st.button("Login", on_click=password_entered)
        return False
    elif not st.session_state["authenticated"]:
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password")
        st.button("Login", on_click=password_entered)
        return False
    return True

# Verifica login antes de carregar o app
if not check_password():
    st.stop()

# 📌 Nome e Introdução do Aplicativo (Agora no TOPO)
st.title("📊 AnalyzeWhats - Análise de Mensagens do WhatsApp")

st.markdown("""
### 📌 Sobre o AnalyzeWhats
O **AnalyzeWhats** é um aplicativo desenvolvido para analisar interações em grupos de Cursos do WhatsApp.  
Com ele, você pode visualizar estatísticas sobre participação dos usuários, tipos de mensagens mais frequentes e gerar **insights** para engajar mais seu grupo.

### 🔎 O que você pode fazer aqui?
✅ **Filtrar mensagens** por período e categorias específicas  
✅ **Descobrir quem são os usuários mais ativos** no grupo  
✅ **Analisar os dias mais movimentados** no WhatsApp  
✅ **Identificar as palavras mais frequentes** nas mensagens  
✅ **Ver a distribuição de mensagens por categoria**  
✅ **Obter sugestões para aumentar o engajamento**  

Use os **filtros na barra lateral** para personalizar sua análise!  
""")

# 📌 Criar variável no `session_state` para armazenar o arquivo
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None

# 📌 Criar botão para resetar e limpar o upload
if st.button("🔄 Limpar e carregar novo arquivo"):
    st.session_state["uploaded_file"] = None
    st.rerun()

# 📌 Upload do arquivo (Agora abaixo da explicação)
uploaded_file = st.file_uploader("📂 Faça o upload do arquivo .txt exportado do WhatsApp", type=["txt"])

# 📌 Verifica se um novo arquivo foi carregado e salva no session_state
if uploaded_file is not None:
    st.session_state["uploaded_file"] = uploaded_file

# 📌 Se nenhum arquivo foi carregado, parar execução
if st.session_state["uploaded_file"] is None:
    st.warning("⚠ Nenhum arquivo carregado. Faça o upload de um arquivo .txt para começar a análise.")
    st.stop()

# 📌 Função para processar o arquivo do WhatsApp
def processar_arquivo(file):
    """Processa o arquivo de conversa exportado do WhatsApp."""
    lines = file.getvalue().decode("utf-8").split("\n")
    
    message_pattern = re.compile(r"(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2}) - ([^:]+): (.+)")
    data = []

    for line in lines:
        match = message_pattern.match(line)
        if match:
            date, time, sender, message = match.groups()
            data.append([date, time, sender, message])

    df = pd.DataFrame(data, columns=["Data", "Hora", "Remetente", "Mensagem"])
    df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y")

    return df

# 📌 Processar o arquivo carregado
df = processar_arquivo(st.session_state["uploaded_file"])

# 📌 Exibir DataFrame processado
st.write("✅ **Arquivo processado com sucesso!** Visualizando os primeiros registros:")
st.dataframe(df.head())

# 📌 Dias da Semana Mais Ativos
st.header("📅 Dias da Semana Mais Ativos")

if not df.empty:
    df["Dia da Semana"] = pd.to_datetime(df["Data"]).dt.day_name()

    # 🔹 Definir a ordem correta dos dias da semana (Segunda → Domingo)
    ordem_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # 🔹 Criar um tipo categórico para garantir a ordenação
    df["Dia da Semana"] = pd.Categorical(df["Dia da Semana"], categories=ordem_dias, ordered=True)

    # 🔹 Contar mensagens e ordenar corretamente
    dias_ativos = df["Dia da Semana"].value_counts().sort_index()

    # 📊 Exibir gráfico com os dias organizados na ordem correta
    st.bar_chart(dias_ativos)

else:
    st.warning("⚠ Nenhum dado disponível para exibir os dias mais ativos.")

# 📌 Frases Mais Frequentes
st.header("🔠 Frases Mais Frequentes")

if not df.empty:
    mensagens_texto = df["Mensagem"].dropna().astype(str)

    # 🔹 Tokenizar as mensagens em palavras
    todas_palavras = " ".join(mensagens_texto).lower().split()

    # 🔹 Remover stopwords e palavras pequenas
    palavras_filtradas = [word for word in todas_palavras if word not in stop_words and len(word) > 3]

    # 🔹 Criar n-gramas (trigramas - frases de 4 palavras)
    trigrams = list(ngrams(palavras_filtradas, 4))  # Gera frases com 3 palavras

    # 🔹 Contar as frases mais frequentes
    frases_comuns = Counter(trigrams).most_common(10)

    # 🔹 Formatando as frases para exibição
    frases_formatadas = [(" ".join(frase), contagem) for frase, contagem in frases_comuns]

    if frases_formatadas:
        st.table(pd.DataFrame(frases_formatadas, columns=["Frase", "Frequência"]))
    else:
        st.warning("⚠ Não há frases suficientes para análise.")
else:
    st.warning("⚠ Nenhuma mensagem disponível para análise de frases.")

# 📌 Rodapé
st.markdown("---")
st.markdown("📌 **Projeto desenvolvido por Beatriz Cardoso Cunha com Scrum para análise de grupos do WhatsApp.**")
