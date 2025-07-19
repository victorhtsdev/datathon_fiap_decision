-- Adiciona colunas ao match_prospects se não existirem

-- Adiciona filter_step_added
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'match_prospects' 
                   AND column_name = 'filter_step_added') THEN
        ALTER TABLE match_prospects ADD COLUMN filter_step_added INTEGER DEFAULT 1;
    END IF;
END $$;

-- Adiciona is_active  
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'match_prospects' 
                   AND column_name = 'is_active') THEN
        ALTER TABLE match_prospects ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
    END IF;
END $$;

-- Atualiza valores padrão para registros existentes
UPDATE match_prospects SET filter_step_added = 1 WHERE filter_step_added IS NULL;
UPDATE match_prospects SET is_active = true WHERE is_active IS NULL;
