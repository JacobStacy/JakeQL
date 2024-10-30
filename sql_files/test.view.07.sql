1: CREATE TABLE students (name TEXT, grade REAL);
1: INSERT INTO students VALUES ('James', 2.4), ('Yaxin', 3.5), ('Li', 3.7), ('Robert', 4.0);
1: CREATE VIEW stu_view AS SELECT name FROM students WHERE grade > 3.0 ORDER BY name;
1: CREATE VIEW stu_view2 AS SELECT name FROM students WHERE grade < 3.0 ORDER BY name;
1: UPDATE students SET grade = 6.0 WHERE grade < 3.0;
1: SELECT * FROM stu_view;
1: SELECT * FROM stu_view2;