DELETE FROM cc_pref WHERE keystr = 'system_version';
INSERT INTO cc_pref (keystr, valstr) VALUES ('system_version', '2.5.8');

ALTER TABLE cc_show ADD COLUMN logo bytea DEFAULT ''; 
ALTER TABLE cc_show_instances ADD COLUMN logo bytea DEFAULT '';