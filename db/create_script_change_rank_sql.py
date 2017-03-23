#!/usr/bin/env python

def change_rank_item(voevent_ivorn, rank):
  '''
  template to change rank for a voevent_ivorn
  '''
  template = """UPDATE "radio_measured_params"
SET rank = {rank}
WHERE voevent_ivorn = '{voevent_ivorn}';

"""
  # context variables in template
  context = {
    "rank":rank,
    "voevent_ivorn":voevent_ivorn
    }
  return template.format(**context)

def write(sql, filename):
  '''
  write sql statements to filename
  '''
  try:
    with open(filename, "w") as sql_out:
      sql_out.write(sql)
  except IOError as e:
    raise # re-raise exception

if __name__=="__main__":
  # updated ranks created by Emily Emily
  new_ranks = [1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 6, 7, 2,
              2, 2, 2, 2, 2, 2, 1, 1, 1, 3, 5, 2, 2, 2, 2, 2, 2, 3, 4, 5, 6,
              7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

  # create list of voevent_ivorns
  for voevent_ivorn in range(1,55):
    try:
      voevent_ivorns.extend(["ivo://unknown" + str(voevent_ivorn)])
    except NameError:
      voevent_ivorns = ["ivo://unknown" + str(voevent_ivorn)]

  dictionary = dict(zip(voevent_ivorns, new_ranks))
  for key in dictionary:
    try:
      sql += change_rank_item(key, dictionary[key])
    except NameError:
      sql = change_rank_item(key, dictionary[key])

  write(sql, "aa-alert_change_rank.sql")
