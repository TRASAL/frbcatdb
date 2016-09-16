CREATE TABLE radio_images_have_radio_measured_params (
  radio_image_id INT UNSIGNED NOT NULL,
  rmp_id INT UNSIGNED NOT NULL,
  PRIMARY KEY (radio_image_id, rmp_id)
);
ALTER TABLE radio_images_have_radio_measured_params ADD CONSTRAINT radio_images_have_radio_measured_params_radio_image_id_fk
FOREIGN KEY (radio_image_id)
REFERENCES radio_images (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;
ALTER TABLE radio_images_have_radio_measured_params ADD CONSTRAINT radio_images_have_radio_measured_params_rmp_id_fk
FOREIGN KEY (rmp_id)
REFERENCES radio_measured_params (id)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE radio_images DROP FOREIGN KEY `radio_images_rmp_id_fk`;
ALTER TABLE radio_images DROP COLUMN rmp_id;
