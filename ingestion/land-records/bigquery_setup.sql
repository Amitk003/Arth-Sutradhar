-- ============================================================
-- Arth-Sutradhar: BigQuery Setup for Land Records Vector Store
-- ============================================================
-- Run each block separately in the BigQuery console.
-- ============================================================

-- BLOCK 1: Drop old table and recreate
DROP TABLE IF EXISTS `arth-sutradhar.arth_sutradhar.land_records_chunks`;

CREATE TABLE IF NOT EXISTS `arth-sutradhar.arth_sutradhar.land_records_chunks` (
  chunk_id          STRING NOT NULL,
  source_file       STRING NOT NULL,
  chunk_index       INT64 NOT NULL,
  content           STRING NOT NULL,
  content_embedding ARRAY<FLOAT64>,
  inserted_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
) CLUSTER BY source_file;

-- BLOCK 2: Create embedding model (takes ~1-2 min)
CREATE OR REPLACE MODEL `arth-sutradhar.arth_sutradhar.land_records_embedding_model`
  REMOTE WITH CONNECTION `asia-south1.vertex-ai-embedding`
  OPTIONS (ENDPOINT = 'text-multilingual-embedding-002');

-- BLOCK 3a: Insert row 1 with inline embedding
INSERT INTO `arth-sutradhar.arth_sutradhar.land_records_chunks`
  (chunk_id, source_file, chunk_index, content, content_embedding)
SELECT 'test_7_12_0000', 'test_7_12.pdf', 0,
  'Farmer name: Ram Bhai Patel, Khata No: 123, Survey No: 45/2, Crop: Cotton (Irrigated), Area: 1.5 hectares, Village: Gandhinagar, Taluka: Gandhinagar, District: Gandhinagar.',
  text_embedding
FROM ML.GENERATE_TEXT_EMBEDDING(
  MODEL `arth-sutradhar.arth_sutradhar.land_records_embedding_model`,
  (SELECT 'Farmer name: Ram Bhai Patel, Khata No: 123, Survey No: 45/2, Crop: Cotton (Irrigated), Area: 1.5 hectares, Village: Gandhinagar, Taluka: Gandhinagar, District: Gandhinagar.' AS content)
);

-- BLOCK 3b: Insert row 2 with inline embedding
INSERT INTO `arth-sutradhar.arth_sutradhar.land_records_chunks`
  (chunk_id, source_file, chunk_index, content, content_embedding)
SELECT 'test_7_12_0001', 'test_7_12.pdf', 1,
  'Irrigation: Borewell, Soil Type: Black Cotton Soil, Previous Crop: Wheat (2024), Land Holder Type: Individual, Encumbrances: None recorded.',
  text_embedding
FROM ML.GENERATE_TEXT_EMBEDDING(
  MODEL `arth-sutradhar.arth_sutradhar.land_records_embedding_model`,
  (SELECT 'Irrigation: Borewell, Soil Type: Black Cotton Soil, Previous Crop: Wheat (2024), Land Holder Type: Individual, Encumbrances: None recorded.' AS content)
);

-- BLOCK 4: Verify and create vector index
SELECT chunk_id, ARRAY_LENGTH(content_embedding) AS emb_len FROM `arth-sutradhar.arth_sutradhar.land_records_chunks`;

CREATE OR REPLACE VECTOR INDEX `arth-sutradhar.arth_sutradhar.land_records_vector_index`
ON `arth-sutradhar.arth_sutradhar.land_records_chunks`(content_embedding)
OPTIONS(
  index_type = 'IVF',
  distance_type = 'COSINE',
  ivf_options = '{"num_lists": 100}'
);

-- BLOCK 5: Test vector search
SELECT base.chunk_id, base.content, distance
FROM VECTOR_SEARCH(
  TABLE `arth-sutradhar.arth_sutradhar.land_records_chunks`,
  'content_embedding',
  (
    SELECT text_embedding
    FROM ML.GENERATE_TEXT_EMBEDDING(
      MODEL `arth-sutradhar.arth_sutradhar.land_records_embedding_model`,
      (SELECT 'cotton farmer with irrigation' AS content)
    )
  ),
  top_k => 5,
  distance_type => 'COSINE',
  fraction_lists_to_search => 0.01
);
