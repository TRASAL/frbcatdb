-- -----------------------------------------------------
-- Table radio_observations_params
-- -----------------------------------------------------
ALTER TABLE radio_observations_params ADD COLUMN beam_semi_major_axis DOUBLE PRECISION;
ALTER TABLE radio_observations_params   ADD COLUMN beam_semi_minor_axis DOUBLE PRECISION;
ALTER TABLE radio_observations_params   ADD COLUMN beam_rotation_angle DOUBLE PRECISION;
ALTER TABLE radio_observations_params   RENAME COLUMN ne2001_dm_limit TO mw_dm_limit;
ALTER TABLE radio_observations_params   DROP COLUMN FWHM CASCADE;
ALTER TABLE radio_observations_params ADD COLUMN galactic_electron_model VARCHAR(255);
ALTER TABLE radio_observations_params   DROP COLUMN pointing_error CASCADE;
UPDATE radio_observations_params SET galactic_electron_model='NE2001' where mw_dm_limit is not null;
-- -----------------------------------------------------
-- Table radio_measured_params
-- -----------------------------------------------------
ALTER TABLE radio_measured_params ADD COLUMN rm DOUBLE PRECISION;
ALTER TABLE radio_measured_params  ADD COLUMN rm_error DOUBLE PRECISION;
ALTER TABLE radio_measured_params  RENAME COLUMN scattering_time TO scattering;
ALTER TABLE radio_measured_params  RENAME COLUMN scattering_time_error TO scattering_error;
ALTER TABLE radio_measured_params  DROP COLUMN z_phot CASCADE;
ALTER TABLE radio_measured_params  DROP COLUMN z_phot_error CASCADE;
ALTER TABLE radio_measured_params  DROP COLUMN z_spec CASCADE;
ALTER TABLE radio_measured_params  DROP COLUMN z_spec_error CASCADE;
ALTER TABLE radio_measured_params ADD COLUMN redshift_inferred DOUBLE PRECISION;
ALTER TABLE radio_measured_params ADD COLUMN redshift_host DOUBLE PRECISION;
ALTER TABLE radio_measured_params ADD COLUMN fluence DOUBLE PRECISION;
ALTER TABLE radio_measured_params ADD COLUMN fluence_error_upper DOUBLE PRECISION;
ALTER TABLE radio_measured_params ADD COLUMN fluence_error_lower DOUBLE PRECISION;
ALTER TABLE radio_measured_params ADD COLUMN dispersion_smearing DOUBLE PRECISION;
ALTER TABLE radio_measured_params ADD COLUMN scattering_model VARCHAR(255);
ALTER TABLE radio_measured_params ADD COLUMN scattering_timescale DOUBLE PRECISION;
ALTER TABLE radio_measured_params  DROP COLUMN voevent_xml CASCADE;
UPDATE radio_measured_params SET scattering_model='One-sided exponential' where scattering is not null;

-- -----------------------------------------------------
-- Table observations
-- -----------------------------------------------------
ALTER TABLE observations ADD COLUMN verified boolean NOT NULL DEFAULT FALSE;
UPDATE observations SET verified=TRUE where id>0;
ALTER TABLE observations  DROP COLUMN type CASCADE;
