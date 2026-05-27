# Riza Malls — Gerador de Relatórios

Site que gera o relatório mensal em PPTX automaticamente a partir do Excel de fundamentos.

## Como usar (todo mês)

1. Acesse o site
2. Faça upload do Excel preenchido com os dados do mês
3. Clique em **Gerar Relatório PPTX**
4. Baixe o arquivo pronto

## Deploy no Railway

### 1. Subir no GitHub

```bash
git init
git add .
git commit -m "feat: gerador de relatórios Riza Malls"
git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git
git push -u origin main
```

### 2. Criar projeto no Railway

1. Acesse [railway.app](https://railway.app) → **New Project**
2. **Deploy from GitHub repo** → selecione o repositório
3. O Railway detecta o `nixpacks.toml` automaticamente e instala tudo (incluindo LibreOffice)

### 3. Configurar variável de ambiente

No painel do Railway → **Variables**:

| Variável | Valor |
|---|---|
| `ANTHROPIC_API_KEY` | `sk-ant-xxxxxxx` (obrigatório para comentários IA) |

### 4. Fazer upload dos arquivos no site

Após o deploy, acesse a URL gerada e faça upload pelo site:
- **Template PPTX** → o arquivo `Relatório_Riza_Malls_TEMPLATE.pptx`

Pronto. A partir daí, todo mês é só fazer upload do Excel atualizado e gerar.

## Estrutura do projeto

```
├── app.py                        # Backend Flask (API + serve frontend)
├── services/
│   ├── excel_service.py          # Lê Excel, extrai gráficos e tabelas do Dashboard
│   ├── pptx_service.py           # Preenche os slots nomeados no template PPTX
│   └── ai_service.py             # Gera comentários analíticos via Claude API
├── frontend/
│   └── index.html                # Interface web
├── data/                         # Excel vai aqui após upload (não versionado)
├── templates/                    # Template PPTX vai aqui após upload (não versionado)
├── requirements.txt
├── nixpacks.toml                 # Build config Railway (instala LibreOffice)
└── railway.toml                  # Deploy config Railway
```

## Slots preenchidos automaticamente

### Gráficos (Chart Objects do Excel → imagem no PPTX)
| Nome no Excel | Slide | Descrição |
|---|---|---|
| `grafico_vendas_metro` | 6 | Vendas por m² |
| `grafico_evolucao_vendas` | 6 | Evolução de Vendas |
| `grafico_noi_metro` | 7 | NOI por m² |
| `grafico_evolucao_noi` | 7 | Evolução do NOI |

### Tabelas (dados das células do Dashboard)
| Nome no PPTX | Slide | Dados |
|---|---|---|
| `tabela_abl` | 5 | ABL por shopping |
| `tabela_taxa_de_ocupacao` | 5 | Taxa de ocupação por shopping |
| `tabela_sss_ssr` | 5 | SSS e SSR por shopping |
| `tabela_resumo` | 8 | Resumo completo dos ativos |

### Comentários (gerados por IA)
| Nome no PPTX | Slide | Sobre |
|---|---|---|
| `comentarios_abl` | 5 | Análise da ABL |
| `comentarios_taxa_de_ocupacao` | 5 | Análise da ocupação |
| `comentarios_sss_ssr` | 5 | Análise de SSS e SSR |
| `comentarios_vendas` | 6 | Análise de vendas |
| `comentarios_inadimplencia` | 6 | Análise de inadimplência |
| `comentarios_noi` | 7 | Análise do NOI |

## Variáveis de ambiente disponíveis

```env
ANTHROPIC_API_KEY=sk-ant-xxx   # Chave Claude API (obrigatória para IA)
EXCEL_FILENAME=dados.xlsx       # Nome do arquivo Excel (padrão)
TEMPLATE_FILENAME=template.pptx # Nome do template PPTX (padrão)
DASHBOARD_SHEET=Dashboard       # Nome da aba do dashboard (padrão)
PORT=5000                       # Porta do servidor (padrão)
```
