import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")
stop_words = set(stopwords.words("portuguese"))

# 📌 Configuração do Login
def check_password():
    """Verifica se o usuário e senha estão corretos."""
    def password_entered():
        if st.session_state["username"] == "projetoestaciobeatriz" and st.session_state["password"] == "Scrum@2025":
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

# 📌 Carregar os dados processados
@st.cache_data
def carregar_dados():
    return pd.read_csv("whatsapp_processado.csv")

df = carregar_dados()

# 📌 Filtros: Selecionar data e categoria
st.sidebar.header("🔎 Filtros")
data_selecionada = st.sidebar.date_input("Selecione a Data", pd.to_datetime(df["Data"]).min())
categoria_selecionada = st.sidebar.selectbox("Selecione a Categoria", df["Categoria"].unique())

# Filtrar dados conforme a seleção do usuário
df_filtrado = df[(pd.to_datetime(df["Data"]) == pd.to_datetime(data_selecionada)) & (df["Categoria"] == categoria_selecionada)]

# 📌 Exibir Mensagens Filtradas
st.header("📅 Mensagens Filtradas")
st.dataframe(df_filtrado[["Data", "Hora", "Remetente", "Mensagem"]])

# 📌 TOP 10 Pessoas Mais Ativas
st.header("🏆 TOP 10 Pessoas Mais Ativas")
top_usuarios = df["Remetente"].value_counts().head(10)
st.table(top_usuarios)

# 📌 Dias da Semana Mais Ativos
st.header("📅 Dias da Semana Mais Ativos")
df["Dia da Semana"] = pd.to_datetime(df["Data"]).dt.day_name()
dias_ativos = df["Dia da Semana"].value_counts()
st.bar_chart(dias_ativos)

# 📌 Palavras Mais Frequentes
from collections import Counter
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")
stop_words = set(stopwords.words("portuguese"))

# Processar palavras mais frequentes
todas_palavras = " ".join(df["Mensagem"]).lower().split()
palavras_filtradas = [word for word in todas_palavras if word not in stop_words and len(word) > 3]
palavras_comuns = Counter(palavras_filtradas).most_common(10)

# Exibir as palavras mais frequentes
st.header("🔠 Palavras Mais Frequentes")
st.table(pd.DataFrame(palavras_comuns, columns=["Palavra", "Frequência"]))

# 📌 Gráfico da Distribuição das Categorias
st.header("📊 Distribuição das Categorias")
categorias_count = df["Categoria"].value_counts()
fig, ax = plt.subplots()
categorias_count.plot(kind="bar", ax=ax)
st.pyplot(fig)

# 📌 Seleção das 2 Categorias Mais Importantes
st.sidebar.header("🌟 Engajamento")
categoria1 = st.sidebar.selectbox("Escolha a 1ª Categoria Mais Importante", df["Categoria"].unique())
categoria2 = st.sidebar.selectbox("Escolha a 2ª Categoria Mais Importante", df["Categoria"].unique())

# 📌 Conselhos para Aumentar o Engajamento
st.header("📢 Dicas para Melhorar o Engajamento")
dicas = {
    "Boas-vindas e Entradas no Grupo": "Envie mensagens personalizadas de boas-vindas e incentive apresentações.",
    "Compartilhamento de Conteúdo e Links": "Poste conteúdos relevantes e incentive o compartilhamento de materiais informativos.",
    "Discussões Técnicas e Consultas": "Proponha perguntas instigantes e crie enquetes para gerar mais interação.",
    "Convites e Organização de Eventos": "Divulgue eventos com antecedência e envie lembretes frequentes.",
    "Mensagens de Apoio, Felicitações e Informais": "Celebre conquistas do grupo e crie um ambiente acolhedor."
}

st.write(f"💡 **Dicas para aumentar {categoria1}:** {dicas[categoria1]}")
st.write(f"💡 **Dicas para aumentar {categoria2}:** {dicas[categoria2]}")

# 📌 Rodapé
st.markdown("---")
st.markdown("📌 **Projeto desenvolvido por Beatriz Cardoso Cunha com Scrum para análise de grupos do WhatsApp.**")

