DELETE FROM cc_pref WHERE keystr = 'system_version';
INSERT INTO cc_pref (keystr, valstr) VALUES ('system_version', '2.5.7');

ALTER TABLE cc_show ALTER COLUMN description TYPE varchar(2048);
ALTER TABLE cc_show_instances ALTER COLUMN description TYPE varchar(2048);
