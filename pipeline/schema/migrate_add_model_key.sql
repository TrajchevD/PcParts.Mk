-- ============================================================
-- Migration: add model_key column and update upsert_offer proc
-- Run once against an existing pc_parts database:
--   mysql -u root -p pc_parts < schema/migrate_add_model_key.sql
-- ============================================================

-- Add model_key column (NULL = couldn't extract, falls back to title matching)
ALTER TABLE products
    ADD COLUMN IF NOT EXISTS model_key VARCHAR(150) NULL AFTER canonical_title,
    ADD UNIQUE KEY IF NOT EXISTS uq_model_key_cat (model_key, category_id);

-- Replace stored procedure with new signature (adds p_model_key parameter)
DROP PROCEDURE IF EXISTS upsert_offer;

DELIMITER $$

CREATE PROCEDURE upsert_offer(
    IN p_store_name  VARCHAR(50),
    IN p_category    VARCHAR(30),
    IN p_title       VARCHAR(500),
    IN p_model_key   VARCHAR(150),
    IN p_price       DECIMAL(10,2),
    IN p_price_text  VARCHAR(50),
    IN p_url         VARCHAR(1000),
    IN p_image       VARCHAR(1000),
    IN p_in_stock    TINYINT(1)
)
BEGIN
    DECLARE v_store_id    INT;
    DECLARE v_category_id INT;
    DECLARE v_product_id  INT;
    DECLARE v_offer_id    INT;
    DECLARE v_old_price   DECIMAL(10,2);

    INSERT IGNORE INTO stores (name) VALUES (p_store_name);
    SELECT store_id INTO v_store_id FROM stores WHERE name = p_store_name LIMIT 1;

    INSERT IGNORE INTO categories (slug, name) VALUES (p_category, p_category);
    SELECT category_id INTO v_category_id FROM categories WHERE slug = p_category LIMIT 1;

    IF p_model_key IS NOT NULL THEN
        SELECT product_id INTO v_product_id
        FROM products
        WHERE model_key = p_model_key AND category_id = v_category_id
        LIMIT 1;
    ELSE
        SELECT product_id INTO v_product_id
        FROM products
        WHERE canonical_title = p_title AND category_id = v_category_id
        LIMIT 1;
    END IF;

    IF v_product_id IS NULL THEN
        INSERT INTO products (category_id, canonical_title, model_key, spec_status)
        VALUES (v_category_id, p_title, p_model_key, 'pending');
        SET v_product_id = LAST_INSERT_ID();
    END IF;

    SELECT offer_id, price INTO v_offer_id, v_old_price
    FROM product_offers
    WHERE product_id = v_product_id AND store_id = v_store_id
    LIMIT 1;

    INSERT INTO product_offers
        (product_id, store_id, title_raw, price, price_text,
         product_url, image_url, in_stock, last_seen_at)
    VALUES
        (v_product_id, v_store_id, p_title, p_price, p_price_text,
         p_url, p_image, p_in_stock, NOW())
    ON DUPLICATE KEY UPDATE
        title_raw    = p_title,
        price        = p_price,
        price_text   = p_price_text,
        product_url  = p_url,
        image_url    = p_image,
        in_stock     = p_in_stock,
        last_seen_at = IF(p_in_stock = 1, NOW(), last_seen_at),
        updated_at   = NOW();

    IF v_offer_id IS NOT NULL
       AND v_old_price IS NOT NULL
       AND p_price IS NOT NULL
       AND v_old_price <> p_price
    THEN
        INSERT INTO offer_price_history (offer_id, price)
        VALUES (v_offer_id, p_price);
    END IF;

END $$

DELIMITER ;

SELECT 'Migration complete' AS status;
