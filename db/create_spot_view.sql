CREATE VIEW spot_view AS
select
  f.name as frb_name, f.utc as frb_utc,
  o.type as obs_type, o.telescope as obs_telescope, o.utc as obs_utc,
  rop.receiver as rop_receiver, rop.backend as rop_backend, rop.beam as rop_beam,
  rop.raj as rop_raj, rop.decj as rop_decj, rop.gl as rop_gl, rop.gb as rop_gb,
  rop.pointing_error as rop_pointing_error, rop.FWHM as rop_FWHM,
  rop.sampling_time as rop_sampling_time, rop.bandwidth as rop_bandwidth,
  rop.centre_frequency as rop_centre_frequency, rop.npol as rop_npol,
  rop.channel_bandwidth as rop_channel_bandwidth, rop.bits_per_sample as rop_bits_per_sample,
  rop.gain as rop_gain, rop.tsys as rop_tsys, rop.ne2001_dm_limit as rop_ne2001_dm_limit,
  armp.ivorn as author_ivorn,
  rmp.voevent_ivorn as rmp_voevent_ivorn,rmp.voevent_xml as rmp_voevent_xml,
  rmp.dm as rmp_dm,rmp.dm_error as rmp_dm_error,rmp.snr as rmp_snr,
  rmp.width as rmp_width,rmp.width_error_upper as rmp_width_error_upper,
  rmp.width_error_lower as rmp_width_error_lower,rmp.flux as rmp_flux,
  rmp.flux_prefix as rmp_flux_prefix,rmp.flux_error_upper as rmp_flux_error_upper,
  rmp.flux_error_lower as rmp_flux_error_lower,rmp.flux_calibrated as rmp_flux_calibrated,
  rmp.dm_index as rmp_dm_index,rmp.dm_index_error as rmp_dm_index_error,
  rmp.scattering_index as rmp_scattering_index,rmp.scattering_index_error as rmp_scattering_index_error,
  rmp.scattering_time as rmp_scattering_time,rmp.scattering_time_error as rmp_scattering_time_error,
  rmp.linear_poln_frac as rmp_linear_poln_frac,rmp.linear_poln_frac_error as rmp_linear_poln_frac_error,
  rmp.circular_poln_frac as rmp_circular_poln_frac,rmp.circular_poln_frac_error as rmp_circular_poln_frac_error,
  rmp.spectral_index as rmp_spectral_index,rmp.spectral_index_error as rmp_spectral_index_error,
  rmp.z_phot as rmp_z_phot,rmp.z_phot_error as rmp_z_phot_error,rmp.z_spec as rmp_z_spec,
  rmp.z_spec_error as rmp_z_spec_error,rmp.rank as rmp_rank
FROM frbs f JOIN observations o ON (f.id = o.frb_id)
            JOIN radio_observations_params rop ON (o.id = rop.obs_id)
            JOIN radio_measured_params rmp ON (rop.id = rmp.rop_id)
            JOIN authors armp ON (rmp.author_id = armp.id)
