CREATE TABLE cadconta (
    codcta VARCHAR,
    codctaagr VARCHAR,
    descrcta VARCHAR,
    tpcusto VARCHAR,
    naturezacta VARCHAR,
    dtaaberturacta TIMESTAMP
);

CREATE TABLE cadctaagr (
    codctaagr VARCHAR,
    descrctaagr VARCHAR,
    dtaabertura TIMESTAMP
);

CREATE TABLE contasporcusto (
    tpcusto VARCHAR,
    conta VARCHAR,
    percentual VARCHAR
);

CREATE TABLE lancamentos_copia (
    sequencia SERIAL PRIMARY KEY,
    datalancto TIMESTAMP,
    roteiro VARCHAR,
    conta VARCHAR,
    vallancto NUMERIC(15,2),
    sinallancto VARCHAR,
    historico VARCHAR,
    complhistorico VARCHAR,
    contraparte VARCHAR,
    dataregistro TIMESTAMP,
    lote VARCHAR,
    sequencialote INTEGER
);

CREATE TABLE custos (
    tpcusto VARCHAR,
    nomecusto VARCHAR
);

CREATE TABLE despesas (
    chv_despesas SERIAL PRIMARY KEY,
    datadesp TIMESTAMP,
    coddesp VARCHAR,
    descrdesp VARCHAR,
    vlrdespesa NUMERIC(15,2),
    origemverba VARCHAR,
    debcred VARCHAR,
    resumogerencial VARCHAR,
    anomesreferencia VARCHAR,
    indicador_continuidade VARCHAR,
    campo1 VARCHAR
);

CREATE TABLE despgrupo (
    codagrup VARCHAR,
    aaaamm VARCHAR,
    vlrdespesa DOUBLE PRECISION
);

CREATE TABLE erros_ao_colar (
    campo0 TEXT
);

CREATE TABLE gerencial (
    gerencial VARCHAR,
    nomegerencial VARCHAR,
    descricao_conteudo TEXT
);

CREATE TABLE lancamentos (
    sequencia SERIAL PRIMARY KEY,
    datalancto TIMESTAMP,
    roteiro VARCHAR,
    conta VARCHAR,
    vallancto NUMERIC(15,2),
    sinallancto VARCHAR,
    historico VARCHAR,
    complhistorico VARCHAR,
    contraparte VARCHAR,
    dataregistro TIMESTAMP,
    lote VARCHAR,
    sequencialote INTEGER,
    quemweb VARCHAR,
    comprovanteweb TEXT
);

CREATE TABLE origemverba (
    codigo SERIAL PRIMARY KEY,
    origemverba VARCHAR,
    descr_origemverba VARCHAR
);

CREATE TABLE parametros (
    codigo SERIAL PRIMARY KEY,
    datalimite TIMESTAMP,
    quem VARCHAR
);

CREATE TABLE rotapucapa (
    rotapur VARCHAR,
    nomerotapur VARCHAR
);

CREATE TABLE rotapudeta (
    rotapur VARCHAR,
    conta VARCHAR,
    sinalcta VARCHAR
);

CREATE TABLE roteirocapa (
    roteiro VARCHAR,
    rotnatureza VARCHAR,
    rotdesc VARCHAR,
    contadanatureza VARCHAR,
    titulolote VARCHAR
);

CREATE TABLE roteirodeta (
    roteiro VARCHAR,
    rotnatureza VARCHAR,
    rotctadeb VARCHAR,
    rotctacred VARCHAR,
    rothist VARCHAR
);

CREATE TABLE saldos (
    dtasaldo TIMESTAMP,
    codcta VARCHAR,
    sdoant DOUBLE PRECISION,
    vlrdebito DOUBLE PRECISION,
    vlrcreito DOUBLE PRECISION
);

CREATE TABLE sdo (
    coddesp VARCHAR,
    datasdo TIMESTAMP,
    sdoestat VARCHAR,
    sdoant DOUBLE PRECISION,
    sdodeb DOUBLE PRECISION,
    sdocre DOUBLE PRECISION
);

CREATE TABLE tabdesp (
    coddesp VARCHAR,
    codagrup VARCHAR,
    nomedesp VARCHAR,
    receitadespesa VARCHAR,
    gerencial VARCHAR
);

CREATE TABLE tabdesp1 (
    coddesp VARCHAR,
    codagrup VARCHAR,
    nomedesp VARCHAR,
    receitadespesa VARCHAR,
    gerencial VARCHAR
);

CREATE TABLE teste (
    codigo SERIAL PRIMARY KEY,
    campo1 VARCHAR,
    campo2 VARCHAR,
    campo3 VARCHAR,
    campo4 VARCHAR,
    campo5 VARCHAR,
    campourl BYTEA,
    campo6 TEXT
);

CREATE TABLE tipoorigem (
    origemverba VARCHAR,
    descrorigem VARCHAR
);
