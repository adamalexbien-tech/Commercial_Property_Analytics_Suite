CREATE TABLE lease_facts AS
SELECT Centre, tenant_name, start_date, end_date, area_sqm, annual_rent, end_year,
    CASE 
        WHEN tenant_name LIKE '%Kmart%' OR tenant_name LIKE '%Target%' OR tenant_name LIKE '%Bunnings%' OR tenant_name LIKE '%Officeworks%' OR tenant_name LIKE '%Priceline%' THEN 'Wesfarmers Group'
        WHEN tenant_name LIKE '%Woolworths%' OR tenant_name LIKE '%Big W%' OR tenant_name LIKE '%Dan Murphys%' OR tenant_name LIKE '%BWS%' THEN 'Woolworths Group'
        WHEN tenant_name LIKE '%Coles%' THEN 'Coles Group'
        WHEN tenant_name LIKE '%Super Retail%' OR tenant_name LIKE '%Rebel%' OR tenant_name LIKE '%Supercheap%' OR tenant_name LIKE '%BCF%' OR tenant_name LIKE '%Macpac%' THEN 'Super Retail Group'
        WHEN tenant_name LIKE '%Anz%' OR tenant_name LIKE '%Commonwealth%' OR tenant_name LIKE '%Nab%' OR tenant_name LIKE '%Westpac%' THEN 'Major Banks'
        ELSE 'Other'
    END as Parent_Group,
    CASE 
        WHEN julianday(end_date) < julianday('2026-01-12') THEN 0
        ELSE (julianday(end_date) - julianday('2026-01-12')) / 365.25 
    END as remaining_years,
    (annual_rent * (
        CASE 
            WHEN julianday(end_date) < julianday('2026-01-12') THEN 0
            ELSE (julianday(end_date) - julianday('2026-01-12')) / 365.25 
        END
    )) as weighted_rent_value,
    (area_sqm * (
        CASE 
            WHEN julianday(end_date) < julianday('2026-01-12') THEN 0
            ELSE (julianday(end_date) - julianday('2026-01-12')) / 365.25 
        END
    )) as weighted_area_value
FROM portfolio_leases;