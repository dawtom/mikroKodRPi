import sqlite3


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
		
        return sqlite3.connect(db_file)
        
    except Error as e:
        print(e)
   
        
        
def main():
	connection = create_connection("/home/pi/Desktop/NRF24L01/pythonsqlite.db")
	c = connection.cursor()
	

	c.execute('''INSERT INTO Arduino_devices VALUES (1234, 2345)''')
	c.execute('''INSERT INTO Arduino_devices VALUES (1234, 2345)''')

	connection.close()

	
 
if __name__ == '__main__':
	main()

