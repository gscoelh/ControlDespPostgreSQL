# ControlDespPostgreSQL

Este projeto é a evolução do sistema atual baseado em Access.

## Objetivos

- Migrar o banco para PostgreSQL
- Criar arquitetura moderna em Python 64 bits
- Permitir expansão para mobile e web
- Eliminar dependências de ODBC e Access

## Estrutura

- src/core: lógica principal
- src/database: conexão e scripts SQL
- src/models: modelos de dados
- src/services: regras de negócio
- src/ui: interface gráfica
- src/utils: funções auxiliares
