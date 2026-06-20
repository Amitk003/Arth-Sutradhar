-- ============================================================
-- Arth-Sutradhar: BigQuery Setup for Land Records Vector Store
-- ============================================================
-- Run these SQL commands in the BigQuery console.
-- 
-- Prerequisites:
-- 1. BigQuery connection to Vertex AI already exists (via Terraform)
--    Connection name: vertex-ai-embedding
-- 2. IAM role roles/aiplatform.user granted to the connection SA
-- ============================================================

-- -------------------------------------------------------
-- Step 1: Create the land records table
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS `arth-sutradhar.arth_sutradhar.land_records_chunks` (
  chunk_id      STRING NOT NULL,
  source_file   STRING NOT NULL,
  chunk_index   INT64 NOT NULL,
  content       STRING NOT NULL,
  content_embedding BYTES,
  inserted_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
) CLUSTER BY source_file;

-- -------------------------------------------------------
-- Step 2: Create the remote embedding model
-- -------------------------------------------------------
-- This creates a model backed by Vertex AI's text-multilingual-embedding-002
-- which supports 100+ languages including Gujarati, Hindi, etc.
-- -------------------------------------------------------
CREATE OR REPLACE MODEL `arth-sutradhar.arth_sutradhar.land_records_embedding_model`
  REMOTE WITH CONNECTION `asia-south1.vertex-ai-embedding`
  OPTIONS (ENDPOINT = 'text-multilingual-embedding-002');

-- -------------------------------------------------------
-- Step 3: Generate embeddings for existing rows
-- -------------------------------------------------------
-- Backfill embeddings for any rows that don't have them yet.
-- For production, run this as a scheduled query or after each batch insert.
-- -------------------------------------------------------
UPDATE `arth-sutradhar.arth_sutradhar.land_records_chunks`
SET content_embedding = (
  SELECT ML.GENERATE_TEXT_EMBEDDING(
    MODEL `arth-sutradhar.arth_sutradhar.land_records_embedding_model`,
    (SELECT content AS text_content),
    STRUCT(TRUE AS flatten_embeddings)
  )['text_embedding']
)
WHERE content_embedding IS NULL;

-- -------------------------------------------------------
-- Step 4: Create vector index for fast similarity search
-- -------------------------------------------------------
-- IVF (Inverted File Index) with cosine similarity.
-- The index is created asynchronously.
-- -------------------------------------------------------
CREATE OR REPLACE VECTOR INDEX `arth-sutradhar.arth_sutradhar.land_records_vector_index`
ON `arth-sutradhar.arth_sutradhar.land_records_chunks`(content_embedding)
OPTIONS(
  index_type = 'IVF',
  distance_type = 'COSINE',
  ivf_options = '{"num_lists": 100}'
);

-- -------------------------------------------------------
-- Step 5: Insert a new record with embedding in one step
-- -------------------------------------------------------
-- Example insert that automatically generates the embedding:
-- -------------------------------------------------------
-- INSERT INTO `arth-sutradhar.arth_sutradhar.land_records_chunks`
--   (chunk_id, source_file, chunk_index, content, content_embedding)
-- SELECT
--   'sample_7_12_0000' AS chunk_id,
--   'sample_7_12.pdf' AS source_file,
--   0 AS chunk_index,
--   'Sample land record content...' AS content,
--   ML.GENERATE_TEXT_EMBEDDING(
--     MODEL `arth-sutradhar.arth_sutradhar.land_records_embedding_model`,
--     (SELECT 'Sample land record content...' AS text_content),
--     STRUCT(TRUE AS flatten_embeddings)
--   )['text_embedding']
-- ;

-- -------------------------------------------------------
-- Step 6: Query with VECTOR_SEARCH
-- -------------------------------------------------------
-- Example search query (to be used by the ADK agent tool):
-- -------------------------------------------------------
-- SELECT * FROM VECTOR_SEARCH(
--   TABLE `arth-sutradhar.arth_sutradhar.land_records_chunks`,
--   'content_embedding',
--   (
--     SELECT ML.GENERATE_TEXT_EMBEDDING(
--       MODEL `arth-sutradhar.arth_sutradhar.land_records_embedding_model`,
--       (SELECT 'irrigated cotton land in small farm' AS text_content),
--       STRUCT(TRUE AS flatten_embeddings)
--     )['text_embedding']
--   ),
--   top_k => 10,
--   distance_type => 'COSINE',
--   fraction_lists_to_search => 0.01
-- );
