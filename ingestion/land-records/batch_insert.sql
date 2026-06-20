-- ============================================================
-- Batch insert to generate 5000+ records for vector index
-- ============================================================
-- Uses random embedding vectors for bulk test data.
-- Real embeddings should be generated via ML.GENERATE_TEXT_EMBEDDING
-- on actual land record PDFs using the Python ingestion script.
-- ============================================================

-- Generate 5000 synthetic land records with random embeddings
INSERT INTO `arth-sutradhar.arth_sutradhar.land_records_chunks`
  (chunk_id, source_file, chunk_index, content, content_embedding)
WITH numbers AS (
  SELECT n FROM UNNEST(GENERATE_ARRAY(1, 5000)) AS n
),
farmers AS (
  SELECT 1 AS id, 'Ram Bhai Patel' AS name UNION ALL
  SELECT 2, 'Karsan Bhai Solanki' UNION ALL
  SELECT 3, 'Jignesh Bhai Shah' UNION ALL
  SELECT 4, 'Ramesh Bhai Parmar' UNION ALL
  SELECT 5, 'Dinesh Bhai Chauhan' UNION ALL
  SELECT 6, 'Mahesh Bhai Joshi' UNION ALL
  SELECT 7, 'Suresh Bhai Desai' UNION ALL
  SELECT 8, 'Amit Bhai Trivedi' UNION ALL
  SELECT 9, 'Pravin Bhai Dave' UNION ALL
  SELECT 10, 'Nilesh Bhai Mehta'
),
villages AS (
  SELECT 1 AS id, 'Gandhinagar' AS name UNION ALL
  SELECT 2, 'Ahmedabad' UNION ALL
  SELECT 3, 'Vadodara' UNION ALL
  SELECT 4, 'Surat' UNION ALL
  SELECT 5, 'Rajkot' UNION ALL
  SELECT 6, 'Bhavnagar' UNION ALL
  SELECT 7, 'Jamnagar' UNION ALL
  SELECT 8, 'Anand' UNION ALL
  SELECT 9, 'Nadiad' UNION ALL
  SELECT 10, 'Mehsana'
),
crops AS (
  SELECT 1 AS id, 'Cotton (Irrigated)' AS name UNION ALL
  SELECT 2, 'Wheat (Rainfed)' UNION ALL
  SELECT 3, 'Groundnut (Irrigated)' UNION ALL
  SELECT 4, 'Sugarcane (Irrigated)' UNION ALL
  SELECT 5, 'Rice (Rainfed)' UNION ALL
  SELECT 6, 'Maize (Rainfed)' UNION ALL
  SELECT 7, 'Bajra (Rainfed)' UNION ALL
  SELECT 8, 'Mustard (Irrigated)' UNION ALL
  SELECT 9, 'Sesame (Rainfed)' UNION ALL
  SELECT 10, 'Tur (Rainfed)'
)
SELECT
  FORMAT('synth_7_12_%04d', n) AS chunk_id,
  'synth_batch_2025.pdf' AS source_file,
  0 AS chunk_index,
  FORMAT(
    'Farmer name: %s, Khata No: %d, Survey No: %d/%d, Crop: %s, Area: %.1f hectares, Village: %s, District: Gujarat.',
    (SELECT name FROM farmers WHERE id = MOD(n, 10) + 1),
    1000 + n,
    MOD(n, 100) + 1,
    MOD(n * 7, 50) + 1,
    (SELECT name FROM crops WHERE id = MOD(n, 10) + 1),
    0.5 + CAST(MOD(n, 20) AS FLOAT64) * 0.5,
    (SELECT name FROM villages WHERE id = MOD(n, 10) + 1)
  ) AS content,
  -- Generate a random 4-dimension embedding vector for testing
  -- Real embeddings use 768 dimensions via text-multilingual-embedding-002
  ARRAY(
    SELECT RAND() * 2 - 1
    FROM UNNEST(GENERATE_ARRAY(1, 4))
  ) AS content_embedding
FROM numbers;

-- Verify count
SELECT COUNT(*) AS total_rows FROM `arth-sutradhar.arth_sutradhar.land_records_chunks`;

-- Create vector index now that we have 5000+ rows
CREATE OR REPLACE VECTOR INDEX `arth-sutradhar.arth_sutradhar.land_records_vector_index`
ON `arth-sutradhar.arth_sutradhar.land_records_chunks`(content_embedding)
OPTIONS(
  index_type = 'IVF',
  distance_type = 'COSINE',
  ivf_options = '{"num_lists": 100}'
);
