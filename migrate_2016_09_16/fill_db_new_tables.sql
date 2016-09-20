insert into authors (id, ivorn) VALUES (1, "ivo://unknown");

ALTER TABLE publications MODIFY COLUMN id INT unsigned not null;
insert into publications (id, type, reference, link, description) SELECT id, type, reference, link, description from refs;

insert into new_frbs (id, author_id, name, utc, private) select id, 1, name, utc, private from frbs;

insert into new_frbs_notes (id, frb_id, last_modified, author, note) select id, frb_id, last_modified, author, note from frbs_notes;

insert into frbs_have_publications (frb_id,pub_id) select frb_id, reference_id from frbs_have_refs;

insert into new_observations (id, frb_id, author_id, type, telescope, utc, data_link, detected) select id, frb_id, 1, type, telescope, utc, data_link, detected from observations;

insert into new_observations_notes (id, obs_id, last_modified, author, note) select id, observation_id, last_modified, author, note from observations_notes;

insert into observations_have_publications (obs_id,pub_id) select obs_id, reference_id from observations_have_refs;

insert into radio_observed_params (id, obs_id, author_id, receiver, backend, beam, raj, decj, gl, gb, pointing_error, FWHM, sampling_time, bandwidth, centre_frequency, npol, channel_bandwidth, bits_per_sample, gain, tsys, ne2001_dm_limit) select id, obs_id, 1, receiver, backend, beam, raj, decj, gl, gb, pointing_error, FWHM, sampling_time, bandwidth, centre_frequency, npol, channel_bandwidth, bits_per_sample, gain, tsys, ne2001_dm_limit from radio_obs_params;

insert into radio_observed_params_notes (id, rop_id, last_modified, author, note) select id, radio_obs_param_id, last_modified, author, note from radio_obs_params_notes;

insert into radio_observed_params_have_publications (rop_id,pub_id) select radio_obs_param_id, reference_id from radio_obs_params_have_refs;

insert into new_radio_measured_params (id, rop_id, author_id, voevent_ivorn, voevent_xml, dm, dm_error, snr, width, width_error_upper, width_error_lower, flux, flux_prefix, flux_error_upper, flux_error_lower, flux_calibrated, dm_index, dm_index_error, scattering_index, scattering_index_error, scattering_time, scattering_time_error, linear_poln_frac, linear_poln_frac_error, circular_poln_frac, circular_poln_frac_error, spectral_index, spectral_index_error, z_phot, z_phot_error, z_spec, z_spec_error, rank) select id, obs_params_id, 1, "ivo://unknown", "", dm, dm_error, snr, width, width_error_upper, width_error_lower, flux, flux_prefix, flux_error_upper, flux_error_lower, flux_calibrated, dm_index, dm_index_error, scattering_index, scattering_index_error, scattering_time, scattering_time_error, linear_poln_frac, linear_poln_frac_error, circular_poln_frac, circular_poln_frac_error, `spectral index`, `spectral index error`, z_phot, z_phot_error, z_spec, z_spec_error, rank from radio_measured_params;

insert into new_radio_measured_params_notes (id, rmp_id, last_modified, author, note) select id, radio_measured_param_id, last_modified, author, note from radio_measured_params_notes;

insert into radio_measured_params_have_publications (rmp_id, pub_id) select radio_measured_param_id,reference_id from radio_measured_params_have_refs;

insert into new_radio_images (id, rmp_id, title, caption, image) select id, radio_obs_params_id, title, caption, image from radio_images;
