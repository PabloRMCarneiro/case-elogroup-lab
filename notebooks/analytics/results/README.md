## **Recapitulação e Justificativa para Escolha dos Três ZCTAs para Expansão de Laboratórios**

Após análise e validação das hipóteses estabelecidas inicialmente para a expansão estratégica dos laboratórios, chega-se ao seguinte conjunto de critérios fundamentais para selecionar três ZCTAs ideais:

### Critérios e Justificativas

1. **Alta População:**
   - Confirmada, através de análises estatísticas (correlação positiva significativa: 0,734 para exames e 0,677 para receita, ambos com p-value muito baixo), que regiões mais populosas apresentam volumes maiores de exames diagnósticos e maior receita potencial.

2. **Distribuição de Renda (Quartis Q1, Q2 e Q4):**
   - Apesar da ausência de correlação direta entre renda média e receita geral dos exames, foi identificado um desempenho claramente inferior em ZCTAs com renda média-alta (quartil Q3). Portanto, foca-se em áreas de baixa (Q1), média baixa (Q2) e alta renda (Q4), evitando a faixa Q3, onde o desempenho financeiro é comprovadamente mais fraco.

3. **Predominância Feminina:**
   - Embora a correlação linear direta entre a proporção de mulheres e volume geral de exames não tenha sido confirmada estatisticamente (correlação fraca, p-value elevado), observou-se um efeito limiar importante. ZCTAs com proporção feminina entre 50%-53% apresentaram um aumento perceptível na demanda por exames diagnósticos.

4. **Indicador de Expansão (expansion_indicator):**
   - Foi desenvolvido um indicador específico que combina gênero e faixa etária: a razão entre o número de adultos jovens e de meia-idade (25-54 anos, faixa com maior demanda) subtraindo a faixa de 0-5 anos (alta complexidade e custo), dividida pela proporção masculina/feminina. Assim, esse indicador reflete o potencial máximo de retorno, favorecendo regiões com mais mulheres e maior concentração etária de alto volume de exames, enquanto penaliza aquelas com elevado número de crianças pequenas, que representam maior custo por exame.

### Conclusão Final:

Com base nesse procedimento, as áreas selecionadas serão aquelas que simultaneamente:
- Apresentam alta densidade populacional (top 3%).
- Não se encontram na faixa de renda média-alta (Q3).
- Obtiveram maior valor do indicador de expansão (expansion_indicator).

Dessa forma, acredita-se garantir a maximização do potencial econômico e estratégico da expansão dos laboratórios, considerando as variáveis mais influentes e já validadas pela análise.
