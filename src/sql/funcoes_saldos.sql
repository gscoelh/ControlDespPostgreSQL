CREATE OR REPLACE FUNCTION efeito_contabil(
    p_conta TEXT,
    p_datalancto DATE,
    p_sinal TEXT,
    p_valor NUMERIC,
    p_contrap TEXT
)
RETURNS NUMERIC AS $$
DECLARE
    nat TEXT;
BEGIN
    SELECT naturezacta INTO nat
    FROM cadconta
    WHERE codcta = p_conta::text;

    IF p_conta = p_contrap THEN
        IF nat = 'D' THEN
            IF p_sinal = 'D' THEN RETURN -p_valor;
            ELSE RETURN  p_valor;
            END IF;
        ELSE
            IF p_sinal = 'C' THEN RETURN -p_valor;
            ELSE RETURN  p_valor;
            END IF;
        END IF;
    END IF;

    IF nat = 'D' THEN
        IF p_sinal = 'D' THEN RETURN  p_valor;
        ELSE RETURN -p_valor;
        END IF;
    ELSE
        IF p_sinal = 'C' THEN RETURN  p_valor;
        ELSE RETURN -p_valor;
        END IF;
    END IF;

END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION saldo_inicial(
    p_conta TEXT,
    p_data DATE
)
RETURNS NUMERIC AS $$
SELECT COALESCE(SUM(
    CASE
        WHEN sinallancto = 'D' THEN vallancto
        WHEN sinallancto = 'C' THEN -vallancto
        ELSE 0
    END
), 0)
FROM lancamentos
WHERE conta = p_conta::text
  AND datalancto < p_data;
$$ LANGUAGE sql;

