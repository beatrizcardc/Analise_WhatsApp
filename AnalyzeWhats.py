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

# 📌 Processar o arquivo carregado
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

    # 📌 Categorizar mensagens
    def categorizar_mensagem(mensagem):
        mensagem = mensagem.lower()
        if any(word in mensagem for word in ["bem-vindo", "boas-vindas", "seja bem", "novo membro"]):
            return "Boas-vindas e Entradas no Grupo"
        if re.search(r"https?://\S+|www\.\S+", mensagem):
            return "Compartilhamento de Conteúdo e Links"
        if "?" in mensagem or any(word in mensagem for word in ["como", "qual", "quando", "onde", "por que"]):
            return "Discussões Técnicas e Consultas"
        if any(word in mensagem for word in ["reunião", "evento", "live", "webinar"]):
            return "Convites e Organização de Eventos"
        if any(word in mensagem for word in ["parabéns", "feliz aniversário", "sucesso", "abraços"]):
            return "Mensagens de Apoio e Felicitações"
        return "Outro"

    df["Categoria"] = df["Mensagem"].apply(categorizar_mensagem)

    return df

df = processar_arquivo(st.session_state["uploaded_file"])

# 📌 Sidebar: Filtros
st.sidebar.header("🔎 Filtros")
data_inicio = st.sidebar.date_input("Data Inicial", df["Data"].min())
data_fim = st.sidebar.date_input("Data Final", df["Data"].max())
categoria_selecionada = st.sidebar.multiselect("Selecione a(s) Categoria(s)", df["Categoria"].unique(), default=df["Categoria"].unique())

# 📌 Aplicar filtros
df_filtrado = df[
    (df["Data"] >= pd.to_datetime(data_inicio)) & 
    (df["Data"] <= pd.to_datetime(data_fim)) & 
    (df["Categoria"].isin(categoria_selecionada))
]

# 📌 Exibir DataFrame processado
st.write("✅ **Arquivo processado com sucesso!** Visualizando os primeiros registros:")
st.dataframe(df_filtrado.head())

# 📌 TOP 10 Pessoas Mais Ativas
st.header("🏆 TOP 10 Pessoas Mais Ativas")

if not df_filtrado.empty:
    top_usuarios = df_filtrado["Remetente"].value_counts().head(10)
    st.table(top_usuarios)
else:
    st.warning("⚠ Nenhum dado para exibir no ranking de usuários mais ativos.")

# 📌 TOP 10 Pessoas Menos Ativas
st.header("📉 TOP 10 Pessoas Menos Ativas")

if not df_filtrado.empty:
    menos_ativos = df_filtrado["Remetente"].value_counts().tail(10)  # Pega os últimos 10 usuários menos ativos
    st.table(menos_ativos)
else:
    st.warning("⚠ Nenhum dado para exibir no ranking de usuários menos ativos.")


# 📌 Dias da Semana Mais Ativos
st.header("📅 Dias da Semana Mais Ativos")

if not df_filtrado.empty:
    df_filtrado["Dia da Semana"] = pd.to_datetime(df_filtrado["Data"]).dt.day_name()

    # 🔹 Definir a ordem correta dos dias da semana (Segunda → Domingo)
    ordem_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # 🔹 Criar um tipo categórico para garantir a ordenação
    df_filtrado["Dia da Semana"] = pd.Categorical(df_filtrado["Dia da Semana"], categories=ordem_dias, ordered=True)

    # 🔹 Contar mensagens e ordenar corretamente
    dias_ativos = df_filtrado["Dia da Semana"].value_counts().sort_index()

    # 📊 Exibir gráfico com os dias organizados na ordem correta
    st.bar_chart(dias_ativos)

else:
    st.warning("⚠ Nenhum dado disponível para exibir os dias mais ativos.")

# 📌 Distribuição das Categorias
st.header("📊 Distribuição das Categorias")

if not df_filtrado.empty:
    categorias_count = df_filtrado["Categoria"].value_counts()

    fig, ax = plt.subplots(figsize=(8,6))
    categorias_count.plot(kind="bar", ax=ax, color="skyblue", edgecolor="black")

    # Melhorando a formatação do gráfico
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(fontsize=10)
    plt.xlabel("Categoria", fontsize=12)
    plt.ylabel("Quantidade", fontsize=12)
    plt.title("Distribuição de Mensagens por Categoria", fontsize=14)

    st.pyplot(fig)
else:
    st.warning("⚠ Nenhuma categoria encontrada no período selecionado.")

# 📌 Frases Mais Frequentes
st.header("🔠 Frases Mais Frequentes")

if not df_filtrado.empty:
    mensagens_texto = df_filtrado["Mensagem"].dropna().astype(str)

    # 🔹 Tokenizar as mensagens em palavras
    todas_palavras = " ".join(mensagens_texto).lower().split()

    # 🔹 Remover stopwords e palavras pequenas
    palavras_filtradas = [word for word in todas_palavras if word not in stop_words and len(word) > 3]

    # 🔹 Criar n-gramas (trigramas - frases de 3 palavras)
    trigrams = list(ngrams(palavras_filtradas, 3))  # Gera frases com 3 palavras

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

# 📌 Engajamento
st.sidebar.header("🌟 Engajamento - Selecione 2 categorias principais para obter dicas de engajamento")
categoria1 = st.sidebar.selectbox("Escolha a 1ª Categoria", df["Categoria"].unique())
categoria2 = st.sidebar.selectbox("Escolha a 2ª Categoria", df["Categoria"].unique())

# 📌 Conselhos para Melhorar o Engajamento
st.header("📢 Dicas para Melhorar o Engajamento")
dicas = {
    "Boas-vindas e Entradas no Grupo": "Envie mensagens personalizadas de boas-vindas e incentive apresentações.",
    "Compartilhamento de Conteúdo e Links": "Poste conteúdos relevantes e incentive o compartilhamento de materiais informativos.",
    "Discussões Técnicas e Consultas": "Proponha perguntas instigantes e crie enquetes para gerar mais interação.",
    "Convites e Organização de Eventos": "Divulgue eventos com antecedência e envie lembretes frequentes.",
    "Mensagens de Apoio e Felicitações": "Celebre conquistas do grupo e crie um ambiente acolhedor.",
    "Outro": "Incentive discussões diversas e mantenha um ambiente colaborativo."
}

st.write(f"💡 **Dicas para aumentar {categoria1}:** {dicas.get(categoria1, 'Nenhuma dica disponível.')}")
st.write(f"💡 **Dicas para aumentar {categoria2}:** {dicas.get(categoria2, 'Nenhuma dica disponível.')}")

# 📌 Rodapé
st.markdown("---")
st.markdown("📌 **Projeto desenvolvido por Beatriz Cardoso Cunha com Scrum para análise de grupos do WhatsApp.**")

