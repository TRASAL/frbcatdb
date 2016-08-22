CREATE TABLE frbs_have_refs (
                frb_id INT UNSIGNED NOT NULL,
                reference_id INT UNSIGNED NOT NULL,
                PRIMARY KEY (frb_id, reference_id)
);

CREATE TABLE observations_have_refs (
                obs_id INT UNSIGNED NOT NULL,
                reference_id INT UNSIGNED NOT NULL,
                PRIMARY KEY (obs_id, reference_id)
);

CREATE TABLE radio_obs_params_have_refs (
                radio_obs_param_id INT UNSIGNED NOT NULL,
                reference_id INT UNSIGNED NOT NULL,
                PRIMARY KEY (radio_obs_param_id, reference_id)
);

CREATE TABLE radio_measured_params_have_refs (
                radio_measured_param_id INT UNSIGNED NOT NULL,
                reference_id INT UNSIGNED NOT NULL,
                PRIMARY KEY (radio_measured_param_id, reference_id)
);



ALTER TABLE frbs_have_refs ADD CONSTRAINT refs_frbs_have_refs_fk
FOREIGN KEY (reference_id)
REFERENCES refs (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE frbs_have_refs ADD CONSTRAINT frbs_frbs_have_refs_fk
FOREIGN KEY (frb_id)
REFERENCES frbs (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;


ALTER TABLE observations_have_refs ADD CONSTRAINT refs_observations_have_refs_fk
FOREIGN KEY (reference_id)
REFERENCES refs (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE observations_have_refs ADD CONSTRAINT observations_observations_have_refs_fk
FOREIGN KEY (obs_id)
REFERENCES observations (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;


ALTER TABLE radio_obs_params_have_refs ADD CONSTRAINT refs_radio_obs_params_have_refs_fk
FOREIGN KEY (reference_id)
REFERENCES refs (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE radio_obs_params_have_refs ADD CONSTRAINT radio_obs_params_radio_obs_params_have_refs_fk
FOREIGN KEY (radio_obs_param_id)
REFERENCES radio_obs_params (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;


ALTER TABLE radio_measured_params_have_refs ADD CONSTRAINT refs_radio_measured_params_have_refs_fk
FOREIGN KEY (reference_id)
REFERENCES refs (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE radio_measured_params_have_refs ADD CONSTRAINT radio_measured_params_radio_measured_params_have_refs_fk
FOREIGN KEY (radio_measured_param_id)
REFERENCES radio_measured_params (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;
