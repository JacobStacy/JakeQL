1: CREATE TABLE students (name TEXT);
1: INSERT INTO students VALUES ('James');
1: BEGIN TRANSACTION;
1: SELECT * FROM students ORDER BY name;
1: DELETE FROM students;
1: SELECT * FROM students ORDER BY name;
1: INSERT INTO students VALUES ('Yaxin');
1: SELECT * FROM students ORDER BY name;
1: UPDATE students SET name = 'Wayne';
1: SELECT * FROM students ORDER BY name;
1: ROLLBACK TRANSACTION;
1: SELECT * FROM students ORDER BY name;
1: INSERT INTO students VALUES ('Li');
1: SELECT * FROM students ORDER BY name;
1: ROLLBACK TRANSACTION;
