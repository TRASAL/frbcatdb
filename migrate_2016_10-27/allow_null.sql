ALTER TABLE frbs_notes MODIFY note LONGTEXT NULL;
ALTER TABLE observations_notes MODIFY note LONGTEXT NULL;
ALTER TABLE radio_observations_params_notes MODIFY note LONGTEXT NULL;
ALTER TABLE radio_measured_params_notes MODIFY note LONGTEXT NULL;

ALTER TABLE observations MODIFY type TEXT NULL;

ALTER TABLE radio_observations_params MODIFY gl FLOAT NULL;
ALTER TABLE radio_observations_params MODIFY gb FLOAT NULL;
ALTER TABLE radio_observations_params MODIFY sampling_time FLOAT NULL;
ALTER TABLE radio_observations_params MODIFY bits_per_sample TINYINT NULL;
ALTER TABLE radio_observations_params MODIFY ne2001_dm_limit FLOAT NULL;

ALTER TABLE radio_measured_params MODIFY flux_prefix VARCHAR(255) NULL;
ALTER TABLE radio_measured_params MODIFY rank INTEGER NULL;

