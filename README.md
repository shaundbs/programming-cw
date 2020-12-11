# programming-cw

## Resources:
### [SQLLITE3:](https://docs.python.org/3/library/sqlite3.html)
1. https://stackoverflow.com/questions/6318126/why-do-you-need-to-create-a-cursor-when-querying-a-sqlite-database
2. To **retrieve data** after executing a SELECT statement, you can either treat the cursor as an **iterator**, call the cursor’s **fetchone()** method to retrieve a single matching row, or call **fetchall()** to get a list of the matching rows.
3. Usually your SQL operations will need to use values from Python variables. You shouldn’t assemble your query using Python’s string operations because doing so is insecure; it makes your program vulnerable to an SQL injection attack (see https://xkcd.com/327/ for humorous example of what can go wrong).
- Instead, use the DB-API’s parameter substitution. Put **?** as a placeholder wherever you want to use a value, and then provide a **tuple** of values as the second argument to the cursor’s execute() method. (Other database modules may use a different placeholder, such as %s or :1.)
### [Bcrypt:](http://zetcode.com/python/bcrypt/)
1. encode before use: line.encode('utf-8'), 
1. salt = **bcrypt.gensalt()**; hashed = **bcrypt.hashpw(passwd, salt)**; if **bcrypt.checkpw(passwd, hashed)**:
### [Tkinter:](https://www.youtube.com/watch?v=YXPyB4XeYLA&feature=youtu.be)
