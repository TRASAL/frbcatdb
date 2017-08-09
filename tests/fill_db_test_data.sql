INSERT INTO authors VALUES (1,'ivo://unknown',NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO publications VALUES (1,'type 0','Nobody et. no one','http://blah','description!'),(2,'type 1','Doe J. 2016','http://zasca','explanation!'),(3,'type 3','Doe J.','http://anda','description!!');

INSERT INTO frbs VALUES (1,1,'FRB010125','2001-01-24 23:29:14',False),(2,1,'FRB010621','2001-06-21 11:02:09',False),(3,1,'FRB010724','2001-07-24 17:50:00',False);
INSERT INTO frbs_have_publications VALUES (1,1),(1,2),(1,3),(2,3),(3,3);
INSERT INTO frbs_notes VALUES (1,1,'2015-10-19 00:40:02','J. Doe','some note'),(2,2,'2015-10-19 00:36:26','J. Doe','some other note');

INSERT INTO observations VALUES (1,1,1,'type 1','telescope 1','2001-01-24 23:29:14','http://data111/',True),(2,1,1,'type 2','telescope 2','2001-01-24 23:29:54','http://data211/',True),(3,2,1,'type 1','telescope 1','2001-06-21 11:02:09','http://data321/',True),(4,3,1,'type 2','telescope 2','2001-07-24 17:50:00','http://data431/',True);
INSERT INTO observations_have_publications VALUES (1,1),(2,1),(1,2),(2,2),(1,3),(2,3),(3,3),(4,3);
INSERT INTO observations_notes VALUES (1,4,'2016-03-13 05:45:12','J. Doe','some note');

INSERT INTO radio_observations_params VALUES (1,1,1,'settings1','receiver 1','backend 1','beam 1','19:06:53','-40:37:14',356.641,-20.0206,11,0.125,288,1372.5,2,NULL,1,0.69,28,110,NULL,NULL,NULL);
INSERT INTO radio_observations_params VALUES (2,2,1,'settings1','receiver 1','backend 2','beam 2','19:06:53','-40:37:14',356.641,-20.0206,NULL,0.25, NULL,NULL, 2,NULL,2,NULL,NULL,523.5,NULL,NULL,NULL);
INSERT INTO radio_observations_params VALUES (3,3,1,'settings1','receiver 2','backend 1','beam 1','05:07:55','-30:90:21',45.2,NULL,NULL,0.25, NULL,NULL, 1,NULL,2,NULL,NULL,523.5,NULL,NULL,NULL);
INSERT INTO radio_observations_params VALUES (4,4,1,'settings1','receiver 3','backend 1','beam 1','21:21:43','22:32:43',31,NULL,NULL,0.25, NULL,NULL, 2,NULL,2,NULL,NULL,523.5,NULL,NULL,NULL);
INSERT INTO radio_observations_params_have_publications VALUES (1,1),(2,1),(1,2),(2,2),(1,3),(2,3),(3,3),(4,3);
INSERT INTO radio_observations_params_notes VALUES (1,2,'2016-03-13 05:45:12','J. Doe','some note');

INSERT INTO radio_measured_params VALUES (1,1,1,'ivo://unknown:frb1','',790,3,17 ,9.4,0.2,0.2 ,0.3  ,'',NULL,NULL,False,2,0.01,-4.2,1.2,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL);
INSERT INTO radio_measured_params VALUES (2,2,1,'ivo://unknown:frb2','',748,3,18 ,8  ,4  ,2.25,0.53 ,'',0.26,0.09,False,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,2,NULL,NULL,NULL);
INSERT INTO radio_measured_params VALUES (3,3,1,'ivo://unknown:frb3','',375,3,100,20 ,0  ,0,   1.574,'',0,0,False,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,2,NULL,NULL,NULL);
INSERT INTO radio_measured_params VALUES (4,4,1,'ivo://unknown:frb4','',375,3,100,20 ,0  ,0,   1.574,'',0,0,False,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,2,NULL,NULL,NULL);
INSERT INTO radio_measured_params_have_publications VALUES (1,1),(2,1),(1,2),(2,2),(1,3),(2,3),(3,3),(4,3);
INSERT INTO radio_measured_params_notes VALUES (1,3,'2016-03-13 05:45:12','J. Doe','some note');

INSERT INTO radio_images VALUES (1,'Radio Image 1', NULL, NULL), (2,'Radio Image 2', NULL, NULL), (3,'Radio Image 3', NULL, NULL), (4,'Radio Image 4', NULL, NULL);
INSERT INTO radio_images_have_radio_measured_params VALUES (1,1),(1,2),(1,3),(1,4),(2,1),(2,2),(3,3),(4,4);

-- Since we manually inserted IDs, we need to reset the serials
SELECT setval('authors_id_seq', COALESCE((SELECT MAX(id)+1 FROM authors), 1), false);
SELECT setval('publications_id_seq', COALESCE((SELECT MAX(id)+1 FROM publications), 1), false);
SELECT setval('frbs_id_seq', COALESCE((SELECT MAX(id)+1 FROM frbs), 1), false);
SELECT setval('frbs_notes_id_seq', COALESCE((SELECT MAX(id)+1 FROM frbs_notes), 1), false);
SELECT setval('observations_id_seq', COALESCE((SELECT MAX(id)+1 FROM observations), 1), false);
SELECT setval('observations_notes_id_seq', COALESCE((SELECT MAX(id)+1 FROM observations_notes), 1), false);
SELECT setval('radio_observations_params_id_seq', COALESCE((SELECT MAX(id)+1 FROM radio_observations_params), 1), false);
SELECT setval('radio_observations_params_notes_id_seq', COALESCE((SELECT MAX(id)+1 FROM radio_observations_params_notes), 1), false);
SELECT setval('radio_measured_params_id_seq', COALESCE((SELECT MAX(id)+1 FROM radio_measured_params), 1), false);
SELECT setval('radio_measured_params_notes_id_seq', COALESCE((SELECT MAX(id)+1 FROM radio_measured_params_notes), 1), false);
SELECT setval('radio_images_id_seq', COALESCE((SELECT MAX(id)+1 FROM radio_images), 1), false);
