# Authors
CREATE TABLE authors (
  id INT UNSIGNED AUTO_INCREMENT NOT NULL,
  ivorn VARCHAR(255) NOT NULL,
  title TINYTEXT,
  logo_url TINYTEXT,
  short_name TINYTEXT,
  contact_name TINYTEXT,
  contact_email TINYTEXT,
  contact_phone TINYTEXT,
  other_information TEXT,
  PRIMARY KEY (id)
);
CREATE UNIQUE INDEX authors_ivorn_idx ON authors ( ivorn );

# References (to publications)
CREATE TABLE publications (
  id INT UNSIGNED AUTO_INCREMENT NOT NULL,
  type TEXT,
  reference TEXT,
  link TEXT,
  description TEXT,
  PRIMARY KEY (id)
);

# FRBs
CREATE TABLE new_frbs (
  id INT UNSIGNED AUTO_INCREMENT NOT NULL,
  author_id INT UNSIGNED NOT NULL,
  name VARCHAR(255) NOT NULL,
  utc DATETIME NOT NULL,
  private TINYINT DEFAULT 0 NOT NULL,
  PRIMARY KEY (id)
);
ALTER TABLE new_frbs MODIFY COLUMN utc TIMESTAMP COMMENT 'at infinite frequency';
CREATE UNIQUE INDEX frbs_name_idx USING BTREE ON new_frbs ( name ASC );
ALTER TABLE new_frbs ADD CONSTRAINT frbs_author_id_fk
FOREIGN KEY (author_id)
REFERENCES authors (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

CREATE TABLE new_frbs_notes (
  id INT UNSIGNED AUTO_INCREMENT NOT NULL,
  frb_id INT UNSIGNED NOT NULL,
  last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  author VARCHAR(32) DEFAULT '' NOT NULL,
  note LONGTEXT NOT NULL,
  PRIMARY KEY (id)
);
ALTER TABLE new_frbs_notes ADD CONSTRAINT frbs_notes_frb_id_fk
FOREIGN KEY (frb_id)
REFERENCES new_frbs (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

CREATE TABLE frbs_have_publications (
  frb_id INT UNSIGNED NOT NULL,
  pub_id INT UNSIGNED NOT NULL,
  PRIMARY KEY (frb_id, pub_id)
);
ALTER TABLE frbs_have_publications ADD CONSTRAINT frbs_have_publications_pub_id_fk
FOREIGN KEY (pub_id)
REFERENCES publications (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;
ALTER TABLE frbs_have_publications ADD CONSTRAINT frbs_have_publications_frb_id_fk
FOREIGN KEY (frb_id)
REFERENCES new_frbs (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

# Observations
CREATE TABLE new_observations (
  id INT UNSIGNED AUTO_INCREMENT NOT NULL,
  frb_id INT UNSIGNED NOT NULL,
  author_id INT UNSIGNED NOT NULL,
  type TEXT NOT NULL,
  telescope TEXT NOT NULL,
  utc DATETIME NOT NULL,
  data_link TEXT,
  detected TINYINT DEFAULT 0 NOT NULL,
  PRIMARY KEY (id)
);
ALTER TABLE new_observations MODIFY COLUMN utc DATETIME COMMENT 'start_utc';
ALTER TABLE new_observations ADD CONSTRAINT observations_author_id_fk
FOREIGN KEY (author_id)
REFERENCES authors (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;
ALTER TABLE new_observations ADD CONSTRAINT observations_frb_id_fk
FOREIGN KEY (frb_id)
REFERENCES new_frbs (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

CREATE TABLE new_observations_notes (
  id INT UNSIGNED AUTO_INCREMENT NOT NULL,
  obs_id INT UNSIGNED NOT NULL,
  last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  author VARCHAR(32) DEFAULT '' NOT NULL,
  note LONGTEXT NOT NULL,
  PRIMARY KEY (id)
);
ALTER TABLE new_observations_notes ADD CONSTRAINT observations_notes_obs_id_fk
FOREIGN KEY (obs_id)
REFERENCES new_observations (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

CREATE TABLE observations_have_publications (
  obs_id INT UNSIGNED NOT NULL,
  pub_id INT UNSIGNED NOT NULL,
  PRIMARY KEY (obs_id, pub_id)
);
ALTER TABLE observations_have_publications ADD CONSTRAINT observations_have_publications_pub_id_fk
FOREIGN KEY (pub_id)
REFERENCES publications (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;
ALTER TABLE observations_have_publications ADD CONSTRAINT observations_have_publications_obs_id_fk
FOREIGN KEY (obs_id)
REFERENCES new_observations (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

# Radio observed parameters
CREATE TABLE radio_observed_params (
  id INT UNSIGNED AUTO_INCREMENT NOT NULL,
  obs_id INT UNSIGNED NOT NULL,
  author_id INT UNSIGNED NOT NULL,
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
ALTER TABLE radio_observed_params MODIFY COLUMN pointing_error FLOAT COMMENT 'pointing accuracy in arcsec';
ALTER TABLE radio_observed_params MODIFY COLUMN FWHM FLOAT COMMENT 'FWHM of beam in arcmin';
ALTER TABLE radio_observed_params MODIFY COLUMN bandwidth FLOAT COMMENT 'in MHz';
ALTER TABLE radio_observed_params MODIFY COLUMN centre_frequency FLOAT COMMENT 'in MHz';
ALTER TABLE radio_observed_params MODIFY COLUMN channel_bandwidth FLOAT COMMENT 'in MHz';
ALTER TABLE radio_observed_params MODIFY COLUMN gain FLOAT COMMENT 'K/Jy';
ALTER TABLE radio_observed_params MODIFY COLUMN tsys FLOAT COMMENT 'K';
ALTER TABLE radio_observed_params ADD CONSTRAINT radio_observed_params_author_id_fk
FOREIGN KEY (author_id)
REFERENCES authors (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;
ALTER TABLE radio_observed_params ADD CONSTRAINT radio_observed_params_obs_id_fk
FOREIGN KEY (obs_id)
REFERENCES new_observations (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

CREATE TABLE radio_observed_params_notes (
  id INT UNSIGNED AUTO_INCREMENT NOT NULL,
  rop_id INT UNSIGNED NOT NULL,
  last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  author VARCHAR(32) DEFAULT '' NOT NULL,
  note LONGTEXT NOT NULL,
  PRIMARY KEY (id)
);
ALTER TABLE radio_observed_params_notes ADD CONSTRAINT radio_observed_params_notes_rop_id_fk
FOREIGN KEY (rop_id)
REFERENCES radio_observed_params (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

CREATE TABLE radio_observed_params_have_publications (
  rop_id INT UNSIGNED NOT NULL,
  pub_id INT UNSIGNED NOT NULL,
  PRIMARY KEY (rop_id, pub_id)
);
ALTER TABLE radio_observed_params_have_publications ADD CONSTRAINT radio_observed_params_have_publications_pub_id_fk
FOREIGN KEY (pub_id)
REFERENCES publications (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;
ALTER TABLE radio_observed_params_have_publications ADD CONSTRAINT radio_observed_params_have_publications_rop_id_fk
FOREIGN KEY (rop_id)
REFERENCES radio_observed_params (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

# Radio measured parameters
CREATE TABLE new_radio_measured_params (
  id INT UNSIGNED AUTO_INCREMENT NOT NULL,
  rop_id INT UNSIGNED NOT NULL,
  author_id INT UNSIGNED NOT NULL,
  voevent_ivorn VARCHAR(255) NOT NULL,
  voevent_xml LONGTEXT NOT NULL,
  dm FLOAT,
  dm_error FLOAT,
  snr FLOAT,
  width FLOAT,
  width_error_upper FLOAT,
  width_error_lower FLOAT,
  flux FLOAT,
  flux_prefix TINYTEXT NOT NULL,
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
ALTER TABLE new_radio_measured_params MODIFY COLUMN scattering_time FLOAT COMMENT 'At 1 GHz';
ALTER TABLE new_radio_measured_params ADD CONSTRAINT radio_measured_params_rop_id_fk
FOREIGN KEY (rop_id)
REFERENCES radio_observed_params (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;
ALTER TABLE new_radio_measured_params ADD CONSTRAINT radio_measured_params_author_id_fk
FOREIGN KEY (author_id)
REFERENCES authors (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

CREATE TABLE new_radio_measured_params_notes (
  id INT UNSIGNED AUTO_INCREMENT NOT NULL,
  rmp_id INT UNSIGNED NOT NULL,
  last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  author VARCHAR(32) DEFAULT '' NOT NULL,
  note LONGTEXT NOT NULL,
  PRIMARY KEY (id)
);
ALTER TABLE new_radio_measured_params_notes ADD CONSTRAINT radio_measured_params_notes_rmp_id_fk
FOREIGN KEY (rmp_id)
REFERENCES new_radio_measured_params (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

CREATE TABLE radio_measured_params_have_publications (
  rmp_id INT UNSIGNED NOT NULL,
  pub_id INT UNSIGNED NOT NULL,
  PRIMARY KEY (rmp_id, pub_id)
);
ALTER TABLE radio_measured_params_have_publications ADD CONSTRAINT radio_measured_params_have_publications_rmp_id_fk
FOREIGN KEY (rmp_id)
REFERENCES new_radio_measured_params (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;
ALTER TABLE radio_measured_params_have_publications ADD CONSTRAINT radio_measured_params_have_publications_pub_id_fk
FOREIGN KEY (pub_id)
REFERENCES publications (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

# Images
CREATE TABLE new_radio_images (
  id INT UNSIGNED AUTO_INCREMENT NOT NULL,
  rmp_id INT UNSIGNED  NOT NULL,
  title TEXT,
  caption LONGTEXT,
  image LONGBLOB,
  PRIMARY KEY (id)
);
ALTER TABLE new_radio_images ADD CONSTRAINT radio_images_rmp_id_fk
FOREIGN KEY (rmp_id)
REFERENCES new_radio_measured_params (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;
