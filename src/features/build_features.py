import os
import sys
import sqlite3
from sqlalchemy import create_engine
#from sqlalchemy.engine.reflection import Inspector
import csv
import pandas as pd
from shutil import copy2

# Create paths to data folders
print("Setting file paths...")

# Create a variable for the project root directory
#proj_root = os.path.join(os.pardir)
proj_root = os.path.join(os.pardir, os.pardir)

# Save the path to the folder that will contain the intermediate data 
# that will be transformed: /data/interim
interim_data_dir = os.path.join(proj_root,
                                "data",
                                "interim")

# Save the path to the SQLite databse containing the untransformed
# Instacart data
db_name = 'instacart_2017_05_01.db'

interim_sqlitedb_path = os.path.join(interim_data_dir,
                                     db_name)

interim_sqlitedb_eng = os.path.join('sqlite:///',
                                    interim_sqlitedb_path)

# Save the path to the SQLite database that will contain the transformed
# Instacart data
db_name_tf = 'instacart_transformed.db'

transformed_sqlitedb_path = os.path.join(interim_data_dir,
                                         db_name_tf)

# Save the engine path to the SQLite database that will contain the 
# transformed Instacart data
transformed_sqlitedb_eng = os.path.join('sqlite:///',
                                        transformed_sqlitedb_path)


# Save the path to the folder that will contain the final,
# processed data: /data/processed
processed_data_dir = os.path.join(proj_root,
                                "data",
                                "processed")

# Save the path to the csv file that will contain the final,
# processed Instacart data
final_csv_name = 'instacart_final.csv'

final_csv_path = os.path.join(processed_data_dir,
                              final_csv_name)


# Put the contents of csv files into a sqlite database
print("Copying the untransformed database...")

# Make a copy of the untransformed database.
copy2(interim_sqlitedb_path, transformed_sqlitedb_path)

# Create a connection to the new database
print("Creating a connection to the new database...")

# Create a sqlite3 connection cursor
conn = sqlite3.connect(transformed_sqlitedb_path)
c = conn.cursor()

# Create an engine to the new SQLite database 
engine = create_engine(transformed_sqlitedb_eng, echo=False)


### Transform the data and create new views and tables
print("Creating new views and tables...")

print("Creating new table 'up_pairs_train'...")

# Create table
c.execute('''CREATE TABLE up_pairs_train AS
             SELECT substr('00'||orders.user_id, -6) || '-' || 
                 substr('0000'||order_products__train.product_id, -6) AS up_pair
             FROM order_products__train
             JOIN orders
             ON orders.order_id = order_products__train.order_id
             GROUP BY up_pair
             ORDER BY user_id ASC, product_id ASC''')

# Save (commit) the changes
conn.commit()

print("Creating new table 'up_pairs_prior'...")

# Create table
c.execute('''CREATE TABLE up_pairs_prior AS
             SELECT substr('00'||orders.user_id, -6) || '-' || 
                 substr('0000'||order_products__prior.product_id, -6) AS up_pair,
                 orders.user_id AS user_id, 
                 order_products__prior.product_id AS product_id,
                 orders.order_number AS order_number
             FROM order_products__prior
             JOIN orders
             ON orders.order_id = order_products__prior.order_id
             ORDER BY user_id ASC, product_id ASC''')

# Save (commit) the changes
conn.commit()

print("Creating new table 'max_order_by_user'...")

# Create table
c.execute('''CREATE TABLE max_order_by_user AS
             SELECT user_id, MAX(order_number) AS max_order_number
             FROM up_pairs_prior
             GROUP BY user_id
             ORDER BY user_id ASC''')

# Save (commit) the changes
conn.commit()

print("Creating new table 'up_pairs_prior_modified'...")

# Create table
c.execute('''CREATE TABLE up_pairs_prior_modified AS
             SELECT up_pairs_prior.*, 
             max_order_by_user.max_order_number,
             (1 + max_order_by_user.max_order_number - up_pairs_prior.order_number) AS order_number_rev
             FROM up_pairs_prior
             JOIN max_order_by_user
             ON max_order_by_user.user_id = up_pairs_prior.user_id''')

# Save (commit) the changes
conn.commit()

print("Creating new table 'first_data_table'...")

# Create table
c.execute('''CREATE TABLE first_data_table AS
             SELECT up_pairs_prior_modified.up_pair AS up_pair,
                 up_pairs_prior_modified.user_id AS user_id, 
                 up_pairs_prior_modified.product_id AS product_id, 
                 CASE WHEN up_pairs_train.up_pair IS NULL THEN 0 ELSE 1 END as 'y',
                 SUM(CASE WHEN (order_number_rev <= 5) THEN 1 ELSE 0 END) AS total_buy_n5,    
                 SUM(CASE WHEN (order_number_rev <= 5) THEN 1 ELSE 0 END) / 5.0 AS total_buy_ratio_n5,                 
                 MAX(order_number_rev) AS max_order_number_rev,
                 CASE WHEN MAX(order_number_rev) > 5
                     THEN (SUM(CASE WHEN (order_number_rev <= 5) THEN 1 ELSE 0 END) / 5.0)
                     ELSE (SUM(CASE WHEN (order_number_rev <= 5) THEN 1 ELSE 0 END) /
                         (MAX(order_number_rev) * 1.0))
                     END AS order_ratio_by_chance_n5                     
             FROM up_pairs_prior_modified
             LEFT JOIN up_pairs_train ON up_pairs_train.up_pair = up_pairs_prior_modified.up_pair
             GROUP BY up_pairs_prior_modified.up_pair''')

# Save (commit) the changes
conn.commit()

print("Creating new view 'n5_view'...")

# Create table
c.execute('''CREATE VIEW n5_view AS
             SELECT user_id, 
                 MAX(order_number) AS order_number_n1,
                 CASE WHEN (MAX(order_number) - 1) < 1 THEN NULL 
                     ELSE (MAX(order_number) - 1) END AS order_number_n2,
                 CASE WHEN (MAX(order_number) - 2) < 1 THEN NULL 
                     ELSE (MAX(order_number) - 2) END AS order_number_n3,
                 CASE WHEN (MAX(order_number) - 3) < 1 THEN NULL 
                     ELSE (MAX(order_number) - 3) END AS order_number_n4,
                 CASE WHEN (MAX(order_number) - 4) < 1 THEN NULL 
                     ELSE (MAX(order_number) - 4) END AS order_number_n5
             FROM orders
             WHERE eval_set = 'prior'
             GROUP BY user_id''')

# Save (commit) the changes
conn.commit()

print("Creating new table 'n5_table'...")

# Create table
c.execute('''CREATE TABLE n5_table AS
             SELECT n5_view.user_id,
                 orders_t1.order_id AS order_id_n1,
                 orders_t2.order_id AS order_id_n2,
                 orders_t3.order_id AS order_id_n3,
                 orders_t4.order_id AS order_id_n4,
                 orders_t5.order_id AS order_id_n5,
                 orders_t1.days_since_prior_order AS days_since_prior_order_n1,
                 orders_t2.days_since_prior_order AS days_since_prior_order_n2,
                 orders_t3.days_since_prior_order AS days_since_prior_order_n3,
                 orders_t4.days_since_prior_order AS days_since_prior_order_n4,
                 orders_t5.days_since_prior_order AS days_since_prior_order_n5
             FROM n5_view
                 LEFT JOIN orders AS orders_t1
                 ON (orders_t1.user_id = n5_view.user_id
                     AND orders_t1.order_number = n5_view.order_number_n1)
                 LEFT JOIN orders AS orders_t2
                 ON (orders_t2.user_id = n5_view.user_id
                     AND orders_t2.order_number = n5_view.order_number_n2)
                 LEFT JOIN orders AS orders_t3
                 ON (orders_t3.user_id = n5_view.user_id
                     AND orders_t3.order_number = n5_view.order_number_n3)
                 LEFT JOIN orders AS orders_t4
                 ON (orders_t4.user_id = n5_view.user_id
                     AND orders_t4.order_number = n5_view.order_number_n4)
                 LEFT JOIN orders AS orders_t5
                 ON (orders_t5.user_id = n5_view.user_id
                     AND orders_t5.order_number = n5_view.order_number_n5)''')

# Save (commit) the changes
conn.commit()

print("Creating new table 'new_table'...")

# Create table
c.execute('''CREATE TABLE new_table AS
             SELECT first_data_table.*,
                 n5_table.order_id_n1,
                 n5_table.order_id_n2,
                 n5_table.order_id_n3,
                 n5_table.order_id_n4,
                 n5_table.order_id_n5
             FROM first_data_table
             LEFT JOIN n5_table
             ON (n5_table.user_id = first_data_table.user_id)
             ''')

# Save (commit) the changes
conn.commit()

print("Creating new table 'new_table_2'...")

# Create table
c.execute('''CREATE TABLE new_table_2 AS
             SELECT new_table.up_pair,
                 new_table.y,
                 new_table.total_buy_n5,
                 new_table.total_buy_ratio_n5,
                 new_table.order_ratio_by_chance_n5,                 
                 n5_table.days_since_prior_order_n1,
                 n5_table.days_since_prior_order_n2,
                 n5_table.days_since_prior_order_n3,
                 n5_table.days_since_prior_order_n4,
                 n5_table.days_since_prior_order_n5,                 
                 CASE WHEN order_products__prior_1.product_id IS NULL THEN 0 ELSE 1 END as bought_n1,
                 CASE WHEN order_products__prior_2.product_id IS NULL THEN 0 ELSE 1 END as bought_n2,
                 CASE WHEN order_products__prior_3.product_id IS NULL THEN 0 ELSE 1 END as bought_n3,
                 CASE WHEN order_products__prior_4.product_id IS NULL THEN 0 ELSE 1 END as bought_n4,
                 CASE WHEN order_products__prior_5.product_id IS NULL THEN 0 ELSE 1 END as bought_n5
             FROM new_table
             LEFT JOIN n5_table
                 ON (n5_table.user_id = new_table.user_id)
             LEFT JOIN order_products__prior AS order_products__prior_1
                 ON (order_products__prior_1.order_id = new_table.order_id_n1
                     AND order_products__prior_1.product_id = new_table.product_id)
             LEFT JOIN order_products__prior AS order_products__prior_2
                 ON (order_products__prior_2.order_id = new_table.order_id_n2
                     AND order_products__prior_2.product_id = new_table.product_id)
             LEFT JOIN order_products__prior AS order_products__prior_3
                 ON (order_products__prior_3.order_id = new_table.order_id_n3
                     AND order_products__prior_3.product_id = new_table.product_id)
             LEFT JOIN order_products__prior AS order_products__prior_4
                 ON (order_products__prior_4.order_id = new_table.order_id_n4
                     AND order_products__prior_4.product_id = new_table.product_id)
             LEFT JOIN order_products__prior AS order_products__prior_5
                 ON (order_products__prior_5.order_id = new_table.order_id_n5
                     AND order_products__prior_5.product_id = new_table.product_id)
             ''')

# Save (commit) the changes
conn.commit()

print("Creating new table 'new_table_3'...")

# Create table
c.execute('''CREATE TABLE new_table_3 AS
             SELECT up_pair, 
                 y, 
                 total_buy_n5, 
                 total_buy_ratio_n5, 
                 order_ratio_by_chance_n5,                 
                 
                 MAX(IFNULL(order_days_n1, 0), 
                     IFNULL(order_days_n2, 0),
                     IFNULL(order_days_n3, 0),
                     IFNULL(order_days_n4, 0),
                     IFNULL(order_days_n5, 0)) AS useritem_order_days_max_n5,
                     
                 CASE WHEN days_since_prior_order_n5 IS NULL THEN
                     MIN(IFNULL(order_days_n1, 1000000), 
                         IFNULL(order_days_n2, 1000000),
                         IFNULL(order_days_n3, 1000000),
                         IFNULL(order_days_n4, 1000000),
                         MAX(IFNULL(order_days_n1, 0), 
                             IFNULL(order_days_n2, 0),
                             IFNULL(order_days_n3, 0),
                             IFNULL(order_days_n4, 0),
                             IFNULL(order_days_n5, 0)))  
                     ELSE
                     MIN(IFNULL(order_days_n1, 1000000), 
                         IFNULL(order_days_n2, 1000000),
                         IFNULL(order_days_n3, 1000000),
                         IFNULL(order_days_n4, 1000000),
                         order_days_n5)
                     END AS useritem_order_days_min_n5

             FROM 
             (
                 SELECT *,
                     CASE WHEN bought_n1 = 0 THEN NULL
                         ELSE days_since_prior_order_n1
                         END AS order_days_n1,
                 
                     CASE WHEN bought_n2 = 0 THEN NULL
                         ELSE CASE WHEN bought_n1 = 0 THEN
                             (days_since_prior_order_n1 + days_since_prior_order_n2)
                             ELSE days_since_prior_order_n2
                             END
                         END AS order_days_n2,
                 
                     CASE WHEN bought_n3 = 0 THEN NULL
                         ELSE 
                         CASE WHEN bought_n2 = 0 THEN 
                             CASE WHEN bought_n1 = 0 THEN
                                 (days_since_prior_order_n1 + days_since_prior_order_n2 +
                                 days_since_prior_order_n3)
                                 ELSE (days_since_prior_order_n2 + days_since_prior_order_n3) 
                                 END                    
                             ELSE days_since_prior_order_n3
                             END
                         END AS order_days_n3,
                         
                     CASE WHEN bought_n4 = 0 THEN NULL
                         ELSE 
                         CASE WHEN bought_n3 = 0 THEN
                             CASE WHEN bought_n2 = 0 THEN
                                 CASE WHEN bought_n1 = 0 THEN
                                     (days_since_prior_order_n1 + days_since_prior_order_n2 +
                                         days_since_prior_order_n3 + days_since_prior_order_n4)
                                     ELSE (days_since_prior_order_n2 + days_since_prior_order_n3 +
                                         days_since_prior_order_n4) 
                                     END                    
                                 ELSE (days_since_prior_order_n3 + days_since_prior_order_n4)
                                 END
                             ELSE days_since_prior_order_n4
                             END
                         END AS order_days_n4,
                         
                     CASE WHEN bought_n4 = 0 THEN
                         CASE WHEN bought_n3 = 0 THEN
                             CASE WHEN bought_n2 = 0 THEN
                                 CASE WHEN bought_n1 = 0 THEN
                                     (days_since_prior_order_n1 + days_since_prior_order_n2 +
                                         days_since_prior_order_n3 + days_since_prior_order_n4 + 
                                         IFNULL(days_since_prior_order_n5, 0))
                                     ELSE (days_since_prior_order_n2 + days_since_prior_order_n3 +
                                         days_since_prior_order_n4 + 
                                         IFNULL(days_since_prior_order_n5, 0)) 
                                     END                    
                                 ELSE (days_since_prior_order_n3 + days_since_prior_order_n4 + 
                                     IFNULL(days_since_prior_order_n5, 0))
                                 END
                             ELSE (days_since_prior_order_n4 + IFNULL(days_since_prior_order_n5, 0))
                             END
                         ELSE IFNULL(days_since_prior_order_n5, 0)
                         END AS order_days_n5
             
                 FROM new_table_2
             )
             GROUP BY up_pair
             ''')

# Save (commit) the changes
conn.commit()


print("Saving 'new_table_3' to 'final_data_table.csv'...")

# Create a list of column names
col_names = [x['name'] for x in Inspector.from_engine(engine).get_columns('new_table_3')]


# Create the csv file that will contain the final, processed Instacart data
data = c.execute("SELECT * FROM new_table_3")
with open(final_csv_path, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(col_names)
    writer.writerows(data)

print("Finished! 'final_data_table.csv' has been created")
