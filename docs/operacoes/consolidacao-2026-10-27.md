# Consolidação da develop — 27/10/2026

## Entrega

Consolidação dos incrementos locais desde a base 5a6fc9c: arquivo imutável, coletores GFS/IFS/ICON/MET, normalização, baseline operacional, manifesto e ledger local, pareamento observacional e comparador exploratório de chuva. Inclui testes de entrega dos avisos de chuva/vento/calor/frio, unidades °C/°F e mensagem acessível estável para HTTP 429.

Auditoria identificou dois achados moderados no Vitest 5.0.2. Lockfile atualizado dentro das versões compatíveis, incluindo Vitest 5.0.5. Instalação reproduzível e auditoria repetidas sem vulnerabilidades.

## Verificação local

- 748 testes backend aprovados em 66,17 s, com warnings como erros, em Docker/Redis isolado na base 15.
- Mypy: 82 módulos aprovados; Ruff src/tests aprovado.
- Frontend: 48 testes, ESLint, vue-tsc e build aprovados após correção do lockfile.
- npm audit: zero vulnerabilidades após correção.
- Hardening local e git diff --check aprovados.

## Limites e sequência

Publicação e resultado de CI/Security devem ser conferidos para o SHA consolidado; execução local não certifica os checks remotos. Sem merge em main ou implantação. Reference-v1 permanece ativa, sem promoção ou ganho científico comprovado da candidate-1.

Próximos: teste auditivo real PT/EN; fechar parâmetros/calendário e controle D+7; equivalência e pareamento das demais variáveis; cobertura contra calendário e incerteza; coleta recorrente somente após aceite; avaliação independente, refinamento e integração condicionada. A aprovação da direção não aprova automaticamente parâmetros quantitativos propostos.
