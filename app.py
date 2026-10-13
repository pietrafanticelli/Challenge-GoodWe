"""
EV ChargeOps - Protótipo Funcional (GoodWe + FIAP)
Sprint 02: Lógica Central de Rateio, Resiliência a Exceções e IA Estrutural Preditiva.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor

# --- CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(
    page_title="GoodWe EV ChargeOps",
    page_icon="⚡",
    layout="wide"
)

# --- 1. BANCO DE DADOS EM MEMÓRIA (DDL LÓGICO) ---
@st.cache_data
def carregar_dados_iniciais():
    usuarios = pd.DataFrame([
        {"id_usuario": 101, "nome": "Carlos Silva", "apartamento": "141-A", "rfid_tag": "RFID_CARLOS_99"},
        {"id_usuario": 102, "nome": "Mariana Costa", "apartamento": "141-A", "rfid_tag": "RFID_MARI_88"},
        {"id_usuario": 103, "nome": "Roberto Souza", "apartamento": "32-B", "rfid_tag": "RFID_BOB_77"}
    ])
    
    carregadores = pd.DataFrame([
        {"charger_id": "GW_EV_987654321", "station_id": "LAB_FIAP_01", "vaga": "Vaga G1-05", "modelo": "GoodWe GW7K-HCA-20", "potencia_max_kw": 7.4}
    ])
    
    telemetria_bruta = [
        # Sessão 1: Carlos Silva (Normal)
        {"timestamp": "2026-06-18 20:00:00", "chargerId": "GW_EV_987654321", "status": "charging", "voltageV": 230.5, "energyDeliveredkWh": 0.00, "rfid": "RFID_CARLOS_99"},
        {"timestamp": "2026-06-18 20:30:00", "chargerId": "GW_EV_987654321", "status": "charging", "voltageV": 229.1, "energyDeliveredkWh": 3.70, "rfid": "RFID_CARLOS_99"},
        {"timestamp": "2026-06-18 21:00:00", "chargerId": "GW_EV_987654321", "status": "finishing", "voltageV": 231.0, "energyDeliveredkWh": 7.40, "rfid": "RFID_CARLOS_99"},
        # Sessão 2: Mariana Costa (Mesma vaga, recuperação após queda de conexão)
        {"timestamp": "2026-06-18 22:00:00", "chargerId": "GW_EV_987654321", "status": "charging", "voltageV": 230.0, "energyDeliveredkWh": 7.40, "rfid": "RFID_MARI_88"},
        {"timestamp": "2026-06-18 23:00:00", "chargerId": "GW_EV_987654321", "status": "finishing", "voltageV": 230.2, "energyDeliveredkWh": 18.50, "rfid": "RFID_MARI_88"},
        # Sessão 3: Roberto Souza (Interrupção forçada / pico)
        {"timestamp": "2026-06-19 08:00:00", "chargerId": "GW_EV_987654321", "status": "charging", "voltageV": 231.2, "energyDeliveredkWh": 18.50, "rfid": "RFID_BOB_77"},
        {"timestamp": "2026-06-19 08:15:00", "chargerId": "GW_EV_987654321", "status": "charging", "voltageV": 228.5, "energyDeliveredkWh": 20.35, "rfid": "RFID_BOB_77"},
        {"timestamp": "2026-06-19 08:16:00", "chargerId": "GW_EV_987654321", "status": "fault", "voltageV": 0.0, "energyDeliveredkWh": 20.40, "rfid": "RFID_BOB_77"}
    ]
    return usuarios, carregadores, pd.DataFrame(telemetria_bruta)

df_usuarios, df_carregadores, df_telemetria = carregar_dados_iniciais()

# --- 2. LÓGICA CENTRAL DE PROCESSAMENTO E RATEIO (MIDDLEWARE) ---
def processar_historico_sessoes(df_raw, df_user, tarifa_kwh=0.85):
    blocos = [df_raw.iloc[0:3], df_raw.iloc[3:5], df_raw.iloc[5:8]]
    sessoes = []
    
    for idx, bloco in enumerate(blocos, start=1001):
        ini = bloco.iloc[0]
        fim = bloco.iloc[-1]
        user_info = df_user[df_user['rfid_tag'] == ini['rfid']].iloc[0]
        
        kwh_consumido = round(fim['energyDeliveredkWh'] - ini['energyDeliveredkWh'], 2)
        custo_sessao = round(kwh_consumido * tarifa_kwh, 2)
        
        status_reg = "Normal (Concluída)" if fim['status'] != 'fault' else "Alerta: Interrupção Abrupta (Recuperada)"
        
        sessoes.append({
            "id_sessao": idx,
            "morador": user_info['nome'],
            "apartamento": user_info['apartamento'],
            "rfid_tag": ini['rfid'],
            "charger_id": ini['chargerId'],
            "inicio": ini['timestamp'],
            "fim": fim['timestamp'],
            "kwh_consumido": kwh_consumido,
            "custo_total_rs": custo_sessao,
            "status_final": status_reg
        })
    return pd.DataFrame(sessoes)

df_sessoes = processar_historico_sessoes(df_telemetria, df_usuarios)

# --- 3. MÓDULO ESTRUTURAL DE INTELIGÊNCIA ARTIFICIAL ---
def treinar_modelo_ia():
    np.random.seed(42)
    horas = np.tile(np.arange(24), 30)
    dias_semana = np.repeat(np.tile(np.arange(7), 5)[:30], 24)
    temperatura = np.random.normal(24, 4, len(horas))
    
    consumo_base = 25 + 15 * np.sin((horas - 6) / 24 * np.pi)
    carga_ve = np.where((horas >= 18) & (horas <= 23), np.random.uniform(14, 22, len(horas)), np.random.uniform(0, 5, len(horas)))
    demanda_total_kw = consumo_base + carga_ve + np.random.normal(0, 1.5, len(horas))
    
    df_historico_ia = pd.DataFrame({
        "hora": horas,
        "dia_semana": dias_semana,
        "temperatura": temperatura,
        "demanda_total_kw": demanda_total_kw
    })
    
    X = df_historico_ia[["hora", "dia_semana", "temperatura"]]
    y = df_historico_ia["demanda_total_kw"]
    
    modelo = RandomForestRegressor(n_estimators=50, random_state=42)
    modelo.fit(X, y)
    return modelo

modelo_ia = treinar_modelo_ia()

# --- INTERFACE VISUAL ---
st.sidebar.title("⚡ EV ChargeOps")
st.sidebar.caption("GoodWe + FIAP | Energy Innovation Lab")
perfil = st.sidebar.radio("Selecione a Visão:", ["📱 Aplicativo do Usuário (Morador)", "🏢 Painel do Administrador (Síndico)", "🧠 Módulo de IA: Proteção da Rede"])

# VISÃO 1: MORADOR
if perfil == "📱 Aplicativo do Usuário (Morador)":
    st.title("Meu Ponto de Recarga — Morador")
    st.subheader("Simulação de Acesso via Aproximação (RFID/NFC)")
    
    morador_selecionado = st.selectbox("Selecione o Usuário / Tag de Aproximação:", df_usuarios["nome"].tolist())
    dados_morador = df_usuarios[df_usuarios["nome"] == morador_selecionado].iloc[0]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Morador", dados_morador["nome"])
    col2.metric("Apartamento", dados_morador["apartamento"])
    col3.metric("Tag Ativa", dados_morador["rfid_tag"])
    
    st.divider()
    st.subheader("Status do Carregador Mais Próximo")
    c_status = df_carregadores.iloc[0]
    st.info(f"**{c_status['modelo']}** ({c_status['vaga']}) — **Disponível para Aproximação** | Potência: {c_status['potencia_max_kw']} kW")
    
    st.subheader("Meu Histórico de Recargas Registradas")
    minhas_sessoes = df_sessoes[df_sessoes["morador"] == morador_selecionado]
    if not minhas_sessoes.empty:
        st.dataframe(minhas_sessoes[["id_sessao", "inicio", "fim", "kwh_consumido", "custo_total_rs", "status_final"]], use_container_width=True)
        st.success(f"Total a ser cobrado na taxa condominial deste mês: **R$ {minhas_sessoes['custo_total_rs'].sum():.2f}** ({minhas_sessoes['kwh_consumido'].sum():.2f} kWh)")
    else:
        st.warning("Nenhuma sessão registrada para este usuário.")

# VISÃO 2: ADMINISTRADOR
elif perfil == "🏢 Painel do Administrador (Síndico)":
    st.title("Painel de Gestão e Rateio Condominial")
    st.caption("Conforme Resolução Normativa ANEEL nº 1.000/2021 (Cobrança Individualizada sem Revenda de Energia)")
    
    k1, k2, k3 = st.columns(3)
    k1.metric("Total de Energia Injetada", f"{df_sessoes['kwh_consumido'].sum():.2f} kWh")
    k2.metric("Faturamento Consolidado", f"R$ {df_sessoes['custo_total_rs'].sum():.2f}")
    k3.metric("Sessões Processadas", len(df_sessoes))
    
    st.divider()
    st.subheader("Fechamento Mensal por Unidade (Apartamento)")
    fechamento_apto = df_sessoes.groupby("apartamento").agg(
        moradores=("morador", lambda x: ", ".join(set(x))),
        total_kwh=("kwh_consumido", "sum"),
        valor_rateio_rs=("custo_total_rs", "sum")
    ).reset_index()
    st.dataframe(fechamento_apto, use_container_width=True)
    
    st.subheader("Auditoria de Transações e Tratamento de Exceções")
    st.dataframe(df_sessoes, use_container_width=True)
    st.caption("Nota técnica: As exceções de queda de sinal e desligamento forçado foram resolvidas utilizando o delta do medidor interno de hardware GoodWe.")

# VISÃO 3: INTELIGÊNCIA ARTIFICIAL
elif perfil == "🧠 Módulo de IA: Proteção da Rede":
    st.title("Módulo Estrutural de IA — Proteção e Gestão de Demanda")
    st.markdown("""
    Este componente preditivo atua na **prevenção de violação da Demanda Contratada** e sobrecarga do transformador predial.
    A IA prevê o consumo das próximas 24 horas considerando a curva de rotina dos moradores e os pontos de recarga veicular GoodWe.
    """)
    
    limite_demanda = st.slider("Demanda Contratada do Condomínio (kW):", min_value=30.0, max_value=60.0, value=45.0, step=1.0)
    
    horas_dia = np.arange(24)
    pred_input = pd.DataFrame({
        "hora": horas_dia,
        "dia_semana": [3] * 24,
        "temperatura": [22 + 4 * np.sin(h/24 * np.pi) for h in horas_dia]
    })
    
    predicoes = modelo_ia.predict(pred_input)
    df_previsao = pd.DataFrame({"Hora": [f"{h:02d}:00" for h in horas_dia], "Demanda Prevista (kW)": np.round(predicoes, 2)})
    df_previsao["Limite de Demanda (kW)"] = limite_demanda
    df_previsao["Risco de Violação"] = df_previsao["Demanda Prevista (kW)"] > limite_demanda
    
    st.line_chart(df_previsao.set_index("Hora")[["Demanda Prevista (kW)", "Limite de Demanda (kW)"]])
    
    picos_risco = df_previsao[df_previsao["Risco de Violação"] == True]
    if not picos_risco.empty:
        st.error(f"⚠️ **Alerta da IA:** Risco iminente de sobrecarga entre {picos_risco.iloc[0]['Hora']} e {picos_risco.iloc[-1]['Hora']}! Pico estimado em {picos_risco['Demanda Prevista (kW)'].max():.2f} kW.")
        st.warning("⚡ **Ação Automática de Smart Charging Recomendada:** O sistema deve modular a corrente das estações GoodWe GW7K-HCA-20 (de 32A para 16A via comando remoto) durante essa janela para manter o condomínio dentro da faixa segura.")
    else:
        st.success("✅ **Operação Segura:** A demanda projetada para as próximas 24 horas permanecerá abaixo da demanda contratada.")
