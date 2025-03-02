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
        if (
            st.session_state["username"] == "projetoestaciobeatriz"
            and st.session_state["password"] == "Scrum@2025"
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

# 📌 Carregar os dados processados
@st.cache_data
def carregar_dados():
    url = "https://raw.githubusercontent.com/beatrizcardc/Analise_WhatsApp/main/whatsapp_processado.csv"  # Substitua pelo link correto do seu GitHub
    return pd.read_csv(url)

df = carregar_dados()

# 📌 Sidebar: Filtros de Período e Categoria
st.sidebar.header("🔎 Filtros")
data_inicio = st.sidebar.date_input("Data Inicial", pd.to_datetime(df["Data"]).min())
data_fim = st.sidebar.date_input("Data Final", pd.to_datetime(df["Data"]).max())
categoria_selecionada = st.sidebar.multiselect("Selecione a(s) Categoria(s)", df["Categoria"].unique(), default=df["Categoria"].unique())

# 📌 Filtrar os dados com base na seleção do usuário
df_filtrado = df[
    (pd.to_datetime(df["Data"]) >= pd.to_datetime(data_inicio)) &
    (pd.to_datetime(df["Data"]) <= pd.to_datetime(data_fim)) &
    (df["Categoria"].isin(categoria_selecionada))
]

# 📌 Exibir Mensagens Filtradas
st.header("📅 Mensagens Filtradas")
if not df_filtrado.empty:
    st.dataframe(df_filtrado[["Data", "Hora", "Remetente", "Mensagem", "Categoria"]])
else:
    st.warning("⚠ Nenhuma mensagem encontrada para o período e categoria selecionados.")

# 📌 TOP 10 Pessoas Mais Ativas
st.header("🏆 TOP 10 Pessoas Mais Ativas")
if not df_filtrado.empty:
    top_usuarios = df_filtrado["Remetente"].value_counts().head(10)
    st.table(top_usuarios)
else:
    st.warning("⚠ Nenhum dado para exibir no ranking de usuários mais ativos.")

# 📌 Dias da Semana Mais Ativos
st.header("📅 Dias da Semana Mais Ativos")
if not df_filtrado.empty:
    df_filtrado["Dia da Semana"] = pd.to_datetime(df_filtrado["Data"]).dt.day_name()
    dias_ativos = df_filtrado["Dia da Semana"].value_counts()
    st.bar_chart(dias_ativos)
else:
    st.warning("⚠ Nenhum dado disponível para exibir os dias mais ativos.")

# 📌 Palavras Mais Frequentes
st.header("🔠 Palavras Mais Frequentes")
if not df_filtrado.empty:
    mensagens_texto = df_filtrado["Mensagem"].dropna().astype(str)  # Removendo NaN
    todas_palavras = " ".join(mensagens_texto).lower().split()
    palavras_filtradas = [word for word in todas_palavras if word not in stop_words and len(word) > 3]
    palavras_comuns = Counter(palavras_filtradas).most_common(10)
    
    if palavras_comuns:
        st.table(pd.DataFrame(palavras_comuns, columns=["Palavra", "Frequência"]))
    else:
        st.warning("⚠ Não há palavras suficientes para análise.")
else:
    st.warning("⚠ Nenhuma mensagem disponível para análise de palavras.")

# 📌 Distribuição das Categorias
st.header("📊 Distribuição das Categorias")
if not df_filtrado.empty:
    categorias_count = df_filtrado["Categoria"].value_counts()

    fig, ax = plt.subplots()
    categorias_count.plot(kind="bar", ax=ax, color="skyblue")
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.warning("⚠ Nenhuma categoria encontrada no período selecionado.")

# 📌 Seleção das 2 Categorias Mais Importantes
st.sidebar.header("🌟 Engajamento")
categoria1 = st.sidebar.selectbox("Escolha a 1ª Categoria Mais Importante", df["Categoria"].unique())
categoria2 = st.sidebar.selectbox("Escolha a 2ª Categoria Mais Importante", df["Categoria"].unique())

# 📌 Conselhos para Melhorar o Engajamento
st.header("📢 Dicas para Melhorar o Engajamento")
dicas = {
    "Boas-vindas e Entradas no Grupo": "Envie mensagens personalizadas de boas-vindas e incentive apresentações.",
    "Compartilhamento de Conteúdo e Links": "Poste conteúdos relevantes e incentive o compartilhamento de materiais informativos.",
    "Discussões Técnicas e Consultas": "Proponha perguntas instigantes e crie enquetes para gerar mais interação.",
    "Convites e Organização de Eventos": "Divulgue eventos com antecedência e envie lembretes frequentes.",
    "Mensagens de Apoio, Felicitações e Informais": "Celebre conquistas do grupo e crie um ambiente acolhedor.",
}

st.write(f"💡 **Dicas para aumentar {categoria1}:** {dicas[categoria1]}")
st.write(f"💡 **Dicas para aumentar {categoria2}:** {dicas[categoria2]}")

# 📌 Rodapé
st.markdown("---")
st.markdown("📌 **Projeto desenvolvido por Beatriz Cardoso Cunha com Scrum para análise de grupos do WhatsApp.**")



