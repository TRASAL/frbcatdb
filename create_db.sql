
CREATE TABLE refs (
                id INT UNSIGNED AUTO_INCREMENT NOT NULL,
                type TEXT,
                reference TEXT,
                link TEXT,
                description TEXT,
                PRIMARY KEY (id)
);


CREATE TABLE radio_obs_params_have_refs (
                radio_obs_param_id INT UNSIGNED NOT NULL,
                reference_id INT UNSIGNED NOT NULL,
                PRIMARY KEY (radio_obs_param_id, reference_id)
);


CREATE TABLE original (
                id INT UNSIGNED AUTO_INCREMENT NOT NULL,
                name VARCHAR(9) DEFAULT '' NOT NULL,
                telescope VARCHAR(32) NOT NULL,
                utc VARCHAR(19),
                beam VARCHAR(8),
                raj VARCHAR(16),
                decj VARCHAR(16),
                gl FLOAT,
                gb FLOAT,
                sampling_time FLOAT,
                bandwidth FLOAT,
                centre_frequency FLOAT,
                dm FLOAT,
                dm_error FLOAT,
                snr FLOAT,
                snr_error FLOAT,
                width FLOAT,
                width_error_upper FLOAT,
                width_error_lower FLOAT,
                flux FLOAT,
                flux_error_upper FLOAT,
                flux_error_lower FLOAT,
                reference_id VARCHAR(8),
                public TINYINT NOT NULL,
                freq_time_plot VARCHAR(256),
                polarization_plot VARCHAR(256),
                dm_galaxy FLOAT,
                dist_comoving FLOAT,
                dist_comoving_error_upper FLOAT,
                dist_comoving_error_lower FLOAT,
                PRIMARY KEY (id)
);


CREATE TABLE frbs (
                id INT UNSIGNED AUTO_INCREMENT NOT NULL,
                name VARCHAR(255) NOT NULL,
                utc TIMESTAMP NOT NULL,
                private TINYINT DEFAULT 0 NOT NULL,
                PRIMARY KEY (id)
);

ALTER TABLE frbs MODIFY COLUMN utc TIMESTAMP COMMENT 'at infinite frequency';


CREATE UNIQUE INDEX name USING BTREE
 ON frbs
 ( name ASC );

CREATE TABLE observations (
                id INT UNSIGNED AUTO_INCREMENT NOT NULL,
                frb_id INT UNSIGNED NOT NULL,
                type TEXT NOT NULL,
                telescope TEXT NOT NULL,
                utc TIMESTAMP NOT NULL,
                data_link TEXT,
                detected TINYINT DEFAULT 0 NOT NULL,
                PRIMARY KEY (id)
);

ALTER TABLE observations MODIFY COLUMN utc TIMESTAMP COMMENT 'start_utc';


CREATE INDEX frb_id USING BTREE
 ON observations
 ( frb_id ASC );

CREATE TABLE radio_obs_params (
                id INT UNSIGNED AUTO_INCREMENT NOT NULL,
                obs_id INT UNSIGNED NOT NULL,
                receiver TEXT,
                backend TEXT,
                beam VARCHAR(8),
                raj VARCHAR(16) DEFAULT '' NOT NULL,
                decj VARCHAR(16) DEFAULT '' NOT NULL,
                gl FLOAT NOT NULL,
                gb FLOAT NOT NULL,
                pointing_error FLOAT NOT NULL,
                FWHM FLOAT NOT NULL,
                sampling_time FLOAT NOT NULL,
                bandwidth FLOAT NOT NULL,
                centre_frequency FLOAT NOT NULL,
                npol INT DEFAULT 2 NOT NULL,
                channel_bandwidth FLOAT NOT NULL,
                bits_per_sample TINYINT NOT NULL,
                gain FLOAT NOT NULL,
                tsys FLOAT NOT NULL,
                ne2001_dm_limit FLOAT NOT NULL,
                PRIMARY KEY (id)
);

ALTER TABLE radio_obs_params MODIFY COLUMN pointing_error FLOAT COMMENT 'pointing accuracy in arcsec';

ALTER TABLE radio_obs_params MODIFY COLUMN FWHM FLOAT COMMENT 'FWHM of beam in arcmin';

ALTER TABLE radio_obs_params MODIFY COLUMN bandwidth FLOAT COMMENT 'in MHz';

ALTER TABLE radio_obs_params MODIFY COLUMN centre_frequency FLOAT COMMENT 'in MHz';

ALTER TABLE radio_obs_params MODIFY COLUMN channel_bandwidth FLOAT COMMENT 'in MHz';

ALTER TABLE radio_obs_params MODIFY COLUMN gain FLOAT COMMENT 'K/Jy';

ALTER TABLE radio_obs_params MODIFY COLUMN tsys FLOAT COMMENT 'K';


CREATE INDEX obs_id USING BTREE
 ON radio_obs_params
 ( obs_id ASC );

CREATE TABLE radio_obs_params_notes (
                id INT UNSIGNED AUTO_INCREMENT NOT NULL,
                radio_obs_param_id INT UNSIGNED NOT NULL,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                author VARCHAR(32) DEFAULT '' NOT NULL,
                note LONGTEXT NOT NULL,
                PRIMARY KEY (id)
);


CREATE INDEX radio_obs_param_id USING BTREE
 ON radio_obs_params_notes
 ( radio_obs_param_id ASC );

CREATE TABLE radio_measured_params (
                id INT UNSIGNED AUTO_INCREMENT NOT NULL,
                obs_params_id INT UNSIGNED NOT NULL,
                dm FLOAT,
                dm_error FLOAT,
                snr FLOAT,
                width FLOAT,
                width_error_upper FLOAT,
                width_error_lower FLOAT,
                flux FLOAT,
                flux_prefix VARCHAR(255) NOT NULL,
                flux_error_upper FLOAT,
                flux_error_lower FLOAT,
                flux_calibrated TINYINT DEFAULT 0 NOT NULL,
                dm_index FLOAT,
                dm_index_error FLOAT,
                scattering_index FLOAT,
                scattering_index_error FLOAT,
                scattering_time FLOAT,
                scattering_time_error FLOAT,
                linear_poln_frac FLOAT,
                linear_poln_frac_error FLOAT,
                circular_poln_frac FLOAT,
                circular_poln_frac_error FLOAT,
                spectral_index FLOAT,
                spectral_index_error FLOAT,
                z_phot FLOAT,
                z_phot_error FLOAT,
                z_spec FLOAT,
                z_spec_error FLOAT,
                rank INT NOT NULL,
                PRIMARY KEY (id)
);

ALTER TABLE radio_measured_params MODIFY COLUMN scattering_time FLOAT COMMENT 'At 1 GHz';


CREATE INDEX obs_params_id USING BTREE
 ON radio_measured_params
 ( obs_params_id ASC );

CREATE TABLE radio_measured_params_notes (
                id INT UNSIGNED AUTO_INCREMENT NOT NULL,
                radio_measured_param_id INT UNSIGNED NOT NULL,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                author VARCHAR(32) DEFAULT '' NOT NULL,
                note LONGTEXT NOT NULL,
                PRIMARY KEY (id)
);


CREATE INDEX radio_measured_param_id USING BTREE
 ON radio_measured_params_notes
 ( radio_measured_param_id ASC );

CREATE TABLE radio_measured_params_have_refs (
                radio_measured_param_id INT UNSIGNED NOT NULL,
                reference_id INT UNSIGNED NOT NULL,
                PRIMARY KEY (radio_measured_param_id, reference_id)
);


CREATE TABLE radio_images (
                id INT UNSIGNED AUTO_INCREMENT NOT NULL,
                radio_obs_params_id INT UNSIGNED NOT NULL,
                title TEXT,
                caption LONGTEXT,
                image LONGBLOB,
                PRIMARY KEY (id)
);


CREATE INDEX radio_images_fk USING BTREE
 ON radio_images
 ( radio_obs_params_id ASC );

CREATE TABLE observations_notes (
                id INT UNSIGNED AUTO_INCREMENT NOT NULL,
                observation_id INT UNSIGNED NOT NULL,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                author VARCHAR(32) DEFAULT '' NOT NULL,
                note LONGTEXT NOT NULL,
                PRIMARY KEY (id)
);


CREATE INDEX observation_id USING BTREE
 ON observations_notes
 ( observation_id ASC );

CREATE TABLE observations_have_refs (
                obs_id INT UNSIGNED NOT NULL,
                reference_id INT UNSIGNED NOT NULL,
                PRIMARY KEY (obs_id, reference_id)
);


CREATE TABLE frbs_notes (
                id INT UNSIGNED AUTO_INCREMENT NOT NULL,
                frb_id INT UNSIGNED NOT NULL,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                author VARCHAR(32) DEFAULT '' NOT NULL,
                note LONGTEXT NOT NULL,
                PRIMARY KEY (id)
);


CREATE INDEX frb_id USING BTREE
 ON frbs_notes
 ( frb_id ASC );

CREATE TABLE frbs_have_refs (
                frb_id INT UNSIGNED NOT NULL,
                reference_id INT UNSIGNED NOT NULL,
                PRIMARY KEY (frb_id, reference_id)
);


ALTER TABLE frbs_have_refs ADD CONSTRAINT refs_frbs_have_refs_fk
FOREIGN KEY (reference_id)
REFERENCES refs (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE observations_have_refs ADD CONSTRAINT refs_observations_have_refs_fk
FOREIGN KEY (reference_id)
REFERENCES refs (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE radio_measured_params_have_refs ADD CONSTRAINT refs_radio_measured_params_have_refs_fk
FOREIGN KEY (reference_id)
REFERENCES refs (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE radio_obs_params_have_refs ADD CONSTRAINT refs_radio_obs_params_have_refs_fk
FOREIGN KEY (reference_id)
REFERENCES refs (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE frbs_have_refs ADD CONSTRAINT frbs_frbs_have_refs_fk
FOREIGN KEY (frb_id)
REFERENCES frbs (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE frbs_notes ADD CONSTRAINT frbs_notes_ibfk_1
FOREIGN KEY (frb_id)
REFERENCES frbs (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE observations ADD CONSTRAINT observations_ibfk_1
FOREIGN KEY (frb_id)
REFERENCES frbs (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE observations_have_refs ADD CONSTRAINT observations_observations_have_refs_fk
FOREIGN KEY (obs_id)
REFERENCES observations (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE observations_notes ADD CONSTRAINT observations_notes_ibfk_1
FOREIGN KEY (observation_id)
REFERENCES observations (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE radio_obs_params ADD CONSTRAINT radio_obs_params_ibfk_1
FOREIGN KEY (obs_id)
REFERENCES observations (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE radio_images ADD CONSTRAINT radio_images_fk
FOREIGN KEY (radio_obs_params_id)
REFERENCES radio_obs_params (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE radio_measured_params ADD CONSTRAINT radio_obs_params_radio_measured_params_fk
FOREIGN KEY (obs_params_id)
REFERENCES radio_obs_params (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE radio_obs_params_notes ADD CONSTRAINT radio_obs_params_radio_obs_params_notes_fk
FOREIGN KEY (radio_obs_param_id)
REFERENCES radio_obs_params (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;


ALTER TABLE radio_obs_params_have_refs ADD CONSTRAINT radio_obs_params_radio_obs_params_have_refs_fk
FOREIGN KEY (radio_obs_param_id)
REFERENCES radio_obs_params (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE radio_measured_params_have_refs ADD CONSTRAINT radio_measured_params_radio_measured_params_have_refs_fk
FOREIGN KEY (radio_measured_param_id)
REFERENCES radio_measured_params (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE radio_measured_params_notes ADD CONSTRAINT radio_measured_params_notes_ibfk_1
FOREIGN KEY (radio_measured_param_id)
REFERENCES radio_measured_params (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;
