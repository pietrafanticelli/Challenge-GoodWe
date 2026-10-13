# EV ChargeOps — GoodWe + FIAP (Sprint 02)

Solução inteligente de gestão operacional, rateio justo e proteção elétrica para infraestruturas compartilhadas de recarga de veículos elétricos, utilizando como referência técnica o carregador **GoodWe GW7K-HCA-20 (linha HCA G2)** do Energy Innovation Lab da FIAP.

---

## 1. Descrição da Solução

O crescimento acelerado de veículos elétricos no Brasil gera conflitos operacionais em condomínios residenciais e edifícios corporativos. A ausência de medição individualizada, a falta de critérios transparentes para rateio e o risco de ultrapassagem da demanda contratada (gerando sobrecarga, disparos de disjuntores gerais e multas de concessionárias) constituem os principais obstáculos.

O **EV ChargeOps** responde diretamente a esse desafio por meio de:
1. **Identificação por Aproximação e Rateio Nominal:** Associação direta do morador e sua unidade habitacional via autenticação RFID, garantindo justiça tarifária mesmo que diferentes veículos utilizem a mesma vaga física.
2. **Resiliência a Quedas de Conectividade:** Processamento por delta de medidor acumulado de hardware, salvaguardando a integridade das leituras mesmo diante de falhas de rede local ou desconexões intempestivas.
3. **Módulo de Inteligência Artificial Estrutural:** Algoritmo preditivo de demanda energética (*Random Forest*) que antecipa picos de carga para as 24 horas seguintes, orientando ações de modulação de potência (*Smart Charging* via protocolo OCPP) para proteção da infraestrutura predial.

---

## 2. Conformidade Regulatória e Técnica

- **RN ANEEL nº 1.000/2021:** Enquadramento na modalidade de prestação de serviço de recarga veicular, assegurando a legitimidade da individualização e cobrança sem caracterizar revenda irregular de energia.
- **ABNT NBR 5410 & IT-41 (Corpo de Bombeiros SP):** Diretrizes de proteção contra sobrecargas e segurança em instalações de recarga coletiva.
- **GoodWe SEMS+ API & Protocolo OCPP:** Integração com telemetria de corrente, tensão, status operacional e energia acumulada.

---

## 3. Arquitetura de Dados

O banco de dados relacional foi estruturado para dissociar a vaga física do motorista, permitindo múltiplos utilizadores e auditoria financeira imutável:
- `usuarios`: Cadastro de moradores e unidades (`id_usuario`, `nome`, `apartamento`).
- `rfids`: Cadastro e vinculação dos cartões de identificação ativa aos moradores.
- `carregadores`: Cadastro dos pontos de carregamento físicos instalados.
- `historico_sessoes`: Registro consolidado das transações de recarga com data, energia líquida (kWh) e status operacional.

---

## 4. Instruções de Execução

### Pré-requisitos
- Python 3.10 ou superior.

### Execução do Protótipo
1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Inicie a aplicação web:
   ```bash
   streamlit run app.py
   ```
3. Abra o navegador no endereço indicado (por padrão `http://localhost:8501`).

---

## 5. Decisões Técnicas e Desvios Planejados

- **Cobrança Integrada ao Condomínio:** Tendo em vista que o carregador físico GoodWe HCA G2 não possui leitor bancário direto (maquininha de cartão) integrado, a cobrança é apurada por relatório e incorporada à cobrança condominial mensal, garantindo conformidade jurídica e facilidade de gestão.
- **Papel da Inteligência Artificial:** A IA foi direcionada para a função estrutural de previsão e proteção de demanda energética em malha preditiva, mitigando o risco de colapso elétrico e penalidades regulatórias.
