USE `mag_2017-10`;

SELECT id, arxiv_id, arxiv_title, arxiv_doi, mag_id, category, category_broad
	FROM `arxiv_connect`
	WHERE mag_id IS NOT NULL
	AND category_broad IS NOT NULL
	AND have_xml = TRUE;
