ALTER TABLE frbs DROP COLUMN reference_id;

alter table observations drop foreign key observations_ibfk_2;
ALTER TABLE observations DROP COLUMN reference_id;

alter table radio_obs_params drop foreign key radio_obs_params_ibfk_3;
ALTER TABLE radio_obs_params DROP COLUMN reference_id;

alter table radio_obs_params drop foreign key radio_obs_params_ibfk_2;
ALTER TABLE radio_obs_params DROP COLUMN frb_id;

alter table radio_measured_params drop foreign key radio_measured_params_ibfk_4;
-- TODO: drop index could not recreated because now there are duplicated entries, what was the point of this unique key anyway?
drop index rank_key on radio_measured_params;

ALTER TABLE radio_measured_params DROP COLUMN reference_id;

alter table radio_measured_params drop foreign key radio_measured_params_ibfk_2;
ALTER TABLE radio_measured_params DROP COLUMN frb_id;


ALTER TABLE radio_images DROP COLUMN obs_id;
ALTER TABLE radio_images DROP COLUMN frb_id;

ALTER TABLE radio_images ADD CONSTRAINT radio_images_fk
FOREIGN KEY (radio_obs_params_id)
REFERENCES radio_obs_params (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;
