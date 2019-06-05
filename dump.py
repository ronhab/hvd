import psycopg2
import psycopg2.extensions
import numpy as np
import json

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)


class Data:
    def __init__(self, config):
        self.cur = psycopg2.connect(config).cursor()

    def fetch(self, sql):
        self.cur.execute(sql)
        return self.cur.fetchall()


if __name__ == "__main__":
    query_all = """
        select
          c.*,
          r.*
        from export.commits as c
        left join export.repositories as r
        on c.repository_id = r.id
    """
    query_vulnerable = """
        select
              c.*,
              r.*
        from export.commits as c
        left join export.repositories as r
        on c.repository_id = r.id
        where c.type = 'blamed_commit'
        limit 40;
    """
    query_unclassified = """
        select
              c.*,
              r.*
        from export.commits as c
        left join export.repositories as r
        on c.repository_id = r.id
        where c.type != 'blamed_commit'
        limit 800;
    """
    with open("var/db_config.json", "r") as config_file:
        json_config = json.loads(config_file.read())
    data = Data("dbname={0} host={1} port={2} user={3}".format(json_config["dbname"], json_config["host"], json_config["port"], json_config["user"]))
    # rows = data.fetch(query_all)
    # np.savez_compressed("var/vcc_data.npz", np.array(rows))
    vcc = data.fetch(query_vulnerable)
    ucc = data.fetch(query_unclassified)
    sample = np.concatenate([vcc, ucc])
    np.random.shuffle(sample)
    np.savez_compressed("var/vcc_data_40x800.npz", sample)
