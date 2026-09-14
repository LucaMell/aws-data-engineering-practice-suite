CREATE OR REPLACE VIEW customer_country_summary AS
SELECT
    country_code,
    COUNT(*) AS customer_count,
    ROUND(AVG(lifetime_value), 2) AS average_lifetime_value,
    ROUND(SUM(lifetime_value), 2) AS total_lifetime_value
FROM accepted_customers
GROUP BY country_code
ORDER BY country_code;


CREATE OR REPLACE VIEW event_type_summary AS
SELECT
    event_type,
    COUNT(*) AS event_count,
    COUNT(DISTINCT customer_id) AS distinct_customers,
    ROUND(
        SUM(
            CASE
                WHEN event_type = 'purchase' THEN amount
                ELSE 0
            END
        ),
        2
    ) AS purchase_amount
FROM accepted_events
GROUP BY event_type
ORDER BY event_type;


CREATE OR REPLACE VIEW customer_activity_summary AS
SELECT
    customers.customer_id,
    customers.country_code,
    COUNT(events.event_id) AS event_count,
    SUM(
        CASE
            WHEN events.event_type = 'purchase' THEN 1
            ELSE 0
        END
    ) AS purchase_count,
    COALESCE(
        ROUND(
            SUM(
                CASE
                    WHEN events.event_type = 'purchase'
                    THEN events.amount
                    ELSE 0
                END
            ),
            2
        ),
        0
    ) AS purchase_amount
FROM accepted_customers AS customers
LEFT JOIN accepted_events AS events
    ON customers.customer_id = events.customer_id
GROUP BY
    customers.customer_id,
    customers.country_code
ORDER BY customers.customer_id;


CREATE OR REPLACE VIEW rejection_reason_summary AS
SELECT
    'customers' AS dataset,
    customer_reason.reason AS rejection_reason,
    COUNT(*) AS rejection_count
FROM rejected_customers,
UNNEST(error_codes) AS customer_reason(reason)
GROUP BY customer_reason.reason

UNION ALL

SELECT
    'events' AS dataset,
    event_reason.reason AS rejection_reason,
    COUNT(*) AS rejection_count
FROM rejected_events,
UNNEST(error_codes) AS event_reason(reason)
GROUP BY event_reason.reason

ORDER BY dataset, rejection_reason;


CREATE OR REPLACE VIEW pipeline_reconciliation AS
WITH processed AS (
    SELECT
        'customers' AS dataset,
        (SELECT COUNT(*) FROM accepted_customers)
            AS accepted_count,
        (SELECT COUNT(*) FROM rejected_customers)
            AS rejected_count

    UNION ALL

    SELECT
        'events' AS dataset,
        (SELECT COUNT(*) FROM accepted_events)
            AS accepted_count,
        (SELECT COUNT(*) FROM rejected_events)
            AS rejected_count
)
SELECT
    source_counts.dataset,
    source_counts.input_count,
    processed.accepted_count,
    processed.rejected_count,
    processed.accepted_count + processed.rejected_count
        AS processed_count,
    source_counts.input_count
        = processed.accepted_count + processed.rejected_count
        AS reconciles
FROM source_counts
JOIN processed
    ON source_counts.dataset = processed.dataset
ORDER BY source_counts.dataset;
