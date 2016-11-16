# -*- coding:utf-8 -*-
import json
import psycopg2
from flask import Flask, request, render_template
from pyfrbcatdb import dbase as dbase

conn, cursor = dbase.connectToDB()
conn.close()

app = Flask(__name__)
app.secret_key = 'Super secret key made up on a monday morning somewhere in a cloudy country, just before leaving to a sunny country ;)...sorry guys'

@app.route('/')
def index():
    col_frbs = ['Event','Telescope','UTC','Obs. setting','RA','Dec','Author','VOEvent',
                'DM','SNR','Width',]
    return render_template('index.html', columns_frbs = col_frbs)

@app.route('/_showFRBs')
def show_FRBs():
    conn, cursor = dbase.connectToDB(dbCursor=psycopg2.extensions.cursor)
    cursor.execute("""
        SELECT f.name,
               o.telescope,to_char(o.utc, 'YYYYMMDD-HH24:MI:SS'),
               rop.settings_id,rop.raj,rop.decj,
               armp.ivorn,rmp.voevent_ivorn,rmp.dm,rmp.snr,rmp.width
        FROM frbs f JOIN observations o ON (f.id = o.frb_id)
                    JOIN radio_observations_params rop ON (o.id = rop.obs_id)
                    JOIN radio_measured_params rmp ON (rop.id = rmp.rop_id)
                    JOIN authors armp ON (rmp.author_id = armp.id)
        ORDER BY f.name,o.utc""")
    data = cursor.fetchall()
    conn.close()
    dataToJSON = {"aaData": data}
    return json.dumps(dataToJSON)

@app.route('/_showObservations',methods=['GET'])
def show_Observations():
    frbName = request.args['frb_name']
    conn, cursor = dbase.connectToDB(dbCursor=psycopg2.extensions.cursor)
    cursor.execute("""
        SELECT f.name,
               a.ivorn,
               o.type,o.telescope,to_char(o.utc, 'YYYYMMDD-HH24:MI:SS'),
               o.data_link,o.detected
        FROM frbs f JOIN observations o on (f.id = o.frb_id)
                    JOIN authors a on (o.author_id = a.id)
        WHERE f.name = %s
        ORDER BY o.utc""", (frbName, ))
    data = cursor.fetchall()
    conn.close()
    dataToJSON = {"aaData": data}
    return json.dumps(dataToJSON)

@app.route('/_showROPs',methods=['GET'])
def show_ROPs():
    frbName = request.args['frb_name']
    conn, cursor = dbase.connectToDB(dbCursor=psycopg2.extensions.cursor)
    cursor.execute("""
        SELECT f.name,
               a.ivorn,
               o.telescope,to_char(o.utc, 'YYYYMMDD-HH24:MI:SS'),
               rop.settings_id,rop.receiver,rop.backend,rop.beam,rop.raj,rop.decj,rop.gl,
               rop.gb,rop.pointing_error,rop.FWHM,rop.sampling_time,rop.bandwidth,
               rop.centre_frequency,rop.npol,rop.channel_bandwidth,rop.bits_per_sample,rop.gain,
               rop.tsys,rop.ne2001_dm_limit
        FROM frbs f JOIN observations o on (f.id = o.frb_id)
                    JOIN radio_observations_params rop on (o.id = rop.obs_id)
                    JOIN authors a on (rop.author_id = a.id)
        WHERE f.name = %s
        ORDER BY o.utc, rop.settings_id""", (frbName, ))
    data = cursor.fetchall()
    conn.close()
    dataToJSON = {"aaData": data}
    return json.dumps(dataToJSON)


@app.route('/_showRMPs',methods=['GET'])
def show_RMPs():
    frbName = request.args['frb_name']
    conn, cursor = dbase.connectToDB(dbCursor=psycopg2.extensions.cursor)
    cursor.execute("""
        SELECT f.name,
               a.ivorn,
               o.telescope,to_char(o.utc, 'YYYYMMDD-HH24:MI:SS'),
               rop.settings_id,
               rmp.voevent_ivorn,
               rmp.dm::text || '&plusmn' || rmp.dm_error::text,
               rmp.snr,
               '<span>' ||  rmp.width::text || '</span><span class=''subsup''><sup>+' || rmp.width_error_upper::text || '</sup><sub>-'|| rmp.width_error_lower::text || '</sub></span>',
               rmp.flux_prefix,
               '<span>' ||  rmp.flux::text || '</span><span class=''subsup''><sup>+' || rmp.flux_error_upper::text || '</sup><sub>-'|| rmp.flux_error_lower::text || '</sub></span>',
               rmp.flux_calibrated,
               rmp.dm_index::text || '&plusmn' || rmp.dm_index_error::text,
               rmp.scattering_index::text || '&plusmn' || rmp.scattering_index_error::text,
               rmp.scattering_time::text || '&plusmn' || rmp.scattering_time_error::text,
               rmp.linear_poln_frac::text || '&plusmn' || rmp.linear_poln_frac_error::text,
               rmp.circular_poln_frac::text || '&plusmn' || rmp.circular_poln_frac_error::text,
               rmp.spectral_index::text || '&plusmn' || rmp.spectral_index_error::text,
               rmp.z_phot::text || '&plusmn' || rmp.z_phot_error::text,
               rmp.z_spec::text || '&plusmn' || rmp.z_spec_error::text,
               rmp.rank
        FROM frbs f JOIN observations o on (f.id = o.frb_id)
                    JOIN radio_observations_params rop on (o.id = rop.obs_id)
                    JOIN radio_measured_params rmp on (rmp.rop_id = rop.id)
                    JOIN authors a on (rmp.author_id = a.id)
        WHERE f.name = %s
        ORDER BY o.utc, rop.settings_id,rmp.voevent_ivorn""", (frbName, ))
    data = cursor.fetchall()
    conn.close()
    dataToJSON = {"aaData": data}
    return json.dumps(dataToJSON)


@app.route('/showFRB',methods=['GET'])
def show_FRB():
    frbName = request.args['frb_name']
    col_obss = ['Event', 'Author', 'Type', 'Telescope', 'UTC', 'Data', 'Detected']
    col_rops = ['Event','Author','Telescope','UTC','Obs. setting','Receiver','Backend','Beam',
                'RA','Dec','gl','gb','Pointing error','FWHM','Sampling time','Bandwidth',
                'Centre Freq.','Num. pol.','Channel Bandwidth','Bits per sample','Gain',
                'TSys','Ne 2001 DM limit']
    col_rmps = ['Event','Author','Telescope','UTC','Obs. setting','VOEvent','DM','SNR','Width',
                'Flux prefix','Flux','Flux calibrated','DM index','Scattering index','Scattering time',
                'Linear poln frac','Circular poln frac','Spectral index','Z phot','Z spec','rank']

    return render_template('frb.html', frb_name = frbName, columns_observations = col_obss, columns_rops =  col_rops, columns_rmps = col_rmps)

@app.route('/showVOEvent',methods=['GET'])
def show_VO_event():
    voEventIvorn = request.args['vo_event_ivorn']
    conn, cursor = dbase.connectToDB(dbCursor=psycopg2.extensions.cursor)
    cursor.execute("SELECT voevent_xml from radio_measured_params where voevent_ivorn = %s", (voEventIvorn,))
    xmlData = cursor.fetchone()[0]
    return render_template('voevent.html', vo_event_xml = xmlData)


if __name__ == '__main__':
    app.run()
